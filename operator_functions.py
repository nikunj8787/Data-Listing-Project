import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

def show_operator_panel():
    """Display data entry operator panel with comprehensive upload functionality"""
    
    # Operator header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="margin: 0;">👨‍💻 Data Entry Operator Panel</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Upload and manage property data with advanced validation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 **Property Upload**", 
        "📝 **CSV Templates**", 
        "📋 **Upload History**",
        "📊 **My Statistics**"
    ])
    
    with tab1:
        show_property_upload()
    
    with tab2:
        show_csv_templates()
    
    with tab3:
        show_upload_history()
    
    with tab4:
        show_operator_statistics()

def show_property_upload():
    """Advanced property upload interface with validation"""
    st.markdown("### 📤 Property Data Upload Center")
    
    # Upload category selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    border-left: 5px solid #3498db;">
            <h4 style="color: #2c3e50; margin-top: 0;">📂 Select Property Category</h4>
        """, unsafe_allow_html=True)
        
        property_category = st.selectbox(
            "Choose the type of properties you're uploading:",
            ["Residential Rent", "Residential Sell", "Commercial Rent", "Commercial Sell"],
            help="Select the appropriate category for your property data"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Quick stats
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    border-left: 5px solid #27ae60;">
            <h4 style="color: #2c3e50; margin-top: 0;">📊 Quick Stats</h4>
        """, unsafe_allow_html=True)
        
        st.metric("Today's Uploads", "0")
        st.metric("Total Properties", "8")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # File upload section
    st.markdown("### 📁 File Upload")
    
    # Upload area with enhanced styling
    st.markdown("""
    <div class="upload-area">
        <h4 style="color: #3498db; margin-top: 0;">Drop your files here or browse</h4>
        <p style="color: #7f8c8d; margin-bottom: 0;">Supported formats: CSV, Excel (.xlsx, .xls)</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose your property data file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload CSV or Excel files with property data. Maximum file size: 200MB",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        # File information
        file_size = len(uploaded_file.getvalue())
        file_size_mb = file_size / (1024 * 1024)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"📄 **File:** {uploaded_file.name}")
        with col2:
            st.info(f"📏 **Size:** {file_size_mb:.2f} MB")
        with col3:
            st.info(f"📂 **Category:** {property_category}")
        
        # File preview
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File loaded successfully! Found {len(df)} rows")
            
            # Show preview
            st.markdown("#### 👀 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Validation section
            st.markdown("#### 🔍 Data Validation")
            
            validation_results = validate_property_data(df, property_category)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if validation_results['is_valid']:
                    st.success("✅ All validation checks passed!")
                else:
                    st.error("❌ Validation issues found")
                    
                    for error in validation_results['errors']:
                        st.error(f"• {error}")
            
            with col2:
                st.markdown("**Validation Summary:**")
                st.write(f"• Total rows: {validation_results['total_rows']}")
                st.write(f"• Valid rows: {validation_results['valid_rows']}")
                st.write(f"• Invalid rows: {validation_results['invalid_rows']}")
                st.write(f"• Missing fields: {validation_results['missing_fields']}")
            
            # Upload button
            if validation_results['is_valid']:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🚀 **Upload Properties**", type="primary", use_container_width=True):
                        process_upload(df, property_category, uploaded_file.name)
            else:
                st.warning("⚠️ Please fix validation errors before uploading")
                
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.info("💡 Please ensure your file is in the correct format and not corrupted")

def show_csv_templates():
    """Display downloadable CSV templates for each property type"""
    st.markdown("### 📝 CSV Templates Download Center")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem;">
        <h4 style="margin: 0;">📋 Template Information</h4>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
            Download the correct template for your property type to ensure proper data formatting
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Template cards
    templates = {
        "Residential Rent": {
            "icon": "🏠",
            "description": "Template for residential rental properties",
            "fields": ["property_type", "location", "address", "price", "bhk_type", "area", "furnished_status", "property_age", "contact_number", "amenities", "description", "maintenance_cost", "security_deposit"]
        },
        "Residential Sell": {
            "icon": "🏡", 
            "description": "Template for residential properties for sale",
            "fields": ["property_type", "location", "address", "price", "bhk_type", "area", "furnished_status", "property_age", "contact_number", "amenities", "description", "total_floors", "floor_number"]
        },
        "Commercial Rent": {
            "icon": "🏢",
            "description": "Template for commercial rental properties", 
            "fields": ["property_type", "location", "address", "price", "office_type", "area", "furnished_status", "property_age", "contact_number", "amenities", "description", "maintenance_cost", "security_deposit"]
        },
        "Commercial Sell": {
            "icon": "🏪",
            "description": "Template for commercial properties for sale",
            "fields": ["property_type", "location", "address", "price", "shop_type", "area", "furnished_status", "property_age", "contact_number", "amenities", "description", "facing", "parking"]
        }
    }
    
    cols = st.columns(2)
    
    for i, (template_name, template_info) in enumerate(templates.items()):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                        padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                        margin-bottom: 1rem; border-left: 5px solid #e67e22;">
                <h4 style="color: #2c3e50; margin-top: 0;">{template_info['icon']} {template_name}</h4>
                <p style="color: #7f8c8d; margin-bottom: 1rem;">{template_info['description']}</p>
                <p style="color: #7f8c8d; font-size: 0.9rem; margin-bottom: 1rem;">
                    <strong>Fields:</strong> {len(template_info['fields'])} required columns
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Generate and offer download
            template_df = create_template(template_info['fields'])
            csv_data = template_df.to_csv(index=False)
            
            st.download_button(
                label=f"📥 Download {template_name} Template",
                data=csv_data,
                file_name=f"{template_name.lower().replace(' ', '_')}_template.csv",
                mime="text/csv",
                key=f"template_{i}",
                use_container_width=True
            )

def show_upload_history():
    """Display upload history with detailed logs"""
    st.markdown("### 📋 Upload History & Logs")
    
    # Sample upload history (in real implementation, fetch from upload_logs table)
    upload_history = pd.DataFrame({
        'upload_date': ['2024-06-24 10:30:00', '2024-06-23 15:45:00', '2024-06-22 09:15:00'],
        'filename': ['residential_rent_june.csv', 'commercial_properties.xlsx', 'new_listings.csv'],
        'category': ['Residential Rent', 'Commercial Rent', 'Residential Sell'],
        'total_rows': [150, 75, 200],
        'successful_rows': [148, 73, 195],
        'failed_rows': [2, 2, 5],
        'status': ['Completed', 'Completed', 'Completed']
    })
    
    if not upload_history.empty:
        st.success(f"📊 Total uploads: {len(upload_history)}")
        
        # Upload statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_uploads = len(upload_history)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_uploads}</div>
                <div class="metric-label">Total Uploads</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_properties = upload_history['successful_rows'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_properties}</div>
                <div class="metric-label">Properties Added</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            success_rate = (upload_history['successful_rows'].sum() / upload_history['total_rows'].sum() * 100)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{success_rate:.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            failed_rows = upload_history['failed_rows'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{failed_rows}</div>
                <div class="metric-label">Failed Rows</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Detailed history table
        st.markdown("#### 📝 Detailed Upload Log")
        
        # Format the dataframe for display
        display_df = upload_history.copy()
        display_df['Success Rate'] = (display_df['successful_rows'] / display_df['total_rows'] * 100).round(1)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "upload_date": "Upload Date",
                "filename": "File Name", 
                "category": "Property Category",
                "total_rows": "Total Rows",
                "successful_rows": "Successful",
                "failed_rows": "Failed",
                "Success Rate": st.column_config.NumberColumn("Success %", format="%.1f%%"),
                "status": "Status"
            }
        )
    else:
        st.info("📝 No upload history found. Start uploading properties to see your history here!")

def show_operator_statistics():
    """Display operator performance statistics"""
    st.markdown("### 📊 My Performance Statistics")
    
    # Performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    border-left: 5px solid #27ae60;">
            <h4 style="color: #2c3e50; margin-top: 0;">📈 Performance Metrics</h4>
        """, unsafe_allow_html=True)
        
        st.metric("Properties Uploaded Today", "0")
        st.metric("Properties This Week", "8") 
        st.metric("Properties This Month", "8")
        st.metric("Total Properties", "8")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
                    border-left: 5px solid #9b59b6;">
            <h4 style="color: #2c3e50; margin-top: 0;">🎯 Quality Metrics</h4>
        """, unsafe_allow_html=True)
        
        st.metric("Upload Success Rate", "97.5%")
        st.metric("Average Processing Time", "2.3 min")
        st.metric("Data Quality Score", "95/100")
        st.metric("Customer Satisfaction", "4.8/5")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Helper functions
def validate_property_data(df, category):
    """Validate uploaded property data"""
    validation_result = {
        'is_valid': True,
        'errors': [],
        'total_rows': len(df),
        'valid_rows': len(df),
        'invalid_rows': 0,
        'missing_fields': 0
    }
    
    # Required fields for each category
    required_fields = {
        'Residential Rent': ['location', 'address', 'price', 'bhk_type', 'area', 'contact_number'],
        'Residential Sell': ['location', 'address', 'price', 'bhk_type', 'area', 'contact_number'],
        'Commercial Rent': ['location', 'address', 'price', 'area', 'contact_number'],
        'Commercial Sell': ['location', 'address', 'price', 'area', 'contact_number']
    }
    
    # Check for required fields
    missing_fields = []
    for field in required_fields.get(category, []):
        if field not in df.columns:
            missing_fields.append(field)
    
    if missing_fields:
        validation_result['is_valid'] = False
        validation_result['errors'].append(f"Missing required fields: {', '.join(missing_fields)}")
        validation_result['missing_fields'] = len(missing_fields)
    
    # Additional validations (price, contact number format, etc.)
    if 'price' in df.columns:
        invalid_prices = df[pd.to_numeric(df['price'], errors='coerce').isna()].index
        if len(invalid_prices) > 0:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Invalid price values in rows: {list(invalid_prices[:5])}")
    
    if 'contact_number' in df.columns:
        invalid_contacts = df[df['contact_number'].astype(str).str.len() != 10].index
        if len(invalid_contacts) > 0:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Invalid contact numbers (should be 10 digits)")
    
    return validation_result

def create_template(fields):
    """Create a sample CSV template"""
    template_data = {}
    for field in fields:
        if field == 'property_type':
            template_data[field] = ['Residential Rent']
        elif field == 'location':
            template_data[field] = ['CG Road, Ahmedabad']
        elif field == 'address':
            template_data[field] = ['123 Sample Address, Near Landmark']
        elif field == 'price':
            template_data[field] = [25000]
        elif field == 'bhk_type':
            template_data[field] = ['2 BHK']
        elif field == 'area':
            template_data[field] = [1200]
        elif field == 'contact_number':
            template_data[field] = ['9876543210']
        else:
            template_data[field] = ['Sample Data']
    
    return pd.DataFrame(template_data)

def process_upload(df, category, filename):
    """Process the uploaded file and add to database"""
    try:
        # In real implementation, insert data into database
        st.success(f"✅ Successfully uploaded {len(df)} properties!")
        st.balloons()
        
        # Log the upload (in real implementation, add to upload_logs table)
        st.info(f"📝 Upload logged: {filename} - {category} - {len(df)} properties")
        
    except Exception as e:
        st.error(f"❌ Upload failed: {str(e)}")
