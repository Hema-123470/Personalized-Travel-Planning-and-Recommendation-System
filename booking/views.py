from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.utils import timezone
from travel.models import Hotel, Transport, TourPackage
from .models import Booking, Notification, ExpenseTracker
from .forms import HotelBookingForm, TransportBookingForm, PackageBookingForm, ExpenseForm


def create_notification(user, title, message, notif_type='booking', link=''):
    Notification.objects.create(
        user=user, title=title, message=message, notif_type=notif_type, link=link
    )


@login_required
def book_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, is_active=True)
    if request.method == 'POST':
        form = HotelBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.booking_type = 'hotel'
            booking.hotel = hotel
            if booking.check_in_date and booking.check_out_date:
                nights = (booking.check_out_date - booking.check_in_date).days
                booking.number_of_nights = nights
                from decimal import Decimal
                booking.base_amount = hotel.price_per_night * nights * booking.number_of_guests
                booking.tax_amount = booking.base_amount * Decimal('18') / Decimal('100')
                booking.total_amount = booking.base_amount + booking.tax_amount
            booking.status = 'confirmed'
            booking.payment_status = 'paid'
            booking.save()
            create_notification(
                request.user,
                'Hotel Booking Confirmed',
                f'Your booking at {hotel.name} has been confirmed. Reference: {booking.booking_reference}',
                link=f'/booking/{booking.id}/'
            )
            messages.success(request, f"Hotel booked successfully! Reference: {booking.booking_reference}")
            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = HotelBookingForm()
    return render(request, 'booking/book_hotel.html', {'hotel': hotel, 'form': form})


@login_required
def book_transport(request, transport_id):
    transport = get_object_or_404(Transport, id=transport_id, is_active=True)
    if request.method == 'POST':
        form = TransportBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.booking_type = 'transport'
            booking.transport = transport
            from decimal import Decimal
            booking.base_amount = transport.price * booking.number_of_guests
            booking.tax_amount = booking.base_amount * Decimal('5') / Decimal('100')
            booking.total_amount = booking.base_amount + booking.tax_amount
            booking.status = 'confirmed'
            booking.payment_status = 'paid'
            booking.save()
            create_notification(
                request.user,
                'Transport Booking Confirmed',
                f'Your transport booking has been confirmed. Reference: {booking.booking_reference}',
            )
            messages.success(request, f"Transport booked! Reference: {booking.booking_reference}")
            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = TransportBookingForm()
    return render(request, 'booking/book_transport.html', {'transport': transport, 'form': form})


@login_required
def book_package(request, package_id):
    package = get_object_or_404(TourPackage, id=package_id, is_active=True)
    if request.method == 'POST':
        form = PackageBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.booking_type = 'package'
            booking.tour_package = package
            booking.payment_reference = request.POST.get('payment_reference', '')
            from decimal import Decimal
            guests = booking.number_of_guests
            price = package.get_discounted_price()
            booking.base_amount = price * guests
            if package.discount_percent > 0:
                original = package.price_per_person * guests
                booking.discount_amount = original - booking.base_amount
            booking.tax_amount = booking.base_amount * Decimal('18') / Decimal('100')
            booking.total_amount = booking.base_amount + booking.tax_amount
            booking.status = 'confirmed'
            booking.payment_status = 'paid'
            booking.save()
            package.total_bookings += 1
            package.save(update_fields=['total_bookings'])
            create_notification(
                request.user,
                'Package Booking Confirmed',
                f'Your booking for {package.name} has been confirmed. Reference: {booking.booking_reference}',
            )
            messages.success(request, f"Package booked! Reference: {booking.booking_reference}")
            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = PackageBookingForm()
    return render(request, 'booking/book_package.html', {'package': package, 'form': form})


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking/booking_detail.html', {'booking': booking})


@login_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user)
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if type_filter:
        bookings = bookings.filter(booking_type=type_filter)
    paginator = Paginator(bookings, 10)
    bookings = paginator.get_page(request.GET.get('page'))
    return render(request, 'booking/booking_history.html', {'bookings': bookings})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.payment_status = 'refunded'
        booking.save()
        create_notification(request.user, 'Booking Cancelled',
                            f'Booking #{booking.booking_reference} has been cancelled.')
        messages.success(request, "Booking cancelled successfully.")
    else:
        messages.error(request, "This booking cannot be cancelled.")
    return redirect('booking_history')


@login_required
def expense_tracker(request):
    expenses = ExpenseTracker.objects.filter(user=request.user)
    total_spent = expenses.aggregate(total=Sum('amount'))['total'] or 0
    by_category = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Expense added successfully.")
            return redirect('expense_tracker')
    else:
        form = ExpenseForm()
    return render(request, 'booking/expense_tracker.html', {
        'expenses': expenses,
        'total_spent': total_spent,
        'by_category': by_category,
        'form': form,
    })


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(ExpenseTracker, id=expense_id, user=request.user)
    expense.delete()
    messages.success(request, "Expense deleted.")
    return redirect('expense_tracker')


@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user)
    user_notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'booking/notifications.html', {'notifications': user_notifications})


# ─── Admin Views ──────────────────────────────────────────────────────────

def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin_user():
            messages.error(request, "Admin access required.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_bookings(request):
    bookings = Booking.objects.all().select_related('user', 'hotel', 'transport', 'tour_package')
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    paginator = Paginator(bookings, 15)
    bookings = paginator.get_page(request.GET.get('page'))
    total_revenue = Booking.objects.filter(status='confirmed').aggregate(total=Sum('total_amount'))['total'] or 0
    return render(request, 'booking/admin/bookings.html', {
        'bookings': bookings,
        'total_revenue': total_revenue,
    })


@admin_required
def admin_booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking/admin/booking_detail.html', {'booking': booking})


@admin_required
def admin_update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    new_status = request.POST.get('status')
    new_payment_status = request.POST.get('payment_status')
    if new_status in dict(Booking.STATUS_CHOICES):
        booking.status = new_status
    if new_payment_status in dict(Booking.PAYMENT_STATUS):
        booking.payment_status = new_payment_status
    booking.save()
    create_notification(
        booking.user, 'Booking Status Updated',
        f'Your booking #{booking.booking_reference} has been updated.'
    )
    messages.success(request, "Booking updated successfully.")
    return redirect('admin_booking_detail', booking_id=booking_id)


@admin_required
def admin_reports(request):
    from django.utils import timezone
    import json
    import calendar

    total_revenue = Booking.objects.filter(status='confirmed').aggregate(total=Sum('total_amount'))['total'] or 0
    bookings_by_type = Booking.objects.values('booking_type').annotate(count=Count('id'))
    bookings_by_status = Booking.objects.values('status').annotate(count=Count('id'))

    now = timezone.localtime(timezone.now())
    monthly_data = []
    for i in range(11, -1, -1):
        month = now.month - i
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        import datetime, calendar
        last_day = calendar.monthrange(year, month)[1]
        start = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc)
        end = datetime.datetime(year, month, last_day, 23, 59, 59, tzinfo=datetime.timezone.utc)
        revenue = Booking.objects.filter(
            created_at__gte=start, created_at__lte=end,
            status='confirmed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        count = Booking.objects.filter(
            created_at__gte=start, created_at__lte=end
        ).count()
        monthly_data.append({
            'month': f"{calendar.month_abbr[month]} {year}",
            'revenue': float(revenue),
            'count': count
        })

    context = {
        'total_revenue': total_revenue,
        'bookings_by_type': bookings_by_type,
        'bookings_by_status': bookings_by_status,
        'monthly_data': json.dumps(monthly_data),
        'total_bookings': Booking.objects.count(),
        'confirmed_bookings': Booking.objects.filter(status='confirmed').count(),
    }
    return render(request, 'booking/admin/reports.html', context)
