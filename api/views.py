"""
Enhanced API Views for Hostel Management System with all features
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta, datetime
from .models import *
from .auth_utils import create_user, authenticate_user, user_to_dict
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


# ============= HELPER FUNCTIONS =============

def get_current_user(request):
    """Extract user from request with proper handling"""
    try:
        if hasattr(request, 'user') and request.user:
            # Try to get user_id from JWT token data
            user_id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None)
            if user_id and isinstance(user_id, str) and len(user_id) == 24:
                user = User.objects(id=ObjectId(user_id)).first()
                if user:
                    return user
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
    return None


def serialize_hostel(hostel):
    """Convert hostel to dict"""
    images = []
    if hasattr(hostel, 'images') and hostel.images:
        images = [
            {
                "image_url": img.image_url,
                "caption": img.caption,
                "is_primary": img.is_primary,
                "order": img.order
            }
            for img in hostel.images
        ]
    
    return {
        "id": str(hostel.id),
        "name": hostel.name,
        "location": hostel.location,
        "description": hostel.description,
        "total_rooms": hostel.total_rooms,
        "available_rooms": hostel.get_available_rooms_count(),
        "price_per_month": hostel.price_per_month,
        "price_per_semester": hostel.price_per_semester,
        "image": hostel.image,
        "images": images,
        "owner": {"id": str(hostel.owner.id), "email": hostel.owner.email, "name": hostel.owner.first_name},
        "amenities": hostel.amenities,
        "is_active": hostel.is_active,
        "created_at": hostel.created_at.isoformat() if hostel.created_at else None,
    }


def serialize_room(room):
    """Convert room to dict"""
    return {
        "id": str(room.id),
        "hostel_id": str(room.hostel.id),
        "room_number": room.room_number,
        "room_type": room.room_type,
        "capacity": room.capacity,
        "price_per_month": room.price_per_month,
        "is_occupied": room.is_occupied,
        "assigned_to": {"id": str(room.assigned_to.id), "email": room.assigned_to.email} if room.assigned_to else None,
        "floor": room.floor,
        "amenities": room.amenities,
    }


def serialize_booking(booking):
    """Convert booking to dict"""
    return {
        "id": str(booking.id),
        "user": {"id": str(booking.user.id), "email": booking.user.email, "name": booking.user.first_name},
        "hostel": {"id": str(booking.hostel.id), "name": booking.hostel.name, "location": booking.hostel.location},
        "room": {
            "id": str(booking.room.id),
            "room_number": booking.room.room_number,
            "floor": booking.room.floor,
            "amenities": booking.room.amenities,
            "price": booking.room.price_per_month
        } if booking.room else None,
        "room_number": booking.room.room_number if booking.room else booking.room_number,
        "status": booking.status,
        "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
        "allocation_date": booking.allocation_date.isoformat() if booking.allocation_date else None,
        "semester_start": booking.semester_start.isoformat() if booking.semester_start else None,
        "semester_end": booking.semester_end.isoformat() if booking.semester_end else None,
        "approved_by": {"id": str(booking.approved_by.id), "email": booking.approved_by.email, "name": booking.approved_by.first_name} if booking.approved_by else None,
        "notes": booking.notes,
        "rejection_reason": booking.rejection_reason,
    }


# ============= AUTHENTICATION VIEWS =============

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Register a new user (Student or Owner)"""
    try:
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")
        name = request.data.get("name", "").strip()
        role = request.data.get("role", "student").lower()

        # Validation
        if not all([email, password, name]):
            return Response(
                {"error": "Email, password, and name are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if role not in ['student', 'owner']:
            return Response(
                {"error": "Role must be 'student' or 'owner'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 6:
            return Response(
                {"error": "Password must be at least 6 characters"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user
        user = create_user(email, password, name, role)

        # Create JWT tokens
        refresh = RefreshToken()
        refresh['user_id'] = str(user.id)
        refresh['email'] = user.email
        refresh['role'] = user.role

        return Response({
            "message": "User registered successfully",
            "user": user_to_dict(user),
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response(
            {"error": "Registration failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Login user and return JWT token"""
    try:
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        if not email or not password:
            return Response(
                {"error": "Email and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate user
        user = authenticate_user(email, password)

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Create JWT tokens
        refresh = RefreshToken()
        refresh['user_id'] = str(user.id)
        refresh['email'] = user.email
        refresh['role'] = user.role

        return Response({
            "message": "Login successful",
            "user": user_to_dict(user),
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response(
            {"error": "Login failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user profile"""
    try:
        user = get_current_user(request)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(user_to_dict(user), status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= HOSTEL MANAGEMENT VIEWS =============

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_hostel(request):
    """Add a new hostel (Owner only) with support for multiple images"""
    try:
        user = get_current_user(request)
        if not user or user.role != 'owner':
            return Response(
                {"error": "Only owners can add hostels"},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data
        required = ["name", "location", "total_rooms", "price_per_month"]
        if not all(field in data for field in required):
            return Response(
                {"error": f"Required fields: {', '.join(required)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        hostel = Hostel(
            owner=user,
            name=data.get("name").strip(),
            location=data.get("location").strip(),
            description=data.get("description", ""),
            total_rooms=int(data.get("total_rooms")),
            available_rooms=int(data.get("total_rooms")),
            price_per_month=float(data.get("price_per_month")),
            price_per_semester=float(data.get("price_per_semester", 0)),
            amenities=data.get("amenities", ""),
        )
        
        # Handle image uploads
        import base64
        import os
        from datetime import datetime
        
        images_data = data.get("images", [])
        if isinstance(images_data, str):
            try:
                images_data = eval(images_data) if images_data.startswith('[') else []
            except:
                images_data = []
        
        for idx, img_data in enumerate(images_data):
            if not img_data or not img_data.startswith('data:'):
                continue
                
            try:
                # Parse base64 image data
                header, b64_data = img_data.split(',', 1)
                image_bytes = base64.b64decode(b64_data)
                
                # Determine file extension
                ext = 'png' if 'png' in header else 'jpg'
                filename = f"hostel_{int(datetime.now().timestamp())}_{idx}.{ext}"
                filepath = os.path.join('hostel_images', filename)
                full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', filepath)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Save image
                with open(full_path, 'wb') as f:
                    f.write(image_bytes)
                
                # Add to hostel images
                from api.models import HostelImageEmbedded
                image_obj = HostelImageEmbedded(
                    image_url=f"/media/{filepath}",
                    caption=f"Hostel Image {idx + 1}",
                    is_primary=(idx == 0),
                    order=idx
                )
                hostel.images.append(image_obj)
            except Exception as img_err:
                logger.error(f"Error saving image: {str(img_err)}")
                continue
        
        # Set primary image from first image if available
        if hostel.images:
            hostel.image = hostel.images[0].image_url
        
        hostel.save()

        return Response({
            "message": "Hostel added successfully",
            "hostel": serialize_hostel(hostel)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Add hostel error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def all_hostels(request):
    """Get all active hostels"""
    try:
        hostels = Hostel.objects(is_active=True)
        return Response({
            "hostels": [serialize_hostel(h) for h in hostels]
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_hostels(request):
    """Get hostels owned by current user"""
    try:
        user = get_current_user(request)
        if not user or user.role != 'owner':
            return Response(
                {"error": "Only owners can view their hostels"},
                status=status.HTTP_403_FORBIDDEN
            )

        hostels = Hostel.objects(owner=user)
        return Response({
            "hostels": [serialize_hostel(h) for h in hostels]
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def hostel_detail(request, hostel_id):
    """Get hostel details"""
    try:
        hostel = Hostel.objects(id=ObjectId(hostel_id)).first()
        if not hostel:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)
        
        rooms = Room.objects(hostel=hostel)
        return Response({
            "hostel": serialize_hostel(hostel),
            "rooms": [serialize_room(r) for r in rooms],
            "total_rooms": hostel.total_rooms,
            "available_rooms": hostel.get_available_rooms_count()
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_hostel(request, hostel_id):
    """Update hostel (Owner only)"""
    try:
        hostel = Hostel.objects(id=ObjectId(hostel_id)).first()
        if not hostel:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = get_current_user(request)
        if not user or hostel.owner.id != user.id:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update fields
        hostel.name = request.data.get("name", hostel.name)
        hostel.location = request.data.get("location", hostel.location)
        hostel.description = request.data.get("description", hostel.description)
        hostel.price_per_month = request.data.get("price_per_month", hostel.price_per_month)
        hostel.amenities = request.data.get("amenities", hostel.amenities)
        hostel.save()

        return Response({
            "message": "Hostel updated successfully",
            "hostel": serialize_hostel(hostel)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= ROOM MANAGEMENT VIEWS =============

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_room(request):
    """Add a room to a hostel (Owner only)"""
    try:
        user = get_current_user(request)
        if not user or user.role != 'owner':
            return Response(
                {"error": "Only owners can add rooms"},
                status=status.HTTP_403_FORBIDDEN
            )

        hostel = Hostel.objects(id=ObjectId(request.data.get("hostel_id"))).first()
        if not hostel or hostel.owner.id != user.id:
            return Response(
                {"error": "Hostel not found or unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        room = Room(
            hostel=hostel,
            room_number=request.data.get("room_number").strip(),
            room_type=request.data.get("room_type", "DOUBLE"),
            capacity=int(request.data.get("capacity", 2)),
            price_per_month=float(request.data.get("price_per_month")),
            floor=int(request.data.get("floor", 1)),
            amenities=request.data.get("amenities", ""),
        )
        room.save()

        return Response({
            "message": "Room added successfully",
            "room": serialize_room(room)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Add room error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_hostel_rooms(request, hostel_id):
    """Get all rooms in a hostel"""
    try:
        hostel = Hostel.objects(id=ObjectId(hostel_id)).first()
        if not hostel:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)
        
        rooms = Room.objects(hostel=hostel)
        return Response({
            "rooms": [serialize_room(r) for r in rooms],
            "total": len(list(rooms)),
            "occupied": len(list(Room.objects(hostel=hostel, is_occupied=True)))
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_room(request, room_id):
    """Update room details (Owner only)"""
    try:
        room = Room.objects(id=ObjectId(room_id)).first()
        if not room:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = get_current_user(request)
        if not user or room.hostel.owner.id != user.id:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        room.price_per_month = request.data.get("price_per_month", room.price_per_month)
        room.amenities = request.data.get("amenities", room.amenities)
        room.save()

        return Response({
            "message": "Room updated successfully",
            "room": serialize_room(room)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= BOOKING MANAGEMENT VIEWS =============

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book_hostel(request):
    """Book a hostel (Student only)"""
    try:
        from datetime import datetime as dt
        
        user = get_current_user(request)
        if not user or user.role != 'student':
            return Response(
                {"error": "Only students can book hostels"},
                status=status.HTTP_403_FORBIDDEN
            )

        hostel = Hostel.objects(id=ObjectId(request.data.get("hostel_id"))).first()
        if not hostel:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if already booked
        existing = Booking.objects(user=user, hostel=hostel, status__in=['PENDING', 'ALLOCATED', 'FINAL_ALLOCATED']).first()
        if existing:
            return Response(
                {"error": "You already have a booking for this hostel"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse dates - handle both string and datetime formats
        semester_start = request.data.get("semester_start")
        semester_end = request.data.get("semester_end")
        
        if isinstance(semester_start, str):
            semester_start = dt.fromisoformat(semester_start.replace('Z', '+00:00'))
        if isinstance(semester_end, str):
            semester_end = dt.fromisoformat(semester_end.replace('Z', '+00:00'))

        booking = Booking(
            user=user,
            hostel=hostel,
            status='PENDING',
            semester_start=semester_start,
            semester_end=semester_end,
            notes=request.data.get("notes", "")
        )
        booking.save()

        return Response({
            "message": "Booking created successfully",
            "booking": serialize_booking(booking)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Book hostel error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    """Get bookings for current student"""
    try:
        user = get_current_user(request)
        bookings = Booking.objects(user=user).order_by('-booking_date')
        
        return Response({
            "bookings": [serialize_booking(b) for b in bookings]
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def owner_bookings(request, hostel_id):
    """Get bookings for a hostel (Owner only)"""
    try:
        hostel = Hostel.objects(id=ObjectId(hostel_id)).first()
        if not hostel:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = get_current_user(request)
        if not user or hostel.owner.id != user.id:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        bookings = Booking.objects(hostel=hostel).order_by('-booking_date')
        return Response({
            "bookings": [serialize_booking(b) for b in bookings],
            "total": len(list(bookings)),
            "pending": len(list(Booking.objects(hostel=hostel, status='PENDING'))),
            "allocated": len(list(Booking.objects(hostel=hostel, status='ALLOCATED')))
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_booking(request, booking_id):
    """Approve a booking and assign room (Owner only)"""
    try:
        booking = Booking.objects(id=ObjectId(booking_id)).first()
        if not booking:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = get_current_user(request)
        if not user or booking.hostel.owner.id != user.id:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        room_id = request.data.get("room_id")
        room = Room.objects(id=ObjectId(room_id), hostel=booking.hostel).first() if room_id else None

        booking.status = 'FINAL_ALLOCATED'
        booking.room = room
        booking.approved_by = user
        booking.approval_date = datetime.utcnow()
        booking.save()

        # Update room if assigned
        if room:
            room.is_occupied = True
            room.assigned_to = booking.user
            room.save()

        # ✅ AUTO-CANCEL all other pending bookings for this student
        other_bookings = Booking.objects(
            user=booking.user, 
            status='PENDING'
        )
        cancelled_count = 0
        for other_booking in other_bookings:
            if str(other_booking.id) != str(booking_id):
                other_booking.status = 'CANCELLED'
                other_booking.rejection_reason = 'Auto-cancelled: Another booking was approved'
                other_booking.save()
                cancelled_count += 1
        
        logger.info(f"Approved booking {booking_id}, auto-cancelled {cancelled_count} other pending bookings for student {booking.user.email}")

        return Response({
            "message": "Booking approved successfully",
            "booking": serialize_booking(booking),
            "auto_cancelled": cancelled_count
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Approve booking error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_booking(request, booking_id):
    """Reject a booking (Owner only)"""
    try:
        booking = Booking.objects(id=ObjectId(booking_id)).first()
        if not booking:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = get_current_user(request)
        if not user or booking.hostel.owner.id != user.id:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        booking.status = 'CANCELLED'
        booking.rejection_reason = request.data.get("reason", "")
        booking.save()

        return Response({
            "message": "Booking rejected successfully",
            "booking": serialize_booking(booking)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= ISSUE/COMPLAINT VIEWS =============

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def report_issue(request):
    """Report a maintenance issue (Student only)"""
    try:
        user = get_current_user(request)
        if not user or user.role != 'student':
            return Response(
                {"error": "Only students can report issues"},
                status=status.HTTP_403_FORBIDDEN
            )

        hostel = Hostel.objects(id=ObjectId(request.data.get("hostel_id"))).first()
        if not hostel:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)

        issue = Issue(
            user=user,
            hostel=hostel,
            title=request.data.get("title").strip(),
            description=request.data.get("description").strip(),
            priority=request.data.get("priority", "MEDIUM"),
        )
        issue.save()

        return Response({
            "message": "Issue reported successfully",
            "issue": {
                "id": str(issue.id),
                "title": issue.title,
                "status": issue.status,
                "priority": issue.priority,
                "created_at": issue.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Report issue error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_issues(request):
    """Get issues reported by current student"""
    try:
        user = get_current_user(request)
        if not user or user.role != 'student':
            return Response(
                {"error": "Only students can access this"},
                status=status.HTTP_403_FORBIDDEN
            )

        issues = Issue.objects(user=user).order_by('-created_at')
        return Response({
            "issues": [{
                "id": str(i.id),
                "title": i.title,
                "description": i.description,
                "hostel": i.hostel.name if i.hostel else "Unknown",
                "status": i.status,
                "priority": i.priority,
                "created_at": i.created_at.isoformat(),
                "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None,
                "resolution_notes": i.resolution_notes if hasattr(i, 'resolution_notes') else ""
            } for i in issues]
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"My issues error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def owner_issues(request, hostel_id):
    """Get issues for a hostel (Owner only)"""
    try:
        hostel = Hostel.objects(id=ObjectId(hostel_id)).first()
        if not hostel:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = get_current_user(request)
        if not user or hostel.owner.id != user.id:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        issues = Issue.objects(hostel=hostel).order_by('-created_at')
        return Response({
            "issues": [{
                "id": str(i.id),
                "title": i.title,
                "description": i.description,
                "user": i.user.email,
                "status": i.status,
                "priority": i.priority,
                "created_at": i.created_at.isoformat()
            } for i in issues]
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def resolve_issue(request, issue_id):
    """Resolve an issue (Owner only)"""
    try:
        issue = Issue.objects(id=ObjectId(issue_id)).first()
        if not issue:
            return Response({"error": "Issue not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = get_current_user(request)
        if not user or issue.hostel.owner.id != user.id:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        issue.status = 'RESOLVED'
        issue.resolution_notes = request.data.get("notes", "")
        issue.resolved_at = datetime.utcnow()
        issue.save()

        return Response({
            "message": "Issue resolved successfully",
            "issue": {
                "id": str(issue.id),
                "status": issue.status,
                "resolved_at": issue.resolved_at.isoformat()
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= NOTICE VIEWS =============

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_notice(request):
    """Send notice to students (Owner only)"""
    try:
        user = get_current_user(request)
        if not user or user.role != 'owner':
            return Response(
                {"error": "Only owners can send notices"},
                status=status.HTTP_403_FORBIDDEN
            )

        hostel = Hostel.objects(id=ObjectId(request.data.get("hostel_id"))).first()
        if not hostel or hostel.owner.id != user.id:
            return Response(
                {"error": "Hostel not found or unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        notice = Notice(
            hostel=hostel,
            owner=user,
            title=request.data.get("title").strip(),
            message=request.data.get("message").strip(),
            priority=request.data.get("priority", "NORMAL"),
        )
        notice.save()

        return Response({
            "message": "Notice sent successfully",
            "notice": {
                "id": str(notice.id),
                "title": notice.title,
                "priority": notice.priority,
                "created_at": notice.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Send notice error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_notices(request, hostel_id):
    """Get notices for a hostel"""
    try:
        hostel = Hostel.objects(id=ObjectId(hostel_id)).first()
        if not hostel:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)
        
        notices = Notice.objects(hostel=hostel, is_active=True).order_by('-created_at')
        return Response({
            "notices": [{
                "id": str(n.id),
                "title": n.title,
                "message": n.message,
                "priority": n.priority,
                "created_at": n.created_at.isoformat()
            } for n in notices]
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= PAYMENT VIEWS =============

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def record_payment(request):
    """Record a payment (Owner only)"""
    try:
        user = get_current_user(request)
        if not user or user.role != 'owner':
            return Response(
                {"error": "Only owners can record payments"},
                status=status.HTTP_403_FORBIDDEN
            )

        booking = Booking.objects(id=ObjectId(request.data.get("booking_id"))).first()
        if not booking or booking.hostel.owner.id != user.id:
            return Response(
                {"error": "Booking not found or unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        payment = Payment(
            booking=booking,
            amount=float(request.data.get("amount")),
            payment_method=request.data.get("payment_method", "MPESA"),
            transaction_id=request.data.get("transaction_id").strip(),
            status='SUCCESS'
        )
        payment.save()

        return Response({
            "message": "Payment recorded successfully",
            "payment": {
                "id": str(payment.id),
                "amount": payment.amount,
                "status": payment.status,
                "created_at": payment.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Record payment error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_payments(request):
    """Get payments for current user"""
    try:
        user = get_current_user(request)
        bookings = Booking.objects(user=user)
        
        payments = []
        for booking in bookings:
            payment_list = Payment.objects(booking=booking)
            payments.extend([{
                "id": str(p.id),
                "booking_id": str(p.booking.id),
                "hostel": p.booking.hostel.name,
                "amount": p.amount,
                "method": p.payment_method,
                "status": p.status,
                "transaction_id": p.transaction_id,
                "created_at": p.created_at.isoformat()
            } for p in payment_list])

        return Response({
            "payments": payments
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def make_payment(request):
    """Record a payment for student's booking (Student only)"""
    try:
        import uuid
        
        user = get_current_user(request)
        if not user or user.role != 'student':
            return Response(
                {"error": "Only students can make payments"},
                status=status.HTTP_403_FORBIDDEN
            )

        booking = Booking.objects(id=ObjectId(request.data.get("booking_id"))).first()
        if not booking or booking.user.id != user.id:
            return Response(
                {"error": "Booking not found or unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate unique transaction ID if not provided
        transaction_id = request.data.get("transaction_id", "").strip()
        if not transaction_id:
            transaction_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"

        payment = Payment(
            booking=booking,
            amount=float(request.data.get("amount")),
            payment_method=request.data.get("payment_method", "MPESA"),
            transaction_id=transaction_id,
            status='SUCCESS'
        )
        payment.save()

        return Response({
            "message": "Payment recorded successfully",
            "payment": {
                "id": str(payment.id),
                "booking_id": str(booking.id),
                "hostel": booking.hostel.name,
                "amount": payment.amount,
                "method": payment.payment_method,
                "status": payment.status,
                "transaction_id": payment.transaction_id,
                "created_at": payment.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Make payment error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def hostel_payments(request, hostel_id):
    """Get payments for a hostel (Owner only)"""
    try:
        hostel = Hostel.objects(id=ObjectId(hostel_id)).first()
        if not hostel:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = get_current_user(request)
        if not user or hostel.owner.id != user.id:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        bookings = Booking.objects(hostel=hostel)
        payments = []
        total = 0
        
        for booking in bookings:
            payment_list = Payment.objects(booking=booking)
            for p in payment_list:
                payments.append({
                    "id": str(p.id),
                    "student": booking.user.email,
                    "amount": p.amount,
                    "method": p.payment_method,
                    "status": p.status,
                    "created_at": p.created_at.isoformat()
                })
                if p.status == 'SUCCESS':
                    total += p.amount

        return Response({
            "payments": payments,
            "total_collected": total,
            "total_payments": len(payments)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= DASHBOARD & ANALYTICS VIEWS =============

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    """Student dashboard with their bookings and payments"""
    try:
        user = get_current_user(request)
        if not user or user.role != 'student':
            return Response(
                {"error": "Only students can access this"},
                status=status.HTTP_403_FORBIDDEN
            )

        bookings = list(Booking.objects(user=user))
        issues = list(Issue.objects(user=user))
        
        # Calculate totals
        total_bookings = len(bookings)
        active_booking = next((b for b in bookings if b.status in ['ALLOCATED', 'FINAL_ALLOCATED']), None)
        
        total_paid = 0
        for booking in bookings:
            payments = Payment.objects(booking=booking, status='SUCCESS')
            total_paid += sum(p.amount for p in payments)

        return Response({
            "user": user_to_dict(user),
            "total_bookings": total_bookings,
            "active_booking": serialize_booking(active_booking) if active_booking else None,
            "pending_issues": len([i for i in issues if i.status in ['OPEN', 'IN_PROGRESS']]),
            "resolved_issues": len([i for i in issues if i.status == 'RESOLVED']),
            "total_paid": total_paid,
            "recent_bookings": [serialize_booking(b) for b in sorted(bookings, key=lambda x: x.booking_date, reverse=True)[:3]]
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def owner_dashboard(request):
    """Owner dashboard with hostel statistics"""
    try:
        user = get_current_user(request)
        if not user or user.role != 'owner':
            return Response(
                {"error": "Only owners can access this"},
                status=status.HTTP_403_FORBIDDEN
            )

        hostels = list(Hostel.objects(owner=user))
        total_students = 0
        total_rooms = 0
        occupied_rooms = 0
        total_revenue = 0
        pending_issues = 0
        pending_bookings = 0
        
        for hostel in hostels:
            # Allocated students
            allocated_bookings = list(Booking.objects(hostel=hostel, status='FINAL_ALLOCATED'))
            total_students += len(allocated_bookings)
            
            # Pending booking requests
            pending = list(Booking.objects(hostel=hostel, status='PENDING'))
            pending_bookings += len(pending)
            
            # Room statistics
            rooms = list(Room.objects(hostel=hostel))
            total_rooms += len(rooms)
            occupied_rooms += len([r for r in rooms if r.is_occupied])
            
            # Issues
            issues = list(Issue.objects(hostel=hostel, status__in=['OPEN', 'IN_PROGRESS']))
            pending_issues += len(issues)
            
            # Revenue - FIXED
            all_bookings = list(Booking.objects(hostel=hostel))
            for booking in all_bookings:
                payments = list(Payment.objects(booking=booking, status='SUCCESS'))
                total_revenue += sum(p.amount for p in payments)

        return Response({
            "user": user_to_dict(user),
            "total_hostels": len(hostels),
            "total_students": total_students,
            "total_rooms": total_rooms,
            "occupied_rooms": occupied_rooms,
            "available_rooms": total_rooms - occupied_rooms,
            "pending_booking_requests": pending_bookings,
            "total_revenue": total_revenue,
            "pending_issues": pending_issues,
            "hostels": [serialize_hostel(h) for h in hostels]
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Owner dashboard error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def hostel_stats(request, hostel_id):
    """Detailed statistics for a hostel (Owner only)"""
    try:
        hostel = Hostel.objects(id=ObjectId(hostel_id)).first()
        if not hostel:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = get_current_user(request)
        if not user or hostel.owner.id != user.id:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        bookings = Booking.objects(hostel=hostel)
        rooms = list(Room.objects(hostel=hostel))
        
        stats = {
            "hostel": serialize_hostel(hostel),
            "total_rooms": len(rooms),
            "occupied_rooms": len([r for r in rooms if r.is_occupied]),
            "available_rooms": len([r for r in rooms if not r.is_occupied]),
            "total_students": len(list(Booking.objects(hostel=hostel, status='FINAL_ALLOCATED'))),
            "pending_approvals": len(list(Booking.objects(hostel=hostel, status='PENDING'))),
            "cancelled_bookings": len(list(Booking.objects(hostel=hostel, status='CANCELLED'))),
            "open_issues": len(list(Issue.objects(hostel=hostel, status__in=['OPEN', 'IN_PROGRESS']))),
            "resolved_issues": len(list(Issue.objects(hostel=hostel, status='RESOLVED'))),
        }

        return Response(stats, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
