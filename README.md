# Yelp Data Scraper

This project provides tools to scrape Yelp data via SerpAPI, enabling users to collect detailed information about restaurants, including reviews, business details, and ratings. The data gathered will be used to build a restaurant recommendation service.

## Features

- **SerpAPI Integration**: Uses SerpAPI to fetch Yelp data without browser automation
- **Comprehensive Data Collection**:
  - Restaurant search results
  - Detailed business information
  - Rich review data including:
    - User profiles
    - Review content and ratings
    - Photos and captions
    - User feedback (useful, funny, cool counts)
    - Review timestamps and positions
- **Data Export**: Save results in both JSON and CSV formats
- **Environment Variable Support**: Secure API key management
- **Flexible Search Options**: Search across all price ranges and categories

## Prerequisites

- Python 3.7+
- SerpAPI account and API key
- Required Python packages (see Installation)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd yelp-data
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your SerpAPI key:
```
SERPAPI_API_KEY=your_api_key_here
```

## Usage

### SerpAPI Scraper

The main script `serpapi_yelp_scraper.py` provides a comprehensive scraper using SerpAPI. Here's how to use it with custom parameters:

```python
from serpapi_yelp_scraper import YelpSerpAPIScraper

# Initialize scraper
scraper = YelpSerpAPIScraper()

# Example search parameters
location = "Seattle, WA"  # City and state, e.g., "New York, NY", "Los Angeles, CA"
query = "Restaurants"  # Search query, e.g., "sushi", "pizza", "vegan food"
max_results = 5  # Number of results to return (1-100)
price = "all"  # Price range: "$", "$$", "$$$", "$$$$", "all"
category = "all"  # Category filter, e.g., "japanese", "chinese", "mexican", "all"

# Search for restaurants with custom parameters
restaurants = scraper.search_restaurants(
    location=location,
    query=query,
    max_results=max_results,
    price=price,
    category=category
)

# Get detailed information for each restaurant
for restaurant in restaurants:
    if restaurant["place_id"]:
        # Get reviews
        reviews = scraper.get_reviews(restaurant["place_id"])
        restaurant["reviews_data"] = reviews
        
        # Get business details
        details = scraper.get_business_details(restaurant["place_id"], location)
        restaurant["details"] = details

# Save results
scraper.save_to_json(restaurants, "yelp_data.json")
scraper.save_to_csv(restaurants, "yelp_data.csv")
```

### Interactive Usage

Run the script directly to use the interactive interface:

```bash
python serpapi_yelp_scraper.py
```

You'll be prompted to enter:
- Location (default: "Seattle, WA")
- Search query (default: "Restaurants")
- Maximum results (1-100, default: 5)
- Price range ("$", "$$", "$$$", "$$$$", "all", default: "all")
- Category (e.g., "italian", "japanese", "chinese", "all", default: "all")

### Available Methods and Parameters

1. **search_restaurants**
   - Parameters:
     - `location`: City and state (e.g., "San Francisco, CA", "Chicago, IL")
     - `query`: Search query (default: "Restaurants")
     - `sort_by`: Sort method ("recommended", "rating", "review_count")
     - `max_results`: Maximum number of results (1-100)
     - `price`: Price range ("$", "$$", "$$$", "$$$$", "all")
     - `category`: Category filter (e.g., "japanese", "chinese", "mexican", "all")

2. **get_reviews**
   - Parameters:
     - `place_id`: Yelp place ID
     - `max_reviews`: Maximum number of reviews to fetch

3. **get_business_details**
   - Parameters:
     - `place_id`: Yelp place ID
     - `location`: City and state (same as search location)

4. **save_to_json/csv**
   - Parameters:
     - `data`: Data to save
     - `filename`: Output filename

## Data Structure

### Restaurant Data
```json
{
    "name": "Restaurant Name",
    "rating": 4.5,
    "reviews": 1000,
    "price": "$$",
    "categories": ["Italian", "Pasta"],
    "neighborhood": "Downtown",
    "phone": "(123) 456-7890",
    "url": "yelp.com/biz/...",
    "place_id": "unique_id",
    "service_options": {},
    "highlights": [],
    "reviews_data": [...],
    "details": {...}
}
```

### Review Data
```json
{
    "position": 1,
    "rating": 5,
    "date": "2025-04-29T22:47:24Z",
    "user": {
        "name": "User Name",
        "user_id": "user_id",
        "link": "profile_url",
        "thumbnail": "image_url",
        "address": "Location",
        "friends": 100,
        "photos": 50,
        "reviews": 200,
        "elite_year": 2025
    },
    "comment": {
        "text": "Review text...",
        "language": "en"
    },
    "feedback": {
        "useful": 10,
        "funny": 2,
        "cool": 5
    },
    "photos": [
        {
            "link": "photo_url",
            "caption": "Photo caption"
        }
    ],
    "tags": ["tag1", "tag2"]
}
```

## Error Handling

The scraper includes comprehensive error handling for:
- API key validation
- API response errors
- Missing or invalid data
- File I/O operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [SerpAPI](https://serpapi.com/) for providing the Yelp data API
- [Yelp](https://www.yelp.com/) for the data source 