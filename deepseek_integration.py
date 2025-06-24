import requests
import streamlit as st
from database_manager import get_properties

# DeepSeek API configuration
DEEPSEEK_API_KEY = "sk-54bd3323c4d14bf08b941f0bff7a47d5"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def search_with_ai(query):
    """Use AI to enhance property search"""
    try:
        # First, get all properties
        all_properties = get_properties()
        
        if all_properties.empty:
            return all_properties
        
        # Use AI to interpret the query and filter properties
        ai_filters = interpret_query_with_ai(query)
        
        # Apply AI-suggested filters
        filtered_properties = apply_ai_filters(all_properties, ai_filters)
        
        return filtered_properties
        
    except Exception as e:
        st.error(f"AI search encountered an error: {str(e)}")
        # Fallback to basic text search
        return basic_text_search(query)

def interpret_query_with_ai(query):
    """Use DeepSeek API to interpret natural language query"""
    try:
        prompt = f"""
        Analyze this real estate search query and extract the following information in JSON format:
        Query: "{query}"
        
        Extract and return a JSON object with these fields (use null if not mentioned):
        {{
            "property_type": "Residential Rent/Residential Sell/Commercial Rent/Commercial Sell",
            "location": "location mentioned",
            "min_price": number or null,
            "max_price": number or null,
            "bhk_type": "1 BHK/2 BHK/3 BHK/4+ BHK/Office/Shop",
            "furnished_status": "Fully Furnished/Semi Furnished/Unfurnished",
            "keywords": ["array", "of", "important", "keywords"]
        }}
        
        Only return the JSON object, no other text.
        """
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Try to parse JSON response
            import json
            try:
                filters = json.loads(ai_response)
                return filters
            except:
                # If JSON parsing fails, return empty filters
                return {}
        else:
            return {}
            
    except Exception as e:
        st.warning(f"AI interpretation failed: {str(e)}")
        return {}

def apply_ai_filters(properties, ai_filters):
    """Apply AI-interpreted filters to properties"""
    if not ai_filters:
        return basic_text_search_fallback(properties)
    
    filtered = properties.copy()
    
    # Apply property type filter
    if ai_filters.get('property_type'):
        filtered = filtered[filtered['property_type'] == ai_filters['property_type']]
    
    # Apply location filter
    if ai_filters.get('location'):
        location_filter = ai_filters['location'].lower()
        filtered = filtered[filtered['location'].str.lower().str.contains(location_filter, na=False)]
    
    # Apply price filters
    if ai_filters.get('min_price'):
        filtered = filtered[filtered['price'] >= ai_filters['min_price']]
    
    if ai_filters.get('max_price'):
        filtered = filtered[filtered['price'] <= ai_filters['max_price']]
    
    # Apply BHK type filter
    if ai_filters.get('bhk_type'):
        filtered = filtered[filtered['bhk_type'] == ai_filters['bhk_type']]
    
    # Apply furnished status filter
    if ai_filters.get('furnished_status'):
        filtered = filtered[filtered['furnished_status'] == ai_filters['furnished_status']]
    
    # Apply keyword search if available
    if ai_filters.get('keywords'):
        for keyword in ai_filters['keywords']:
            keyword_lower = keyword.lower()
            # Search in location, features, and other text fields
            mask = (
                filtered['location'].str.lower().str.contains(keyword_lower, na=False) |
                filtered['features'].str.lower().str.contains(keyword_lower, na=False) |
                filtered['bhk_type'].str.lower().str.contains(keyword_lower, na=False)
            )
            filtered = filtered[mask]
    
    return filtered

def basic_text_search(query):
    """Fallback basic text search"""
    all_properties = get_properties()
    
    if all_properties.empty:
        return all_properties
    
    query_lower = query.lower()
    
    # Search in multiple fields
    mask = (
        all_properties['location'].str.lower().str.contains(query_lower, na=False) |
        all_properties['property_type'].str.lower().str.contains(query_lower, na=False) |
        all_properties['bhk_type'].str.lower().str.contains(query_lower, na=False) |
        all_properties['furnished_status'].str.lower().str.contains(query_lower, na=False)
    )
    
    return all_properties[mask]

def basic_text_search_fallback(properties):
    """Simple fallback when AI filters are empty"""
    # Return all properties if no specific filters could be applied
    return properties
