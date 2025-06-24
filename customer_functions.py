import streamlit as st
from database_manager import get_user_data, get_contact_history

def show_customer_profile():
    """Display customer profile information"""
    st.subheader("👤 Customer Profile")
    
    user_data = get_user_data(st.session_state.user_email)
    
    if not user_data.empty:
        user = user_data.iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Account Information")
            st.write(f"**Email:** {user['email']}")
            st.write(f"**Role:** {user['role'].title()}")
            st.write(f"**Member Since:** {user['created_at'][:10]}")
            st.write(f"**Verification:** {'✅ Verified' if user['is_verified'] else '⏳ Pending'}")
        
        with col2:
            st.markdown("### Subscription Details")
            st.write(f"**Plan:** {user['plan_type']}")
            st.write(f"**Start Date:** {user['plan_start_date']}")
            st.write(f"**End Date:** {user['plan_end_date']}")

def show_contact_history():
    """Display customer's contact viewing history"""
    contact_history = get_contact_history(st.session_state.user_email)
    
    if contact_history.empty:
        st.info("📝 You haven't viewed any contact details yet")
    else:
        st.success(f"📊 You have viewed {len(contact_history)} property contacts")
        st.dataframe(contact_history, use_container_width=True)

def show_payment_info():
    """Display payment information"""
    st.subheader("💳 Payment Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Bank Details:**")
        st.write("Bank: ABC Real Estate Bank")
        st.write("Account: 1234567890123456")
        st.write("IFSC: ABCD0001234")
    
    with col2:
        st.markdown("**QR Code Payment:**")
        st.info("📱 Scan QR code for UPI payment")
