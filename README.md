# Restaurant Recommendation Service

A comprehensive restaurant analytics and recommendation system that combines web scraping, AI-powered analysis, and database management to provide intelligent restaurant insights and personalized recommendations.

## 🎯 Project Overview

This system leverages SerpAPI to scrape Yelp restaurant data and uses OpenAI's GPT models for advanced sentiment analysis, competitive insights, and personalized recommendations. The project processes restaurant data at scale and provides actionable business intelligence for restaurant owners and personalized recommendations for users.

## ✨ Key Features

### 🔍 Data Collection
- **Multi-criteria restaurant search** (location, price, category, rating)
- **Comprehensive review collection** with user profiles and engagement metrics  
- **Business details extraction** (hours, address, photos, menu information)
- **Batch processing** with rate limiting and error handling
- **Multiple output formats** (JSON, CSV)

### 🤖 AI-Powered Analysis
- **Sentiment Analysis**: Extract sentiment patterns from customer reviews
- **Competitive Analysis**: Market positioning and competitive comparison insights
- **Business Intelligence**: Identify strengths, weaknesses, and improvement opportunities
- **Trend Analysis**: Cross-restaurant market trend identification

### 📊 Data Processing
- **Smart filtering and ranking algorithms**
- **Statistical analysis** of review distributions
- **Database integration** with Supabase for scalable data storage
- **Token-efficient data preparation** for AI processing

### 🎯 Recommendation Engine
- **Personalized recommendations** based on user criteria (price, rating, cuisine)
- **Multiple analysis focuses**: top-rated, most-reviewed, category-specific, neighborhood-based
- **Representative sampling** across popularity levels

## 🏗️ Architecture

```
restaurant_recommendation_project/
├── src/
│   ├── api/                    # Data collection from external APIs
│   │   ├── serpapi_yelp_scraper.py    # Primary Yelp data scraper
│   │   └── serpapi_yelp_scraper2.py   # Alternative scraper implementation
│   ├── data_processing/        # Data processing and analysis
│   │   ├── process_yelp_api_data.py   # Core data processing engine
│   │   ├── extract_data.py            # Large dataset utilities
│   │   ├── load_json_to_db.py         # Database loading operations
│   │   └── load_csv_to_db.py          # CSV data loading
│   └── ai/                     # AI integration and analysis
│       ├── openai_client.py           # OpenAI API wrapper
│       └── prompt_templates.py        # Specialized analysis prompts
├── data/                       # Raw and processed data files
├── tests/                      # Comprehensive test suite
├── samples/                    # Sample data and templates
└── logs/                       # Application logs
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- SerpAPI account and API key
- OpenAI API account and key
- Supabase account (for database features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd restaurant_recommendation_project
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   SERPAPI_API_KEY=your_serpapi_key_here
   OPENAI_API_KEY=your_openai_key_here
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

### Basic Usage

#### 1. Scrape Restaurant Data
```python
from src.api.serpapi_yelp_scraper import YelpSerpAPIScraper

# Initialize scraper
scraper = YelpSerpAPIScraper()

# Search for restaurants
restaurants = scraper.search_restaurants(
    location="Seattle, WA",
    query="Italian restaurants",
    max_results=10,
    price="$$",
    category="italian"
)

# Get detailed reviews and business information
for restaurant in restaurants:
    if restaurant["place_id"]:
        reviews = scraper.get_reviews(restaurant["place_id"])
        details = scraper.get_business_details(restaurant["place_id"], "Seattle, WA")
        restaurant.update({"reviews_data": reviews, "details": details})

# Save results
scraper.save_to_json(restaurants, "data/seattle_italian.json")
```

#### 2. Process and Analyze Data
```python
from src.data_processing.process_yelp_api_data import load_and_process_data

# Load and process restaurant data
restaurants = load_and_process_data("data/seattle_italian.json")

# Get top-rated restaurants
top_rated = get_top_rated_restaurants(restaurants, min_rating=4.5, min_reviews=50)

# Get restaurants by category
italian_restaurants = filter_by_categories(restaurants, ["Italian", "Pizza"])
```

#### 3. Generate AI Insights
```python
from src.ai.openai_client import OpenAIClient
from src.ai.prompt_templates import get_sentiment_analysis_prompt

# Initialize OpenAI client
ai_client = OpenAIClient()

# Analyze restaurant sentiment
restaurant_data = restaurants[0]  # Example restaurant
prompt = get_sentiment_analysis_prompt(restaurant_data)
insights = ai_client.get_restaurant_insights(prompt)
```

#### 4. Load Data to Database
```python
from src.data_processing.load_json_to_db import load_restaurants_to_supabase

# Load processed data to Supabase
load_restaurants_to_supabase("data/seattle_italian.json")
```

## 📋 Available Analysis Types

### Sentiment Analysis
- Extract overall sentiment from customer reviews
- Identify positive and negative phrases
- Analyze customer satisfaction trends
- Generate sentiment-based recommendations

### Competitive Analysis  
- Market positioning assessment
- Competitive comparison insights
- Differentiation strategy recommendations
- Market gap identification

### General Restaurant Analysis
- Overall assessment of restaurant performance
- Identification of strengths and weaknesses
- Improvement recommendations
- Customer preference analysis

### Trend Analysis
- Cross-restaurant trend identification
- Category-specific insights
- Neighborhood-based patterns
- Price point analysis

## 🗄️ Data Schema

### Restaurant Data Structure
```json
{
  "name": "Restaurant Name",
  "rating": 4.5,
  "reviews_count": 1000,
  "price": "$$",
  "categories": ["Italian", "Wine Bars"],
  "neighborhood": "Downtown",
  "phone": "(555) 123-4567",
  "url": "https://yelp.com/biz/restaurant-name",
  "place_id": "unique_yelp_id",
  "service_options": {
    "delivery": true,
    "takeout": true
  },
  "highlights": ["Popular for dinner", "Good for groups"],
  "reviews_data": [...],
  "details": {...}
}
```

### Database Tables
- **restaurants**: Core restaurant information and metrics
- **reviews**: Individual review data with user profiles and engagement
- **restaurant_details**: Extended information (hours, address, website, photos)

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test modules
python tests/test_openai_integration.py
python tests/test_prompts.py
```

## 🔧 Configuration Options

### Scraper Configuration
- **Location filtering**: City, state, or specific neighborhoods
- **Price range**: "$", "$$", "$$$", "$$$$", or "all"
- **Category filtering**: Cuisine types, restaurant styles
- **Sorting options**: "recommended", "rating", "review_count"
- **Results limit**: 1-100 restaurants per search

### AI Analysis Configuration
- **Model selection**: GPT-3.5-turbo or GPT-4 models
- **Token optimization**: Efficient data preparation for cost control
- **Analysis types**: Sentiment, competitive, general, trend analysis
- **Response formatting**: Structured insights and recommendations

## 🚦 Rate Limits & Best Practices

- **SerpAPI**: Respect rate limits based on your plan
- **OpenAI**: Monitor token usage and implement cost controls
- **Database**: Use batch operations for large datasets
- **Error Handling**: Implement retry logic for API failures

## 📝 Sample Use Cases

1. **Restaurant Owner**: Get competitive analysis and improvement recommendations
2. **Food Blogger**: Analyze restaurant trends and sentiment patterns
3. **Consumer**: Get personalized restaurant recommendations
4. **Market Researcher**: Analyze restaurant industry trends and patterns
5. **App Developer**: Integrate restaurant recommendation capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [SerpAPI](https://serpapi.com/) for Yelp data access
- [OpenAI](https://openai.com/) for AI analysis capabilities
- [Supabase](https://supabase.com/) for database infrastructure
- [Yelp](https://www.yelp.com/) as the data source

## 📞 Support

For questions, issues, or feature requests, please open an issue in the GitHub repository.