"""
Authentication Service - Handle user registration and login
"""
import hashlib
import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from app.models.database import get_db

def hash_password(password: str) -> str:
    """Hash password using PBKDF2-SHA256"""
    salt = os.urandom(32)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex() + pwd_hash.hex()

def verify_password(stored_hash: str, password: str) -> bool:
    """Verify password against hash"""
    try:
        salt = bytes.fromhex(stored_hash[:64])
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return pwd_hash.hex() == stored_hash[64:]
    except:
        return False

def register_user(username: str, email: str, password: str) -> Dict[str, Any]:
    """
    Register a new user
    Args:
        username: Username
        email: Email address
        password: Plain text password
    Returns: Dict with status and user info
    """
    try:
        # Validate inputs
        if not username or len(username) < 3:
            return {
                "status": "error",
                "message": "Username must be at least 3 characters"
            }
        
        if not email or "@" not in email:
            return {
                "status": "error",
                "message": "Invalid email address"
            }
        
        if not password or len(password) < 6:
            return {
                "status": "error",
                "message": "Password must be at least 6 characters"
            }
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            return {
                "status": "error",
                "message": "Username or email already exists"
            }
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, datetime.now()))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "user_id": user_id,
            "username": username,
            "email": email
        }
    
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return {
            "status": "error",
            "message": f"Registration failed: {str(e)}"
        }


def login_user(username: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user login
    Args:
        username: Username
        password: Plain text password
    Returns: Dict with status and user info
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Find user
        cursor.execute("""
            SELECT user_id, username, email, password_hash, role, created_at
            FROM users
            WHERE username = ?
        """, (username,))
        
        user = cursor.fetchone()
        if not user:
            return {
                "status": "error",
                "message": "Username or password incorrect"
            }
        
        user_id, username, email, password_hash, role, created_at = user
        
        # Verify password
        if not verify_password(password_hash, password):
            return {
                "status": "error",
                "message": "Username or password incorrect"
            }
        
        # Update last login
        cursor.execute("""
            UPDATE users SET last_login = ? WHERE user_id = ?
        """, (datetime.now(), user_id))
        conn.commit()
        
        # Generate token (simple JWT-like)
        import json
        import base64
        token_payload = json.dumps({"user_id": user_id, "username": username, "role": role})
        access_token = base64.b64encode(token_payload.encode()).decode()
        
        return {
            "status": "success",
            "message": "Login successful",
            "access_token": access_token,
            "user_id": user_id,
            "username": username,
            "email": email,
            "role": role,
            "created_at": created_at
        }
    
    except Exception as e:
        print(f"❌ Login error: {e}")
        return {
            "status": "error",
            "message": f"Login failed: {str(e)}"
        }


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, username, email, created_at, last_login
            FROM users
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        user_id, username, email, created_at, last_login = row
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "created_at": created_at,
            "last_login": last_login
        }
    
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return None
