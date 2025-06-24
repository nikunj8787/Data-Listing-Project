import streamlit as st
from database_manager import get_user_data

def show_customer_profile():
    """Display customer profile information"""
    st.subheader("Your Profile")
    
    user_data = get_user_data(st.session_state.user_email)
    
    if not user_data.empty:
        user = user_data.iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Account Information")
            st.write(f"**Email:** {user['email']}")
            st.write(f"**Role:** {user['role'].title()}")
            st.write(f"**Member Since:** {user['created_at']}")
        
        with col2:
            st.markdown("### Subscription Details")
            st.write(f"**Plan:** {user['plan_type']}")
            st.write(f"**Start Date:** {user['plan_start_date']}")
            st.write(f"**End Date:** {user['plan_end_date']}")
