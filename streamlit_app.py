import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
import random
import string
import requests
import json

# Import custom modules
from database_manager import initialize_database, get_user_data, add_user, get_properties
from auth_handler import handle_authentication
from property_search import show_property_search
from admin_functions import show_admin_panel
from operator_functions import show_operator_panel
from customer_functions import show_customer_profile

# Page configuration
st.set_page_config(
    page_title="Real Estate Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
.main {
    background-color: #f8f9fa;
}
.stButton > button {
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 500;
}
.stButton > button:hover {
    background-color: #0056b3;
    color: white;
}
.property-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 1rem 0;
}
.header-style {
    background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize database on first run
    initialize_database()
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.session_state.current_otp = None
    
    # Main header
    st.markdown("""
    <div class="header-style">
        <h1>🏢 Real Estate Data Listing Platform</h1>
        <p>Comprehensive property management solution for brokers and customers</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication check
    if not st.session_state.authenticated:
        handle_authentication()
    else:
        # Show logout button in sidebar
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_role = None
            st.rerun()
        
        # Display appropriate panel based on user role
        st.sidebar.markdown(f"**Logged in as:** {st.session_state.user_email}")
        st.sidebar.markdown(f"**Role:** {st.session_state.user_role.title()}")
        
        if st.session_state.user_role == "admin":
            show_admin_panel()
        elif st.session_state.user_role == "operator":
            show_operator_panel()
        elif st.session_state.user_role == "customer":
            show_customer_panel()

def show_customer_panel():
    """Main customer panel with navigation"""
    st.header(f"Welcome, {st.session_state.user_email}")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Property Search", "📞 Contact History", "👤 Profile", "💰 Payments"])
    
    with tab1:
        show_property_search()
    
    with tab2:
        st.subheader("Contact View History")
        contact_history = get_contact_history(st.session_state.user_email)
        if contact_history.empty:
            st.info("You haven't viewed any contact details yet")
        else:
            st.dataframe(contact_history, use_container_width=True)
    
    with tab3:
        show_customer_profile()
    
    with tab4:
        show_payment_info()

def get_contact_history(user_email):
    """Get contact view history for customer"""
    try:
        conn = sqlite3.connect('real_estate.db')
        query = '''
        SELECT p.property_type, p.location, p.bhk_type, p.price, cv.viewed_at
        FROM contact_views cv
        JOIN properties p ON cv.property_id = p.property_id
        JOIN users u ON cv.customer_id = u.user_id
        WHERE u.email = ?
        ORDER BY cv.viewed_at DESC
        '''
        df = pd.read_sql_query(query, conn, params=(user_email,))
        conn.close()
        return df
    except:
        return pd.DataFrame()

def show_payment_info():
    """Show payment information and QR code"""
    st.subheader("Payment Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Bank Details for Payment:**
        - Bank Name: ABC Real Estate Bank
        - Account Number: 1234567890123456
        - IFSC Code: ABCD0001234
        - Account Name: Real Estate Platform
        """)
        
        # Plan details
        user_data = get_user_data(st.session_state.user_email)
        if not user_data.empty:
            user = user_data.iloc[0]
            st.markdown(f"""
            **Your Plan Details:**
            - Plan Type: {user['plan_type']}
            - Start Date: {user['plan_start_date']}
            - End Date: {user['plan_end_date']}
            """)
    
    with col2:
        # Display QR code (placeholder)
        st.markdown("**Payment QR Code:**")
        st.markdown("""
        <div style="border: 2px dashed #ccc; padding: 20px; text-align: center;">
            <p>📱 QR Code for Payment</p>
            <p style="font-size: 48px;">⬜</p>
            <p><small>Scan with any UPI app</small></p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
