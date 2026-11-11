from django.contrib import admin
from .models import RecommendationHistory, ChatMessage


@admin.register(RecommendationHistory)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'query', 'budget', 'duration_days', 'created_at']
    list_filter = ['preferred_climate', 'created_at']
    search_fields = ['user__username', 'query']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'session_id', 'created_at']
    list_filter = ['role']
    search_fields = ['user__username', 'content']
