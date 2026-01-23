from django.urls import path
from .views import *

app_name = 'api'

urlpatterns = [
    # Authentication
    path("auth/register/", register, name="register"),
    path("auth/login/", login, name="login"),
    path("auth/profile/", user_profile, name="user_profile"),

    # Hostels
    path("hostels/", all_hostels, name="all_hostels"),
    path("hostels/add/", add_hostel, name="add_hostel"),
    path("hostels/my/", my_hostels, name="my_hostels"),
    path("hostels/<hostel_id>/", hostel_detail, name="hostel_detail"),
    path("hostels/<hostel_id>/update/", update_hostel, name="update_hostel"),

    # Rooms
    path("rooms/add/", add_room, name="add_room"),
    path("rooms/hostel/<hostel_id>/", get_hostel_rooms, name="get_hostel_rooms"),
    path("rooms/<room_id>/update/", update_room, name="update_room"),

    # Bookings
    path("bookings/book/", book_hostel, name="book_hostel"),
    path("bookings/my/", my_bookings, name="my_bookings"),
    path("bookings/owner/<hostel_id>/", owner_bookings, name="owner_bookings"),
    path("bookings/<booking_id>/approve/", approve_booking, name="approve_booking"),
    path("bookings/<booking_id>/reject/", reject_booking, name="reject_booking"),

    # Issues
    path("issues/report/", report_issue, name="report_issue"),
    path("issues/owner/<hostel_id>/", owner_issues, name="owner_issues"),
    path("issues/<issue_id>/resolve/", resolve_issue, name="resolve_issue"),

    # Notices
    path("notices/send/", send_notice, name="send_notice"),
    path("notices/<hostel_id>/", get_notices, name="get_notices"),

    # Payments
    path("payments/my/", my_payments, name="my_payments"),
    path("payments/make/", make_payment, name="make_payment"),
    path("payments/record/", record_payment, name="record_payment"),
    path("payments/hostel/<hostel_id>/", hostel_payments, name="hostel_payments"),

    # Dashboard & Analytics
    path("dashboard/student/", student_dashboard, name="student_dashboard"),
    path("dashboard/owner/", owner_dashboard, name="owner_dashboard"),
    path("analytics/hostel/<hostel_id>/", hostel_stats, name="hostel_stats"),
]