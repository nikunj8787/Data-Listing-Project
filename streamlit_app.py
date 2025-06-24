# Real Estate Data Listing & Management Platform
# Main Application File - streamlit_app.py

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
from auth_handler import handle_authentication, check_plan_validity
from property_search import show_property_search
from admin_functions import show_admin_panel
from operator_functions import show_operator_panel
from customer_functions import show_customer_profile, show_contact_history, show_payment_info

# Page configuration with professional settings
st.set_page_config(
    page_title="Real Estate Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': "https://www.example.com/bug",
        'About': "# Real Estate Platform\nProfessional property management solution"
    }
)

# Enhanced CSS for professional UI/UX
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Custom Header Styles */
    .platform-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
    }
    
    .platform-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .platform-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Content Container */
    .content-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Professional Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2980b9 0%, #1f618d 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: #2c3e50;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    .css-1d391kg .stMarkdown {
        color: white;
    }
    
    /* Success/Error Message Styling */
    .stSuccess {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        border: none;
    }
    
    .stError {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        border: none;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        border: none;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        border: none;
    }
    
    /* Input Field Styling */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.9);
        border: 2px solid #e3e8ef;
        border-radius: 10px;
        padding: 0.7rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    
    .stSelectbox > div > div > div {
        background: rgba(255,255,255,0.9);
        border: 2px solid #e3e8ef;
        border-radius: 10px;
    }
    
    /* Property Card Styling */
    .property-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .property-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    .property-card h4 {
        color: #2c3e50;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .property-card .price {
        color: #27ae60;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .property-card .property-details {
        color: #7f8c8d;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .metric-card .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .metric-card .metric-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Upload Area Styling */
    .upload-area {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px dashed #3498db;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #2980b9;
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .platform-header h1 {
            font-size: 2rem;
        }
        
        .content-container {
            padding: 1rem;
            margin: 0.5rem;
        }
        
        .property-card {
            margin: 0.5rem 0;
            padding: 1rem;
        }
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
        st.session_state.verification_pending = False
    
    # Professional Header
    st.markdown("""
    <div class="platform-header">
        <h1>🏢 Real Estate Management Platform</h1>
        <p>Professional Property Management & Listing Solution</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content container
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    
    # Authentication check
    if not st.session_state.authenticated:
        handle_authentication()
    else:
        # Check if user needs verification (for customers)
        if st.session_state.user_role == 'customer' and not check_plan_validity(st.session_state.user_email):
            st.error("🚫 Your account is pending admin verification or your plan has expired. Please contact the administrator.")
            if st.button("🚪 Logout"):
                reset_session()
            st.stop()
        
        # Professional sidebar
        with st.sidebar:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); 
                        padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                <h3 style="color: white; margin: 0;">Welcome Back!</h3>
                <p style="color: white; opacity: 0.8; margin: 0.5rem 0 0 0;">{st.session_state.user_email}</p>
                <p style="color: white; opacity: 0.6; margin: 0;">{st.session_state.user_role.title()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Logout", key="sidebar_logout"):
                reset_session()
        
        # Display appropriate panel based on user role
        if st.session_state.user_role == "admin":
            show_admin_panel()
        elif st.session_state.user_role == "operator":
            show_operator_panel()
        elif st.session_state.user_role == "customer":
            show_customer_panel()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_customer_panel():
    """Enhanced customer panel with professional UI"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="margin: 0;">🏠 Property Discovery Center</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Find your perfect property with advanced search and AI assistance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs with enhanced styling
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 **Property Search**", "📞 **Contact History**", "👤 **My Profile**", "💳 **Payments**"])
    
    with tab1:
        show_property_search()
    
    with tab2:
        st.markdown("### 📞 Contact View History")
        show_contact_history()
    
    with tab3:
        st.markdown("### 👤 My Profile")
        show_customer_profile()
    
    with tab4:
        st.markdown("### 💳 Payment Information")
        show_payment_info()

def reset_session():
    """Reset session state for logout"""
    for key in ['authenticated', 'user_email', 'user_role', 'current_otp', 'verification_pending']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

if __name__ == "__main__":
    main()
