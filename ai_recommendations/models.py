from django.db import models
from django.conf import settings
from travel.models import Destination


class RecommendationHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    query = models.TextField(help_text='What user asked for')
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration_days = models.IntegerField(null=True, blank=True)
    preferred_climate = models.CharField(max_length=50, blank=True)
    travel_style = models.CharField(max_length=100, blank=True)
    recommended_destinations = models.ManyToManyField(Destination, blank=True, related_name='recommended_in')
    ai_response = models.TextField(blank=True, help_text='Full AI response')
    itinerary = models.TextField(blank=True, help_text='Generated itinerary JSON')
    cost_estimate = models.TextField(blank=True, help_text='Cost breakdown JSON')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendation_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s recommendation - {self.created_at.strftime('%d %b %Y')}"


class ChatMessage(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    session_id = models.CharField(max_length=100)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} ({self.role}): {self.content[:50]}"
