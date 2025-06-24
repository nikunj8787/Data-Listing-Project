# streamlit_app.py
import streamlit as st
from database_manager import initialize_database, get_user_data, check_user_exists, add_user, get_properties, log_audit_action, save_property, get_saved_properties
from auth_handler import handle_authentication, check_plan_validity, verify_otp, cleanup_otp_session
from property_search import show_property_search
from admin_functions import show_admin_panel
from operator_functions import show_operator_panel
from customer_functions import show_customer_profile, show_contact_history, show_payment_info

st.set_page_config(
    page_title="Real Estate Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': 'https://www.example.com/bug',
        'About': '# Real Estate Management Platform'
    }
)

# Custom CSS for sleek UI
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    .stApp {
        background: transparent;
    }
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
    .content-container {
        background: rgba(255,255,255,0.95);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
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
    /* Additional styling omitted for brevity, see previous code for full CSS */
</style>
""", unsafe_allow_html=True)

def main():
    initialize_database()
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
        st.session_state['user_email'] = None
        st.session_state['user_role'] = None
        st.session_state['current_otp'] = None

    # Header
    st.markdown("""
    <div class="platform-header">
        <h1>🏢 Real Estate Management Platform</h1>
        <p>Modern, professional property listing & management system</p>
    </div>
    """, unsafe_allow_html=True)

    # Content container
    st.markdown('<div class="content-container">', unsafe_allow_html=True)

    if not st.session_state['authenticated']:
        handle_authentication()
    else:
        if st.session_state['user_role'] == 'admin':
            show_admin_panel()
        elif st.session_state['user_role'] == 'operator':
            show_operator_panel()
        elif st.session_state['user_role'] == 'customer':
            show_customer_panel()

    st.markdown('</div>', unsafe_allow_html=True)

def show_customer_panel():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="margin: 0;">🏠 Property Discovery Center</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Find your perfect property with advanced filters and AI search</p>
    </div>
    """, unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 **Search**", "📞 **Contact History**", "👤 **Profile**", "💳 **Payments**"])
    with tab1:
        show_property_search()
    with tab2:
        show_contact_history()
    with tab3:
        show_customer_profile()
    with tab4:
        show_payment_info()

if __name__ == "__main__":
    main()
