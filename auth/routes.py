print("Routes module loaded")  # Debugging log

from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity, 
    get_jwt
)
from auth.models import User, db, TokenBlocklist, ResetToken
from auth.utils import roles_required, is_strong_password
from auth import auth_bp
import uuid
from flask_mail import Mail, Message
from datetime import timedelta, datetime

# In-memory store for revoked tokens (for simplicity)
revoked_tokens = set()
mail = Mail()

@auth_bp.route('/register', methods=['POST'])
def register():

    print("Register endpoint hit")  # Debugging log

    data = request.get_json()

    print(f"Received data: {data}")  # Log received data

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not username or not email or not password:
        return jsonify({"msg": "Username, email, and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 400
    
        # Check password strength
    is_valid, message = is_strong_password(password)
    if not is_valid:
        return jsonify({"msg": message}), 400

    new_user = User(username=username, email=email, role=role)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid credentials"}), 401

    identity = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_access_token}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # Get the token's JTI
    # Save the revoked token to the database
    revoked_token = TokenBlocklist(jti=jti)
    db.session.add(revoked_token)
    db.session.commit()

    return jsonify({"msg": "Access token revoked"}), 200


@auth_bp.route('/admin/users', methods=['GET'])
@jwt_required()
@roles_required('admin', 'manager')
def get_all_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@auth_bp.route('/manager/tasks', methods=['GET'])
@jwt_required()
@roles_required('admin', 'manager')
def get_manager_tasks():
    return jsonify({"msg": "Welcome, Manager or Admin!"})


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        # Get the current user ID from the JWT token
        current_user_data = get_jwt_identity()
        user_id = current_user_data['user_id']

        # Query the User model for user details
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404


        # Prepare the user's profile data
        profile_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.strftime('%Y-%m-%d'),
        }

        # Return the profile data as JSON
        return jsonify({"msg": "Profile loaded successfully", "user": profile_data}), 200

    except Exception as e:
        return jsonify({"msg": f"Error fetching profile: {str(e)}"}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def request_password_reset():
    """Request a password reset email."""
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User with that email does not exist"}), 404

    # Generate a unique token (UUID)
    token = str(uuid.uuid4())

    # Store the token in the database
    reset_token = ResetToken(token=token, user_id=user.id)
    db.session.add(reset_token)
    db.session.commit()

    # Create the reset URL (point to the frontend)
    reset_url = f"http://127.0.0.1:5173/reset-password/{token}"  # Frontend route

    # Send the reset email
    msg = Message(
        'Password Reset Request',
        recipients=[user.email]
    )
    msg.body = f"Hi {user.username},\nClick the link below to reset your password:\n{reset_url}"

    mail.send(msg)

    return jsonify({"msg": "Password reset email sent"}), 200


@auth_bp.route('/validate-reset-password/<token>', methods=['GET'])
def validate_reset_token(token):
    """Validate the password reset token."""
    reset_token = ResetToken.query.filter_by(token=token, used=False).first()

    if not reset_token:
        return jsonify({"msg": "Invalid or expired token"}), 400

    return jsonify({"msg": "Token is valid"}), 200

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset the user's password using the provided token."""
    reset_token = ResetToken.query.filter_by(token=token, used=False).first()

    if not reset_token:
        return jsonify({"msg": "Invalid or expired token"}), 400

    user = User.query.get(reset_token.user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    new_password = data.get('password')

    if not new_password:
        return jsonify({"msg": "Password is required"}), 400

    is_valid, message = is_strong_password(new_password)
    if not is_valid:
        return jsonify({"msg": message}), 400

    try:
        user.set_password(new_password)
        reset_token.used = True  # Mark the token as used
        db.session.commit()
        return jsonify({"msg": "Password updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error updating password: {str(e)}"}), 500


@auth_bp.route('/admin/cleanup-tokens', methods=['DELETE'])
@jwt_required()
@roles_required('admin')
def cleanup_tokens():
    """Remove tokens older than 30 days."""
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    ResetToken.query.filter(ResetToken.created_at < cutoff_date).delete()
    db.session.commit()
    return jsonify({"msg": "Old tokens cleaned up"}), 200
