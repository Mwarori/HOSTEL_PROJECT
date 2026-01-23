"""
Helper utilities for API views - MongoDB compatible
"""
from .models import Hostel, Room, Booking, Issue, Notice, Payment, User
from bson import ObjectId
from datetime import datetime


def hostel_to_dict(hostel, include_images=True):
    """Convert hostel object to dictionary"""
    if not hostel:
        return None
    
    data = {
        "id": str(hostel.id),
        "name": hostel.name,
        "location": hostel.location,
        "description": hostel.description or "",
        "total_rooms": hostel.total_rooms,
        "available_rooms": hostel.get_available_rooms_count(),
        "price_per_month": hostel.price_per_month,
        "price_per_semester": hostel.price_per_semester,
        "amenities": hostel.amenities or "",
        "is_active": hostel.is_active,
        "created_at": hostel.created_at.isoformat() if hostel.created_at else None,
    }
    
    if include_images and hasattr(hostel, 'images') and hostel.images:
        data["images"] = [
            {
                "url": img.image_url,
                "caption": img.caption,
                "is_primary": img.is_primary,
                "order": img.order
            }
            for img in hostel.images
        ]
    
    if hasattr(hostel, 'owner') and hostel.owner:
        data["owner_id"] = str(hostel.owner.id)
        data["owner_name"] = hostel.owner.get_full_name()
        data["owner_email"] = hostel.owner.email
    
    return data


def room_to_dict(room):
    """Convert room object to dictionary"""
    if not room:
        return None
    
    return {
        "id": str(room.id),
        "room_number": room.room_number,
        "room_type": room.room_type,
        "capacity": room.capacity,
        "price_per_month": room.price_per_month,
        "is_occupied": room.is_occupied,
        "floor": room.floor,
        "amenities": room.amenities or "",
        "created_at": room.created_at.isoformat() if room.created_at else None,
    }


def booking_to_dict(booking):
    """Convert booking object to dictionary"""
    if not booking:
        return None
    
    data = {
        "id": str(booking.id),
        "status": booking.status,
        "room_number": booking.room_number,
        "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
        "allocation_date": booking.allocation_date.isoformat() if booking.allocation_date else None,
        "is_active": booking.is_active,
        "notes": booking.notes or "",
    }
    
    if hasattr(booking, 'user') and booking.user:
        data["user_id"] = str(booking.user.id)
        data["user_email"] = booking.user.email
        data["user_name"] = booking.user.get_full_name()
    
    if hasattr(booking, 'hostel') and booking.hostel:
        data["hostel_id"] = str(booking.hostel.id)
        data["hostel_name"] = booking.hostel.name
    
    return data


def issue_to_dict(issue):
    """Convert issue object to dictionary"""
    if not issue:
        return None
    
    return {
        "id": str(issue.id),
        "title": issue.title,
        "description": issue.description,
        "status": issue.status,
        "priority": issue.priority,
        "created_at": issue.created_at.isoformat() if issue.created_at else None,
        "resolved_at": issue.resolved_at.isoformat() if issue.resolved_at else None,
        "resolution_notes": issue.resolution_notes or "",
        "user_email": issue.user.email if issue.user else None,
        "hostel_name": issue.hostel.name if issue.hostel else None,
    }


def notice_to_dict(notice):
    """Convert notice object to dictionary"""
    if not notice:
        return None
    
    return {
        "id": str(notice.id),
        "title": notice.title,
        "message": notice.message,
        "priority": notice.priority,
        "is_active": notice.is_active,
        "created_at": notice.created_at.isoformat() if notice.created_at else None,
        "expires_at": notice.expires_at.isoformat() if notice.expires_at else None,
        "posted_by": notice.owner.get_full_name() if notice.owner else None,
    }


def payment_to_dict(payment):
    """Convert payment object to dictionary"""
    if not payment:
        return None
    
    return {
        "id": str(payment.id),
        "amount": payment.amount,
        "payment_method": payment.payment_method,
        "transaction_id": payment.transaction_id,
        "status": payment.status,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
        "updated_at": payment.updated_at.isoformat() if payment.updated_at else None,
    }


def validate_user_role(user, allowed_roles):
    """Check if user has one of the allowed roles"""
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    return user and user.role in allowed_roles


def get_hostel_by_id(hostel_id, owner=None):
    """Get hostel by ID, optionally checking owner"""
    try:
        if isinstance(hostel_id, str):
            hostel_id = ObjectId(hostel_id)
        
        query = {"id": hostel_id}
        if owner:
            query["owner"] = owner
        
        return Hostel.objects(**query).first()
    except:
        return None


def get_booking_by_id(booking_id, owner=None):
    """Get booking by ID"""
    try:
        if isinstance(booking_id, str):
            booking_id = ObjectId(booking_id)
        
        return Booking.objects(id=booking_id).first()
    except:
        return None


def get_user_by_email(email):
    """Get user by email"""
    try:
        return User.objects(email=email).first()
    except:
        return None
