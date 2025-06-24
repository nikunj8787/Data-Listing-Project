import streamlit as st
import pandas as pd
from database_manager import get_properties, log_contact_view, save_property, get_saved_properties
from deepseek_integration import search_with_ai

def show_property_search():
    """Enhanced property search interface with professional styling"""
    
    # Search method tabs with improved styling
    search_tab, filter_tab, saved_tab = st.tabs([
        "🤖 **AI Search**", 
        "🔧 **Advanced Filters**", 
        "❤️ **Saved Properties**"
    ])
    
    with search_tab:
        show_ai_search()
    
    with filter_tab:
        show_filter_search()
    
    with saved_tab:
        show_saved_properties()

def show_ai_search():
    """AI-powered natural language search"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem;">
        <h3 style="margin: 0;">🤖 AI-Powered Property Search</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
            Describe your ideal property in natural language and let AI find the perfect matches
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI search input with enhanced styling
    col1, col2 = st.columns([4, 1])
    
    with col1:
        ai_query = st.text_input(
            "🗣️ **Describe what you're looking for:**",
            placeholder="e.g., '2 BHK furnished apartment near CG Road under 30,000 rent' or 'office space with parking in Ahmedabad'",
            help="Use natural language to describe your requirements",
            key="ai_search_input"
        )
    
    with col2:
        search_button = st.button("🔍 **Search**", type="primary", use_container_width=True)
    
    if search_button and ai_query:
        with st.spinner("🔍 AI is analyzing your request..."):
            results = search_with_ai(ai_query)
            if not results.empty:
                st.success(f"🎯 Found {len(results)} properties matching your description!")
                display_property_results(results, f"AI Search Results for: '{ai_query}'")
            else:
                st.info("🔍 No properties found matching your criteria. Try adjusting your description.")
    
    # Example queries section
    st.markdown("### 💡 **Try These Example Searches:**")
    
    examples = [
        ("2 BHK furnished apartment under 30,000 rent", "🏠"),
        ("Commercial office space with parking in Ahmedabad", "🏢"),
        ("3 BHK house for sale under 50 lakhs", "🏡"),
        ("Shop for rent on main road with good footfall", "🏪")
    ]
    
    cols = st.columns(2)
    for i, (example, icon) in enumerate(examples):
        with cols[i % 2]:
            if st.button(f"{icon} {example}", key=f"example_{i}", use_container_width=True):
                st.session_state.ai_search_input = example
                st.rerun()

def show_filter_search():
    """Advanced filter-based property search"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e67e22 0%, #d35400 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem;">
        <h3 style="margin: 0;">🔧 Advanced Property Filters</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
            Use multiple criteria to find properties that match your exact requirements
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter sections
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🏠 **Property Details**")
            property_type = st.selectbox(
                "Property Type:",
                ["All Types", "Residential Rent", "Residential Sell", "Commercial Rent", "Commercial Sell"],
                help="Select the type of property you're looking for"
            )
            
            bhk_type = st.selectbox(
                "BHK/Type:",
                ["Any", "1 BHK", "2 BHK", "3 BHK", "4+ BHK", "Office", "Shop"],
                help="Choose the configuration you need"
            )
            
            furnished_status = st.selectbox(
                "Furnished Status:",
                ["Any", "Fully Furnished", "Semi Furnished", "Unfurnished"]
            )
        
        with col2:
            st.markdown("#### 📍 **Location & Price**")
            location = st.text_input(
                "Location:",
                placeholder="e.g., CG Road, Satellite, Ahmedabad",
                help="Enter area, landmark, or city name"
            )
            
            price_range = st.slider(
                "Price Range (₹):",
                min_value=0,
                max_value=50000000,
                value=(0, 5000000),
                step=100000,
                format="₹%d",
                help="Adjust the price range according to your budget"
            )
        
        with col3:
            st.markdown("#### 🏗️ **Property Features**")
            property_age = st.selectbox(
                "Property Age:",
                ["Any", "Under Construction", "Newly Built", "1-5 Years", "5+ Years"]
            )
            
            area_range = st.slider(
                "Area (sq.ft):",
                min_value=0,
                max_value=10000,
                value=(0, 5000),
                step=100,
                help="Select the area range you prefer"
            )
            
            # Additional filters
            st.markdown("**Additional Requirements:**")
            parking_required = st.checkbox("🚗 Parking Required")
            lift_required = st.checkbox("🛗 Lift Available")
    
    # Apply filters button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 **Apply Filters**", type="primary", use_container_width=True):
            filters = {
                'property_type': property_type,
                'location': location,
                'min_price': price_range[0],
                'max_price': price_range[1],
                'bhk_type': bhk_type if bhk_type != "Any" else None,
                'furnished_status': furnished_status if furnished_status != "Any" else None,
                'property_age': property_age if property_age != "Any" else None,
                'min_area': area_range[0],
                'max_area': area_range[1],
                'parking_required': parking_required,
                'lift_required': lift_required
            }
            
            results = get_properties(filters, st.session_state.user_email)
            display_property_results(results, "Filtered Search Results")

def show_saved_properties():
    """Display customer's saved/favorite properties"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem;">
        <h3 style="margin: 0;">❤️ Your Saved Properties</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
            Properties you've bookmarked for future reference
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    saved_properties = get_saved_properties(st.session_state.user_email)
    
    if saved_properties.empty:
        st.info("📝 You haven't saved any properties yet. Use the ❤️ button on property cards to save them!")
    else:
        st.success(f"📋 You have {len(saved_properties)} saved properties")
        
        for i, (_, property_data) in enumerate(saved_properties.iterrows()):
            display_property_card(property_data, f"saved_{i}", show_save_button=False)

def display_property_results(results, title="Search Results"):
    """Display property search results with enhanced styling"""
    
    if results.empty:
        st.info("🔍 No properties found matching your criteria. Try adjusting your search terms or filters.")
        return
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); 
                color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="margin: 0;">📊 {title}</h4>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Found {len(results)} properties matching your criteria</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display options
    col1, col2 = st.columns([3, 1])
    with col1:
        view_type = st.radio(
            "Display as:", 
            ["🎴 Property Cards", "📋 Data Table"], 
            horizontal=True,
            help="Choose how you want to view the results"
        )
    
    with col2:
        sort_option = st.selectbox(
            "Sort by:",
            ["Price: Low to High", "Price: High to Low", "Newest First", "Area: Large to Small"]
        )
    
    # Sort results
    results_sorted = sort_properties(results, sort_option)
    
    if view_type == "🎴 Property Cards":
        display_card_view(results_sorted)
    else:
        display_table_view(results_sorted)

def sort_properties(df, sort_option):
    """Sort properties based on user selection"""
    if sort_option == "Price: Low to High":
        return df.sort_values('price', ascending=True)
    elif sort_option == "Price: High to Low":
        return df.sort_values('price', ascending=False)
    elif sort_option == "Newest First":
        return df.sort_values('created_at', ascending=False)
    elif sort_option == "Area: Large to Small":
        return df.sort_values('area', ascending=False)
    return df

def display_card_view(results):
    """Display properties in enhanced card format"""
    cols = st.columns(2)
    
    for i, (_, property_data) in enumerate(results.iterrows()):
        with cols[i % 2]:
            display_property_card(property_data, f"card_{i}")

def display_property_card(property_data, key_suffix, show_save_button=True):
    """Display individual property card with professional styling"""
    
    # Determine property type color
    type_colors = {
        "Residential Rent": "#3498db",
        "Residential Sell": "#e74c3c", 
        "Commercial Rent": "#f39c12",
        "Commercial Sell": "#9b59b6"
    }
    
    type_color = type_colors.get(property_data['property_type'], "#7f8c8d")
    
    st.markdown(f"""
    <div class="property-card" style="border-left: 5px solid {type_color};">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <h4 style="margin: 0; color: #2c3e50;">{property_data['bhk_type']} in {property_data['location']}</h4>
            <span style="background: {type_color}; color: white; padding: 0.3rem 0.8rem; 
                         border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                {property_data['property_type']}
            </span>
        </div>
        
        <div class="price" style="color: #27ae60; font-size: 1.4rem; font-weight: 700; margin-bottom: 1rem;">
            ₹{property_data['price']:,}
            {' /month' if 'Rent' in property_data['property_type'] else ''}
        </div>
        
        <div class="property-details">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 1rem;">
                <div><strong>📐 Area:</strong> {property_data['area']} sq.ft</div>
                <div><strong>🏠 Furnished:</strong> {property_data['furnished_status']}</div>
                <div><strong>📅 Age:</strong> {property_data['property_age']}</div>
                <div><strong>🏢 Floor:</strong> {property_data.get('floor_number', 'N/A')}/{property_data.get('total_floors', 'N/A')}</div>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <strong>📍 Address:</strong> {property_data.get('address', property_data['location'])}
            </div>
            
            {f"<div style='margin-bottom: 1rem;'><strong>🎯 Amenities:</strong> {property_data.get('amenities', 'Basic amenities')}</div>" if property_data.get('amenities') else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Contact button with masking
        phone = str(property_data['contact_number'])
        masked_phone = f"{phone[:2]}XXXXXX{phone[-2:]}"
        
        if st.button(f"📞 {masked_phone}", key=f"contact_{key_suffix}", use_container_width=True):
            log_contact_view(st.session_state.user_email, property_data['property_id'])
            st.success(f"📱 **Full Contact:** {phone}")
            st.balloons()
    
    with col2:
        if show_save_button and st.button("❤️ Save", key=f"save_{key_suffix}", use_container_width=True):
            if save_property(st.session_state.user_email, property_data['property_id']):
                st.success("✅ Property saved to favorites!")
            else:
                st.info("ℹ️ Property already in your favorites")
    
    with col3:
        if st.button("📋 Details", key=f"details_{key_suffix}", use_container_width=True):
            show_property_details(property_data)

def display_table_view(results):
    """Display properties in enhanced table format"""
    # Prepare display dataframe
    display_df = results.copy()
    
    # Format columns for better display
    display_df['Price'] = display_df['price'].apply(lambda x: f"₹{x:,}")
    display_df['Area'] = display_df['area'].apply(lambda x: f"{x} sq.ft")
    display_df['Contact'] = display_df['contact_number'].apply(lambda x: f"{str(x)[:2]}XXXXXX{str(x)[-2:]}")
    
    # Select and rename columns
    columns_to_show = [
        'property_type', 'location', 'bhk_type', 'Price', 'Area', 
        'furnished_status', 'property_age', 'Contact'
    ]
    
    display_df = display_df[columns_to_show]
    display_df.columns = [
        'Type', 'Location', 'BHK/Office', 'Price', 'Area', 
        'Furnished', 'Age', 'Contact'
    ]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Type": st.column_config.TextColumn(width="medium"),
            "Location": st.column_config.TextColumn(width="medium"),
            "Price": st.column_config.TextColumn(width="small"),
            "Contact": st.column_config.TextColumn(width="small")
        }
    )
    
    # Contact reveal functionality
    st.markdown("### 📞 **Reveal Contact Numbers**")
    
    if len(results) > 0:
        selected_index = st.selectbox(
            "Select property to view contact:",
            range(len(results)),
            format_func=lambda x: f"{results.iloc[x]['bhk_type']} in {results.iloc[x]['location']} - ₹{results.iloc[x]['price']:,}",
            key="table_contact_select"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📱 **Reveal Contact**", type="primary"):
                selected_property = results.iloc[selected_index]
                log_contact_view(st.session_state.user_email, selected_property['property_id'])
                
                with col2:
                    st.success(f"📞 **Contact:** {selected_property['contact_number']}")
                    st.balloons()

def show_property_details(property_data):
    """Show detailed property information in a modal-like display"""
    with st.expander(f"🏠 **Detailed Information - {property_data['bhk_type']} in {property_data['location']}**", expanded=True):
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏠 **Property Information**")
            st.write(f"**Type:** {property_data['property_type']}")
            st.write(f"**BHK/Configuration:** {property_data['bhk_type']}")
            st.write(f"**Area:** {property_data['area']} sq.ft")
            st.write(f"**Price:** ₹{property_data['price']:,}")
            st.write(f"**Furnished Status:** {property_data['furnished_status']}")
            st.write(f"**Property Age:** {property_data['property_age']}")
            
        with col2:
            st.markdown("#### 📍 **Location & Features**") 
            st.write(f"**Location:** {property_data['location']}")
            st.write(f"**Address:** {property_data.get('address', 'Not specified')}")
            st.write(f"**Floor:** {property_data.get('floor_number', 'N/A')}/{property_data.get('total_floors', 'N/A')}")
            st.write(f"**Facing:** {property_data.get('facing', 'Not specified')}")
            st.write(f"**Parking:** {'✅ Available' if property_data.get('parking') else '❌ Not Available'}")
            st.write(f"**Lift:** {'✅ Available' if property_data.get('lift_available') else '❌ Not Available'}")
        
        if property_data.get('amenities'):
            st.markdown("#### 🎯 **Amenities**")
            st.write(property_data['amenities'])
        
        if property_data.get('description'):
            st.markdown("#### 📝 **Description**")
            st.write(property_data['description'])
        
        # Additional costs for rentals
        if 'Rent' in property_data['property_type']:
            if property_data.get('maintenance_cost') or property_data.get('security_deposit'):
                st.markdown("#### 💰 **Additional Costs**")
                if property_data.get('maintenance_cost'):
                    st.write(f"**Maintenance:** ₹{property_data['maintenance_cost']:,}/month")
                if property_data.get('security_deposit'):
                    st.write(f"**Security Deposit:** ₹{property_data['security_deposit']:,}")
