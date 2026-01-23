from mongoengine import (
    Document, StringField, IntField, FloatField, BooleanField, 
    DateTimeField, FileField, ReferenceField, ListField, EmbeddedDocument,
    EmbeddedDocumentField, PULL, ValidationError, NotUniqueError
)
from datetime import datetime
from bson import ObjectId

# ============= CHOICE FIELDS =============
ROLE_CHOICES = ('student', 'owner', 'admin')
STATUS_CHOICES = ('PENDING', 'AWAITING_ALLOCATION', 'ALLOCATED', 'FINAL_ALLOCATED', 'CANCELLED')
ISSUE_STATUS_CHOICES = ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED')
ROOM_TYPE_CHOICES = ('SINGLE', 'DOUBLE', 'TRIPLE')
PAYMENT_METHOD_CHOICES = ('MPESA', 'CARD', 'BANK')
PAYMENT_STATUS_CHOICES = ('PENDING', 'SUCCESS', 'FAILED')
PRIORITY_CHOICES = ('LOW', 'MEDIUM', 'HIGH')


# ============= USER MODEL =============
class User(Document):
    """User document with role management"""
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    first_name = StringField(max_length=30)
    last_name = StringField(max_length=30)
    role = StringField(choices=ROLE_CHOICES, default='student')
    phone_number = StringField(max_length=15)
    profile_picture = StringField()  # File path/URL
    is_verified = BooleanField(default=False)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'users',
        'indexes': [
            'email',
            'username',
            'role',
            'created_at',
            ('email', 'username'),
        ]
    }

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_role_display(self):
        role_display = {
            'student': 'Student',
            'owner': 'Owner',
            'admin': 'Admin'
        }
        return role_display.get(self.role, self.role)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


# ============= HOSTEL IMAGE EMBEDDED DOCUMENT =============
class HostelImageEmbedded(EmbeddedDocument):
    """Embedded document for hostel images"""
    image_url = StringField(required=True)
    caption = StringField()
    is_primary = BooleanField(default=False)
    uploaded_at = DateTimeField(default=datetime.utcnow)
    order = IntField(default=0)

    def __str__(self):
        return f"Image - {self.caption or 'Hostel'}"


# ============= HOSTEL MODEL =============
class Hostel(Document):
    """Hostel/Accommodation document"""
    owner = ReferenceField(User, required=True)
    name = StringField(required=True, max_length=150)
    location = StringField(required=True, max_length=200)
    description = StringField()
    total_rooms = IntField(required=True, min_value=1)
    available_rooms = IntField(required=True, min_value=0)
    price_per_month = FloatField(required=True, min_value=0)
    price_per_semester = FloatField(min_value=0)
    image = StringField()  # Main/primary image
    images = ListField(EmbeddedDocumentField(HostelImageEmbedded))
    amenities = StringField()  # Comma-separated list
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'hostels',
        'indexes': [
            'owner',
            'is_active',
            'location',
            'created_at',
        ]
    }

    def __str__(self):
        return f"{self.name} - {self.location}"

    def get_available_rooms_count(self):
        """Calculate available rooms based on bookings"""
        try:
            allocated = Booking.objects(
                hostel=self,
                status='FINAL_ALLOCATED'
            ).count()
            return self.total_rooms - allocated
        except:
            return self.available_rooms

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


# ============= ROOM MODEL =============
class Room(Document):
    """Individual Room document"""
    hostel = ReferenceField(Hostel, required=True)
    room_number = StringField(required=True, max_length=20)
    room_type = StringField(choices=ROOM_TYPE_CHOICES, default='DOUBLE')
    capacity = IntField(required=True, min_value=1, default=2)
    price_per_month = FloatField(required=True, min_value=0)
    is_occupied = BooleanField(default=False)
    assigned_to = ReferenceField(User, allow_null=True)
    floor = IntField()
    amenities = StringField()  # Comma-separated
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'rooms',
        'indexes': [
            ('hostel', 'room_number'),
            'hostel',
            'is_occupied',
            'assigned_to',
        ]
    }

    def __str__(self):
        return f"Room {self.room_number} - {self.hostel.name}"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


# ============= BOOKING MODEL =============
class Booking(Document):
    """Booking/Room Allocation document"""
    user = ReferenceField(User, required=True)
    hostel = ReferenceField(Hostel, required=True)
    room = ReferenceField(Room, allow_null=True)
    status = StringField(choices=STATUS_CHOICES, default='PENDING')
    room_number = StringField(max_length=20)
    booking_date = DateTimeField(default=datetime.utcnow)
    allocation_date = DateTimeField()
    semester_start = DateTimeField()
    semester_end = DateTimeField()
    notes = StringField()
    approved_by = ReferenceField(User, allow_null=True)
    approval_date = DateTimeField()
    rejection_reason = StringField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'bookings',
        'indexes': [
            'user',
            'hostel',
            'status',
            'is_active',
            'booking_date',
            ('user', 'hostel'),
        ]
    }

    def __str__(self):
        return f"{self.user.email} - {self.hostel.name} ({self.status})"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


# ============= ISSUE MODEL =============
class Issue(Document):
    """Maintenance/Issue Report document"""
    user = ReferenceField(User, required=True)
    hostel = ReferenceField(Hostel, required=True)
    booking = ReferenceField(Booking, allow_null=True)
    title = StringField(required=True, max_length=200)
    description = StringField(required=True)
    priority = StringField(choices=PRIORITY_CHOICES, default='MEDIUM')
    status = StringField(choices=ISSUE_STATUS_CHOICES, default='OPEN')
    attachment = StringField()  # File path/URL
    created_at = DateTimeField(default=datetime.utcnow)
    resolved_at = DateTimeField()
    resolution_notes = StringField()
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'issues',
        'indexes': [
            'hostel',
            'status',
            'priority',
            'user',
            'created_at',
        ]
    }

    def __str__(self):
        return f"{self.title} - {self.hostel.name} ({self.status})"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


# ============= NOTICE MODEL =============
class Notice(Document):
    """Notice/Announcement document"""
    hostel = ReferenceField(Hostel, required=True)
    owner = ReferenceField(User, required=True)
    title = StringField(required=True, max_length=200)
    message = StringField(required=True)
    priority = StringField(choices=['LOW', 'NORMAL', 'HIGH'], default='NORMAL')
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'notices',
        'indexes': [
            'hostel',
            'is_active',
            'created_at',
            ('hostel', 'is_active'),
        ]
    }

    def __str__(self):
        return f"{self.title} - {self.hostel.name}"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


# ============= PAYMENT MODEL =============
class Payment(Document):
    """Payment Transaction document"""
    booking = ReferenceField(Booking, required=True)
    amount = FloatField(required=True, min_value=0)
    payment_method = StringField(choices=PAYMENT_METHOD_CHOICES, default='MPESA')
    transaction_id = StringField(unique=True, sparse=True)
    status = StringField(choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'payments',
        'indexes': [
            'booking',
            'status',
            'transaction_id',
            'created_at',
        ]
    }

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

