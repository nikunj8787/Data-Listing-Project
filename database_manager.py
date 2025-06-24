import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# Database file name
DB_FILE = 'real_estate.db'

def initialize_database():
    """Initialize the database with all required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL,
        operator_id INTEGER,
        plan_start_date TEXT,
        plan_end_date TEXT,
        plan_type TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Properties table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS properties (
        property_id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_type TEXT NOT NULL,
        location TEXT NOT NULL,
        price REAL NOT NULL,
        bhk_type TEXT,
        area REAL,
        furnished_status TEXT,
        property_age TEXT,
        contact_number TEXT,
        operator_id INTEGER,
        features TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (operator_id) REFERENCES users(user_id)
    )
    ''')
    
    # Audit logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        action_type TEXT,
        details TEXT,
        property_id INTEGER,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Contact views table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contact_views (
        view_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        property_id INTEGER,
        viewed_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES users(user_id),
        FOREIGN KEY (property_id) REFERENCES properties(property_id)
    )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        insert_sample_data(cursor)
    
    conn.commit()
    conn.close()

def insert_sample_data(cursor):
    """Insert sample users and properties"""
    # Sample users
    users = [
        ('admin@realestateplatform.com', 'admin', None, '2024-01-01', '2025-12-31', 'Enterprise'),
        ('operator@realestateplatform.com', 'operator', None, '2024-01-01', '2025-12-31', 'Professional'),
        ('customer@realestateplatform.com', 'customer', 2, '2024-01-01', '2024-12-31', 'Premium')
    ]
    
    for user in users:
        cursor.execute('''
        INSERT INTO users (email, role, operator_id, plan_start_date, plan_end_date, plan_type)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', user)
    
    # Sample properties
    properties = [
        ('Residential Rent', 'CG Road, Ahmedabad', 25000, '2 BHK', 1200, 'Fully Furnished', '1-5 Years', '9876543210', 2, '{"parking": true, "gym": true}'),
        ('Residential Sell', 'Satellite, Ahmedabad', 4500000, '3 BHK', 1800, 'Semi Furnished', 'Newly Built', '9876543211', 2, '{"parking": true, "swimming_pool": true}'),
        ('Commercial Rent', 'Vastrapur, Ahmedabad', 75000, 'Office', 2500, 'Fully Furnished', '1-5 Years', '9876543212', 2, '{"parking": true, "conference_room": true}'),
        ('Commercial Sell', 'SG Highway, Ahmedabad', 15000000, 'Shop', 1000, 'Unfurnished', '5+ Years', '9876543213', 2, '{"parking": true, "front_facing": true}'),
        ('Residential Rent', 'Bodakdev, Ahmedabad', 35000, '3 BHK', 1600, 'Fully Furnished', 'Newly Built', '9876543214', 2, '{"parking": true, "gym": true, "swimming_pool": true}')
    ]
    
    for prop in properties:
        cursor.execute('''
        INSERT INTO properties (property_type, location, price, bhk_type, area, furnished_status, property_age, contact_number, operator_id, features)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', prop)

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

def get_properties(filters=None):
    """Get properties with optional filters"""
    conn = sqlite3.connect(DB_FILE)
    
    if filters:
        # Build dynamic query based on filters
        query = "SELECT * FROM properties WHERE 1=1"
        params = []
        
        if filters.get('property_type') and filters['property_type'] != 'All Types':
            query += " AND property_type = ?"
            params.append(filters['property_type'])
        
        if filters.get('location'):
            query += " AND location LIKE ?"
            params.append(f"%{filters['location']}%")
        
        if filters.get('min_price') is not None and filters.get('max_price') is not None:
            query += " AND price BETWEEN ? AND ?"
            params.extend([filters['min_price'], filters['max_price']])
        
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query("SELECT * FROM properties", conn)
    
    conn.close()
    return df

def log_contact_view(customer_email, property_id):
    """Log when a customer views a contact"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get customer ID
    cursor.execute("SELECT user_id FROM users WHERE email = ?", (customer_email,))
    customer_id = cursor.fetchone()[0]
    
    # Insert contact view
    cursor.execute('''
    INSERT INTO contact_views (customer_id, property_id)
    VALUES (?, ?)
    ''', (customer_id, property_id))
    
    conn.commit()
    conn.close()

def add_user(email, role, plan_type="Basic", operator_id=None):
    """Add a new user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
    
    cursor.execute('''
    INSERT INTO users (email, role, operator_id, plan_start_date, plan_end_date, plan_type)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (email, role, operator_id, start_date, end_date, plan_type))
    
    conn.commit()
    conn.close()
