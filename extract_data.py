# import pandas as pd
# import requests

# file = '/Users/isaac/Documents/Python/Restaurant Recommendation Project/Data/yelp_categories.csv'

# df = pd.read_csv(file)
# print(df.head())
import ijson
import json
import os
import sys
import argparse
from tqdm import tqdm

def extract_json_snippet_streaming(file_path, max_items=5, depth=2):
    """"
    Extract and display a snippet from a gigantic JSON file using streaming parser.
    
    Args:
        file_path (str): Path to the JSON file
        max_items (int): Maximum number of items to display per level
        depth (int): Maximum depth to traverse in the JSON structure
    
    Returns:
        dict or list: A snippet of the JSON data
    """
    try:
        # Get file size in GB for information
        file_size_gb = os.path.getsize(file_path) / (1024 * 1024 * 1024)
        print(f"processing JSON file of size: {file_size_gb:.2f} GB")

        # Determine if the root is a dict or list by looking at the first character
        with open(file_path, 'rb') as file:
            first_char = file.read(1).decode('utf-8').strip()
            is_dict = first_char == '{'

        result = {} if is_dict else []
        count = 0
        
        print("Analyzing JSON structure...")

        # Process differently based on root type
        with open(file_path, 'rb') as file:
            if is_dict:
                # For objects, extract some top-level keys and their values
                for prefix, event, value in ijson.parse(file):
                    for prefix, event, value in ijson.parse(file):
                        if prefix == '' and event == 'map_key':
                            key = value
                            if count < max_items:
                                # Get a sample of the value for this key
                                value_sample = extract_value_sample(file_path, key, max_items, depth)
                                result[key] = value_sample
                                count += 1
                            else:
                                break
            else:
                # For arrays, extract some items from the beginning
                items = ijson.items(file, 'item')
                for item in items:
                    if count < max_items:
                        result.append(sample_structure(item, max_items, current_depth=1, max_depth=depth))
                        count += 1
                    else:
                        break
            # Print the snippet with nice formatting
        print("\nJSON SNIPPET:")
        print(json.dumps(result, indent=2))
            
        return result
            
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def extract_ndjson_snippet(file_path, max_items=9, depth=2):
    """
    Extract and display snippets from a Yelp-style NDJSON file
    (JSON Lines format - one JSON object per line)
    """
    try:
        file_size_gb = os.path.getsize(file_path) / (1024 * 1024 * 1024)
        print(f"Processing JSON file of size: {file_size_gb:.2f} GB")
        
        results = []
        count = 0
        
        with open(file_path, 'r', encoding='utf-8') as file:
            print("Analyzing JSON Lines structure...")
            for line in file:
                if count >= max_items:
                    break
                    
                try:
                    # Parse each line as an individual JSON object
                    obj = json.loads(line.strip())
                    
                    # Sample the structure to avoid huge nested objects
                    sampled_obj = sample_structure(obj, max_items, current_depth=0, max_depth=depth)
                    results.append(sampled_obj)
                    count += 1
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing line: {e}")
                    continue
        
        # Print and return the results
        print(f"\nFound {count} JSON objects. Showing first {min(count, max_items)}:")
        print(json.dumps(results, indent=2))
        
        return results
        
    except Exception as e:
        print(f"Error: {e}")
        return None
    

def sample_structure(value, max_items, current_depth=0, max_depth=2):
    """Sample a nested structure up to a certain depth and item count."""
    if current_depth >= max_depth:
        if isinstance(value, (dict, list)) and len(value) > 0:
            return f"[Complex {type(value).__name__} with {len(value)} items]"
        return value
    
    if isinstance(value, dict):
        result = {}
        for i, (k, v) in enumerate(value.items()):
            if i >= max_items:
                remaining = len(value) - max_items
                result["..."] = f"[{remaining} more keys not shown]"
                break
            result[k] = sample_structure(v, max_items, current_depth + 1, max_depth)
        return result
    
    elif isinstance(value, list):
        result = []
        for i, item in enumerate(value):
            if i >= max_items:
                remaining = len(value) - max_items
                result.append(f"[{remaining} more items not shown]")
                break
            result.append(sample_structure(item, max_items, current_depth + 1, max_depth))
        return result
    
    else:
        return value
    

def main():
    parser = argparse.ArgumentParser(description='Extract a snippet from a large JSON file')
    parser.add_argument('file_path', help='Path to the JSON file')
    parser.add_argument('--max-items', type=int, default=5, help='Maximum number of items to display per level')
    parser.add_argument('--depth', type=int, default=2, help='Maximum depth to traverse in the JSON structure')
    
    args = parser.parse_args()
    
    extract_ndjson_snippet(args.file_path, args.max_items, args.depth)

if __name__ == "__main__":
    main()