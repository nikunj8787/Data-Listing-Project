import streamlit as st
import pandas as pd

def show_operator_panel():
    """Display data entry operator panel"""
    st.header("👨‍💻 Data Entry Operator Panel")
    
    tab1, tab2 = st.tabs(["📤 Upload Properties", "📋 Upload History"])
    
    with tab1:
        show_property_upload()
    
    with tab2:
        show_upload_history()

def show_property_upload():
    """Property upload interface"""
    st.subheader("Upload Property Data")
    
    property_category = st.selectbox(
        "Select Property Category",
        ["Residential Rent", "Residential Sell", "Commercial Rent", "Commercial Sell"]
    )
    
    uploaded_file = st.file_uploader(
        "Choose CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your property data file"
    )
    
    if uploaded_file:
        if st.button("Process Upload"):
            try:
                # Read the uploaded file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"Successfully processed {len(df)} properties!")
                st.dataframe(df.head())
                
                # Here you would insert the data into the database
                st.info("Properties will be made live instantly after upload")
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

def show_upload_history():
    """Upload history display"""
    st.subheader("Upload History")
    st.info("Upload history will be displayed here")
