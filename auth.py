# auth.py (Clean, Argon2-Only Hashing)

import database
from passlib.context import CryptContext
import psycopg2.extras 

# --- Password Hashing Setup ---
# ONLY Argon2 is used. This avoids all Bcrypt initialization conflicts.
pwd_context = CryptContext(
    schemes=["argon2"], 
    deprecated="auto"
)

def verify_password(plain_password, hashed_password):
    """Verifies a plain password against a hashed one (Argon2 only)."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hashes a plain password using Argon2."""
    return pwd_context.hash(password)

# --- Authentication Functions (Uses Argon2) ---
def signup_user(username, email, password, first_name, last_name, address, dob, gender, phone_number):
    if not all([username, email, password, first_name, last_name, dob, gender]):
        return "Error: Please fill in all required fields."
    
    password_hash = get_password_hash(password)
    message = database.add_user(
        username, email, password_hash, first_name,
        last_name, address, dob, gender, phone_number
    )
    return message

def login_user(email, password):
    """Logs in an existing user."""
    if not email or not password:
        return {"error": "Email and password are required."}

    user = database.get_user_by_email(email)
    
    # This now only attempts verification against the Argon2 scheme
    if user and verify_password(password, user['password_hash']):
        database.update_last_login(email)
        return dict(user)
    
    return {"error": "Invalid email or password."}