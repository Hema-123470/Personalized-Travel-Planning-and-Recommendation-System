from django.contrib import admin
from .models import Booking, Notification, ExpenseTracker


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'user', 'booking_type', 'total_amount', 'status', 'payment_status', 'created_at']
    list_filter = ['booking_type', 'status', 'payment_status']
    search_fields = ['booking_reference', 'user__username', 'user__email']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notif_type', 'is_read', 'created_at']
    list_filter = ['notif_type', 'is_read']


@admin.register(ExpenseTracker)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'amount', 'category', 'date']
    list_filter = ['category']
    search_fields = ['user__username', 'title']
