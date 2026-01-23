"""
Authentication utilities for MongoDB-based user management
"""
from django.contrib.auth.hashers import make_password, check_password
from .models import User
from mongoengine import NotUniqueError
from bson import ObjectId


def create_user(email, password, name, role='student', username=None):
    """Create a new user"""
    if not username:
        username = email
    
    # Check if user exists
    if User.objects(email=email):
        raise ValueError("Email already registered")
    
    if User.objects(username=username):
        raise ValueError("Username already taken")
    
    # Create user with hashed password
    user = User(
        username=username,
        email=email,
        password=make_password(password),
        first_name=name,
        role=role
    )
    user.save()
    return user


def authenticate_user(email, password):
    """Authenticate user by email and password"""
    try:
        user = User.objects(email=email).first()
        if user and check_password(password, user.password):
            return user
    except:
        pass
    return None


def user_to_dict(user):
    """Convert user object to dictionary"""
    if not user:
        return None
    
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "name": user.get_full_name(),
        "role": user.role,
        "phone_number": user.phone_number,
        "is_verified": user.is_verified,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }
