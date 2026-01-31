"""
Auth Controller - Handle authentication logic
"""
from typing import Dict, Any
from app.services.auth_service import register_user, login_user, get_user_by_id


def controller_register(username: str, email: str, password: str) -> Dict[str, Any]:
    """
    Controller for user registration
    """
    return register_user(username, email, password)


def controller_login(username: str, password: str) -> Dict[str, Any]:
    """
    Controller for user login
    """
    return login_user(username, password)


def controller_get_user(user_id: int) -> Dict[str, Any]:
    """
    Controller to get user info
    """
    user = get_user_by_id(user_id)
    
    if not user:
        return {
            "status": "error",
            "message": f"User {user_id} not found"
        }
    
    return {
        "status": "success",
        "user": user
    }
