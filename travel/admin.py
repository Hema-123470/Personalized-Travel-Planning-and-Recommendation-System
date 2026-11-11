from django.contrib import admin
from .models import Category, Destination, Hotel, Transport, TourPackage, Attraction, Favorite, TripPlan, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'city', 'category', 'is_featured', 'is_active', 'rating']
    list_filter = ['is_featured', 'is_active', 'climate', 'category']
    search_fields = ['name', 'country', 'city']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured', 'is_active']


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'destination', 'stars', 'price_per_night', 'is_featured', 'is_active']
    list_filter = ['stars', 'is_active', 'is_featured']
    search_fields = ['name', 'destination__name']


@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ['name', 'transport_type', 'from_location', 'to_location', 'price', 'is_active']
    list_filter = ['transport_type', 'is_active']
    search_fields = ['name', 'from_location', 'to_location']


@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'destination', 'duration_days', 'price_per_person', 'is_featured', 'is_active']
    list_filter = ['is_featured', 'is_active', 'difficulty']
    search_fields = ['name', 'destination__name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ['name', 'destination', 'attraction_type', 'entry_fee', 'is_active']
    list_filter = ['attraction_type', 'is_active']
    search_fields = ['name', 'destination__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating']
    list_editable = ['is_approved']


admin.site.register(Favorite)
admin.site.register(TripPlan)
