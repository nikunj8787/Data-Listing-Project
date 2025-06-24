def get_contact_history(customer_email):
    """Get contact view history for a customer"""
    conn = sqlite3.connect(DB_FILE)
    query = '''
    SELECT p.property_type, p.location, p.bhk_type, p.price, p.contact_number, cv.viewed_at
    FROM contact_views cv
    JOIN properties p ON cv.property_id = p.property_id
    JOIN users u ON cv.customer_id = u.user_id
    WHERE u.email = ?
    ORDER BY cv.viewed_at DESC
    '''
    df = pd.read_sql_query(query, conn, params=(customer_email,))
    conn.close()
    return df
