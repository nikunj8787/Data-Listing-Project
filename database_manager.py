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
         '{"balcony": 2, "bathrooms": 2}', 'Gym, Swimming Pool, Parking', 'Spacious 2BHK with modern amenities', 3, 12, 'East', True, True, True
