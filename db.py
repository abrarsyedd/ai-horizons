"""
Database module for AI Horizons.
Handles the MySQL connection pool and provides helper functions
for executing queries.
"""

import mysql.connector
from mysql.connector import pooling
import config

try:
    # Create a connection pool. This is more efficient than creating
    # a new connection for every single request.
    db_pool = pooling.MySQLConnectionPool(
        pool_name="ai_horizons_pool",
        pool_size=5,
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DB
    )
    print("✅ Successfully created MySQL connection pool.")

except mysql.connector.Error as err:
    print(f"❌ Error creating MySQL connection pool: {err}")
    db_pool = None

def get_db_connection():
    """Get a connection from the pool."""
    if db_pool is None:
        raise Exception("Database pool is not initialized. Check 'db.py' and 'config.py'.")
        
    try:
        return db_pool.get_connection()
    except mysql.connector.Error as err:
        print(f"❌ Error getting connection from pool: {err}")
        return None

def execute_query(query, args=(), fetchone=False, fetchall=False, commit=False):
    """
    A helper function to execute database queries.
    - query: The SQL query string.
    - args: A tuple of arguments for the query.
    - fetchone: Set to True to fetch one result.
    - fetchall: Set to True to fetch all results.
    - commit: Set to True for INSERT/UPDATE/DELETE queries.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            return None # Failed to get connection
            
        # Use a dictionary cursor to get results as Python dicts
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, args)
        
        if commit:
            conn.commit()
            return cursor.lastrowid # Return ID for INSERTs
            
        if fetchone:
            return cursor.fetchone()
            
        if fetchall:
            return cursor.fetchall()
            
        return None # Default return if no fetch/commit
        
    except mysql.connector.Error as err:
        print(f"❌ Database Query Error: {err}")
        print(f"   Query: {query}")
        print(f"   Args: {args}")
        if conn and commit:
            conn.rollback() # Rollback changes on error
        return None
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() # Return the connection to the pool
