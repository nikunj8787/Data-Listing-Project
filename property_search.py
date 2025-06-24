import streamlit as st
import pandas as pd
from database_manager import get_properties, log_contact_view
from deepseek_integration import search_with_ai

def show_property_search():
    """Display the property search interface"""
    st.subheader("🔍 Find Your Perfect Property")
    
    # Create tabs for different search methods
    search_tab, filter_tab = st.tabs(["🤖 AI Search", "🔧 Advanced Filters"])
    
    with search_tab:
        show_ai_search()
    
    with filter_tab:
        show_filter_search()

def show_ai_search():
    """Natural language AI-powered search"""
    st.markdown("### Ask in Natural Language")
    st.write("Describe what you're looking for in plain English!")
    
    # AI search input
    ai_query = st.text_input(
        "What kind of property are you looking for?",
        placeholder="e.g., '2 BHK apartment near CG Road under 50 lakh' or 'affordable office space with parking'",
        help="Use natural language to describe your requirements"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 AI Search", type="primary"):
            if ai_query:
                with st.spinner("🔍 Searching with AI..."):
                    # Get AI-enhanced search results
                    results = search_with_ai(ai_query)
                    display_property_results(results, f"AI Search Results for: '{ai_query}'")
            else:
                st.warning("Please enter your search query")
    
    # Example queries
    st.markdown("### 💡 Example Queries")
    examples = [
        "2 BHK furnished apartment under 30,000 rent",
        "Commercial office space with parking in Ahmedabad",
        "3 BHK house for sale under 50 lakhs",
        "Shop for rent on main road"
    ]
    
    for example in examples:
        if st.button(f"Try: {example}", key=f"example_{example}"):
            st.session_state.example_query = example
            st.rerun()

def show_filter_search():
    """Traditional filter-based search"""
    st.markdown("### Filter Properties")
    
    # Create filter columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        property_type = st.selectbox(
            "Property Type",
            ["All Types", "Residential Rent", "Residential Sell", "Commercial Rent", "Commercial Sell"]
        )
        
        location = st.text_input("Location", placeholder="e.g., CG Road, Ahmedabad")
    
    with col2:
        price_range = st.slider(
            "Price Range (₹)",
            min_value=0,
            max_value=20000000,
            value=(0, 5000000),
            step=100000,
            format="₹%d"
        )
        
        bhk_type = st.selectbox(
            "BHK/Type",
            ["Any", "1 BHK", "2 BHK", "3 BHK", "4+ BHK", "Office", "Shop"]
        )
    
    with col3:
        furnished_status = st.selectbox(
            "Furnished Status",
            ["Any", "Fully Furnished", "Semi Furnished", "Unfurnished"]
        )
        
        property_age = st.selectbox(
            "Property Age",
            ["Any", "Under Construction", "Newly Built", "1-5 Years", "5+ Years"]
        )
    
    # Apply filters button
    if st.button("🔍 Apply Filters", type="primary"):
        filters = {
            'property_type': property_type,
            'location': location,
            'min_price': price_range[0],
            'max_price': price_range[1],
            'bhk_type': bhk_type if bhk_type != "Any" else None,
            'furnished_status': furnished_status if furnished_status != "Any" else None,
            'property_age': property_age if property_age != "Any" else None
        }
        
        results = get_properties(filters)
        display_property_results(results, "Filtered Search Results")

def display_property_results(results, title="Search Results"):
    """Display property search results"""
    st.markdown(f"### {title}")
    
    if results.empty:
        st.info("🔍 No properties found matching your criteria. Try adjusting your search terms.")
        return
    
    st.success(f"✅ Found {len(results)} properties matching your criteria")
    
    # Display options
    view_type = st.radio("View as:", ["📱 Cards", "📋 Table"], horizontal=True)
    
    if view_type == "📱 Cards":
        display_card_view(results)
    else:
        display_table_view(results)

def display_card_view(results):
    """Display properties in card format"""
    # Create columns for cards
    cols = st.columns(2)
    
    for i, (_, property_data) in enumerate(results.iterrows()):
        with cols[i % 2]:
            # Property card
            st.markdown(f"""
            <div class="property-card">
                <h4>{property_data['bhk_type']} in {property_data['location']}</h4>
                <p><strong>₹{property_data['price']:,}</strong></p>
                <p>📍 {property_data['property_type']}</p>
                <p>📐 {property_data['area']} sq.ft</p>
                <p>🏠 {property_data['furnished_status']}</p>
                <p>📅 {property_data['property_age']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Contact button with masking
            phone = str(property_data['contact_number'])
            masked_phone = f"{phone[:2]}XXXXXX{phone[-2:]}"
            
            if st.button(f"📞 Contact: {masked_phone}", key=f"contact_card_{i}"):
                # Log the contact view
                log_contact_view(st.session_state.user_email, property_data['property_id'])
                st.success(f"📱 Full Contact: {phone}")
                st.balloons()
            
            st.markdown("---")

def display_table_view(results):
    """Display properties in table format"""
    # Prepare display dataframe
    display_df = results.copy()
    display_df['Price'] = display_df['price'].apply(lambda x: f"₹{x:,}")
    display_df['Contact'] = display_df['contact_number'].apply(lambda x: f"{str(x)[:2]}XXXXXX{str(x)[-2:]}")
    
    # Select columns to display
    columns_to_show = ['property_type', 'location', 'bhk_type', 'Price', 'area', 'furnished_status', 'Contact']
    display_df = display_df[columns_to_show]
    
    # Rename columns for better display
    display_df.columns = ['Type', 'Location', 'BHK/Office', 'Price', 'Area (sq.ft)', 'Furnished', 'Contact']
    
    st.dataframe(display_df, use_container_width=True)
    
    # Contact reveal functionality
    st.markdown("### 📞 Reveal Contact Numbers")
    selected_index = st.selectbox(
        "Select property to view contact:",
        range(len(results)),
        format_func=lambda x: f"{results.iloc[x]['bhk_type']} in {results.iloc[x]['location']} - ₹{results.iloc[x]['price']:,}"
    )
    
    if st.button("📱 Reveal Contact Number"):
        selected_property = results.iloc[selected_index]
        log_contact_view(st.session_state.user_email, selected_property['property_id'])
        st.success(f"📞 Contact Number: {selected_property['contact_number']}")
        st.balloons()
