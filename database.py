import psycopg2 
import psycopg2.extras
import streamlit as st 
import os
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO


load_dotenv()
# --- Database Configuration ---
# NOTE: Using your provided credentials
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.OperationalError:
        st.error("Database connection failed. Please check your credentials in database.py and ensure PostgreSQL is running.")
        return None

def create_users_table():
    """Creates the users table in the database if it does not already exist."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        first_name VARCHAR(100),
                        last_name VARCHAR(100),
                        address TEXT,
                        dob DATE,
                        gender VARCHAR(50),
                        phone_number VARCHAR(20),
                        is_premium BOOLEAN DEFAULT FALSE,
                        credits INTEGER DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP WITH TIME ZONE
                    );
                """)
                conn.commit()
        except Exception as e:
            st.error(f"DB Error (create_users_table): {e}")
        finally:
            conn.close()

def create_history_table():
    """
    Creates the image history table if it does not exist.
    This table stores the image bytes (BLOB) directly.
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS history (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        style VARCHAR(100) NOT NULL,
                        processed_image_bytes BYTEA NOT NULL,
                        timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        original_filename VARCHAR(255),
                        processed_mime_type VARCHAR(50)
                    );
                """)
                conn.commit()
        except Exception as e:
            st.error(f"DB Error (create_history_table): {e}")
        finally:
            conn.close()

def add_user(username, email, password_hash, first_name, last_name, address, dob, gender, phone_number):
    """Adds a new user to the users table."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (username, email, password_hash, first_name, last_name, address, dob, gender, phone_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (username, email, password_hash, first_name, last_name, address, dob, gender, phone_number)
                )
                conn.commit()
                return "User registered successfully!"
        except psycopg2.IntegrityError as e:
            conn.rollback()
            if 'users_username_key' in str(e):
                return "Error: Username already exists."
            elif 'users_email_key' in str(e):
                return "Error: Email already registered."
            else:
                return f"Database Error: {e}"
        except Exception as e:
            conn.rollback()
            return f"An unexpected error occurred: {e}"
        finally:
            conn.close()
    return "Database connection failed."

def get_user_by_email(email):
    """Retrieves a user's details from the database by their email."""
    conn = get_db_connection()
    user = None
    if conn:
        # Use DictCursor to get results as dictionaries for easy access in app.py
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE email = %s;", (email,))
            user = cur.fetchone()
        conn.close()
    return user
def get_user_data_by_id(user_id):
    """Retrieves a single user's data as a dictionary by their ID."""
    conn = get_db_connection()
    user = None
    if conn:
        try:
            # Use DictCursor to get results as dictionaries for easy access in app.py
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
                user = cur.fetchone()
                
                # Convert the DictRow result to a standard dict before returning
                if user:
                    return dict(user)
        except Exception as e:
            st.error(f"DB Error (get_user_data_by_id): {e}")
        finally:
            conn.close()
    return user
def update_last_login(email):
    """Updates the last_login timestamp for a user."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET last_login = %s WHERE email = %s;",
                    (datetime.now(), email)
                )
                conn.commit()
        except Exception as e:
            st.error(f"DB Error (update_last_login): {e}")
        finally:
            conn.close()

def update_user_to_premium(user_id):
    """Sets a user's status to premium."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET is_premium = TRUE WHERE id = %s;",
                    (user_id,)
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            st.error(f"DB Error (update_premium): {e}")
            return False
        finally:
            conn.close()
    return False

def add_credits_to_user(user_id, amount):
    """Adds a specified amount of credits to a user's current balance."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET credits = credits + %s WHERE id = %s;",
                    (amount, user_id)
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            st.error(f"DB Error (add_credits): {e}")
            return False
        finally:
            conn.close()
    return False

def deduct_credit_from_user(user_id, amount):
    """Deducts a specified amount of credits from a user's current balance."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Ensure user has enough credits before deducting
                cur.execute(
                    "UPDATE users SET credits = credits - %s WHERE id = %s AND credits >= %s;",
                    (amount, user_id, amount)
                )
                # Check if a row was updated (meaning deduction occurred)
                if cur.rowcount == 1:
                    conn.commit()
                    return True
                else:
                    conn.rollback()
                    st.warning("Deduction failed: User has insufficient credits.")
                    return False
        except Exception as e:
            conn.rollback()
            st.error(f"DB Error (deduct_credits): {e}")
            return False
        finally:
            conn.close()
    return False

def save_transformation_history(user_id, style, processed_image_bytes, original_filename, processed_mime_type):
    """Saves a record of the transformed image to the history table."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO history (user_id, style, processed_image_bytes, original_filename, processed_mime_type)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (user_id, style, processed_image_bytes, original_filename, processed_mime_type)
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            st.error(f"DB Error (save_history): {e}")
            return False
        finally:
            conn.close()
    return False


def get_transformation_history(user_id):
    """Retrieves all transformation records for a given user, ordered by most recent first."""
    conn = get_db_connection()
    if conn:
        try:
            # Use DictCursor for easier column access
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, style, processed_image_bytes, timestamp, original_filename, processed_mime_type
                    FROM history 
                    WHERE user_id = %s
                    ORDER BY timestamp DESC;
                    """,
                    (user_id,)
                )
                # Convert results to a list of dictionaries
                records = [dict(row) for row in cur.fetchall()]
                return records
        except Exception as e:
            st.error(f"DB Error (get_history): {e}")
            return []
        finally:
            conn.close()
    return []
