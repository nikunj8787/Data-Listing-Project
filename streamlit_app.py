import streamlit as st
from database_manager import initialize_database, get_user_data, get_properties, log_audit_action
from auth_handler import handle_authentication, check_plan_validity
from property_search import show_property_search
from admin_functions import show_admin_panel
from operator_functions import show_operator_panel
from customer_functions import show_customer_profile, show_contact_history, show_payment_info

# Basic page config
st.set_page_config(
    page_title="Real Estate Platform",
    page_icon="🏢",
    layout="wide"
)

# Simplified CSS for clarity and visibility
st.markdown("""
<style>
    /* Reset and fix form styling for visibility */
    .stTextInput > div > div > input {
        background-color: #fff !important;
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
    .stSelectbox [data-baseweb="select"] {
        background-color: #fff !important;
        border: 2px solid #3498db !important;
        border-radius: 8px !important;
    }
    [data-baseweb="menu"] {
        background-color: #fff !important;
        border: 1px solid #3498db !important;
        border-radius: 8px !important;
    }
    [data-baseweb="option"] {
        background-color: #fff !important;
        color: #2c3e50 !important;
    }
    [data-baseweb="option"]:hover {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
    }
    /* Buttons */
    .stButton > button {
        background: #3498db !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: #2980b9 !important;
        transform: translateY(-1px) !important;
    }
    /* Container styles for login */
    .login-container {
        background: #fff !important;
        padding: 2rem !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important;
        border: 1px solid #e3e8ef !important;
        margin: 1rem 0 !important;
    }
    .section-title {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        border-bottom: 2px solid #3498db !important;
        padding-bottom: 0.5rem !important;
        color: #2c3e50 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
initialize_database()

# Main app logic
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'current_otp' not in st.session_state:
    st.session_state['current_otp'] = None

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #2c3e50, #3498db); padding: 2rem; border-radius: 15px; text-align: center; color: #fff;">
<h1 style="margin: 0;">🏢 Real Estate Management Platform</h1>
<p style="margin: 0.5rem 0 0 0;">Professional Property Listing & Management System</p>
</div>
""", unsafe_allow_html=True)

# Authentication flow
if not st.session_state['authenticated']:
    handle_authentication()
else:
    # Show logout button
    with st.sidebar:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2c3e50, #34495e); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h4 style="color: #fff; margin: 0;">Welcome, {st.session_state['user_email']}</h4>
            <p style="color: #ccc; margin: 0;">Role: {st.session_state['user_role'].title()}</p>
            <form method="post">
                <button type="submit" name="logout" style="background:#e74c3c; border:none; padding:0.5rem 1rem; border-radius:8px; color:#fff; cursor:pointer;">🚪 Logout</button>
            </form>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.get('logout'):
            for key in ['authenticated', 'user_email', 'user_role', 'current_otp']:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()

    # Show role-based panels
    if st.session_state['user_role'] == 'admin':
        show_admin_panel()
    elif st.session_state['user_role'] == 'operator':
        show_operator_panel()
    elif st.session_state['user_role'] == 'customer':
        show_customer_panel()

# --- End of main app ---

# --- Helper functions for login ---
def handle_authentication():
    """Login form with role selection and email input"""
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔐 Login to Your Account</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        # Role selection
        role_choice = st.selectbox("Select Role:", ["Customer Login", "Data Entry Operator", "Master Admin"], key="role_select")
        role_map = {
            "Customer Login": "customer",
            "Data Entry Operator": "operator",
            "Master Admin": "admin"
        }
        role = role_map[role_choice]
        # Email input
        email = st.text_input("Email:", placeholder="your.email@example.com", key="email_input")
        if st.button("📤 Send OTP", key="send_otp"):
            if email:
                if check_user_exists(email):
                    # Generate OTP
                    otp = ''.join(random.choices(string.digits, k=6))
                    st.session_state['current_otp'] = otp
                    st.session_state['otp_email'] = email
                    st.session_state['otp_role'] = role
                    # Send OTP (simulate)
                    st.success(f"OTP sent! (Development Mode): {otp}")
                    log_audit_action(email, "OTP_REQUESTED", f"OTP requested for {role}")
                else:
                    st.error("User not found.")
            else:
                st.warning("Please enter your email.")
    with col2:
        # OTP verification
        if 'current_otp' in st.session_state:
            st.markdown('<div style="margin-top:1rem;">', unsafe_allow_html=True)
            otp_input = st.text_input("Enter OTP:", placeholder="6-digit code", type="password", key="otp_input")
            if st.button("🚀 Verify & Login", key="verify_login"):
                if otp_input:
                    if otp_input == st.session_state['current_otp']:
                        # Successful login
                        st.session_state['authenticated'] = True
                        st.session_state['user_email'] = st.session_state['otp_email']
                        st.session_state['user_role'] = st.session_state['otp_role']
                        # Clear OTP
                        del st.session_state['current_otp']
                        del st.session_state['otp_email']
                        del st.session_state['otp_role']
                        st.success("Login successful!")
                        st.experimental_rerun()
                    else:
                        st.error("Invalid OTP.")
                else:
                    st.warning("Please enter the OTP.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Request OTP first.")

# --- End of helper functions ---
