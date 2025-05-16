import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def setup_openai_client():
    """
    Set up the OpenAI client with API key
    """
    # Try to get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # If not found in environment, you could ask for it
    if not api_key:
        api_key = input("Please enter your OpenAI API key: ")
        # Optionally save to environment for current session
        os.environ["OPENAI_API_KEY"] = api_key
    
    # Initialize client
    client = OpenAI(api_key=api_key)
    return client

def test_openai_connection(client):
    """
    Simple test to verify OpenAI API connection
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # You can use gpt-4 if available to you
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, can you hear me? Please respond with a simple 'Yes, I can hear you.'"}
            ],
            max_tokens=20
        )
        
        print("Connection successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    
def get_restaurant_insights(client, prompt, model="gpt-3.5-turbo"):
    """
    Get restaurant insights from OpenAI based on a prompt
    """
    try:
        print(f"Sending prompt to OpenAI ({len(prompt)} characters)...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a restaurant analytics expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,  # Lower temperature for more factual analysis
            max_tokens=1000  # Adjust based on your needs
        )
        
        print("Response received successfully.")
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error getting insights from OpenAI: {e}")
        return None