from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
import re

def roles_required(*roles):
    """Decorator to restrict access based on user roles."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            print(f"Current User: {current_user}")  # Debugging log

            if current_user['role'] not in roles:
                print(f"Access denied for role: {current_user['role']}")  # Debugging log
                return jsonify({"msg": "Access denied!"}), 403

            print(f"Access granted for role: {current_user['role']}")  # Debugging log
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def is_strong_password(password):
    """Check if the password meets the strength requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."

    return True, "Password is strong."
