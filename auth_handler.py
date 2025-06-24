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
            return True
    
    return True

def handle_authentication():
    """Enhanced authentication interface with fixed visibility issues"""
    
    # Fixed CSS with proper contrast and visibility
    st.markdown("""
    <style>
    /* Reset and fix form styling */
    .stSelectbox > div > div > div {
        background-color: white !important;
        color: #2c3e50 !important;
        border: 2px solid #3498db !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div > div > div {
        color: #2c3e50 !important;
        background-color: white !important;
    }
    
    .stTextInput > div > div > input {
        background-color: white !important;
        color: #2c3e50 !important;
        border: 2px solid #3498db !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        font-size: 16px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2980b9 !important;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2) !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #7f8c8d !important;
        opacity: 0.7 !important;
    }
    
    /* Fix button styling */
    .stButton > button {
        background: #3498db !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        background: #2980b9 !important;
        transform: translateY(-1px) !important;
    }
    
    /* Fix selectbox dropdown */
    .stSelectbox [data-baseweb="select"] {
        background-color: white !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background-color: white !important;
        color: #2c3e50 !important;
        border: 2px solid #3498db !important;
    }
    
    /* Fix dropdown options */
    [data-baseweb="menu"] {
        background-color: white !important;
        border: 1px solid #3498db !important;
        border-radius: 8px !important;
    }
    
    [data-baseweb="option"] {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    
    [data-baseweb="option"]:hover {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
    }
    
    /* Fix label visibility */
    .stSelectbox > label, .stTextInput > label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Container styling */
    .login-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid #e3e8ef;
        margin: 1rem 0;
    }
    
    .form-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    
    .section-title {
        color: #2c3e50;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Clean header without problematic styling
    st.markdown("""
    <div style="background: #3498db; color: white; padding: 2rem; border-radius: 15px; 
                text-align: center; margin-bottom: 2rem;">
        <h2 style="margin: 0;">🔐 Login to Real Estate Platform</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
            Choose your role and authenticate with OTP verification
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create clean, functional login form
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">👤 Select Your Role</div>', unsafe_allow_html=True)
        
        # Role selection with forced white background
        user_type = st.selectbox(
            "Choose your login type:",
            ["Customer Login", "Data Entry Operator", "Master Admin"],
            help="Select your user type to access the appropriate panel",
            key="user_type_select"
        )
        
        # Role mapping
        role_mapping = {
            "Customer Login": "customer",
            "Data Entry Operator": "operator", 
            "Master Admin": "admin"
        }
        selected_role = role_mapping[user_type]
        
        st.markdown('<div class="section-title">📧 Email Address</div>', unsafe_allow_html=True)
        
        # Email input with fixed styling
        email = st.text_input(
            "Enter your registered email address:",
            placeholder="your.email@example.com",
            help="Use test accounts for demo purposes",
            key="email_input",
            label_visibility="collapsed"
        )
        
        # Display current values for debugging
        if user_type:
            st.write(f"**Selected Role:** {user_type}")
        if email:
            st.write(f"**Email Entered:** {email}")
        
        # OTP Generation button
        if st.button("📤 Send OTP", type="primary", use_container_width=True, key="send_otp_btn"):
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
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔒 OTP Verification</div>', unsafe_allow_html=True)
        
        if 'current_otp' in st.session_state:
            st.success("✅ OTP sent successfully!")
            
            # OTP input with fixed styling
            otp_input = st.text_input(
                "Enter the 6-digit OTP:",
                type="password",
                max_chars=6,
                placeholder="Enter OTP here",
                help="Check the OTP displayed above (Development Mode)",
                key="otp_input",
                label_visibility="visible"
            )
            
            # Display entered OTP for debugging
            if otp_input:
                st.write(f"**OTP Entered:** {otp_input}")
            
            if st.button("🚀 Verify & Login", type="primary", use_container_width=True, key="verify_btn"):
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
            st.info("📬 Please request OTP first by entering your email and clicking 'Send OTP'")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Test accounts section with better styling
    with st.expander("🧪 **Test Accounts & Demo Information**", expanded=False):
        st.markdown("""
        ### 🔑 Available Test Accounts
        
        **🔧 Master Admin:**
        - Email: `admin@realestateplatform.com`
        - Access: Complete system administration
        
        **👨‍💻 Data Entry Operator:**
        - Email: `operator@realestateplatform.com`
        - Access: Property upload and management
        
        **👤 Customer (Verified):**
        - Email: `customer@realestateplatform.com`
        - Access: Property search and contact viewing
        
        ---
        
        ### 📝 **How to Login:**
        1. Select your role from the dropdown
        2. Enter the test email address
        3. Click "Send OTP" 
        4. Copy the OTP shown on screen
        5. Paste it in the OTP field and click "Verify & Login"
        
        ### 🔒 **Security Features:**
        - Email-based OTP authentication
        - Role-based access control
        - Session management
        - Audit logging
        """)

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
