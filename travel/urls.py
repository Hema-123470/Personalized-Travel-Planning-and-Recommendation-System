from django.urls import path
from . import views

urlpatterns = [
    # Public/Traveler routes
    path('destinations/', views.destination_list, name='destination_list'),
    path('destinations/<slug:slug>/', views.destination_detail, name='destination_detail'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('packages/', views.package_list, name='package_list'),
    path('packages/<slug:slug>/', views.package_detail, name='package_detail'),
    path('attractions/', views.attraction_list, name='attraction_list'),
    path('favorites/', views.my_favorites, name='my_favorites'),
    path('favorites/toggle/<int:destination_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('trips/', views.my_trips, name='my_trips'),
    path('trips/plan/', views.plan_trip, name='plan_trip'),
    path('trips/<int:trip_id>/', views.trip_detail, name='trip_detail'),
    path('trips/<int:trip_id>/delete/', views.delete_trip, name='delete_trip'),

    # Admin CRUD routes
    path('admin-panel/categories/', views.admin_categories, name='admin_categories'),
    path('admin-panel/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin-panel/categories/<int:pk>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin-panel/categories/<int:pk>/delete/', views.admin_category_delete, name='admin_category_delete'),

    path('admin-panel/destinations/', views.admin_destinations, name='admin_destinations'),
    path('admin-panel/destinations/create/', views.admin_destination_create, name='admin_destination_create'),
    path('admin-panel/destinations/<int:pk>/edit/', views.admin_destination_edit, name='admin_destination_edit'),
    path('admin-panel/destinations/<int:pk>/delete/', views.admin_destination_delete, name='admin_destination_delete'),

    path('admin-panel/hotels/', views.admin_hotels, name='admin_hotels'),
    path('admin-panel/hotels/create/', views.admin_hotel_create, name='admin_hotel_create'),
    path('admin-panel/hotels/<int:pk>/edit/', views.admin_hotel_edit, name='admin_hotel_edit'),
    path('admin-panel/hotels/<int:pk>/delete/', views.admin_hotel_delete, name='admin_hotel_delete'),

    path('admin-panel/transports/', views.admin_transports, name='admin_transports'),
    path('admin-panel/transports/create/', views.admin_transport_create, name='admin_transport_create'),
    path('admin-panel/transports/<int:pk>/edit/', views.admin_transport_edit, name='admin_transport_edit'),
    path('admin-panel/transports/<int:pk>/delete/', views.admin_transport_delete, name='admin_transport_delete'),

    path('admin-panel/packages/', views.admin_packages, name='admin_packages'),
    path('admin-panel/packages/create/', views.admin_package_create, name='admin_package_create'),
    path('admin-panel/packages/<int:pk>/edit/', views.admin_package_edit, name='admin_package_edit'),
    path('admin-panel/packages/<int:pk>/delete/', views.admin_package_delete, name='admin_package_delete'),

    path('admin-panel/attractions/', views.admin_attractions, name='admin_attractions'),
    path('admin-panel/attractions/create/', views.admin_attraction_create, name='admin_attraction_create'),
    path('admin-panel/attractions/<int:pk>/edit/', views.admin_attraction_edit, name='admin_attraction_edit'),
    path('admin-panel/attractions/<int:pk>/delete/', views.admin_attraction_delete, name='admin_attraction_delete'),

    path('admin-panel/reviews/', views.admin_reviews, name='admin_reviews'),
    path('admin-panel/reviews/<int:pk>/approve/', views.admin_review_approve, name='admin_review_approve'),
    path('admin-panel/reviews/<int:pk>/delete/', views.admin_review_delete, name='admin_review_delete'),
]
