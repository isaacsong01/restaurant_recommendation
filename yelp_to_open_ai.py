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
    