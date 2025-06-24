import streamlit as st
import random
import string
from datetime import datetime
from database_manager import check_user_exists, get_user_data, log_audit_action

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    """Simulate sending OTP via email"""
    # In production, integrate with actual email service (SendGrid, AWS SES, etc.)
    st.info(f"📧 OTP sent to {email}")
    st.success(f"🔐 Development Mode - Your OTP: **{otp}**")

def check_plan_validity(email):
    """Check if user's plan is active and verified"""
    user_data = get_user_data(email)
    if user_data.empty:
        return False
    
    user = user_data.iloc[0]
    
    # Check if user is verified
    if not user['is_verified']:
        return False
    
    # Check plan expiry
    if user['plan_end_date']:
        try:
            end_date = datetime.strptime(user['plan_end_date'], '%Y-%m-%d')
            if datetime.now() > end_date:
                return False
        except:
            return True  # If date parsing fails, allow access
    
    return True

def handle_authentication():
    """Enhanced authentication interface with professional styling"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%); 
                color: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="margin: 0; text-align: center;">🔐 Secure Access Portal</h2>
        <p style="margin: 0.5rem 0 0 0; text-align: center; opacity: 0.9;">
            Choose your role and authenticate with OTP verification
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create professional login form
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 👤 Select Your Role")
        user_type = st.selectbox(
            "Login Type:",
            ["Customer Login", "Data Entry Operator", "Master Admin"],
            help="Select your user type to access the appropriate panel"
        )
        
        # Role mapping
        role_mapping = {
            "Customer Login": "customer",
            "Data Entry Operator": "operator", 
            "Master Admin": "admin"
        }
        selected_role = role_mapping[user_type]
        
        st.markdown("### 📧 Email Address")
        email = st.text_input(
            "Enter your registered email:",
            placeholder="your.email@example.com",
            help="Use test accounts for demo"
        )
        
        # OTP Generation with enhanced styling
        if st.button("📤 Send OTP", type="primary", use_container_width=True):
            if email:
                if validate_email_and_role(email, selected_role):
                    # Generate and send OTP
                    otp = generate_otp()
                    st.session_state.current_otp = otp
                    st.session_state.otp_email = email
                    st.session_state.otp_role = selected_role
                    
                    send_otp_email(email, otp)
                    log_audit_action(email, "OTP_REQUESTED", f"OTP requested for {selected_role} login")
                else:
                    st.error(f"❌ Invalid credentials or account not found for {selected_role}")
            else:
                st.warning("⚠️ Please enter your email address")
    
    with col2:
        st.markdown("### 🔒 OTP Verification")
        
        if 'current_otp' in st.session_state:
            st.success("✅ OTP sent successfully!")
            
            otp_input = st.text_input(
                "Enter 6-digit OTP:",
                type="password",
                max_chars=6,
                placeholder="000000",
                help="Check your email for the verification code"
            )
            
            if st.button("🚀 Verify & Login", type="primary", use_container_width=True):
                if otp_input:
                    if verify_otp(otp_input):
                        # Successful authentication
                        st.session_state.authenticated = True
                        st.session_state.user_email = st.session_state.otp_email
                        st.session_state.user_role = st.session_state.otp_role
                        
                        # Log successful login
                        log_audit_action(
                            st.session_state.user_email, 
                            "LOGIN_SUCCESS", 
                            f"Successful login as {st.session_state.user_role}"
                        )
                        
                        # Clear OTP data
                        cleanup_otp_session()
                        
                        st.success("🎉 Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid OTP. Please try again.")
                        log_audit_action(
                            st.session_state.get('otp_email', 'unknown'), 
                            "LOGIN_FAILED", 
                            "Invalid OTP entered"
                        )
                else:
                    st.warning("⚠️ Please enter the OTP")
        else:
            st.info("📬 Please request OTP first by entering your email")
    
    # Test accounts section
    display_test_accounts()

def validate_email_and_role(email, role):
    """Validate email exists and has correct role"""
    if not check_user_exists(email):
        return False
    
    user_data = get_user_data(email)
    if user_data.empty:
        return False
    
    user = user_data.iloc[0]
    return user['role'] == role

def verify_otp(input_otp):
    """Verify the entered OTP"""
    if 'current_otp' in st.session_state:
        return input_otp == st.session_state.current_otp
    return False

def cleanup_otp_session():
    """Clean up OTP-related session data"""
    otp_keys = ['current_otp', 'otp_email', 'otp_role']
    for key in otp_keys:
        if key in st.session_state:
            del st.session_state[key]

def display_test_accounts():
    """Display test account information"""
    with st.expander("🧪 **Test Accounts & Demo Information**", expanded=False):
        st.markdown("""
        ### Available Test Accounts
        
        **🔧 Master Admin:**
        - Email: `admin@realestateplatform.com`
        - Access: Complete system administration, user verification, analytics
        
        **👨‍💻 Data Entry Operator:**
        - Email: `operator@realestateplatform.com`
        - Access: Property upload, CSV processing, data management
        
        **👤 Customer (Verified):**
        - Email: `customer@realestateplatform.com`
        - Access: Property search, contact viewing, profile management
        
        **👤 Customer (Pending Verification):**
        - Email: `newcustomer@example.com`
        - Status: Awaiting admin verification
        
        ---
        
        ### 🚀 Features Available
        - ✅ Email OTP Authentication
        - ✅ Role-based Access Control  
        - ✅ AI-powered Property Search
        - ✅ CSV Upload with Validation
        - ✅ Contact Masking & Tracking
        - ✅ Comprehensive Admin Panel
        - ✅ Professional UI/UX Design
        
        ### 🔒 Security Features
        - Multi-factor authentication with OTP
        - Admin verification for customer accounts
        - Comprehensive audit logging
        - Session management and auto-logout
        - Plan expiry enforcement
        """)
