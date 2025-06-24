import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database_manager import get_user_data, get_contact_history

def show_customer_profile():
    """Display customer profile with professional styling and comprehensive information"""
    
    user_data = get_user_data(st.session_state.user_email)
    
    if user_data.empty:
        st.error("❌ Unable to load user profile data")
        return
    
    user = user_data.iloc[0]
    
    # Profile header with gradient background
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h3 style="margin: 0;">👤 Customer Profile</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Your account information and subscription details</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Profile information in professional cards
    col1, col2 = st.columns(2)
    
    with col1:
        # Account Information Card
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    margin-bottom: 1rem; border-left: 5px solid #3498db;">
            <h4 style="color: #2c3e50; margin-top: 0;">📧 Account Information</h4>
        """, unsafe_allow_html=True)
        
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Account Type:** {user['role'].title()}")
        st.write(f"**Member Since:** {user['created_at'][:10]}")
        st.write(f"**Verification Status:** {'✅ Verified' if user['is_verified'] else '⏳ Pending'}")
        
        # Calculate days since joining
        join_date = datetime.strptime(user['created_at'][:10], '%Y-%m-%d')
        days_since_joining = (datetime.now() - join_date).days
        st.write(f"**Days Active:** {days_since_joining} days")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Operator Assignment Card (if applicable)
        if user.get('operator_id'):
            st.markdown("""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                        padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                        margin-bottom: 1rem; border-left: 5px solid #f39c12;">
                <h4 style="color: #2c3e50; margin-top: 0;">👨‍💼 Assigned Operator</h4>
            """, unsafe_allow_html=True)
            
            st.write(f"**Operator ID:** {user['operator_id']}")
            st.write("**Status:** Active Assignment")
            st.write("**Properties Access:** Available from assigned operator only")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Subscription Details Card
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    margin-bottom: 1rem; border-left: 5px solid #27ae60;">
            <h4 style="color: #2c3e50; margin-top: 0;">💎 Subscription Plan</h4>
        """, unsafe_allow_html=True)
        
        st.write(f"**Plan Type:** {user['plan_type']}")
        st.write(f"**Start Date:** {user['plan_start_date']}")
        st.write(f"**End Date:** {user['plan_end_date']}")
        
        # Calculate remaining days
        if user['plan_end_date']:
            end_date = datetime.strptime(user['plan_end_date'], '%Y-%m-%d')
            remaining_days = (end_date - datetime.now()).days
            
            if remaining_days > 0:
                st.write(f"**Days Remaining:** {remaining_days} days")
                if remaining_days <= 7:
                    st.warning(f"⚠️ Plan expires in {remaining_days} days!")
            else:
                st.error("❌ Plan has expired")
        
        # Plan Status
        plan_status = "✅ Active" if user['is_verified'] and remaining_days > 0 else "❌ Inactive"
        st.write(f"**Status:** {plan_status}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Usage Statistics Card
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    margin-bottom: 1rem; border-left: 5px solid #9b59b6;">
            <h4 style="color: #2c3e50; margin-top: 0;">📊 Usage Statistics</h4>
        """, unsafe_allow_html=True)
        
        # Get contact view statistics
        contact_history = get_contact_history(st.session_state.user_email)
        total_contacts = len(contact_history)
        
        # Calculate today's contact views
        today = datetime.now().strftime('%Y-%m-%d')
        today_contacts = len(contact_history[contact_history['viewed_at'].str.startswith(today)])
        
        st.write(f"**Total Contact Views:** {total_contacts}")
        st.write(f"**Today's Views:** {today_contacts}")
        
        # Calculate saved properties (placeholder)
        st.write("**Saved Properties:** 0")  # This would be calculated from saved_properties table
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_contact_history():
    """Display customer's contact viewing history with enhanced visualization"""
    
    # Header with professional styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e67e22 0%, #d35400 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem;">
        <h3 style="margin: 0;">📞 Contact View History</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
            Track all the property contacts you've accessed
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get contact history data
    contact_history = get_contact_history(st.session_state.user_email)
    
    if contact_history.empty:
        st.info("📝 You haven't viewed any contact details yet. Start browsing properties to see your contact history here!")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Total Contacts</div>
        </div>
        """.format(len(contact_history)), unsafe_allow_html=True)
    
    with col2:
        # Today's contacts
        today = datetime.now().strftime('%Y-%m-%d')
        today_contacts = len(contact_history[contact_history['viewed_at'].str.startswith(today)])
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Today's Views</div>
        </div>
        """.format(today_contacts), unsafe_allow_html=True)
    
    with col3:
        # This week's contacts
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        week_contacts = len(contact_history[contact_history['viewed_at'] >= week_ago])
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">This Week</div>
        </div>
        """.format(week_contacts), unsafe_allow_html=True)
    
    with col4:
        # Unique properties
        unique_properties = contact_history['location'].nunique()
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Unique Properties</div>
        </div>
        """.format(unique_properties), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        # Date filter
        date_filter = st.selectbox(
            "Filter by Date:",
            ["All Time", "Today", "This Week", "This Month"]
        )
    
    with col2:
        # Property type filter
        property_types = ["All Types"] + list(contact_history['property_type'].unique())
        type_filter = st.selectbox(
            "Filter by Property Type:",
            property_types
        )
    
    # Apply filters
    filtered_history = contact_history.copy()
    
    if date_filter == "Today":
        today = datetime.now().strftime('%Y-%m-%d')
        filtered_history = filtered_history[filtered_history['viewed_at'].str.startswith(today)]
    elif date_filter == "This Week":
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        filtered_history = filtered_history[filtered_history['viewed_at'] >= week_ago]
    elif date_filter == "This Month":
        month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        filtered_history = filtered_history[filtered_history['viewed_at'] >= month_ago]
    
    if type_filter != "All Types":
        filtered_history = filtered_history[filtered_history['property_type'] == type_filter]
    
    # Display filtered results
    if filtered_history.empty:
        st.info("No contact views found for the selected filters.")
    else:
        st.success(f"Showing {len(filtered_history)} contact views")
        
        # Group by date for better organization
        filtered_history['date'] = pd.to_datetime(filtered_history['viewed_at']).dt.date
        
        for date, group in filtered_history.groupby('date'):
            st.markdown(f"### 📅 {date.strftime('%B %d, %Y')}")
            
            for _, contact in group.iterrows():
                # Create property contact card
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                            padding: 1rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
                            margin: 0.5rem 0; border-left: 4px solid #3498db;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h5 style="margin: 0; color: #2c3e50;">{contact['bhk_type']} in {contact['location']}</h5>
                            <p style="margin: 0.25rem 0; color: #7f8c8d; font-size: 0.9rem;">
                                {contact['property_type']} • ₹{contact['price']:,}
                            </p>
                            <p style="margin: 0; color: #27ae60; font-weight: 600;">
                                📞 Contact: {contact['contact_number']}
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <small style="color: #7f8c8d;">
                                {pd.to_datetime(contact['viewed_at']).strftime('%I:%M %p')}
                            </small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Export functionality
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📥 Export Contact History")
        st.write("Download your complete contact viewing history for your records.")
    
    with col2:
        if st.button("📊 Download CSV", type="primary"):
            csv_data = contact_history.to_csv(index=False)
            st.download_button(
                label="💾 Download History",
                data=csv_data,
                file_name=f"contact_history_{st.session_state.user_email}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

def show_payment_info():
    """Display payment information with professional styling and comprehensive details"""
    
    # Header with gradient background
    st.markdown("""
    <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem;">
        <h3 style="margin: 0;">💳 Payment Information</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
            Manage your subscription payments and view billing details
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user data for plan information
    user_data = get_user_data(st.session_state.user_email)
    
    if user_data.empty:
        st.error("❌ Unable to load payment information")
        return
    
    user = user_data.iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bank Details Card
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    margin-bottom: 1.5rem; border-left: 5px solid #3498db;">
            <h4 style="color: #2c3e50; margin-top: 0;">🏦 Bank Transfer Details</h4>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        **Bank Name:** ABC Real Estate Bank  
        **Account Number:** 1234567890123456  
        **IFSC Code:** ABCD0001234  
        **Account Name:** Real Estate Platform  
        **Branch:** Main Branch, Business District  
        """)
        
        st.info("💡 Use your email address as payment reference")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Current Plan Details
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    margin-bottom: 1.5rem; border-left: 5px solid #27ae60;">
            <h4 style="color: #2c3e50; margin-top: 0;">📋 Current Plan Details</h4>
        """, unsafe_allow_html=True)
        
        st.write(f"**Current Plan:** {user['plan_type']}")
        st.write(f"**Start Date:** {user['plan_start_date']}")
        st.write(f"**End Date:** {user['plan_end_date']}")
        
        # Calculate remaining days and show renewal info
        if user['plan_end_date']:
            end_date = datetime.strptime(user['plan_end_date'], '%Y-%m-%d')
            remaining_days = (end_date - datetime.now()).days
            
            if remaining_days > 0:
                st.write(f"**Days Remaining:** {remaining_days} days")
                if remaining_days <= 30:
                    st.warning(f"⚠️ Plan expires in {remaining_days} days. Consider renewal!")
            else:
                st.error("❌ Plan has expired. Please renew to continue access.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # QR Code and UPI Payment
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    margin-bottom: 1.5rem; border-left: 5px solid #9b59b6;">
            <h4 style="color: #2c3e50; margin-top: 0;">📱 UPI Payment</h4>
        """, unsafe_allow_html=True)
        
        # QR Code placeholder (in production, generate actual QR code)
        st.markdown("""
        <div style="text-align: center; padding: 2rem; border: 2px dashed #3498db; 
                    border-radius: 15px; background: #f8f9fa;">
            <div style="font-size: 80px; color: #3498db;">📱</div>
            <h4 style="color: #2c3e50; margin: 1rem 0;">UPI QR Code</h4>
            <p style="color: #7f8c8d; margin: 0;">
                <strong>UPI ID:</strong> realestate@upi<br>
                <strong>Merchant:</strong> Real Estate Platform
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("✅ Scan with any UPI app to pay instantly")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Plan Options
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    margin-bottom: 1.5rem; border-left: 5px solid #f39c12;">
            <h4 style="color: #2c3e50; margin-top: 0;">💎 Available Plans</h4>
        """, unsafe_allow_html=True)
        
        plans = {
            "Basic": {"price": "₹999", "duration": "3 months", "features": ["Property Search", "Basic Support"]},
            "Premium": {"price": "₹1,999", "duration": "6 months", "features": ["Property Search", "AI Search", "Priority Support"]},
            "Professional": {"price": "₹3,999", "duration": "12 months", "features": ["All Premium Features", "Advanced Analytics", "24/7 Support"]}
        }
        
        for plan_name, details in plans.items():
            status = "Current" if plan_name == user['plan_type'] else "Available"
            color = "#27ae60" if plan_name == user['plan_type'] else "#3498db"
            
            st.markdown(f"""
            <div style="border: 1px solid {color}; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: {color};">{plan_name}</strong>
                        <span style="color: #7f8c8d; font-size: 0.8rem;">({status})</span>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: bold; color: #2c3e50;">{details['price']}</div>
                        <div style="font-size: 0.8rem; color: #7f8c8d;">{details['duration']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Payment Instructions
    st.markdown("---")
    st.markdown("### 📝 Payment Instructions")
    
    instructions_col1, instructions_col2 = st.columns(2)
    
    with instructions_col1:
        st.markdown("""
        **For Bank Transfer:**
        1. Use the bank details provided above
        2. Include your email address in payment reference
        3. Send payment screenshot to admin
        4. Plan will be activated within 24 hours
        """)
    
    with instructions_col2:
        st.markdown("""
        **For UPI Payment:**
        1. Scan the QR code with any UPI app
        2. Enter the payment amount for your chosen plan
        3. Complete the payment process
        4. Screenshot the transaction for records
        """)
    
    # Contact Support
    st.markdown("---")
    st.info("💬 **Need Help?** Contact our support team at support@realestateplatform.com for payment assistance.")
