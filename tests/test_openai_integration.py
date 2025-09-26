from openai_client import setup_openai_client, test_openai_connection, get_restaurant_insights
from prompt_templates import create_general_analysis_prompt
import json

def test_with_minimal_data():
    """
    Test OpenAI integration with minimal data to save tokens/cost
    """
    # Very minimal test data (just one restaurant with minimal info)
    test_data = [
        {
            "name": "Test Restaurant",
            "rating": 4.5,
            "categories": ["Test Category"],
            "sample_reviews": [
                {"rating": 5, "text": "This is a test review."}
            ]
        }
    ]
    
    # Format data for prompt
    formatted_data = json.dumps(test_data, indent=2)
    
    # Create a shortened test prompt
    test_prompt = f"""
    Briefly analyze this restaurant:
    
    {formatted_data}
    
    Keep your answer under 100 words.
    """
    
    # Setup client
    client = setup_openai_client()
    
    # Test connection
    if test_openai_connection(client):
        # Get insights
        insights = get_restaurant_insights(client, test_prompt)
        
        if insights:
            print("\nRestaurant Insights:")
            print("===================")
            print(insights)
            return True
    
    return False

if __name__ == "__main__":
    test_with_minimal_data()