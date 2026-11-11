from django.db import models
from django.conf import settings
from travel.models import Hotel, Transport, TourPackage, Destination


class Booking(models.Model):
    BOOKING_TYPE = [
        ('hotel', 'Hotel'),
        ('transport', 'Transport'),
        ('package', 'Tour Package'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    booking_type = models.CharField(max_length=15, choices=BOOKING_TYPE)
    booking_reference = models.CharField(max_length=20, unique=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    tour_package = models.ForeignKey(TourPackage, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')

    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    travel_date = models.DateField(null=True, blank=True)
    number_of_guests = models.IntegerField(default=1)
    number_of_nights = models.IntegerField(default=1)

    base_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)

    special_requests = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.booking_reference} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            import random
            import string
            self.booking_reference = 'ATP' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)


class Notification(models.Model):
    NOTIF_TYPE = [
        ('booking', 'Booking'),
        ('system', 'System'),
        ('promotion', 'Promotion'),
        ('reminder', 'Reminder'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notif_type = models.CharField(max_length=15, choices=NOTIF_TYPE, default='system')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ExpenseTracker(models.Model):
    CATEGORY_CHOICES = [
        ('accommodation', 'Accommodation'),
        ('transport', 'Transport'),
        ('food', 'Food & Dining'),
        ('activities', 'Activities'),
        ('shopping', 'Shopping'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    date = models.DateField()
    description = models.TextField(blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'expense_tracker'
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.title} (₹{self.amount})"
