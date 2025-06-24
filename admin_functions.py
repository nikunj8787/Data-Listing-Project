import streamlit as st
import pandas as pd
from database_manager import get_user_data, add_user
import plotly.express as px

def show_admin_panel():
    """Display admin panel with full system controls"""
    st.header("🔧 Master Admin Panel")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 User Management", "💰 Plans & Payments", "📊 Analytics", "📋 Audit Logs"])
    
    with tab1:
        show_user_management()
    
    with tab2:
        show_plan_management()
    
    with tab3:
        show_analytics()
    
    with tab4:
        show_audit_logs()

def show_user_management():
    """User management interface"""
    st.subheader("User Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Add New User")
        new_email = st.text_input("Email Address")
        new_role = st.selectbox("Role", ["customer", "operator", "admin"])
        plan_type = st.selectbox("Plan Type", ["Basic", "Premium", "Professional", "Enterprise"])
        
        if st.button("Add User"):
            if new_email:
                add_user(new_email, new_role, plan_type)
                st.success(f"User {new_email} added successfully!")
            else:
                st.error("Please enter email address")
    
    with col2:
        st.markdown("### Current Users")
        # Display existing users would go here
        st.info("User list functionality will be displayed here")

def show_plan_management():
    """Plan and payment management"""
    st.subheader("Plans & Payments")
    st.info("Payment management interface will be implemented here")

def show_analytics():
    """System analytics dashboard"""
    st.subheader("Platform Analytics")
    
    # Sample analytics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Properties", "1,234", "12%")
    
    with col2:
        st.metric("Active Users", "56", "8%")
    
    with col3:
        st.metric("Contact Views", "789", "15%")

def show_audit_logs():
    """System audit logs"""
    st.subheader("System Audit Logs")
    st.info("Audit log display will be implemented here")
