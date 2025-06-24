import requests
import streamlit as st
import pandas as pd
from database_manager import get_properties
import json

# DeepSeek API configuration
DEEPSEEK_API_KEY = "sk-54bd3323c4d14bf08b941f0bff7a47d5"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def search_with_ai(query):
    """Use AI to enhance property search with natural language processing"""
    try:
        # First, get all properties available to the customer
        all_properties = get_properties(customer_email=st.session_state.user_email)
        
        if all_properties.empty:
            return all_properties
        
        # Use AI to interpret the query and create filters
        ai_filters = interpret_query_with_ai(query)
        
        # Apply AI-suggested filters to the properties
        filtered_properties = apply_ai_filters(all_properties, ai_filters, query)
        
        return filtered_properties
        
    except Exception as e:
        st.warning(f"AI search encountered an issue: {str(e)}. Falling back to basic search.")
        # Fallback to basic text search
        return basic_text_search(query)

def interpret_query_with_ai(query):
    """Use DeepSeek API to interpret natural language query into structured filters"""
    try:
        prompt = f"""
        Analyze this real estate search query and extract filtering criteria. Return a JSON object with these exact fields:

        Query: "{query}"
        
        Extract information and return JSON with these fields (use null if not mentioned):
        {{
            "property_type": "Residential Rent" or "Residential Sell" or "Commercial Rent" or "Commercial Sell" or null,
            "location_keywords": ["array", "of", "location", "words"],
            "min_price": number or null,
            "max_price": number or null,
            "bhk_type": "1 BHK" or "2 BHK" or "3 BHK" or "4+ BHK" or "Office" or "Shop" or null,
            "furnished_status": "Fully Furnished" or "Semi Furnished" or "Unfurnished" or null,
            "property_age": "Under Construction" or "Newly Built" or "1-5 Years" or "5+ Years" or null,
            "area_preference": "small" or "medium" or "large" or null,
            "budget_preference": "affordable" or "moderate" or "premium" or "luxury" or null,
            "special_features": ["parking", "gym", "pool", "security", "lift"],
            "urgency": "urgent" or "flexible" or null
        }}
        
        Rules:
        - For price mentions like "under 50 lakh", set max_price to 5000000
        - For "affordable", set budget_preference to "affordable"
        - For area mentions, extract location keywords
        - Only include features mentioned in the query
        - Return only valid JSON, no other text
        """
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Try to parse JSON response
            try:
                # Clean the response to extract JSON
                ai_response = ai_response.strip()
                if ai_response.startswith('```
                    ai_response = ai_response[7:]
                if ai_response.endswith('```'):
                    ai_response = ai_response[:-3]
                ai_response = ai_response.strip()
                
                filters = json.loads(ai_response)
                return filters
            except json.JSONDecodeError as e:
                st.warning(f"AI response parsing failed: {str(e)}")
                return extract_basic_filters(query)
        else:
            st.warning(f"AI API request failed with status {response.status_code}")
            return extract_basic_filters(query)
            
    except Exception as e:
        st.warning(f"AI interpretation failed: {str(e)}")
        return extract_basic_filters(query)

def extract_basic_filters(query):
    """Extract basic filters from query using simple keyword matching"""
    query_lower = query.lower()
    filters = {}
    
    # Property type detection
    if 'rent' in query_lower and 'residential' in query_lower:
        filters['property_type'] = 'Residential Rent'
    elif 'sell' in query_lower and 'residential' in query_lower:
        filters['property_type'] = 'Residential Sell'
    elif 'rent' in query_lower and ('office' in query_lower or 'commercial' in query_lower):
        filters['property_type'] = 'Commercial Rent'
    elif 'sell' in query_lower and ('shop' in query_lower or 'commercial' in query_lower):
        filters['property_type'] = 'Commercial Sell'
    
    # BHK detection
    if '1 bhk' in query_lower:
        filters['bhk_type'] = '1 BHK'
    elif '2 bhk' in query_lower:
        filters['bhk_type'] = '2 BHK'
    elif '3 bhk' in query_lower:
        filters['bhk_type'] = '3 BHK'
    
    # Location keywords
    location_keywords = []
    common_locations = ['cg road', 'satellite', 'bodakdev', 'vastrapur', 'ahmedabad', 'paldi', 'navrangpura']
    for location in common_locations:
        if location in query_lower:
            location_keywords.append(location)
    
    if location_keywords:
        filters['location_keywords'] = location_keywords
    
    # Price detection
    if 'under' in query_lower:
        if 'lakh' in query_lower:
            # Extract number before lakh
            words = query_lower.split()
            for i, word in enumerate(words):
                if word == 'lakh' and i > 0:
                    try:
                        amount = float(words[i-1])
                        filters['max_price'] = amount * 100000
                        break
                    except:
                        pass
    
    # Budget preference
    if any(word in query_lower for word in ['affordable', 'cheap', 'budget']):
        filters['budget_preference'] = 'affordable'
    elif any(word in query_lower for word in ['luxury', 'premium', 'high-end']):
        filters['budget_preference'] = 'luxury'
    
    # Special features
    special_features = []
    if 'parking' in query_lower:
        special_features.append('parking')
    if 'gym' in query_lower:
        special_features.append('gym')
    if 'pool' in query_lower:
        special_features.append('pool')
    
    if special_features:
        filters['special_features'] = special_features
    
    return filters

def apply_ai_filters(properties, ai_filters, original_query):
    """Apply AI-interpreted filters to properties dataset"""
    if not ai_filters:
        return basic_text_search(original_query)
    
    filtered = properties.copy()
    
    # Apply property type filter
    if ai_filters.get('property_type'):
        filtered = filtered[filtered['property_type'] == ai_filters['property_type']]
    
    # Apply location filters
    if ai_filters.get('location_keywords'):
        location_mask = pd.Series([False] * len(filtered), index=filtered.index)
        for keyword in ai_filters['location_keywords']:
            keyword_lower = keyword.lower()
            location_mask |= (
                filtered['location'].str.lower().str.contains(keyword_lower, na=False) |
                filtered['address'].str.lower().str.contains(keyword_lower, na=False)
            )
        filtered = filtered[location_mask]
    
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
    
    # Apply property age filter
    if ai_filters.get('property_age'):
        filtered = filtered[filtered['property_age'] == ai_filters['property_age']]
    
    # Apply budget preference filter
    if ai_filters.get('budget_preference'):
        if ai_filters['budget_preference'] == 'affordable':
            # Filter for lower price range
            median_price = filtered['price'].median()
            filtered = filtered[filtered['price'] <= median_price]
        elif ai_filters['budget_preference'] == 'luxury':
            # Filter for higher price range
            q75_price = filtered['price'].quantile(0.75)
            filtered = filtered[filtered['price'] >= q75_price]
    
    # Apply area preference filter
    if ai_filters.get('area_preference'):
        if ai_filters['area_preference'] == 'large':
            median_area = filtered['area'].median()
            filtered = filtered[filtered['area'] >= median_area]
        elif ai_filters['area_preference'] == 'small':
            median_area = filtered['area'].median()
            filtered = filtered[filtered['area'] <= median_area]
    
    # Apply special features filter
    if ai_filters.get('special_features'):
        for feature in ai_filters['special_features']:
            if feature == 'parking':
                filtered = filtered[filtered['parking'] == True]
            elif feature in ['gym', 'pool', 'security']:
                # Search in amenities field
                filtered = filtered[
                    filtered['amenities'].str.lower().str.contains(feature, na=False)
                ]
    
    # If no results found, try with relaxed filters
    if filtered.empty and not properties.empty:
        st.info("🔍 No exact matches found. Showing similar properties...")
        return relaxed_search(properties, ai_filters, original_query)
    
    return filtered

def relaxed_search(properties, ai_filters, original_query):
    """Perform a more relaxed search when exact filters return no results"""
    filtered = properties.copy()
    
    # Apply only the most important filters
    if ai_filters.get('property_type'):
        filtered = filtered[filtered['property_type'] == ai_filters['property_type']]
    
    # Relaxed location search
    if ai_filters.get('location_keywords'):
        location_mask = pd.Series([False] * len(filtered), index=filtered.index)
        for keyword in ai_filters['location_keywords']:
            keyword_lower = keyword.lower()
            location_mask |= filtered['location'].str.lower().str.contains(keyword_lower, na=False)
        if location_mask.any():
            filtered = filtered[location_mask]
    
    # Relaxed price filter (expand range by 20%)
    if ai_filters.get('max_price'):
        relaxed_max_price = ai_filters['max_price'] * 1.2
        filtered = filtered[filtered['price'] <= relaxed_max_price]
    
    if filtered.empty:
        # Final fallback to basic text search
        return basic_text_search(original_query)
    
    return filtered

def basic_text_search(query):
    """Fallback basic text search when AI search fails"""
    try:
        all_properties = get_properties(customer_email=st.session_state.user_email)
        
        if all_properties.empty:
            return all_properties
        
        query_lower = query.lower()
        
        # Search in multiple fields
        mask = (
            all_properties['location'].str.lower().str.contains(query_lower, na=False) |
            all_properties['address'].str.lower().str.contains(query_lower, na=False) |
            all_properties['property_type'].str.lower().str.contains(query_lower, na=False) |
            all_properties['bhk_type'].str.lower().str.contains(query_lower, na=False) |
            all_properties['furnished_status'].str.lower().str.contains(query_lower, na=False) |
            all_properties['amenities'].str.lower().str.contains(query_lower, na=False)
        )
        
        return all_properties[mask]
        
    except Exception as e:
        st.error(f"Search failed: {str(e)}")
        return pd.DataFrame()

def get_search_suggestions(query):
    """Get search suggestions based on available properties"""
    try:
        all_properties = get_properties(customer_email=st.session_state.user_email)
        
        if all_properties.empty:
            return []
        
        suggestions = []
        
        # Get unique locations
        locations = all_properties['location'].unique()
        suggestions.extend([f"Properties in {loc}" for loc in locations[:3]])
        
        # Get price ranges
        min_price = all_properties['price'].min()
        max_price = all_properties['price'].max()
        suggestions.append(f"Properties under ₹{int(max_price/2):,}")
        
        # Get BHK types
        bhk_types = all_properties['bhk_type'].unique()
        suggestions.extend([f"{bhk} properties" for bhk in bhk_types[:2]])
        
        return suggestions[:5]
        
    except:
        return []
