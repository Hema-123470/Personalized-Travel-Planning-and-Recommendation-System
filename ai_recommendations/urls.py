from django.urls import path
from . import views

urlpatterns = [
    path('', views.ai_dashboard, name='ai_dashboard'),
    path('recommendations/', views.get_recommendations, name='ai_recommendations'),
    path('itinerary/', views.generate_trip_itinerary, name='ai_itinerary'),
    path('cost-estimator/', views.cost_estimator, name='ai_cost_estimator'),
    path('weather/', views.weather_info, name='ai_weather'),
    path('nearby/', views.nearby_attractions, name='ai_nearby'),
    path('chat/', views.ai_chat, name='ai_chat'),
    path('chat/message/', views.ai_chat_message, name='ai_chat_message'),
    path('history/', views.recommendation_history, name='ai_history'),
    path('chat/clear/', views.clear_chat, name='clear_chat'),
]
