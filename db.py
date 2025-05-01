# db.py

import mysql.connector
from mysql.connector import Error

# Global connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',             
            password='password',       
            database='public_library_management_system'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL:", e)
        return None

# General function to fetch all data
def fetch_all(query, params=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Execute insert/update/delete
def execute_query(query, params=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()
    cursor.close()
    conn.close()
