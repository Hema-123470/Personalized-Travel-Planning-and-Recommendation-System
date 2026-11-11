from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import (Destination, Hotel, Transport, TourPackage,
                     Attraction, Category, Favorite, TripPlan, Review)
from .forms import (DestinationForm, HotelForm, TransportForm, TourPackageForm,
                    AttractionForm, CategoryForm, TripPlanForm, ReviewForm)


# ─── Public / Traveler Views ───────────────────────────────────────────────

def home(request):
    featured_destinations = Destination.objects.filter(is_featured=True, is_active=True)[:6]
    featured_packages = TourPackage.objects.filter(is_featured=True, is_active=True)[:4]
    categories = Category.objects.filter(is_active=True)[:8]
    featured_hotels = Hotel.objects.filter(is_featured=True, is_active=True)[:4]
    total_destinations = Destination.objects.filter(is_active=True).count()
    total_packages = TourPackage.objects.filter(is_active=True).count()
    return render(request, 'home.html', {
        'featured_destinations': featured_destinations,
        'featured_packages': featured_packages,
        'categories': categories,
        'featured_hotels': featured_hotels,
        'total_destinations': total_destinations,
        'total_packages': total_packages,
    })


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_body = request.POST.get('message', '').strip()
        if name and email and subject and message_body:
            messages.success(request, "Thank you! Your message has been sent. We'll get back to you soon.")
        else:
            messages.error(request, "Please fill in all fields.")
    return render(request, 'contact.html')


def destination_list(request):
    destinations = Destination.objects.filter(is_active=True)
    search = request.GET.get('search', '')
    category_slug = request.GET.get('category', '')
    country = request.GET.get('country', '')
    climate = request.GET.get('climate', '')
    min_budget = request.GET.get('min_budget', '')
    max_budget = request.GET.get('max_budget', '')
    sort_by = request.GET.get('sort', '-rating')

    if search:
        destinations = destinations.filter(
            Q(name__icontains=search) |
            Q(country__icontains=search) |
            Q(city__icontains=search) |
            Q(description__icontains=search)
        )
        # When searching by name, ignore climate filter — user may not know the climate type
        climate = ''
    if category_slug:
        destinations = destinations.filter(category__slug=category_slug)
    if country:
        destinations = destinations.filter(country__icontains=country)
    if climate:
        destinations = destinations.filter(climate=climate)
    if min_budget:
        destinations = destinations.filter(average_budget__gte=min_budget)
    if max_budget:
        destinations = destinations.filter(average_budget__lte=max_budget)

    valid_sorts = ['-rating', 'average_budget', '-average_budget', 'name', '-created_at']
    if sort_by in valid_sorts:
        destinations = destinations.order_by(sort_by)

    paginator = Paginator(destinations, 9)
    page = request.GET.get('page')
    destinations = paginator.get_page(page)

    countries = Destination.objects.filter(is_active=True).values_list('country', flat=True).distinct()
    context = {
        'destinations': destinations,
        'search': search,
        'countries': countries,
        'current_category': category_slug,
        'current_country': country,
        'current_climate': climate,
        'sort_by': sort_by,
    }
    return render(request, 'travel/destination_list.html', context)


def destination_detail(request, slug):
    destination = get_object_or_404(Destination, slug=slug, is_active=True)
    destination.views_count += 1
    destination.save(update_fields=['views_count'])

    hotels = Hotel.objects.filter(destination=destination, is_active=True)
    attractions = Attraction.objects.filter(destination=destination, is_active=True)
    transports = Transport.objects.filter(destination=destination, is_active=True)
    packages = TourPackage.objects.filter(destination=destination, is_active=True)
    reviews = Review.objects.filter(destination=destination, is_approved=True)
    related = Destination.objects.filter(
        category=destination.category, is_active=True
    ).exclude(id=destination.id)[:4]

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, destination=destination).exists()

    review_form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.destination = destination
            review.is_approved = True  # auto-approve
            review.save()

            # Recalculate destination rating and total_reviews
            approved_reviews = Review.objects.filter(
                destination=destination, is_approved=True
            )
            total = approved_reviews.count()
            avg = approved_reviews.aggregate(avg=Avg('rating'))['avg'] or 0
            destination.rating = round(avg, 1)
            destination.total_reviews = total
            destination.save(update_fields=['rating', 'total_reviews'])

            messages.success(request, "Review submitted successfully!")
            return redirect('destination_detail', slug=slug)

    context = {
        'destination': destination,
        'hotels': hotels,
        'attractions': attractions,
        'transports': transports,
        'packages': packages,
        'reviews': reviews,
        'related': related,
        'is_favorited': is_favorited,
        'review_form': review_form,
    }
    return render(request, 'travel/destination_detail.html', context)


def hotel_list(request):
    hotels = Hotel.objects.filter(is_active=True)
    search = request.GET.get('search', '')
    destination_id = request.GET.get('destination', '')
    stars = request.GET.get('stars', '')
    max_price = request.GET.get('max_price', '')

    if search:
        hotels = hotels.filter(Q(name__icontains=search) | Q(destination__name__icontains=search))
    if destination_id:
        hotels = hotels.filter(destination_id=destination_id)
    if stars:
        hotels = hotels.filter(stars=stars)
    if max_price:
        hotels = hotels.filter(price_per_night__lte=max_price)

    paginator = Paginator(hotels, 9)
    hotels = paginator.get_page(request.GET.get('page'))
    destinations = Destination.objects.filter(is_active=True)
    return render(request, 'travel/hotel_list.html', {
        'hotels': hotels,
        'destinations': destinations,
        'search': search,
    })


def package_list(request):
    packages = TourPackage.objects.filter(is_active=True)
    search = request.GET.get('search', '')
    destination_id = request.GET.get('destination', '')
    difficulty = request.GET.get('difficulty', '')
    max_price = request.GET.get('max_price', '')
    duration = request.GET.get('duration', '')

    if search:
        packages = packages.filter(Q(name__icontains=search) | Q(destination__name__icontains=search))
    if destination_id:
        packages = packages.filter(destination_id=destination_id)
    if difficulty:
        packages = packages.filter(difficulty=difficulty)
    if max_price:
        packages = packages.filter(price_per_person__lte=max_price)
    if duration:
        packages = packages.filter(duration_days__lte=duration)

    paginator = Paginator(packages, 9)
    packages = paginator.get_page(request.GET.get('page'))
    destinations = Destination.objects.filter(is_active=True)
    return render(request, 'travel/package_list.html', {
        'packages': packages,
        'destinations': destinations,
        'search': search,
    })


def package_detail(request, slug):
    package = get_object_or_404(TourPackage, slug=slug, is_active=True)
    related = TourPackage.objects.filter(
        destination=package.destination, is_active=True
    ).exclude(id=package.id)[:3]
    reviews = Review.objects.filter(tour_package=package, is_approved=True)
    return render(request, 'travel/package_detail.html', {
        'package': package,
        'related': related,
        'reviews': reviews,
    })


def attraction_list(request):
    attractions = Attraction.objects.filter(is_active=True)
    destination_id = request.GET.get('destination', '')
    attraction_type = request.GET.get('type', '')
    if destination_id:
        attractions = attractions.filter(destination_id=destination_id)
    if attraction_type:
        attractions = attractions.filter(attraction_type=attraction_type)
    paginator = Paginator(attractions, 12)
    attractions = paginator.get_page(request.GET.get('page'))
    destinations = Destination.objects.filter(is_active=True)
    return render(request, 'travel/attraction_list.html', {
        'attractions': attractions,
        'destinations': destinations,
    })


@login_required
def toggle_favorite(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, destination=destination)
    if not created:
        fav.delete()
        msg = "Removed from favorites"
        is_fav = False
    else:
        msg = "Added to favorites"
        is_fav = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'is_favorited': is_fav, 'message': msg})
    messages.success(request, msg)
    return redirect('destination_detail', slug=destination.slug)


@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('destination')
    return render(request, 'travel/favorites.html', {'favorites': favorites})


@login_required
def plan_trip(request):
    if request.method == 'POST':
        form = TripPlanForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user
            trip.save()
            messages.success(request, "Trip plan created successfully!")
            return redirect('my_trips')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = TripPlanForm()
        dest_id = request.GET.get('destination')
        if dest_id:
            try:
                form.fields['destination'].initial = dest_id
            except Exception:
                pass
    return render(request, 'travel/plan_trip.html', {'form': form})


@login_required
def my_trips(request):
    trips = TripPlan.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'travel/my_trips.html', {'trips': trips})


@login_required
def trip_detail(request, trip_id):
    trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
    return render(request, 'travel/trip_detail.html', {'trip': trip})


@login_required
def delete_trip(request, trip_id):
    trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
    trip.delete()
    messages.success(request, "Trip plan deleted.")
    return redirect('my_trips')


# ─── Admin CRUD Views ──────────────────────────────────────────────────────

def admin_required(view_func):
    """Decorator to require admin role."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin_user():
            messages.error(request, "Admin access required.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# Categories
@admin_required
def admin_categories(request):
    categories = Category.objects.all()
    return render(request, 'travel/admin/categories.html', {'categories': categories})


@admin_required
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect('admin_categories')
    else:
        form = CategoryForm()
    return render(request, 'travel/admin/category_form.html', {'form': form, 'action': 'Create'})


@admin_required
def admin_category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'travel/admin/category_form.html', {'form': form, 'action': 'Edit'})


@admin_required
def admin_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect('admin_categories')
    return render(request, 'travel/admin/confirm_delete.html', {'obj': category, 'type': 'Category'})


# Destinations
@admin_required
def admin_destinations(request):
    destinations = Destination.objects.all().order_by('-created_at')
    search = request.GET.get('search', '')
    if search:
        destinations = destinations.filter(Q(name__icontains=search) | Q(country__icontains=search))
    paginator = Paginator(destinations, 10)
    destinations = paginator.get_page(request.GET.get('page'))
    return render(request, 'travel/admin/destinations.html', {'destinations': destinations, 'search': search})


@admin_required
def admin_destination_create(request):
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Destination created successfully.")
            return redirect('admin_destinations')
    else:
        form = DestinationForm()
    return render(request, 'travel/admin/destination_form.html', {'form': form, 'action': 'Create'})


@admin_required
def admin_destination_edit(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES, instance=destination)
        if form.is_valid():
            form.save()
            messages.success(request, "Destination updated successfully.")
            return redirect('admin_destinations')
    else:
        form = DestinationForm(instance=destination)
    return render(request, 'travel/admin/destination_form.html', {'form': form, 'action': 'Edit'})


@admin_required
def admin_destination_delete(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        destination.delete()
        messages.success(request, "Destination deleted.")
        return redirect('admin_destinations')
    return render(request, 'travel/admin/confirm_delete.html', {'obj': destination, 'type': 'Destination'})


# Hotels
@admin_required
def admin_hotels(request):
    hotels = Hotel.objects.all().select_related('destination')
    paginator = Paginator(hotels, 10)
    hotels = paginator.get_page(request.GET.get('page'))
    return render(request, 'travel/admin/hotels.html', {'hotels': hotels})


@admin_required
def admin_hotel_create(request):
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Hotel created successfully.")
            return redirect('admin_hotels')
    else:
        form = HotelForm()
    return render(request, 'travel/admin/hotel_form.html', {'form': form, 'action': 'Create'})


@admin_required
def admin_hotel_edit(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, "Hotel updated.")
            return redirect('admin_hotels')
    else:
        form = HotelForm(instance=hotel)
    return render(request, 'travel/admin/hotel_form.html', {'form': form, 'action': 'Edit'})


@admin_required
def admin_hotel_delete(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == 'POST':
        hotel.delete()
        messages.success(request, "Hotel deleted.")
        return redirect('admin_hotels')
    return render(request, 'travel/admin/confirm_delete.html', {'obj': hotel, 'type': 'Hotel'})


# Transport
@admin_required
def admin_transports(request):
    transports = Transport.objects.all().select_related('destination')
    paginator = Paginator(transports, 10)
    transports = paginator.get_page(request.GET.get('page'))
    return render(request, 'travel/admin/transports.html', {'transports': transports})


@admin_required
def admin_transport_create(request):
    if request.method == 'POST':
        form = TransportForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Transport created.")
            return redirect('admin_transports')
    else:
        form = TransportForm()
    return render(request, 'travel/admin/transport_form.html', {'form': form, 'action': 'Create'})


@admin_required
def admin_transport_edit(request, pk):
    transport = get_object_or_404(Transport, pk=pk)
    if request.method == 'POST':
        form = TransportForm(request.POST, instance=transport)
        if form.is_valid():
            form.save()
            messages.success(request, "Transport updated.")
            return redirect('admin_transports')
    else:
        form = TransportForm(instance=transport)
    return render(request, 'travel/admin/transport_form.html', {'form': form, 'action': 'Edit'})


@admin_required
def admin_transport_delete(request, pk):
    transport = get_object_or_404(Transport, pk=pk)
    if request.method == 'POST':
        transport.delete()
        messages.success(request, "Transport deleted.")
        return redirect('admin_transports')
    return render(request, 'travel/admin/confirm_delete.html', {'obj': transport, 'type': 'Transport'})


# Packages
@admin_required
def admin_packages(request):
    packages = TourPackage.objects.all().select_related('destination')
    paginator = Paginator(packages, 10)
    packages = paginator.get_page(request.GET.get('page'))
    return render(request, 'travel/admin/packages.html', {'packages': packages})


@admin_required
def admin_package_create(request):
    if request.method == 'POST':
        form = TourPackageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Package created.")
            return redirect('admin_packages')
    else:
        form = TourPackageForm()
    return render(request, 'travel/admin/package_form.html', {'form': form, 'action': 'Create'})


@admin_required
def admin_package_edit(request, pk):
    package = get_object_or_404(TourPackage, pk=pk)
    if request.method == 'POST':
        form = TourPackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, "Package updated.")
            return redirect('admin_packages')
    else:
        form = TourPackageForm(instance=package)
    return render(request, 'travel/admin/package_form.html', {'form': form, 'action': 'Edit'})


@admin_required
def admin_package_delete(request, pk):
    package = get_object_or_404(TourPackage, pk=pk)
    if request.method == 'POST':
        package.delete()
        messages.success(request, "Package deleted.")
        return redirect('admin_packages')
    return render(request, 'travel/admin/confirm_delete.html', {'obj': package, 'type': 'Tour Package'})


# Attractions
@admin_required
def admin_attractions(request):
    attractions = Attraction.objects.all().select_related('destination')
    paginator = Paginator(attractions, 10)
    attractions = paginator.get_page(request.GET.get('page'))
    return render(request, 'travel/admin/attractions.html', {'attractions': attractions})


@admin_required
def admin_attraction_create(request):
    if request.method == 'POST':
        form = AttractionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Attraction created.")
            return redirect('admin_attractions')
    else:
        form = AttractionForm()
    return render(request, 'travel/admin/attraction_form.html', {'form': form, 'action': 'Create'})


@admin_required
def admin_attraction_edit(request, pk):
    attraction = get_object_or_404(Attraction, pk=pk)
    if request.method == 'POST':
        form = AttractionForm(request.POST, request.FILES, instance=attraction)
        if form.is_valid():
            form.save()
            messages.success(request, "Attraction updated.")
            return redirect('admin_attractions')
    else:
        form = AttractionForm(instance=attraction)
    return render(request, 'travel/admin/attraction_form.html', {'form': form, 'action': 'Edit'})


@admin_required
def admin_attraction_delete(request, pk):
    attraction = get_object_or_404(Attraction, pk=pk)
    if request.method == 'POST':
        attraction.delete()
        messages.success(request, "Attraction deleted.")
        return redirect('admin_attractions')
    return render(request, 'travel/admin/confirm_delete.html', {'obj': attraction, 'type': 'Attraction'})


# Admin Reviews
@admin_required
def admin_reviews(request):
    reviews = Review.objects.all().select_related('user')
    return render(request, 'travel/admin/reviews.html', {'reviews': reviews})


@admin_required
def admin_review_approve(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.is_approved = not review.is_approved
    review.save()
    status = "approved" if review.is_approved else "unapproved"
    messages.success(request, f"Review {status}.")
    return redirect('admin_reviews')


@admin_required
def admin_review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    messages.success(request, "Review deleted.")
    return redirect('admin_reviews')
