from django.urls import path
from . import views

urlpatterns = [
    path('hotel/<int:hotel_id>/', views.book_hotel, name='book_hotel'),
    path('transport/<int:transport_id>/', views.book_transport, name='book_transport'),
    path('package/<int:package_id>/', views.book_package, name='book_package'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('history/', views.booking_history, name='booking_history'),
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('expenses/', views.expense_tracker, name='expense_tracker'),
    path('expenses/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('notifications/', views.notifications, name='notifications'),
    # Admin
    path('admin-panel/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin-panel/bookings/<int:booking_id>/', views.admin_booking_detail, name='admin_booking_detail'),
    path('admin-panel/bookings/<int:booking_id>/status/', views.admin_update_booking_status, name='admin_update_booking_status'),
    path('admin-panel/reports/', views.admin_reports, name='admin_reports'),
]
