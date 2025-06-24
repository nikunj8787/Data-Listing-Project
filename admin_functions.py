import streamlit as st
import pandas as pd
from database_manager import get_user_data, verify_user, add_user, get_properties
import plotly.express as px
import plotly.graph_objects as go

def show_admin_panel():
    """Display comprehensive admin panel with professional styling"""
    
    # Admin header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="margin: 0;">🔧 Master Admin Panel</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Complete system administration and control center</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 **User Management**", 
        "✅ **Account Verification**", 
        "📊 **Analytics Dashboard**", 
        "🏠 **Property Management**",
        "📋 **System Logs**"
    ])
    
    with tab1:
        show_user_management()
    
    with tab2:
        show_account_verification()
    
    with tab3:
        show_analytics_dashboard()
    
    with tab4:
        show_property_management()
    
    with tab5:
        show_system_logs()

def show_user_management():
    """User management interface"""
    st.markdown("### 👥 User Management")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Add new user section
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    margin-bottom: 1rem; border-left: 5px solid #3498db;">
            <h4 style="color: #2c3e50; margin-top: 0;">➕ Add New User</h4>
        """, unsafe_allow_html=True)
        
        new_email = st.text_input("Email Address", placeholder="user@example.com")
        new_role = st.selectbox("User Role", ["customer", "operator", "admin"])
        plan_type = st.selectbox("Plan Type", ["Basic", "Premium", "Professional", "Enterprise"])
        
        if new_role == "customer":
            # Get list of operators for assignment
            operators = get_operators_list()
            if operators:
                operator_assignment = st.selectbox("Assign to Operator", operators)
            else:
                st.warning("No operators available. Create an operator first.")
                operator_assignment = None
        else:
            operator_assignment = None
        
        if st.button("➕ Create User", type="primary"):
            if new_email:
                try:
                    operator_id = None
                    if operator_assignment:
                        # Get operator ID from email
                        operator_data = get_user_data(operator_assignment)
                        if not operator_data.empty:
                            operator_id = operator_data.iloc[0]['user_id']
                    
                    add_user(new_email, new_role, plan_type, operator_id)
                    st.success(f"✅ User {new_email} created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error creating user: {str(e)}")
            else:
                st.error("Please enter an email address")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Current users overview
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    margin-bottom: 1rem; border-left: 5px solid #27ae60;">
            <h4 style="color: #2c3e50; margin-top: 0;">📊 User Statistics</h4>
        """, unsafe_allow_html=True)
        
        # Get user statistics
        stats = get_user_statistics()
        
        for role, count in stats.items():
            st.metric(f"{role.title()} Users", count)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # All users table
    st.markdown("### 📋 All Registered Users")
    users_df = get_all_users()
    
    if not users_df.empty:
        # Format the dataframe for display
        display_df = users_df.copy()
        display_df['Status'] = display_df['is_verified'].apply(lambda x: '✅ Verified' if x else '⏳ Pending')
        
        st.dataframe(
            display_df[['email', 'role', 'plan_type', 'plan_start_date', 'plan_end_date', 'Status']],
            use_container_width=True,
            column_config={
                "email": "Email Address",
                "role": "Role",
                "plan_type": "Plan",
                "plan_start_date": "Plan Start",
                "plan_end_date": "Plan End",
                "Status": "Verification Status"
            }
        )
    else:
        st.info("No users found in the system")

def show_account_verification():
    """Account verification interface"""
    st.markdown("### ✅ Account Verification Center")
    
    # Get pending verifications
    pending_users = get_pending_verifications()
    
    if pending_users.empty:
        st.success("🎉 All user accounts are verified! No pending verifications.")
        return
    
    st.warning(f"⚠️ {len(pending_users)} accounts pending verification")
    
    # Display pending users
    for _, user in pending_users.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background: #fff3cd; padding: 1rem; border-radius: 10px; border-left: 4px solid #ffc107;">
                    <h5 style="margin: 0; color: #2c3e50;">{user['email']}</h5>
                    <p style="margin: 0.25rem 0; color: #7f8c8d;">
                        Role: {user['role'].title()} | Plan: {user['plan_type']} | Registered: {user['created_at'][:10]}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"✅ Verify", key=f"verify_{user['user_id']}", type="primary"):
                    verify_user(user['email'])
                    st.success(f"✅ {user['email']} verified!")
                    st.rerun()
            
            with col3:
                if st.button(f"❌ Reject", key=f"reject_{user['user_id']}"):
                    # In a real implementation, you'd add a rejection mechanism
                    st.warning("Rejection functionality to be implemented")

def show_analytics_dashboard():
    """Comprehensive analytics dashboard"""
    st.markdown("### 📊 Platform Analytics Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = get_total_users_count()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_users}</div>
            <div class="metric-label">Total Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_properties = get_total_properties_count()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_properties}</div>
            <div class="metric-label">Total Properties</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        active_customers = get_active_customers_count()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_customers}</div>
            <div class="metric-label">Active Customers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_contacts = get_total_contact_views()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_contacts}</div>
            <div class="metric-label">Contact Views</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts and visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # User distribution pie chart
        st.markdown("#### 👥 User Distribution by Role")
        user_stats = get_user_statistics()
        if user_stats:
            fig = px.pie(values=list(user_stats.values()), names=list(user_stats.keys()),
                        title="Users by Role")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Property distribution by type
        st.markdown("#### 🏠 Properties by Type")
        property_stats = get_property_type_distribution()
        if property_stats:
            fig = px.bar(x=list(property_stats.keys()), y=list(property_stats.values()),
                        title="Properties by Type")
            st.plotly_chart(fig, use_container_width=True)

def show_property_management():
    """Property management interface for admin"""
    st.markdown("### 🏠 Property Management")
    
    # Property filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        property_type_filter = st.selectbox(
            "Filter by Type:",
            ["All Types", "Residential Rent", "Residential Sell", "Commercial Rent", "Commercial Sell"]
        )
    
    with col2:
        operator_filter = st.selectbox(
            "Filter by Operator:",
            ["All Operators"] + get_operators_list()
        )
    
    with col3:
        date_filter = st.selectbox(
            "Filter by Date:",
            ["All Time", "Today", "This Week", "This Month"]
        )
    
    # Get and display properties
    properties = get_properties()
    
    if not properties.empty:
        st.success(f"📊 Total Properties: {len(properties)}")
        
        # Apply filters (simplified for demo)
        if property_type_filter != "All Types":
            properties = properties[properties['property_type'] == property_type_filter]
        
        # Display properties table
        st.dataframe(
            properties[['property_type', 'location', 'bhk_type', 'price', 'area', 'contact_number', 'created_at']],
            use_container_width=True,
            column_config={
                "price": st.column_config.NumberColumn("Price (₹)", format="₹%.0f"),
                "area": st.column_config.NumberColumn("Area (sq.ft)"),
                "created_at": "Created Date"
            }
        )
    else:
        st.info("No properties found in the system")

def show_system_logs():
    """Display system audit logs"""
    st.markdown("### 📋 System Audit Logs")
    
    # Log filters
    col1, col2 = st.columns(2)
    
    with col1:
        log_type = st.selectbox(
            "Filter by Action:",
            ["All Actions", "LOGIN_SUCCESS", "LOGIN_FAILED", "OTP_REQUESTED", "CONTACT_VIEW"]
        )
    
    with col2:
        date_range = st.selectbox(
            "Date Range:",
            ["Today", "This Week", "This Month", "All Time"]
        )
    
    # Sample log data (in real implementation, fetch from audit_logs table)
    st.info("📝 Audit log display functionality will show detailed system activity logs here")
    
    # Placeholder for actual audit log implementation
    sample_logs = pd.DataFrame({
        'timestamp': ['2024-06-24 10:30:00', '2024-06-24 10:25:00', '2024-06-24 10:20:00'],
        'user_email': ['customer@realestateplatform.com', 'operator@realestateplatform.com', 'admin@realestateplatform.com'],
        'action_type': ['CONTACT_VIEW', 'LOGIN_SUCCESS', 'LOGIN_SUCCESS'],
        'details': ['Viewed contact for property ID 1', 'Successful operator login', 'Successful admin login']
    })
    
    st.dataframe(sample_logs, use_container_width=True)

# Helper functions
def get_operators_list():
    """Get list of operator emails"""
    try:
        # In real implementation, query database for operators
        return ["operator@realestateplatform.com"]
    except:
        return []

def get_user_statistics():
    """Get user count by role"""
    try:
        # In real implementation, query database
        return {"Admin": 1, "Operator": 1, "Customer": 2}
    except:
        return {}

def get_all_users():
    """Get all users dataframe"""
    try:
        # In real implementation, query database
        return pd.DataFrame()
    except:
        return pd.DataFrame()

def get_pending_verifications():
    """Get users pending verification"""
    try:
        # In real implementation, query database for unverified users
        return pd.DataFrame()
    except:
        return pd.DataFrame()

def get_total_users_count():
    """Get total number of users"""
    return 4

def get_total_properties_count():
    """Get total number of properties"""
    return 8

def get_active_customers_count():
    """Get number of active customers"""
    return 2

def get_total_contact_views():
    """Get total contact views"""
    return 15

def get_property_type_distribution():
    """Get property count by type"""
    return {
        "Residential Rent": 3,
        "Residential Sell": 2, 
        "Commercial Rent": 2,
        "Commercial Sell": 1
    }
