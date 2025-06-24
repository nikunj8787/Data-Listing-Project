import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import json

# Database file name
DB_FILE = 'real_estate.db'

def initialize_database():
    """Initialize the database with all required tables and sample data"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Users table with verification status
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('admin', 'operator', 'customer')),
        operator_id INTEGER,
        plan_start_date TEXT,
        plan_end_date TEXT,
        plan_type TEXT DEFAULT 'Basic',
        is_verified BOOLEAN DEFAULT FALSE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (operator_id) REFERENCES users(user_id)
    )
    ''')
    
    # Enhanced properties table with all mandatory fields
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS properties (
        property_id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_type TEXT NOT NULL CHECK (property_type IN ('Residential Rent', 'Residential Sell', 'Commercial Rent', 'Commercial Sell')),
        location TEXT NOT NULL,
        address TEXT NOT NULL,
        price REAL NOT NULL,
        bhk_type TEXT NOT NULL,
        area REAL NOT NULL,
        furnished_status TEXT CHECK (furnished_status IN ('Fully Furnished', 'Semi Furnished', 'Unfurnished')),
        property_age TEXT CHECK (property_age IN ('Under Construction', 'Newly Built', '1-5 Years', '5+ Years')),
        contact_number TEXT NOT NULL,
        operator_id INTEGER NOT NULL,
        features TEXT,
        amenities TEXT,
        description TEXT,
        floor_number INTEGER,
        total_floors INTEGER,
        facing TEXT,
        parking BOOLEAN DEFAULT FALSE,
        lift_available BOOLEAN DEFAULT FALSE,
        power_backup BOOLEAN DEFAULT FALSE,
        water_supply TEXT,
        maintenance_cost REAL DEFAULT 0,
        security_deposit REAL DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (operator_id) REFERENCES users(user_id)
    )
    ''')
    
    # Enhanced audit logs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        action_type TEXT NOT NULL,
        details TEXT,
        property_id INTEGER,
        ip_address TEXT,
        user_agent TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (property_id) REFERENCES properties(property_id)
    )
    ''')
    
    # Contact views tracking
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contact_views (
        view_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        property_id INTEGER NOT NULL,
        viewed_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES users(user_id),
        FOREIGN KEY (property_id) REFERENCES properties(property_id)
    )
    ''')
    
    # Upload logs for tracking file uploads
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS upload_logs (
        upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
        operator_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        file_size INTEGER,
        property_category TEXT NOT NULL,
        total_rows INTEGER,
        successful_rows INTEGER,
        failed_rows INTEGER,
        error_details TEXT,
        upload_status TEXT DEFAULT 'Processing',
        batch_id TEXT,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (operator_id) REFERENCES users(user_id)
    )
    ''')
    
    # Saved properties for customers
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS saved_properties (
        save_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        property_id INTEGER NOT NULL,
        saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (customer_id) REFERENCES users(user_id),
        FOREIGN KEY (property_id) REFERENCES properties(property_id),
        UNIQUE(customer_id, property_id)
    )
    ''')
    
    # Payment tracking
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT,
        transaction_id TEXT,
        payment_status TEXT DEFAULT 'Pending',
        receipt_image TEXT,
        payment_date TEXT,
        plan_extended_to TEXT,
        recorded_by TEXT,
        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES users(user_id)
    )
    ''')
    
    # Notifications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        notification_type TEXT DEFAULT 'info',
        is_read BOOLEAN DEFAULT FALSE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        insert_sample_data(cursor)
    
    # Create indexes for better performance
    create_indexes(cursor)
    
    conn.commit()
    conn.close()

def create_indexes(cursor):
    """Create database indexes for better performance"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(location)",
        "CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price)",
        "CREATE INDEX IF NOT EXISTS idx_properties_type ON properties(property_type)",
        "CREATE INDEX IF NOT EXISTS idx_properties_bhk ON properties(bhk_type)",
        "CREATE INDEX IF NOT EXISTS idx_properties_operator ON properties(operator_id)",
        "CREATE INDEX IF NOT EXISTS idx_contact_views_customer ON contact_views(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_email)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)"
    ]
    
    for index in indexes:
        cursor.execute(index)

def insert_sample_data(cursor):
    """Insert comprehensive sample data"""
    # Sample users with verification status
    users = [
        ('admin@realestateplatform.com', 'admin', None, '2024-01-01', '2025-12-31', 'Enterprise', True),
        ('operator@realestateplatform.com', 'operator', None, '2024-01-01', '2025-12-31', 'Professional', True),
        ('customer@realestateplatform.com', 'customer', 2, '2024-01-01', '2024-12-31', 'Premium', True),
        ('newcustomer@example.com', 'customer', 2, '2024-06-01', '2024-12-01', 'Basic', False)
    ]
    
    for user in users:
        cursor.execute('''
        INSERT INTO users (email, role, operator_id, plan_start_date, plan_end_date, plan_type, is_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', user)
    
    # Comprehensive sample properties
    properties = [
        ('Residential Rent', 'CG Road', '123 CG Road, Near Ellis Bridge', 25000, '2 BHK', 1200, 'Fully Furnished', '1-5 Years', '9876543210', 2, 
         '{"balcony": 2, "bathrooms": 2}', 'Gym, Swimming Pool, Parking', 'Spacious 2BHK with modern amenities', 3, 12, 'East', True, True, True, '24/7', 2000, 50000),
        
        ('Residential Sell', 'Satellite', '456 Satellite Road, Near SG Mall', 4500000, '3 BHK', 1800, 'Semi Furnished', 'Newly Built', '9876543211', 2,
         '{"balcony": 3, "bathrooms": 3}', 'Gym, Swimming Pool, Kids Play Area', 'Premium 3BHK apartment', 8, 15, 'North', True, True, True, '24/7', 0, 0),
        
        ('Commercial Rent', 'Vastrapur', '789 Vastrapur Main Road', 75000, 'Office', 2500, 'Fully Furnished', '1-5 Years', '9876543212', 2,
         '{"conference_rooms": 2, "workstations": 50}', 'Reception, Parking, Cafeteria', 'Modern office space with all facilities', 4, 8, 'West', True, True, True, '24/7', 15000, 150000),
        
        ('Commercial Sell', 'SG Highway', '321 SG Highway, Prime Location', 15000000, 'Shop', 1000, 'Unfurnished', '5+ Years', '9876543213', 2,
         '{"display_area": 800, "storage": 200}', 'Prime Location, High Footfall', 'Commercial shop in premium location', 1, 1, 'Main Road', True, False, True, 'Municipal', 5000, 0),
        
        ('Residential Rent', 'Bodakdev', '654 Bodakdev Cross Roads', 35000, '3 BHK', 1600, 'Fully Furnished', 'Newly Built', '9876543214', 2,
         '{"balcony": 2, "bathrooms": 3, "study_room": 1}', 'Swimming Pool, Gym, Garden', 'Luxury 3BHK with premium amenities', 10, 20, 'South', True, True, True, '24/7', 3000, 70000),
        
        ('Residential Sell', 'Paldi', '987 Paldi Main Road', 3200000, '2 BHK', 1100, 'Semi Furnished', '1-5 Years', '9876543215', 2,
         '{"balcony": 1, "bathrooms": 2}', 'Parking, Security', 'Well-maintained 2BHK apartment', 5, 10, 'East', True, True, False, 'Borewell', 1500, 0),
        
        ('Commercial Rent', 'Navrangpura', '147 Navrangpura Circle', 45000, 'Office', 1500, 'Semi Furnished', 'Newly Built', '9876543216', 2,
         '{"cabins": 3, "workstations": 25}', 'Parking, Reception', 'Corporate office space', 2, 6, 'North', True, True, True, '24/7', 8000, 90000),
        
        ('Residential Rent', 'Maninagar', '258 Maninagar East', 18000, '1 BHK', 650, 'Unfurnished', '1-5 Years', '9876543217', 2,
         '{"balcony": 1, "bathrooms": 1}', 'Basic Amenities', 'Affordable 1BHK for singles', 2, 4, 'West', False, False, False, 'Municipal', 1000, 18000)
    ]
    
    for prop in properties:
        cursor.execute('''
        INSERT INTO properties (property_type, location, address, price, bhk_type, area, furnished_status, 
                               property_age, contact_number, operator_id, features, amenities, description,
                               floor_number, total_floors, facing, parking, lift_available, power_backup,
                               water_supply, maintenance_cost, security_deposit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', prop)

# Database helper functions
def get_user_data(email):
    """Get user data by email"""
    conn = sqlite3.connect(DB_FILE)
    query = "SELECT * FROM users WHERE email = ?"
    df = pd.read_sql_query(query, conn, params=(email,))
    conn.close()
    return df

def check_user_exists(email):
    """Check if user exists"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def verify_user(email):
    """Verify a user account"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_verified = TRUE WHERE email = ?", (email,))
    conn.commit()
    conn.close()

def get_properties(filters=None, customer_email=None):
    """Get properties with optional filters"""
    conn = sqlite3.connect(DB_FILE)
    
    query = "SELECT * FROM properties WHERE is_active = TRUE"
    params = []
    
    # If customer, only show properties from assigned operator
    if customer_email:
        query += " AND operator_id = (SELECT operator_id FROM users WHERE email = ? AND role = 'customer')"
        params.append(customer_email)
    
    # Apply filters
    if filters:
        if filters.get('property_type') and filters['property_type'] != 'All Types':
            query += " AND property_type = ?"
            params.append(filters['property_type'])
        
        if filters.get('location'):
            query += " AND (location LIKE ? OR address LIKE ?)"
            location_param = f"%{filters['location']}%"
            params.extend([location_param, location_param])
        
        if filters.get('min_price') is not None and filters.get('max_price') is not None:
            query += " AND price BETWEEN ? AND ?"
            params.extend([filters['min_price'], filters['max_price']])
        
        if filters.get('bhk_type') and filters['bhk_type'] != 'Any':
            query += " AND bhk_type = ?"
            params.append(filters['bhk_type'])
        
        if filters.get('furnished_status') and filters['furnished_status'] != 'Any':
            query += " AND furnished_status = ?"
            params.append(filters['furnished_status'])
    
    query += " ORDER BY created_at DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def log_contact_view(customer_email, property_id):
    """Log when a customer views a contact"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get customer ID
    cursor.execute("SELECT user_id FROM users WHERE email = ?", (customer_email,))
    result = cursor.fetchone()
    if result:
        customer_id = result[0]
        
        # Insert contact view
        cursor.execute('''
        INSERT INTO contact_views (customer_id, property_id)
        VALUES (?, ?)
        ''', (customer_id, property_id))
        
        conn.commit()
    
    conn.close()

def log_audit_action(user_email, action_type, details, property_id=None):
    """Log audit actions"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO audit_logs (user_email, action_type, details, property_id)
    VALUES (?, ?, ?, ?)
    ''', (user_email, action_type, details, property_id))
    
    conn.commit()
    conn.close()

def add_user(email, role, plan_type="Basic", operator_id=None):
    """Add a new user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=180 if role == 'customer' else 365)).strftime('%Y-%m-%d')
    is_verified = role in ['admin', 'operator']  # Auto-verify admin and operators
    
    cursor.execute('''
    INSERT INTO users (email, role, operator_id, plan_start_date, plan_end_date, plan_type, is_verified)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (email, role, operator_id, start_date, end_date, plan_type, is_verified))
    
    conn.commit()
    conn.close()

def save_property(customer_email, property_id, notes=""):
    """Save a property to customer's favorites"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get customer ID
    cursor.execute("SELECT user_id FROM users WHERE email = ?", (customer_email,))
    result = cursor.fetchone()
    if result:
        customer_id = result[0]
        
        try:
            cursor.execute('''
            INSERT INTO saved_properties (customer_id, property_id, notes)
            VALUES (?, ?, ?)
            ''', (customer_id, property_id, notes))
            conn.commit()
            return True
        except:
            return False  # Already saved or error
    
    conn.close()
    return False

def get_saved_properties(customer_email):
    """Get customer's saved properties"""
    conn = sqlite3.connect(DB_FILE)
    query = '''
    SELECT p.*, sp.saved_at, sp.notes
    FROM saved_properties sp
    JOIN properties p ON sp.property_id = p.property_id
    JOIN users u ON sp.customer_id = u.user_id
    WHERE u.email = ?
    ORDER BY sp.saved_at DESC
    '''
    df = pd.read_sql_query(query, conn, params=(customer_email,))
    conn.close()
    return df
