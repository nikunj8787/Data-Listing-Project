# property_search.py
import streamlit as st
import pandas as pd
from database_manager import get_properties, log_contact_view, save_property, get_saved_properties
from deepseek_integration import search_with_ai

def show_property_search():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem;">
        <h3 style="margin: 0;">🤖 AI-Powered Search</h3>
        <p style="margin: 0.5rem 0 0 0;">Describe your needs and let AI find matches</p>
    </div>
    """, unsafe_allow_html=True)
    ai_query = st.text_input("🗣️ Describe your ideal property:", placeholder="e.g., '2 BHK near CG Road under 50 lakh'")
    if st.button("🔍 Search with AI") and ai_query:
        with st.spinner("Analyzing with AI..."):
            results = search_with_ai(ai_query)
            if not results.empty:
                st.success(f"Found {len(results)} properties.")
                display_property_results(results, f"AI Search: '{ai_query}'")
            else:
                st.info("No matches found.")
    st.markdown("### Example Queries")
    examples = [
        ("2 BHK furnished apartment under 30,000 rent", "🏠"),
        ("Commercial office with parking in Ahmedabad", "🏢"),
        ("3 BHK house for sale under 50 lakhs", "🏡"),
        ("Shop for rent on main road", "🏪")
    ]
    for text, icon in examples:
        if st.button(f"{icon} {text}"):
            st.session_state['ai_query'] = text
            st.rerun()

def show_filter_search():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e67e22 0%, #d35400 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem;">
        <h3 style="margin: 0;">🔧 Advanced Filters</h3>
        <p style="margin: 0.5rem 0 0 0;">Refine your search with multiple criteria</p>
    </div>
    """, unsafe_allow_html=True)
    with st.form("filter_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            property_type = st.selectbox("Property Type:", ["All Types", "Residential Rent", "Residential Sell", "Commercial Rent", "Commercial Sell"])
            bhk_type = st.selectbox("BHK/Type:", ["Any", "1 BHK", "2 BHK", "3 BHK", "4+ BHK", "Office", "Shop"])
            furnished_status = st.selectbox("Furnished Status:", ["Any", "Fully Furnished", "Semi Furnished", "Unfurnished"])
        with col2:
            location = st.text_input("Location:", placeholder="e.g., CG Road")
            min_price, max_price = st.slider("Price Range (₹):", 0, 50000000, (0, 5000000), step=100000)
            property_age = st.selectbox("Property Age:", ["Any", "Under Construction", "Newly Built", "1-5 Years", "5+ Years"])
        with col3:
            min_area, max_area = st.slider("Area (sq.ft):", 0, 10000, (0, 5000), step=100)
            parking_req = st.checkbox("🚗 Parking Required")
            lift_req = st.checkbox("🛗 Lift Available")
        if st.form_submit_button("🔍 Apply Filters"):
            filters = {
                'property_type': property_type,
                'location': location,
                'min_price': min_price,
                'max_price': max_price,
                'bhk_type': bhk_type if bhk_type != 'Any' else None,
                'furnished_status': furnished_status if furnished_status != 'Any' else None,
                'property_age': property_age if property_age != 'Any' else None,
                'min_area': min_area,
                'max_area': max_area,
                'parking_required': parking_req,
                'lift_required': lift_req
            }
            results = get_properties(filters, st.session_state['user_email'])
            display_property_results(results, "Filtered Results")

def display_property_results(results, title="Results"):
    if results.empty:
        st.info("No properties match your criteria.")
        return
    st.markdown(f"<h4>📊 {title} ({len(results)} found)</h4>", unsafe_allow_html=True)
    view = st.radio("View as:", ["🎴 Cards", "📋 Table"], index=0)
    if view == "🎴 Cards":
        display_card_view(results)
    else:
        display_table_view(results)

def display_card_view(df):
    cols = st.columns(2)
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i % 2]:
            display_property_card(row, f"card_{i}")

def display_property_card(row, key_suffix):
    type_colors = {
        "Residential Rent": "#3498db",
        "Residential Sell": "#e74c3c",
        "Commercial Rent": "#f39c12",
        "Commercial Sell": "#9b59b6"
    }
    color = type_colors.get(row['property_type'], "#7f8c8d")
    st.markdown(f"""
    <div style="border-left: 5px solid {color}; background:#fff; padding:1rem; border-radius:10px; margin-bottom:1rem; box-shadow:0 4px 8px rgba(0,0,0,0.1);">
        <h4 style="margin-top:0;">{row['bhk_type']} in {row['location']}</h4>
        <div style="font-size:1.2rem; font-weight:700; color:#27ae60;">₹{row['price']:,} {'/month' if 'Rent' in row['property_type'] else ''}</div>
        <div style="margin-top:0.5rem;">
            <strong>Type:</strong> {row['property_type']}<br>
            <strong>Area:</strong> {row['area']} sq.ft<br>
            <strong>Furnished:</strong> {row['furnished_status']}<br>
            <strong>Age:</strong> {row['property_age']}
        </div>
        <div style="margin-top:0.5rem;">
            <button style="background:#2980b9; color:#fff; border:none; padding:0.5rem 1rem; border-radius:5px; cursor:pointer;" onclick="window.location.reload();">📞 {f'{row["contact_number"][:2]}XXXXXX{row["contact_number"][-2:]}'}</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_table_view(df):
    df_display = df.copy()
    df_display['Price'] = df_display['price'].apply(lambda x: f"₹{x:,}")
    df_display['Contact'] = df_display['contact_number'].apply(lambda x: f"{str(x)[:2]}XXXXXX{str(x)[-2:]}")
    df_display = df_display[['property_type', 'location', 'bhk_type', 'Price', 'area', 'furnished_status', 'property_age', 'Contact']]
    df_display.columns = ['Type', 'Location', 'BHK', 'Price', 'Area', 'Furnished', 'Age', 'Contact']
    st.dataframe(df_display, use_container_width=True)

def log_contact_view(user_email, property_id):
    from database_manager import log_contact_view
    log_contact_view(user_email, property_id)
