# database_manager.py
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import json

DB_PATH = 'real_estate.db'

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create tables with comprehensive schema
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        role TEXT,
        operator_id INTEGER,
        plan_start_date TEXT,
        plan_end_date TEXT,
        plan_type TEXT,
        is_verified BOOLEAN DEFAULT FALSE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS properties (
        property_id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_type TEXT,
        location TEXT,
        address TEXT,
        price REAL,
        bhk_type TEXT,
        area REAL,
        furnished_status TEXT,
        property_age TEXT,
        contact_number TEXT,
        operator_id INTEGER,
        features TEXT,
        amenities TEXT,
        description TEXT,
        floor_number INTEGER,
        total_floors INTEGER,
        facing TEXT,
        parking BOOLEAN,
        lift_available BOOLEAN,
        power_backup BOOLEAN,
        water_supply TEXT,
        maintenance_cost REAL,
        security_deposit REAL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS contact_views (
        view_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        property_id INTEGER,
        viewed_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(customer_id) REFERENCES users(user_id),
        FOREIGN KEY(property_id) REFERENCES properties(property_id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        action_type TEXT,
        details TEXT,
        property_id INTEGER,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    # Insert sample data if empty
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        # Add admin, operator, customer
        now = datetime.now()
        c.execute('INSERT INTO users (email, role, plan_start_date, plan_end_date, plan_type, is_verified) VALUES (?, ?, ?, ?, ?, ?)',
                  ('admin@realestate.com', 'admin', now.strftime('%Y-%m-%d'), (now + timedelta(days=365)).strftime('%Y-%m-%d'), 'Enterprise', True))
        c.execute('INSERT INTO users (email, role, plan_start_date, plan_end_date, plan_type, is_verified) VALUES (?, ?, ?, ?, ?, ?)',
                  ('operator@realestate.com', 'operator', now.strftime('%Y-%m-%d'), (now + timedelta(days=365)).strftime('%Y-%m-%d'), 'Pro', True))
        c.execute('INSERT INTO users (email, role, operator_id, plan_start_date, plan_end_date, plan_type, is_verified) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  ('customer@realestate.com', 'customer', 2, now.strftime('%Y-%m-%d'), (now + timedelta(days=180)).strftime('%Y-%m-%d'), 'Premium', True))
    conn.commit()
    conn.close()

def check_user_exists(email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users WHERE email=?', (email,))
    exists = c.fetchone()[0] > 0
    conn.close()
    return exists

def get_user_data(email):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql('SELECT * FROM users WHERE email=?', conn, params=(email,))
    conn.close()
    return df

def get_properties(filters=None, customer_email=None):
    conn = sqlite3.connect(DB_PATH)
    query = 'SELECT * FROM properties WHERE is_active=1'
    params = []
    if customer_email:
        query += ' AND operator_id = (SELECT user_id FROM users WHERE email=? AND role="customer")'
        params.append(customer_email)
    if filters:
        if filters.get('property_type') and filters['property_type'] != 'All Types':
            query += ' AND property_type=?'
            params.append(filters['property_type'])
        if filters.get('location'):
            query += ' AND (location LIKE ? OR address LIKE ?)'
            loc = f"%{filters['location']}%"
            params.extend([loc, loc])
        if filters.get('min_price') is not None and filters.get('max_price') is not None:
            query += ' AND price BETWEEN ? AND ?'
            params.extend([filters['min_price'], filters['max_price']])
        if filters.get('bhk_type') and filters['bhk_type'] != 'Any':
            query += ' AND bhk_type=?'
            params.append(filters['bhk_type'])
        if filters.get('furnished_status') and filters['furnished_status'] != 'Any':
            query += ' AND furnished_status=?'
            params.append(filters['furnished_status'])
        if filters.get('property_age') and filters['property_age'] != 'Any':
            query += ' AND property_age=?'
            params.append(filters['property_age'])
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def log_audit_action(user_email, action_type, details, property_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO audit_logs (user_email, action_type, details, property_id) VALUES (?, ?, ?, ?)',
              (user_email, action_type, details, property_id))
    conn.commit()
    conn.close()

def save_property(user_email, property_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users WHERE email=?', (user_email,))
    user_id = c.fetchone()[0]
    try:
        c.execute('INSERT INTO saved_properties (customer_id, property_id) VALUES (?, ?)', (user_id, property_id))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_saved_properties(user_email):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql('''
        SELECT p.*, sp.saved_at, sp.notes
        FROM saved_properties sp
        JOIN properties p ON sp.property_id=p.property_id
        JOIN users u ON sp.customer_id=u.user_id
        WHERE u.email=?
        ORDER BY sp.saved_at DESC
    ''', conn, params=(user_email,))
    conn.close()
    return df
