"""
Main URL Configuration for AI Travel Planning Project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from travel import views as travel_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', travel_views.home, name='home'),
    path('about/', travel_views.about, name='about'),
    path('contact/', travel_views.contact, name='contact'),
    path('accounts/', include('accounts.urls')),
    path('travel/', include('travel.urls')),
    path('booking/', include('booking.urls')),
    path('ai/', include('ai_recommendations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
