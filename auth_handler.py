# auth_handler.py
import streamlit as st
import random
import string
from datetime import datetime
from database_manager import check_user_exists, get_user_data, log_audit_action

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    st.info(f"📧 OTP sent to {email}")
    st.success(f"🔐 Development Mode - OTP: **{otp}**")

def check_plan_validity(email):
    user_df = get_user_data(email)
    if user_df.empty:
        return False
    user = user_df.iloc[0]
    if not user['is_verified']:
        return False
    if user['plan_end_date']:
        end_date = datetime.strptime(user['plan_end_date'], '%Y-%m-%d')
        if datetime.now() > end_date:
            return False
    return True

def handle_authentication():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%); 
                padding: 2rem; border-radius: 15px; text-align: center; color: white;">
        <h2>🔐 Secure Login</h2>
        <p>Select role and authenticate with OTP</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown("### Role Selection")
        user_type = st.selectbox("Login as:", ["Customer Login", "Data Entry Operator", "Master Admin"])
        role_map = {"Customer Login": "customer", "Data Entry Operator": "operator", "Master Admin": "admin"}
        role = role_map[user_type]
        email = st.text_input("Email:", placeholder="your.email@example.com")
        if st.button("📤 Send OTP"):
            if email:
                if check_user_exists(email):
                    user_df = get_user_data(email)
                    if not user_df.empty and user_df.iloc[0]['role'] == role:
                        if role == 'customer' and not check_plan_validity(email):
                            st.error("❌ Your plan expired or account pending verification.")
                        else:
                            otp = generate_otp()
                            st.session_state['current_otp'] = otp
                            st.session_state['otp_email'] = email
                            st.session_state['otp_role'] = role
                            send_otp_email(email, otp)
                            log_audit_action(email, "OTP_REQUESTED", f"OTP requested for {role}")
                    else:
                        st.error(f"❌ No {role} account with this email.")
                else:
                    st.error("❌ Email not registered.")
            else:
                st.warning("⚠️ Enter email to receive OTP.")
    with col2:
        st.markdown("### OTP Verification")
        if 'current_otp' in st.session_state:
            otp_input = st.text_input("Enter OTP:", type="password")
            if st.button("🚀 Verify & Login"):
                if otp_input:
                    if otp_input == st.session_state['current_otp']:
                        st.session_state['authenticated'] = True
                        st.session_state['user_email'] = st.session_state['otp_email']
                        st.session_state['user_role'] = st.session_state['otp_role']
                        log_audit_action(st.session_state['user_email'], "LOGIN_SUCCESS", "Successful login")
                        cleanup_otp_session()
                        st.success("🎉 Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid OTP.")
                else:
                    st.warning("⚠️ Enter OTP.")
        else:
            st.info("📬 Request OTP first.")
    # Test accounts info
    with st.expander("🧪 Test Accounts & Demo", expanded=False):
        st.markdown("""
        - **Admin:** admin@realestate.com
        - **Operator:** operator@realestate.com
        - **Customer:** customer@realestate.com
        """)
def verify_otp(input_otp):
    return input_otp == st.session_state.get('current_otp', '')

def cleanup_otp_session():
    for key in ['current_otp', 'otp_email', 'otp_role']:
        if key in st.session_state:
            del st.session_state[key]
