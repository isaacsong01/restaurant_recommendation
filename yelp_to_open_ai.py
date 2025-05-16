import pandas as pd
import json
import os
from openai import OpenAI
from typing import List, Dict, Any

json_path = '/Users/isaac/Documents/Python/restaurant_recommendation_project/yelp_data_20250506_080923.json'


def load_json(json_path):
    """
    Load Yelp data from a JSON file.

    Args:
        json_path: Path to the JSON file.

    Returns:
        List of restaurant data dictionaries.
    """
    # First opens the the json file in read mode. It then loads the data into a variable called data.
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)

        # if the data instance is a list, it returns the data as is.
        if isinstance(data, list):
            return data
        # if the data instance is a dictionary, it reutns the data with the key 'restaurants'.
        if isinstance(data, dict) and "restaurants" in data:
            return data['restaurants']
        # if the data is neither a list or discttionary, it raises a ValueError.
        raise ValueError(f"Unexcpected JSON structure in {json_path}.")
    
    # If there is an error in opening the file, it prints the error message and returns an empty list.
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return []

def preprocess_for_llm(restraunts: List[Dict[str, Any]], max_restaurants: int = 3):
    """ 
    Prepare Yelp restaurant data for LLM analysis by extracting relevant infor and limiting the volume to stay within the token limits.
    
    Args:
        restruants: List of restaurant data dictionaries
        max_restaurants: Maximum number of restaurants to include in the output.
        
    Returns:
        List of preprocessed restaurant dictionaries with key information.
    """
    # Limit the number of restaurant to the max_restaurants parameter if needed.
    restaurant_batch = restraunts[:max_restaurants] if len(restraunts) > max_restaurants else restraunts

    processed_data = []
    for restaurant in restaurant_batch:
        # Extract impoortant information from the restaurant data.
        processed_restaurant = {
            "name": restaurant.get("name"),
            "rating": restaurant.get("rating"),
            "reviews_count": restaurant.get("reviews_count"),
            "price": restaurant.get("price"),
            "categories": restaurant.get("categories"),
            "neighborhood": restaurant.get("neighborhood"),

        }
        # Add highlights if available.
        if "highlights" in restaurant and restaurant["highlights"]:
            processed_restaurant["highlights"] = restaurant["highlights"]
        # Add review data if available
        if "reviews_data" in restaurant and restaurant["reviews_data"]:
            review = restaurant["reviews_data"]
            # Limit the number of reviews to 3 
            sample_reviews = review[:3]
            # Create a processed review list to store processed reviews
            processed_reviews = []
            for review in sample_reviews:
                # Extract key information from the review data such as rating and comments
                processed_review = {
                    "rating": review.get("rating",0),
                }

                if "comment" in review and isinstance(review["comment"], dict):
                    processed_review["text"]  = review["comment"].get("text","")
                else:
                    processed_review["text"] = review.get("text","")
                # Add max 3 reviews to the processed reviews list
                processed_reviews.append(processed_review)
            # Add the procssed_review in the processed review list to the processed resetaurant dictionary.
            processed_restaurant["sample_reviews"] = processed_reviews
        # Add the processed restaurant to the processed data list.
        processed_data.append(processed_restaurant)

    return processed_data
    

def convert_json_to_dataframe(restaurants: List[Dict[str, Any]]):
    """
    Convert a list of restaurant dictionaries to a pandas DataFrame.
    
    Args:
        restaurants: List of restaurant data dictionaries.
        
    Returns:
        Pandas Dataframe conainting the resturant data.
    """
    # Created a flattened version of the data for a DataFrame.
    flattened_data = []

    for restaurant in restaurants:
        flat_restaurant = restaurant.copy()

        for key, value in flat_restaurant.items():
            # If the value is a list or dict, convert it to a json string object. If its not, it will be added to the flattened data as is.
            if isinstance(value, (dict,list)):
                flat_restaurant[key] = json.dumps(value)
        
        flattened_data.append(flat_restaurant)

    return pd.DataFrame(flat_restaurant)

def filter_restaurants(restaurants: List[Dict[str, Any]],
                       min_rating: float = 0,
                       categories: List[str] = None,
                       neighborhood: str = None):
     
    """"
    Filter restaurants based on rating, categories, and neighborhood.
    
    Args:
        restaurants: List of restaurant data disctionaries.
        min_rating: Minimum rating to include
        categories: List of categories to filter by (any match)
        neighborhood: Specific neighborhood to filter by.
        
    Returns:
        Filtered list of restaurant dictionaries.
    """
    filtered = []

    for restaurant in restaurants:
        # Check rating
        if restaurant.get("rating", 0) < min_rating:
            continue

        # Check categories
        if categories:
            restaurant_categories = restaurant.get("categories", [])
            # If restaurant_categories is a string, convert to list
            if isinstance(restaurant_categories, str):
                try:
                    restaurant_categories = json.loads(restaurant_categories)
                except:
                    restaurant_categories = [restaurant_categories]
             # Check if any category matches
            if not any(cat in restaurant_categories for cat in categories):
                continue
        

        # Check neighborhood
        if neighborhood and restaurant.get("neighborhood") != neighborhood:
            continue

        filtered.append(restaurant)

    return filtered

def get_top_restaurants(restaurants: List[Dict[str, Any]], 
                       count: int = 5, 
                       sort_by: str = "rating") -> List[Dict[str, Any]]:
    """
    Get top restaurants sorted by specified criteria
    
    Args:
        restaurants: List of restaurant data dictionaries
        count: Number of top restaurants to return
        sort_by: Field to sort by ('rating', 'reviews', etc.)
        
    Returns:
        List of top restaurant dictionaries
    """
    # Convert to DataFrame for easier sorting
    df = convert_json_to_dataframe(restaurants)
    
    # Sort by the specified column
    if sort_by in df.columns:
        df_sorted = df.sort_values(by=sort_by, ascending=False)
        
        # Convert back to list of dictionaries
        top_restaurants = df_sorted.head(count).to_dict('records')
        
        # Convert string representations back to objects
        for restaurant in top_restaurants:
            for key, value in restaurant.items():
                if isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
                    try:
                        restaurant[key] = json.loads(value)
                    except:
                        pass  # Keep as string if can't be parsed
        
        return top_restaurants
    else:
        print(f"Warning: Sort field '{sort_by}' not found. Returning unsorted restaurants.")
        return restaurants[:count]

def analyze_reviews_distribution(restaurants: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze the distribution of reviews across restaurants
    
    Args:
        restaurants: List of restaurant data dictionaries
        
    Returns:
        Dictionary with analysis of reviews distribution
    """
    # Extract ratings and review counts
    ratings = [restaurant.get("rating", 0) for restaurant in restaurants]
    review_counts = [restaurant.get("reviews", 0) for restaurant in restaurants]
    
    # Calculate statistics
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    avg_reviews = sum(review_counts) / len(review_counts) if review_counts else 0
    max_reviews = max(review_counts) if review_counts else 0
    min_reviews = min(review_counts) if review_counts else 0
    
    # Count restaurants by rating range
    rating_ranges = {
        "5-star": sum(1 for r in ratings if r >= 4.75),
        "4.5-5": sum(1 for r in ratings if 4.5 <= r < 4.75),
        "4-4.5": sum(1 for r in ratings if 4.0 <= r < 4.5),
        "3.5-4": sum(1 for r in ratings if 3.5 <= r < 4.0),
        "3-3.5": sum(1 for r in ratings if 3.0 <= r < 3.5),
        "below-3": sum(1 for r in ratings if r < 3.0)
    }
    
    return {
        "total_restaurants": len(restaurants),
        "average_rating": round(avg_rating, 2),
        "average_reviews": round(avg_reviews, 2),
        "max_reviews": max_reviews,
        "min_reviews": min_reviews,
        "rating_distribution": rating_ranges
    }

def extract_sample_from_all_restaurants(restaurants: List[Dict[str, Any]], 
                                       sample_size: int = 5) -> Dict[str, Any]:
    """
    Create a representative sample from multiple restaurants
    Useful when you want to analyze a trend across all restaurants
    
    Args:
        restaurants: List of restaurant data dictionaries
        sample_size: Number of restaurants to include in sample
        
    Returns:
        Dictionary with sample data and metadata
    """
    # Sort restaurants by review count (most reviewed first)
    sorted_restaurants = sorted(restaurants, key=lambda x: x.get("reviews", 0), reverse=True)
    
    # Take a sample of restaurants across different popularity levels
    samples = []
    
    # Most popular
    if len(sorted_restaurants) > 0:
        samples.append(sorted_restaurants[0])
    
    # Mid-range popularity
    mid_idx = len(sorted_restaurants) // 2
    if mid_idx < len(sorted_restaurants):
        samples.append(sorted_restaurants[mid_idx])
    
    # Less popular but still has reviews
    less_popular_idx = min(len(sorted_restaurants) - 1, 3 * len(sorted_restaurants) // 4)
    if less_popular_idx > 0 and less_popular_idx < len(sorted_restaurants):
        samples.append(sorted_restaurants[less_popular_idx])
    
    # Add additional random samples to reach sample_size
    import random
    remaining_count = sample_size - len(samples)
    
    if remaining_count > 0 and len(sorted_restaurants) > len(samples):
        # Get remaining restaurant indices (excluding already sampled)
        remaining_indices = [i for i in range(len(sorted_restaurants)) 
                           if sorted_restaurants[i] not in samples]
        
        # Randomly select additional restaurants
        additional_indices = random.sample(remaining_indices, 
                                         min(remaining_count, len(remaining_indices)))
        
        for idx in additional_indices:
            samples.append(sorted_restaurants[idx])
    
    # Preprocess the samples for LLM
    processed_samples = preprocess_for_llm(samples, max_restaurants=sample_size)
    
    return {
        "sample_restaurants": processed_samples,
        "total_restaurants": len(restaurants),
        "sample_size": len(processed_samples),
        "sampling_method": "Representative sampling across popularity levels"
    }

def main_data_processing(json_path: str, 
                       analysis_focus: str = "all",
                       max_restaurants: int = 5) -> Dict[str, Any]:
    """
    Main function to load and process Yelp data for different analysis focuses
    
    Args:
        json_path: Path to the JSON file
        analysis_focus: Type of analysis focus ('all', 'top_rated', 'specific_category', etc.)
        max_restaurants: Maximum number of restaurants to include
        
    Returns:
        Processed data ready for LLM analysis
    """
    # Load data
    restaurants = load_yelp_data_from_json(json_path)
    
    if not restaurants:
        return {"error": f"No valid data found in {json_path}"}
    
    # Process based on analysis focus
    if analysis_focus == "top_rated":
        selected_restaurants = get_top_restaurants(restaurants, count=max_restaurants, sort_by="rating")
        processed_data = preprocess_for_llm(selected_restaurants, max_restaurants=max_restaurants)
        analysis_context = "Top-rated restaurants analysis"
        
    elif analysis_focus == "most_reviewed":
        selected_restaurants = get_top_restaurants(restaurants, count=max_restaurants, sort_by="reviews")
        processed_data = preprocess_for_llm(selected_restaurants, max_restaurants=max_restaurants)
        analysis_context = "Most reviewed restaurants analysis"
        
    elif analysis_focus == "specific_category":
        # Example: Focus on Italian restaurants
        filtered = filter_restaurants(restaurants, categories=["Italian"])
        selected_restaurants = filtered[:max_restaurants]
        processed_data = preprocess_for_llm(selected_restaurants, max_restaurants=max_restaurants)
        analysis_context = "Italian restaurants analysis"
        
    elif analysis_focus == "neighborhood":
        # Example: Focus on Downtown restaurants
        filtered = filter_restaurants(restaurants, neighborhood="Downtown")
        selected_restaurants = filtered[:max_restaurants]
        processed_data = preprocess_for_llm(selected_restaurants, max_restaurants=max_restaurants)
        analysis_context = "Downtown restaurants analysis"
        
    elif analysis_focus == "review_trends":
        # Get a representative sample for trend analysis
        sample_data = extract_sample_from_all_restaurants(restaurants, sample_size=max_restaurants)
        processed_data = sample_data["sample_restaurants"]
        analysis_context = "Review trends analysis across different restaurant types"
        
    else:  # Default to "all"
        # Just take the first max_restaurants
        selected_restaurants = restaurants[:max_restaurants]
        processed_data = preprocess_for_llm(selected_restaurants, max_restaurants=max_restaurants)
        analysis_context = "General restaurant analysis"
    
    # Include overall statistics
    stats = analyze_reviews_distribution(restaurants)
    
    return {
        "processed_restaurants": processed_data,
        "analysis_context": analysis_context,
        "dataset_statistics": stats,
        "source_file": json_path,
        "total_restaurants_in_source": len(restaurants)
    }

# Example usage
if __name__ == "__main__":
    result = main_data_processing(
        json_path="yelp_data_20250506_080923.json",
        analysis_focus="top_rated",
        max_restaurants=3
    )
    
    print(f"Processed {len(result['processed_restaurants'])} restaurants for {result['analysis_context']}")
    print(f"Dataset statistics: {json.dumps(result['dataset_statistics'], indent=2)}")