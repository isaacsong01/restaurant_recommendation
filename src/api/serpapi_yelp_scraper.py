import os
import json
from serpapi import GoogleSearch
from dotenv import load_dotenv
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

class YelpSerpAPIScraper:
    def __init__(self):
        """
        Initialize the Yelp scraper with SerpAPI
        """
        # Load environment variables from .env file
        load_dotenv()
        
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY not found in environment variables")
        
    def search_restaurants(self, 
                         location: str, 
                         query: str = "Restaurants",
                         sort_by: str = "recommended",
                         max_results: int = 20,
                         price: Optional[str] = None,
                         category: Optional[str] = None) -> List[Dict]:
        """
        Search for restaurants in a specific location with optional filters
        
        Args:
            location: City and state (e.g., "San Francisco, CA")
            query: Search query (default: "Restaurants")
            sort_by: Sort method ("recommended", "rating", "review_count")
            max_results: Maximum number of results to return (1-100)
            price: Price range filter ("$", "$$", "$$$", "$$$$", "all")
            category: Category filter (e.g., "italian", "chinese", "all")
        """
        params = {
            "engine": "yelp",
            "find_desc": query,
            "find_loc": location,
            "sortby": sort_by,
            "api_key": self.api_key
        }
        
        # Add optional filters
        if price and price != "all":
            params["attrs"] = f"RestaurantsPriceRange2.{len(price)}"
        if category and category != "all":
            params["cflt"] = category
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            raise Exception(f"API Error: {results['error']}")
            
        restaurants = []
        for result in results.get("organic_results", [])[:max_results]:
            restaurant = {
                "name": result.get("title", ""),
                "rating": result.get("rating", 0),
                "reviews": result.get("reviews", 0),
                "price": result.get("price", ""),
                "categories": [cat["title"] for cat in result.get("categories", [])],
                "neighborhood": result.get("neighborhoods", ""),
                "phone": result.get("phone", ""),
                "url": result.get("link", ""),
                "place_id": result.get("place_ids", [""])[0] if result.get("place_ids") else "",
                "service_options": result.get("service_options", {}),
                "highlights": result.get("highlights", [])
            }
            restaurants.append(restaurant)
            
        return restaurants
    
    def get_reviews(self, place_id: str, max_reviews: int = 10) -> List[Dict]:
        """
        Get reviews for a specific restaurant using the yelp_reviews engine
        
        Args:
            place_id: Yelp place ID
            max_reviews: Maximum number of reviews to fetch
        """
        print(f"\nFetching reviews for place_id: {place_id}")
        
        params = {
            "engine": "yelp_reviews",
            "place_id": place_id,
            "api_key": self.api_key
        }
        
        print("API Request Parameters:", json.dumps(params, indent=2))
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            print(f"API Error: {results['error']}")
            raise Exception(f"API Error: {results['error']}")
            
        print("\nAPI Response Structure:")
        print(json.dumps({k: type(v).__name__ for k, v in results.items()}, indent=2))
        
        reviews = []
        raw_reviews = results.get("reviews", [])
        print(f"\nNumber of reviews found: {len(raw_reviews)}")
        
        for i, review in enumerate(raw_reviews[:max_reviews], 1):
            print(f"\nProcessing review {i}:")
            print(f"Review data: {json.dumps(review, indent=2)}")
            
            # Extract user information
            user = review.get("user", {})
            user_data = {
                "name": user.get("name", ""),
                "user_id": user.get("user_id", ""),
                "link": user.get("link", ""),
                "thumbnail": user.get("thumbnail", ""),
                "address": user.get("address", ""),
                "friends": user.get("friends", 0),
                "photos": user.get("photos", 0),
                "reviews": user.get("reviews", 0),
                "elite_year": user.get("elite_year", 0)
            }
            
            # Extract comment information
            comment = review.get("comment", {})
            comment_data = {
                "text": comment.get("text", ""),
                "language": comment.get("language", "")
            }
            
            # Extract feedback information
            feedback = review.get("feedback", {})
            feedback_data = {
                "useful": feedback.get("useful", 0),
                "funny": feedback.get("funny", 0),
                "cool": feedback.get("cool", 0)
            }
            
            # Extract photos if available
            photos = []
            for photo in review.get("photos", []):
                photos.append({
                    "link": photo.get("link", ""),
                    "caption": photo.get("caption", "")
                })
            
            review_data = {
                "position": review.get("position", 0),
                "rating": review.get("rating", 0),
                "date": review.get("date", ""),
                "user": user_data,
                "comment": comment_data,
                "feedback": feedback_data,
                "photos": photos,
                "tags": review.get("tags", [])
            }
            
            print(f"Extracted review data: {json.dumps(review_data, indent=2)}")
            reviews.append(review_data)
            
        print(f"\nTotal reviews processed: {len(reviews)}")
        return reviews
    
    def get_business_details(self, place_id: str, location: str) -> Dict:
        """
        Get detailed information about a specific business using the yelp engine
        
        Args:
            place_id: Yelp place ID
            location: City and state (e.g., "San Francisco, CA")
        """
        params = {
            "engine": "yelp",
            "place_id": place_id,
            "find_loc": location,
            "api_key": self.api_key
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            raise Exception(f"API Error: {results['error']}")
            
        # Extract business details from the first result
        business = results.get("organic_results", [{}])[0]
        
        return {
            "hours": business.get("hours", {}),
            "address": business.get("address", ""),
            "website": business.get("website", ""),
            "photos": business.get("photos", []),
            "menu": business.get("menu", {}),
            "health_score": business.get("health_score", 0),
            "service_options": business.get("service_options", {}),
            "highlights": business.get("highlights", []),
            "neighborhood": business.get("neighborhoods", ""),
            "phone": business.get("phone", ""),
            "categories": [cat["title"] for cat in business.get("categories", [])]
        }
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """
        Save data to CSV file
        """
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    
    def save_to_json(self, data: List[Dict], filename: str):
        """
        Save data to JSON file
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {filename}")

def get_user_input(prompt: str, default: str = None) -> str:
    """
    Get user input with a default value
    """
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def main():
    # Initialize scraper
    scraper = YelpSerpAPIScraper()
    
    print("\nWelcome to Yelp Data Scraper!")
    print("Please enter your search parameters (press Enter to use default values):\n")
    
    # Get user input for search parameters
    location = get_user_input("Enter location (city and state)", "Seattle, WA")
    query = get_user_input("Enter search query", "Restaurants")
    max_results = int(get_user_input("Enter maximum number of results (1-100)", "5"))
    price = get_user_input("Enter price range ($, $$, $$$, $$$$, all)", "all")
    category = get_user_input("Enter category (e.g., italian, japanese, chinese, all)", "all")
    
    print("\nSearching for restaurants...")
    restaurants = scraper.search_restaurants(
        location=location,
        query=query,
        max_results=max_results,
        price=price,
        category=category
    )
    
    print(f"\nFound {len(restaurants)} restaurants. Getting detailed information...")
    
    # Get detailed information for each restaurant
    for i, restaurant in enumerate(restaurants, 1):
        print(f"\nProcessing restaurant {i}/{len(restaurants)}: {restaurant['name']}")
        if restaurant["place_id"]:
            # Get reviews
            reviews = scraper.get_reviews(restaurant["place_id"])
            restaurant["reviews_data"] = reviews
            
            # Get business details
            details = scraper.get_business_details(restaurant["place_id"], location)
            restaurant["details"] = details
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save results
    json_filename = f"yelp_data_{timestamp}.json"
    csv_filename = f"yelp_data_{timestamp}.csv"
    
    scraper.save_to_json(restaurants, json_filename)
    scraper.save_to_csv(restaurants, csv_filename)
    
    print(f"\nData saved to {json_filename} and {csv_filename}")

if __name__ == "__main__":
    main() 