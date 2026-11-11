from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/traveler/', views.traveler_dashboard, name='traveler_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('users/', views.admin_users, name='admin_users'),
    path('users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
]
