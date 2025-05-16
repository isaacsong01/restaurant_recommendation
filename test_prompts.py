import json
from prompt_templates import (
    create_general_analysis_prompt,
    create_sentiment_analysis_prompt,
    create_competitive_analysis_prompt
)

# Load a small sample of preprocessed data
def load_sample_data():
    # This could be from your preprocessing step, but for testing:
    sample_data = [
        {
            "name": "The Pink Door",
            "rating": 4.4,
            "reviews_count": 7615,
            "price": "$$",
            "categories": ["Italian", "Wine Bars", "Pasta Shops"],
            "neighborhood": "Downtown",
            "sample_reviews": [
                {"rating": 5, "text": "Great food and atmosphere!"},
                {"rating": 4, "text": "Good food but service was slow."}
            ]
        },
        {
            "name": "Biscuit Bitch",
            "rating": 4.2,
            "reviews_count": 5011,
            "price": "$$",
            "categories": ["Breakfast & Brunch", "Coffee & Tea", "Southern"],
            "neighborhood": "Downtown",
            "sample_reviews": [
                {"rating": 5, "text": "Best breakfast in town!"},
                {"rating": 3, "text": "Long wait but decent food."}
            ]
        }
    ]
    return sample_data

# Format data as neat JSON string for the prompt
def format_data_for_prompt(data):
    return json.dumps(data, indent=2)

# Test the prompts
def test_prompts():
    # Load sample data
    sample_data = load_sample_data()
    formatted_data = format_data_for_prompt(sample_data)
    
    # Generate and print prompts
    print("\n=== GENERAL ANALYSIS PROMPT ===")
    general_prompt = create_general_analysis_prompt(formatted_data)
    print(general_prompt)
    
    print("\n=== SENTIMENT ANALYSIS PROMPT ===")
    sentiment_prompt = create_sentiment_analysis_prompt(formatted_data)
    print(sentiment_prompt)
    
    print("\n=== COMPETITIVE ANALYSIS PROMPT ===")
    competitive_prompt = create_competitive_analysis_prompt(formatted_data)
    print(competitive_prompt)
    
    # Save prompts to files for reference
    with open("sample_general_prompt.txt", "w") as f:
        f.write(general_prompt)
    
    with open("sample_sentiment_prompt.txt", "w") as f:
        f.write(sentiment_prompt)
    
    with open("sample_competitive_prompt.txt", "w") as f:
        f.write(competitive_prompt)
    
    print("\nPrompt samples saved to files.")

if __name__ == "__main__":
    test_prompts()