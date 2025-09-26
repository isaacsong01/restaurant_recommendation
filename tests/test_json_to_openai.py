import json

# Create a tiny test dataset with just 2 restaurants
test_data = [
    {
        "name": "Tasty Burger",
        "rating": 4.5,
        "reviews": 120,
        "categories": ["American", "Burgers"]
    },
    {
        "name": "Pizza Palace",
        "rating": 4.2,
        "reviews": 85,
        "categories": ["Italian", "Pizza"]
    }
]

# Write to a file
with open("tiny_test_restaurants.json", "w") as f:
    json.dump(test_data, f, indent=2)

print("Created test JSON file: tiny_test_restaurants.json")

import json
from typing import List, Dict, Any

def simple_load_json(file_path: str) -> Any:
    """Simply load a JSON file and return whatever is inside"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    print(f"Type of loaded data: {type(data)}")
    print(f"Content preview: {data[:1] if isinstance(data, list) else data}")
    
    return data

# Test it
test_data = simple_load_json("tiny_test_restaurants.json")

def explore_json_structure(file_path: str):
    """Load JSON and explore its structure with lots of print statements"""
    print(f"Opening file: {file_path}")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    print(f"\nData loaded successfully!")
    print(f"Type of data: {type(data)}")
    
    # Check if it's a list
    if isinstance(data, list):
        print("\nThis JSON contains a LIST of items")
        print(f"Number of items: {len(data)}")
        print(f"First item preview: {list(data[0].items())[:2]}...")
        return "List structure"
    
    # Check if it's a dict with 'restaurants' key
    elif isinstance(data, dict):
        print("\nThis JSON contains a DICTIONARY")
        print(f"Keys in dictionary: {list(data.keys())}")
        
        if "restaurants" in data:
            print("\nFound 'restaurants' key in dictionary!")
            restaurants = data["restaurants"]
            print(f"Type of data in 'restaurants': {type(restaurants)}")
            print(f"Number of restaurants: {len(restaurants)}")
            return "Dictionary with 'restaurants' key"
        else:
            print("\nNo 'restaurants' key found in dictionary")
            return "Dictionary without 'restaurants' key"
    
    # Neither a list nor a dict
    else:
        print(f"\nUnexpected structure: neither a list nor a dictionary")
        return "Unknown structure"

# Test with our file
result = explore_json_structure("tiny_test_restaurants.json")
print(f"\nConclusion: {result}")

# Create a JSON with a 'restaurants' wrapper
wrapped_test_data = {
    "restaurants": [
        {
            "name": "Sushi Spot",
            "rating": 4.8,
            "reviews": 200,
            "categories": ["Japanese", "Sushi"]
        },
        {
            "name": "Taco Time",
            "rating": 4.0,
            "reviews": 150,
            "categories": ["Mexican", "Tacos"]
        }
    ],
    "metadata": {
        "city": "Seattle",
        "date_generated": "2025-05-12"
    }
}

# Write to a file
with open("wrapped_test_restaurants.json", "w") as f:
    json.dump(wrapped_test_data, f, indent=2)

print("Created wrapped test JSON file: wrapped_test_restaurants.json")

# Test this structure too
result = explore_json_structure("wrapped_test_restaurants.json")
print(f"\nConclusion for wrapped data: {result}")