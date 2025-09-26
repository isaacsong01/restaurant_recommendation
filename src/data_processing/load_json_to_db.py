import os
import json
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("yelp_to_supabase.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class YelpToSupabase:
    """
    Class to handle loading Yelp data from JSON file to Supabase database.
    """
    
    def __init__(self):
        """ 
        Initialize with Supabase credentials from environment variables.
        """
        # Load environment variables
        load_dotenv()

        # Get Supabase credentials
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            logger.error("Supabase URL or Key not found in environment variables.")
            raise ValueError("Supabase URL or Key not found in environment variables.")
                        
        # Intialize Supabase client
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        logger.info("Supabase client initialized.")


    
    def insert_restaurant(self, restaurant: Dict[str, Any]) -> bool:
        """
        Insert a restaurant into the public.restaurants table
        
        Args:
            restaurant: Dictionary with restaurant data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract restaurant data
            restaurant_data = {
                "place_id": restaurant.get("place_id", ""),
                "name": restaurant.get("name", ""),
                "rating": restaurant.get("rating", 0),
                "reviews_count": restaurant.get("reviews", 0),
                "price": restaurant.get("price", ""),
                "categories": json.dumps(restaurant.get("categories", [])),
                "neighborhood": restaurant.get("neighborhood", ""),
                "phone": restaurant.get("phone", ""),
                "url": restaurant.get("url", ""),
                "service_options": json.dumps(restaurant.get("service_options", {})),
                "highlights": json.dumps(restaurant.get("highlights", []))
            }
            
            # Insert restaurant data into public.restaurants
            result = self.supabase.postgrest.schema("public").table("restaurants").upsert(
                restaurant_data, 
                on_conflict="place_id"
            ).execute()
            
            logger.info(f"Inserted restaurant: {restaurant.get('name')}")
            return True
        except Exception as e:
            logger.error(f"Error inserting restaurant {restaurant.get('name', 'unknown')}: {str(e)}")
            return False
    
    def insert_reviews(self, place_id: str, reviews: List[Dict[str, Any]]) -> bool:
        """
        Insert reviews for a restaurant into the public.reviews table
        
        Args:
            place_id: Restaurant place_id
            reviews: List of review dictionaries
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not reviews:
                logger.warning(f"No reviews to insert for place_id: {place_id}")
                return True
                
            # Process and insert reviews
            for review in reviews:
                user_data = review.get("user", {})
                
                review_data = {
                    "place_id": place_id,
                    "position": review.get("position", 0),
                    "rating": review.get("rating", 0),
                    "date": review.get("date", ""),
                    "user_id": user_data.get("user_id", ""),
                    "user_name": user_data.get("name", ""),
                    "user_data": json.dumps(user_data),
                    "comment": review.get("comment", {}).get("text", ""),
                    "photos": json.dumps(review.get("photos", [])),
                    "tags": json.dumps(review.get("tags", [])),
                    "feedback": json.dumps(review.get("feedback", {}))
                }
                
                # Insert review data into public.reviews
                self.supabase.postgrest.schema("public").table("reviews").insert(review_data).execute()
            
            logger.info(f"Inserted {len(reviews)} reviews for place_id: {place_id}")
            return True
        except Exception as e:
            logger.error(f"Error inserting reviews for place_id {place_id}: {str(e)}")
            return False
    
    def insert_restaurant_details(self, place_id: str, details: Dict[str, Any]) -> bool:
        """
        Insert restaurant details into the public.restaurant_details table
        
        Args:
            place_id: Restaurant place_id
            details: Dictionary with restaurant details
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not details:
                logger.warning(f"No details to insert for place_id: {place_id}")
                return True
                
            # Extract details data
            details_data = {
                "place_id": place_id,
                "hours": json.dumps(details.get("hours", {})),
                "address": details.get("address", ""),
                "website": details.get("website", ""),
                "photos": json.dumps(details.get("photos", [])),
                "menu": json.dumps(details.get("menu", {})),
                "health_score": details.get("health_score", 0)
            }
            
            # Insert details data into public.restaurant_details
            result = self.supabase.postgrest.schema("public").table("restaurant_details").upsert(
                details_data, 
                on_conflict="place_id"
            ).execute()
            
            logger.info(f"Inserted details for place_id: {place_id}")
            return True
        except Exception as e:
            logger.error(f"Error inserting details for place_id {place_id}: {str(e)}")
            return False
    
    def load_json_to_supabase(self, json_file_path: str) -> bool:
        """
        Load Yelp data from JSON file into Supabase PUBLIC schema
        
        Args:
            json_file_path: Path to JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read JSON file
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded JSON data from {json_file_path}")
            
            # Load data into Supabase
            for restaurant in data:
                # Insert restaurant
                self.insert_restaurant(restaurant)
                
                # Insert reviews
                self.insert_reviews(restaurant.get("place_id", ""), restaurant.get("reviews_data", []))
                
                # Insert details
                self.insert_restaurant_details(restaurant.get("place_id", ""), restaurant.get("details", {}))
            
            logger.info(f"Successfully loaded {len(data)} restaurants into Supabase")
            return True
        except Exception as e:
            logger.error(f"Error loading JSON data to Supabase: {str(e)}")
            return False

def main():
    # Create loader instance
    loader = YelpToSupabase()

    
    # Load JSON data to Supabase
    json_file_path = input("Enter the path to the Yelp JSON file: ")
    if not os.path.exists(json_file_path):
        logger.error(f"File not found: {json_file_path}")
        return
    
    result = loader.load_json_to_supabase(json_file_path)
    if result:
        logger.info("Data successfully loaded to Supabase PUBLIC schema")
    else:
        logger.error("Failed to load data to Supabase PUBLIC schema")

if __name__ == "__main__":
    main()