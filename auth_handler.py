import streamlit as st
import random
import string
from database_manager import check_user_exists, get_user_data
from datetime import datetime

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    """Simulate sending OTP via email (for production, implement actual email sending)"""
    # In a real application, you would use an email service like SendGrid, AWS SES, etc.
    # For demo purposes, we'll just display the OTP
    st.info(f"📧 OTP sent to {email}")
    st.success(f"🔐 Your OTP: {otp} (Development Mode)")

def verify_user_plan(email):
    """Check if user's plan is still active"""
    user_data = get_user_data(email)
    if user_data.empty:
        return False
    
    user = user_data.iloc[0]
    end_date = datetime.strptime(user['plan_end_date'], '%Y-%m-%d')
    
    if datetime.now() > end_date:
        return False
    
    return True

def handle_authentication():
    """Handle the authentication process"""
    st.subheader("🔐 Login to Real Estate Platform")
    
    # Create two columns for better layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Select Your Role")
        user_type = st.selectbox(
            "Login as:",
            ["Customer Login", "Data Entry Operator", "Master Admin"],
            help="Select your user type to access the appropriate panel"
        )
        
        # Map user type to role
        role_mapping = {
            "Customer Login": "customer",
            "Data Entry Operator": "operator", 
            "Master Admin": "admin"
        }
        selected_role = role_mapping[user_type]
        
        st.markdown("### Enter Your Email")
        email = st.text_input(
            "Email Address:",
            placeholder="Enter your registered email",
            help="Use the test accounts: admin@realestateplatform.com, operator@realestateplatform.com, or customer@realestateplatform.com"
        )
        
        # OTP Generation
        if st.button("📧 Send OTP", type="primary"):
            if email:
                # Check if user exists and has the correct role
                if check_user_exists(email):
                    user_data = get_user_data(email)
                    if not user_data.empty and user_data.iloc[0]['role'] == selected_role:
                        # Check plan validity for customers
                        if selected_role == "customer" and not verify_user_plan(email):
                            st.error("❌ Your plan has expired. Please contact admin to renew.")
                        else:
                            # Generate and send OTP
                            otp = generate_otp()
                            st.session_state.current_otp = otp
                            st.session_state.otp_email = email
                            st.session_state.otp_role = selected_role
                            send_otp_email(email, otp)
                    else:
                        st.error(f"❌ No {selected_role} account found with this email")
                else:
                    st.error("❌ Email not found in the system")
            else:
                st.warning("⚠️ Please enter your email address")
    
    with col2:
        st.markdown("### Verify OTP")
        
        # Show OTP input only if OTP has been generated
        if 'current_otp' in st.session_state:
            st.success("✅ OTP has been sent to your email")
            
            otp_input = st.text_input(
                "Enter OTP:",
                type="password",
                max_chars=6,
                placeholder="Enter 6-digit OTP",
                help="Check your email for the OTP code"
            )
            
            if st.button("🚀 Verify & Login", type="primary"):
                if otp_input:
                    if otp_input == st.session_state.current_otp:
                        # Successful authentication
                        st.session_state.authenticated = True
                        st.session_state.user_email = st.session_state.otp_email
                        st.session_state.user_role = st.session_state.otp_role
                        
                        # Clear OTP data
                        del st.session_state.current_otp
                        del st.session_state.otp_email
                        del st.session_state.otp_role
                        
                        st.success(f"🎉 Welcome! Logging in as {st.session_state.user_role}")
                        st.rerun()
                    else:
                        st.error("❌ Invalid OTP. Please try again.")
                else:
                    st.warning("⚠️ Please enter the OTP")
        else:
            st.info("📬 Please request OTP first by entering your email and clicking 'Send OTP'")
    
    # Test accounts information
    with st.expander("🧪 Test Accounts", expanded=False):
        st.markdown("""
        **Available Test Accounts:**
        
        🔧 **Master Admin:**
        - Email: `admin@realestateplatform.com`
        - Access: Full system administration
        
        👨‍💻 **Data Entry Operator:**
        - Email: `operator@realestateplatform.com`
        - Access: Property upload and management
        
        👤 **Customer:**
        - Email: `customer@realestateplatform.com` 
        - Access: Property search and contact viewing
        
        **Note:** OTPs are displayed on screen for testing purposes.
        """)
