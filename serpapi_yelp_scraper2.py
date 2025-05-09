import os
import json
from serpapi import GoogleSearch
from dotenv import load_dotenv
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from supabase import create_client
import time

class YelpSerpAPIScraper:
    def __init__(self):
        """
        Initialize the Yelp scraper with SerpAPI
        """
        # Load environment variables from .env file
        load_dotenv()
        
        # self.api_key = '640382298fbdfe97550a46c7742b36a52b313afca5cbe37fdc9567fab3cce86f'
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



class YelpSupabaseScraper(YelpSerpAPIScraper):
    """
    Enhanced Yelp scraper with Supabase integration for persistent storage
    and incremental scraping capabilities.
    """
    
    def __init__(self, supabase_url=None, supabase_key=None):
        """
        Initialize the Yelp scraper with SerpAPI and Supabase integration
        
        Args:
            supabase_url: Your Supabase project URL
            supabase_key: Your Supabase API key
        """
        # Initialize the parent class
        super().__init__()
        
        # Set up Supabase client if credentials are provided
        self.supabase = None
        if supabase_url and supabase_key:
            self.supabase = create_client(supabase_url, supabase_key)
        else:
            # Try to load from environment variables
            load_dotenv()
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_API_KEY")
            
            if supabase_url and supabase_key:
                self.supabase = create_client(supabase_url, supabase_key)
            else:
                print("WARNING: Supabase credentials not provided. Database features will be disabled.")
    
    def check_supabase_connection(self):
        """Verify Supabase connection is configured"""
        if not self.supabase:
            raise ValueError("Supabase is not configured. Please provide credentials.")
        return True
    
    # ---- Metadata management methods ----
    
    def get_scrape_metadata(self, location: str, query: str) -> Optional[Dict]:
        """
        Retrieve metadata about previous scraping runs
        
        Args:
            location: Location that was scraped
            query: Search query that was used
        
        Returns:
            Dictionary with metadata or None if not found
        """
        self.check_supabase_connection()
        
        try:
            response = self.supabase.table("scrape_metadata").select("*") \
                .eq("location", location) \
                .eq("query", query) \
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error retrieving scrape metadata: {str(e)}")
            return None
    
    def update_scrape_metadata(self, location: str, query: str, 
                              page: int = 0, 
                              status: str = "completed",
                              total_count: int = 0, 
                              error: str = None) -> Dict:
        """
        Update or create metadata entry for a scraping run
        
        Args:
            location: Location being scraped
            query: Search query being used
            page: Current page number
            status: Status of the scraping process
            total_count: Total number of restaurants scraped
            error: Error message if any
        
        Returns:
            The created or updated metadata record
        """
        self.check_supabase_connection()
        
        now = datetime.now().isoformat()
        metadata = {
            "location": location,
            "query": query,
            "last_page": page,
            "last_updated": now,
            "status": status,
            "total_count": total_count
        }
        
        if error:
            metadata["error"] = error
        
        try:
            # Check if entry exists
            existing = self.get_scrape_metadata(location, query)
            
            if existing:
                # Update existing record
                result = self.supabase.table("scrape_metadata") \
                    .update(metadata) \
                    .eq("id", existing["id"]) \
                    .execute()
            else:
                # Create new record
                result = self.supabase.table("scrape_metadata") \
                    .insert(metadata) \
                    .execute()
            
            return result.data[0] if result.data else metadata
        
        except Exception as e:
            print(f"Error updating scrape metadata: {str(e)}")
            return metadata
    
    # ---- Restaurant data management methods ----
    
    def get_restaurant(self, place_id: str) -> Optional[Dict]:
        """
        Retrieve a restaurant by place_id
        
        Args:
            place_id: Yelp place ID
        
        Returns:
            Restaurant data or None if not found
        """
        self.check_supabase_connection()
        
        try:
            response = self.supabase.table("restaurants") \
                .select("*") \
                .eq("place_id", place_id) \
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error retrieving restaurant: {str(e)}")
            return None
    
    def save_restaurant(self, restaurant_data: Dict) -> Optional[Dict]:
        """
        Save restaurant data to Supabase
        
        Args:
            restaurant_data: Restaurant data to save
        
        Returns:
            The saved restaurant data with ID
        """
        self.check_supabase_connection()
        
        # Add timestamp
        restaurant_data["updated_at"] = datetime.now().isoformat()
        
        try:
            # Check if restaurant exists
            existing = self.get_restaurant(restaurant_data["place_id"])
            
            if existing:
                # Update existing record
                result = self.supabase.table("restaurants") \
                    .update(restaurant_data) \
                    .eq("id", existing["id"]) \
                    .execute()
                
                restaurant_id = existing["id"]
            else:
                # Create new record
                restaurant_data["created_at"] = datetime.now().isoformat()
                result = self.supabase.table("restaurants") \
                    .insert(restaurant_data) \
                    .execute()
                
                restaurant_id = result.data[0]["id"] if result.data else None
            
            return {"id": restaurant_id, **restaurant_data}
        
        except Exception as e:
            print(f"Error saving restaurant {restaurant_data.get('name', 'Unknown')}: {str(e)}")
            return None
    
    # ---- Review data management methods ----
    
    def save_review(self, review_data: Dict) -> Optional[Dict]:
        """
        Save a review to Supabase
        
        Args:
            review_data: Review data to save
        
        Returns:
            The saved review data
        """
        self.check_supabase_connection()
        
        # Add timestamp
        review_data["updated_at"] = datetime.now().isoformat()
        
        try:
            # Check if review already exists using user_id and restaurant_id
            response = self.supabase.table("reviews") \
                .select("*") \
                .eq("user_id", review_data["user_id"]) \
                .eq("restaurant_id", review_data["restaurant_id"]) \
                .execute()
            
            if response.data and len(response.data) > 0:
                # Update existing review
                existing = response.data[0]
                result = self.supabase.table("reviews") \
                    .update(review_data) \
                    .eq("id", existing["id"]) \
                    .execute()
            else:
                # Create new review
                review_data["created_at"] = datetime.now().isoformat()
                result = self.supabase.table("reviews") \
                    .insert(review_data) \
                    .execute()
            
            return result.data[0] if result.data else review_data
        
        except Exception as e:
            print(f"Error saving review: {str(e)}")
            return None
    
    # ---- Enhanced scraping methods with database integration ----
    
    def search_and_save(self, 
                      location: str, 
                      query: str = "Restaurants",
                      start_page: int = 0,
                      max_pages: int = 5,
                      results_per_page: int = 20,
                      **search_params) -> Tuple[List[Dict], Dict]:
        """
        Search for restaurants and save results to Supabase
        
        Args:
            location: City and state
            query: Search query
            start_page: Page to start scraping from
            max_pages: Maximum number of pages to scrape
            results_per_page: Number of results per page
            **search_params: Additional search parameters
        
        Returns:
            Tuple of (list of restaurants scraped, metadata about the scrape)
        """
        all_restaurants = []
        current_page = start_page
        total_count = 0
        
        try:
            # Update metadata to indicate scraping has started
            metadata = self.update_scrape_metadata(
                location=location,
                query=query,
                page=current_page,
                status="in_progress",
                total_count=total_count
            )
            
            for page_num in range(start_page, start_page + max_pages):
                current_page = page_num
                
                print(f"Scraping page {page_num + 1} of {start_page + max_pages}...")
                
                # Update metadata for current page
                metadata = self.update_scrape_metadata(
                    location=location,
                    query=query,
                    page=current_page,
                    status="processing_page",
                    total_count=total_count
                )
                
                # Set up pagination parameters
                params = {
                    "engine": "yelp",
                    "find_desc": query,
                    "find_loc": location,
                    "start": page_num * results_per_page,  # For pagination
                    "api_key": self.api_key
                }
                
                # Add optional filters
                if "price" in search_params and search_params["price"] != "all":
                    params["attrs"] = f"RestaurantsPriceRange2.{len(search_params['price'])}"
                if "category" in search_params and search_params["category"] != "all":
                    params["cflt"] = search_params["category"]
                if "sort_by" in search_params:
                    params["sortby"] = search_params["sort_by"]
                
                # Make API request
                search = GoogleSearch(params)
                results = search.get_dict()
                
                if "error" in results:
                    raise Exception(f"API Error: {results['error']}")
                
                # Process restaurants on this page
                page_restaurants = []
                
                for result in results.get("organic_results", []):
                    # Extract basic restaurant data
                    restaurant = {
                        "name": result.get("title", ""),
                        "rating": result.get("rating", 0),
                        "reviews_count": result.get("reviews", 0),
                        "price": result.get("price", ""),
                        "categories": result.get("categories", []),
                        "neighborhood": result.get("neighborhoods", ""),
                        "phone": result.get("phone", ""),
                        "url": result.get("link", ""),
                        "place_id": result.get("place_id", ""),
                        "service_options": result.get("service_options", {}),
                        "highlights": result.get("highlights", []),
                        "location": location,
                        "query": query
                    }
                    
                    # Skip if no place_id
                    if not restaurant["place_id"]:
                        print(f"Skipping restaurant without place_id: {restaurant['name']}")
                        continue
                    
                    # Save restaurant to database
                    if self.supabase:
                        saved_restaurant = self.save_restaurant(restaurant)
                        
                        if saved_restaurant and saved_restaurant.get("id"):
                            restaurant_id = saved_restaurant["id"]
                            
                            # Get and save reviews
                            try:
                                reviews = self.get_reviews(restaurant["place_id"])
                                
                                for review in reviews:
                                    # Extract user information
                                    user = review.get("user", {})
                                    
                                    # Prepare review data for database
                                    review_data = {
                                        "restaurant_id": restaurant_id,
                                        "user_id": user.get("user_id", ""),
                                        "user_name": user.get("name", ""),
                                        "rating": review.get("rating", 0),
                                        "date": review.get("date", ""),
                                        "text": review.get("comment", {}).get("text", ""),
                                        "useful": review.get("feedback", {}).get("useful", 0),
                                        "funny": review.get("feedback", {}).get("funny", 0),
                                        "cool": review.get("feedback", {}).get("cool", 0)
                                    }
                                    
                                    # Save review
                                    if review_data["user_id"]:
                                        self.save_review(review_data)
                            
                            except Exception as e:
                                print(f"Error processing reviews for {restaurant['name']}: {str(e)}")
                    
                    page_restaurants.append(restaurant)
                
                # Add page results to overall results
                all_restaurants.extend(page_restaurants)
                total_count = len(all_restaurants)
                
                # Update metadata for completed page
                metadata = self.update_scrape_metadata(
                    location=location,
                    query=query,
                    page=current_page,
                    status="processing",
                    total_count=total_count
                )
                
                # If we got fewer than expected results, we've reached the end
                if len(page_restaurants) < results_per_page:
                    break
                
                # Delay between requests to avoid rate limiting
                time.sleep(2)
            
            # Update metadata to indicate scraping has completed
            metadata = self.update_scrape_metadata(
                location=location,
                query=query,
                page=current_page,
                status="completed",
                total_count=total_count
            )
            
            return all_restaurants, metadata
            
        except Exception as e:
            error_message = str(e)
            print(f"Error during scraping: {error_message}")
            
            # Update metadata to indicate error
            metadata = self.update_scrape_metadata(
                location=location,
                query=query,
                page=current_page,
                status="failed",
                total_count=total_count,
                error=error_message
            )
            
            return all_restaurants, metadata
    
    def resume_scraping(self, location: str, query: str, **search_params) -> Tuple[List[Dict], Dict]:
        """
        Resume scraping from the last page
        
        Args:
            location: Location to scrape
            query: Search query
            **search_params: Additional search parameters
        
        Returns:
            Tuple of (list of restaurants scraped, metadata about the scrape)
        """
        # Get the last run metadata
        metadata = self.get_scrape_metadata(location, query)
        
        if not metadata:
            print(f"No previous scraping data found for {location} - {query}. Starting from page 0.")
            return self.search_and_save(location, query, start_page=0, **search_params)
        
        # Get the last page that was processed
        last_page = metadata.get("last_page", 0)
        
        print(f"Resuming scraping for {location} - {query} from page {last_page + 1}")
        return self.search_and_save(location, query, start_page=last_page + 1, **search_params)



def get_user_input(prompt: str, default: str = None) -> str:
    """
    Get user input with a default value
    """
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

# ---- Enhanced main function with Supabase integration ----

def main_supabase():
    """Main function for Yelp scraper with Supabase integration"""
    print("\n===== Yelp Data Scraper with Supabase Integration =====\n")
    
    # Initialize scraper
    scraper = YelpSupabaseScraper()
    
    # Get search parameters
    location = get_user_input("Enter location (city and state)", "Seattle, WA")
    query = get_user_input("Enter search query", "Restaurants")
    
    # Check for previous runs
    metadata = scraper.get_scrape_metadata(location, query)
    
    if metadata:
        print("\nPrevious scraping data found:")
        print(f"Last updated: {metadata.get('last_updated')}")
        print(f"Last page: {metadata.get('last_page')}")
        print(f"Status: {metadata.get('status')}")
        print(f"Total restaurants: {metadata.get('total_count')}")
        
        resume = get_user_input("Would you like to resume from the last page? (y/n)", "y").lower() == "y"
    else:
        print("\nNo previous scraping data found. Starting fresh.")
        resume = False
    
    # Get additional search parameters
    max_pages = int(get_user_input("Enter maximum number of pages to scrape", "5"))
    price = get_user_input("Enter price range ($, $$, $$$, $$$$, all)", "all")
    category = get_user_input("Enter category (e.g., italian, japanese, chinese, all)", "all")
    sort_by = get_user_input("Sort by (recommended, rating, review_count)", "recommended")
    
    # Set up search parameters
    search_params = {
        "max_pages": max_pages,
        "price": price,
        "category": category,
        "sort_by": sort_by
    }
    
    # Start or resume scraping
    if resume:
        restaurants, final_metadata = scraper.resume_scraping(location, query, **search_params)
    else:
        restaurants, final_metadata = scraper.search_and_save(location, query, **search_params)
    
    # Print results
    print("\n===== Scraping Completed =====")
    print(f"Total restaurants scraped: {len(restaurants)}")
    print(f"Status: {final_metadata.get('status')}")
    
    # Optionally save to local files
    save_local = get_user_input("Would you like to save results to local files? (y/n)", "y").lower() == "y"
    
    if save_local:
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filenames
        location_slug = location.replace(", ", "_").replace(" ", "_").lower()
        json_filename = f"yelp_{location_slug}_{timestamp}.json"
        csv_filename = f"yelp_{location_slug}_{timestamp}.csv"
        
        # Save to files
        scraper.save_to_json(restaurants, json_filename)
        scraper.save_to_csv(restaurants, csv_filename)
        
        print(f"\nData also saved to local files:")
        print(f"- JSON: {json_filename}")
        print(f"- CSV: {csv_filename}")


if __name__ == "__main__":
    main_supabase()

# def main():
#     # Initialize scraper
#     scraper = YelpSerpAPIScraper()
    
#     print("\nWelcome to Yelp Data Scraper!")
#     print("Please enter your search parameters (press Enter to use default values):\n")
    
#     # Get user input for search parameters
#     location = get_user_input("Enter location (city and state)", "Seattle, WA")
#     query = get_user_input("Enter search query", "Restaurants")
#     max_results = int(get_user_input("Enter maximum number of results (1-100)", "5"))
#     price = get_user_input("Enter price range ($, $$, $$$, $$$$, all)", "all")
#     category = get_user_input("Enter category (e.g., italian, japanese, chinese, all)", "all")
    
#     print("\nSearching for restaurants...")
#     restaurants = scraper.search_restaurants(
#         location=location,
#         query=query,
#         max_results=max_results,
#         price=price,
#         category=category
#     )
    
#     print(f"\nFound {len(restaurants)} restaurants. Getting detailed information...")
    
#     # Get detailed information for each restaurant
#     for i, restaurant in enumerate(restaurants, 1):
#         print(f"\nProcessing restaurant {i}/{len(restaurants)}: {restaurant['name']}")
#         if restaurant["place_id"]:
#             # Get reviews
#             reviews = scraper.get_reviews(restaurant["place_id"])
#             restaurant["reviews_data"] = reviews
            
#             # Get business details
#             details = scraper.get_business_details(restaurant["place_id"], location)
#             restaurant["details"] = details
    
#     # Generate timestamp for filenames
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
#     # Save results
#     json_filename = f"yelp_data_{timestamp}.json"
#     csv_filename = f"yelp_data_{timestamp}.csv"
    
#     scraper.save_to_json(restaurants, json_filename)
#     scraper.save_to_csv(restaurants, csv_filename)
    
#     print(f"\nData saved to {json_filename} and {csv_filename}")

# if __name__ == "__main__":
#     main() 