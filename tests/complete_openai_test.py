import json
import os
from prompt_templates import create_general_analysis_prompt
from openai_client import setup_openai_client, get_restaurant_insights

def run_complete_test():
    """
    Run a more complete test with a real analysis prompt
    """
    # Load your sample processed data
    # For testing, you can use a very small sample to limit costs
    sample_data = [
        {
            "name": "The Pink Door",
            "rating": 4.4,
            "reviews_count": 100,  # Reduced for testing
            "price": "$$",
            "categories": ["Italian", "Wine Bars"],
            "neighborhood": "Downtown",
            "sample_reviews": [
                {"rating": 5, "text": "Amazing food and great atmosphere!"},
                {"rating": 3, "text": "Service was slow but food was decent."}
            ]
        },
        {
            "name": "Biscuit Bitch",
            "rating": 4.2,
            "reviews_count": 80,  # Reduced for testing
            "price": "$$",
            "categories": ["Breakfast & Brunch"],
            "neighborhood": "Downtown",
            "sample_reviews": [
                {"rating": 5, "text": "Best breakfast in Seattle!"},
                {"rating": 4, "text": "Long wait but worth it."}
            ]
        }
    ]
    
    # Format data for the prompt
    formatted_data = json.dumps(sample_data, indent=2)
    
    # Create real analysis prompt
    prompt = create_general_analysis_prompt(formatted_data)
    
    # Set up client
    client = setup_openai_client()
    
    # Get insights
    insights = get_restaurant_insights(client, prompt)
    
    if insights:
        print("\nRestaurant Analysis:")
        print("===================")
        print(insights)
        
        # Save insights to file
        with open("sample_analysis_result.txt", "w") as f:
            f.write(insights)
        
        print("\nAnalysis saved to sample_analysis_result.txt")
        return True
    
    return False

if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable before running this script.")
        print("You can do this by running: export OPENAI_API_KEY='your-api-key'")
    else:
        run_complete_test()