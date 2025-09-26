def create_general_analysis_prompt(restaurants_data):
    """
    Create a prompt for general restaurant analysis
    """
    return f"""
    You are an expert restaurant analyst with deep knowledge of the food industry.
    
    Analyze the following {len(restaurants_data)} restaurants and provide insights:
    
    {restaurants_data}
    
    Please provide:
    1. An overall summary of the restaurants (1-2 paragraphs)
    2. Key strengths and weaknesses for each restaurant based on reviews
    3. Common themes across all restaurants
    4. Suggestions for improvement for each restaurant
    
    Format your response with clear headings and bullet points where appropriate.
    """

def create_sentiment_analysis_prompt(restaurants_data):
    """
    Create a prompt focused on sentiment analysis of reviews
    """
    return f"""
    You are an expert in sentiment analysis for the restaurant industry.
    
    Analyze the reviews for these {len(restaurants_data)} restaurants:
    
    {restaurants_data}
    
    For each restaurant:
    1. Identify the overall sentiment (positive, negative, or mixed)
    2. Extract key positive phrases customers use
    3. Extract key negative phrases customers use
    4. Identify specific aspects receiving praise (food, service, atmosphere, etc.)
    5. Identify specific aspects receiving criticism
    
    Use specific quotes from reviews to support your analysis.
    """

def create_competitive_analysis_prompt(restaurants_data):
    """
    Create a prompt for competitive analysis between restaurants
    """
    return f"""
    You are a restaurant industry consultant specializing in competitive analysis.
    
    Compare and contrast these {len(restaurants_data)} restaurants:
    
    {restaurants_data}
    
    Provide:
    1. A comparison table of key metrics (rating, price point, popularity)
    2. Each restaurant's unique selling proposition
    3. Areas where each restaurant outperforms competitors
    4. Areas where each restaurant underperforms
    5. Market positioning analysis
    6. Recommendations for each restaurant to improve competitive position
    
    Format your analysis with clear sections for each point of comparison.
    """