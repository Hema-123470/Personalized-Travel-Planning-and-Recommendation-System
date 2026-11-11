from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from .forms import (
    UserRegistrationForm, UserLoginForm,
    UserProfileUpdateForm, CustomPasswordResetForm
)
from booking.models import Booking
from travel.models import Destination, Hotel, TourPackage
from ai_recommendations.models import RecommendationHistory
from django.db.models import Sum, Count
import json

User = get_user_model()


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'traveler'
            user.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect('traveler_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def dashboard(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    return redirect('traveler_dashboard')


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user():
        messages.error(request, "Access denied. Admin only.")
        return redirect('traveler_dashboard')

    total_users = User.objects.filter(role='traveler').count()
    total_destinations = Destination.objects.filter(is_active=True).count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(status='confirmed').aggregate(
        total=Sum('total_amount'))['total'] or 0

    recent_bookings = Booking.objects.select_related('user', 'tour_package').order_by('-created_at')[:10]
    recent_users = User.objects.filter(role='traveler').order_by('-date_joined')[:5]

    # Monthly bookings for chart (last 6 months) — timezone-safe
    from django.utils import timezone
    from django.db.models.functions import TruncMonth
    from django.db.models import Count as DCount
    import calendar

    now = timezone.localtime(timezone.now())
    months_data = []
    for i in range(5, -1, -1):
        month = now.month - i
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        import datetime, calendar
        # Use date range to avoid MySQL timezone-aware year/month extraction bug
        last_day = calendar.monthrange(year, month)[1]
        start = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc)
        end = datetime.datetime(year, month, last_day, 23, 59, 59, tzinfo=datetime.timezone.utc)
        count = Booking.objects.filter(created_at__gte=start, created_at__lte=end).count()
        month_label = f"{calendar.month_abbr[month]} {year}"
        months_data.append({'month': month_label, 'count': count})

    context = {
        'total_users': total_users,
        'total_destinations': total_destinations,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'recent_users': recent_users,
        'months_data': json.dumps(months_data),
        'total_hotels': Hotel.objects.count(),
        'total_packages': TourPackage.objects.count(),
        'ai_recommendations': RecommendationHistory.objects.count(),
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def traveler_dashboard(request):
    if request.user.is_admin_user():
        return redirect('admin_dashboard')

    my_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')[:5]
    from travel.models import Favorite, TripPlan
    my_favorites = Favorite.objects.filter(user=request.user).select_related('destination')[:6]
    my_trips = TripPlan.objects.filter(user=request.user).order_by('-created_at')[:3]
    recent_recommendations = RecommendationHistory.objects.filter(
        user=request.user).order_by('-created_at')[:3]

    total_spent = Booking.objects.filter(
        user=request.user, status='confirmed'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'my_bookings': my_bookings,
        'my_favorites': my_favorites,
        'my_trips': my_trips,
        'recent_recommendations': recent_recommendations,
        'total_bookings': Booking.objects.filter(user=request.user).count(),
        'total_spent': total_spent,
        'total_favorites': Favorite.objects.filter(user=request.user).count(),
    }
    return render(request, 'accounts/traveler_dashboard.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = UserProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
            # Generate a temporary password
            temp_password = get_random_string(10)
            user.password = make_password(temp_password)
            user.save()
            try:
                send_mail(
                    subject='AI Travel Planner - Password Reset',
                    message=f'''Hello {user.first_name or user.username},

Your temporary password is: {temp_password}

Please login with this password and change it immediately in your profile settings.

Best regards,
AI Travel Planner Team''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, "A temporary password has been sent to your email.")
            except Exception:
                messages.warning(request, f"Email sending failed. Your temporary password is: {temp_password}")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "No account found with that email address.")
    return render(request, 'accounts/forgot_password.html')


# Admin User Management Views
@login_required
def admin_users(request):
    if not request.user.is_admin_user():
        messages.error(request, "Access denied.")
        return redirect('traveler_dashboard')
    users = User.objects.all().order_by('-date_joined')
    search = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    if search:
        users = users.filter(username__icontains=search) | users.filter(email__icontains=search)
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'accounts/admin_users.html', {'users': users, 'search': search})


@login_required
def toggle_user_status(request, user_id):
    if not request.user.is_admin_user():
        messages.error(request, "Access denied.")
        return redirect('traveler_dashboard')
    try:
        user = User.objects.get(id=user_id)
        if user != request.user:
            user.is_active = not user.is_active
            user.save()
            status = "activated" if user.is_active else "deactivated"
            messages.success(request, f"User {user.username} has been {status}.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    return redirect('admin_users')
