from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from .models import RecommendationHistory, ChatMessage
from .ai_engine import (
    get_budget_recommendations, generate_itinerary, calculate_travel_cost,
    get_personalized_recommendations, get_nearby_attractions, get_weather_info,
    chat_with_ai
)
from travel.models import Destination


def _clean_markdown(text):
    """Remove markdown symbols from Gemini/AI responses for clean chat display."""
    import re
    # Remove ### headings → keep text, add newline
    text = re.sub(r'#{1,6}\s*', '', text)
    # Remove **bold** → keep text
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # Remove *italic* → keep text
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Remove __bold__ → keep text
    text = re.sub(r'__(.+?)__', r'\1', text)
    # Remove _italic_ → keep text
    text = re.sub(r'_(.+?)_', r'\1', text)
    # Remove bullet * or - at line start → replace with •
    text = re.sub(r'^\s*[\*\-]\s+', '• ', text, flags=re.MULTILINE)
    # Remove horizontal rules ---
    text = re.sub(r'\n-{3,}\n', '\n', text)
    # Remove backtick code blocks
    text = re.sub(r'`{1,3}.*?`{1,3}', '', text, flags=re.DOTALL)
    # Collapse more than 2 consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


@login_required
def ai_dashboard(request):
    """Main AI features hub."""
    personalized = get_personalized_recommendations(request.user, limit=6)
    recent_history = RecommendationHistory.objects.filter(user=request.user)[:5]
    featured_destinations = Destination.objects.filter(is_featured=True, is_active=True)[:4]
    return render(request, 'ai/dashboard.html', {
        'personalized': personalized,
        'recent_history': recent_history,
        'featured_destinations': featured_destinations,
    })


@login_required
def get_recommendations(request):
    """AI-powered destination recommendation form and results."""
    if request.method == 'POST':
        budget = request.POST.get('budget', 0)
        duration = int(request.POST.get('duration', 3))
        travelers = int(request.POST.get('travelers', 1))
        climate = request.POST.get('climate', '')
        travel_style = request.POST.get('travel_style', '')
        query = request.POST.get('query', '')

        recommendations = get_budget_recommendations(float(budget) if budget else 50000, duration, travelers)

        # Filter by query keyword — match against category slug only
        if query:
            q = query.lower().strip()
            # Map common trip type words to category slugs
            keyword_to_slug = {
                'beach': 'beach',
                'sea': 'beach',
                'coastal': 'beach',
                'goa': 'beach',
                'mountain': 'mountains',
                'mountains': 'mountains',
                'snow': 'mountains',
                'trekking': 'mountains',
                'hill': 'hill-stations',
                'hill station': 'hill-stations',
                'hills': 'hill-stations',
                'heritage': 'heritage-culture',
                'culture': 'heritage-culture',
                'historical': 'heritage-culture',
                'fort': 'heritage-culture',
                'palace': 'heritage-culture',
                'spiritual': 'spiritual',
                'temple': 'spiritual',
                'pilgrimage': 'spiritual',
                'religious': 'spiritual',
                'adventure': 'adventure',
                'trek': 'adventure',
                'rafting': 'adventure',
                'camping': 'adventure',
                'wildlife': 'wildlife',
                'safari': 'wildlife',
                'jungle': 'wildlife',
                'city': 'city-tours',
                'urban': 'city-tours',
                'shopping': 'city-tours',
            }
            # Find matching category slug
            matched_slug = None
            for keyword, slug in keyword_to_slug.items():
                if keyword in q:
                    matched_slug = slug
                    break

            if matched_slug:
                filtered = [
                    r for r in recommendations
                    if r['destination'].category and r['destination'].category.slug == matched_slug
                ]
                if filtered:
                    recommendations = filtered
            else:
                # Fallback: search by destination name or city
                filtered = [
                    r for r in recommendations
                    if q in r['destination'].name.lower() or q in r['destination'].city.lower()
                ]
                if filtered:
                    recommendations = filtered

        # Filter by climate if specified
        if climate:
            climate_filtered = [r for r in recommendations if r['destination'].climate == climate]
            if climate_filtered:
                recommendations = climate_filtered

        # Save to history
        history = RecommendationHistory.objects.create(
            user=request.user,
            query=query or f"Budget: ₹{budget}, Duration: {duration} days, Travelers: {travelers}",
            budget=budget if budget else None,
            duration_days=duration,
            preferred_climate=climate,
            travel_style=travel_style,
        )
        if recommendations:
            history.recommended_destinations.set([r['destination'] for r in recommendations[:5]])

        return render(request, 'ai/recommendations.html', {
            'recommendations': recommendations,
            'budget': budget,
            'duration': duration,
            'travelers': travelers,
            'history': history,
        })

    return render(request, 'ai/recommendation_form.html', {
        'destinations': Destination.objects.filter(is_active=True),
    })


@login_required
def generate_trip_itinerary(request):
    """Generate AI day-wise itinerary."""
    if request.method == 'POST':
        destination_id = request.POST.get('destination')
        duration = int(request.POST.get('duration', 3))
        budget = request.POST.get('budget', '')

        try:
            destination = Destination.objects.get(id=destination_id, is_active=True)
            itinerary = generate_itinerary(destination, duration, float(budget) if budget else None)
            cost_estimate = calculate_travel_cost(destination, duration, 1)

            return render(request, 'ai/itinerary.html', {
                'destination': destination,
                'itinerary': itinerary,
                'cost_estimate': cost_estimate,
                'duration': duration,
                'budget': budget,
            })
        except Destination.DoesNotExist:
            messages.error(request, "Destination not found.")

    destinations = Destination.objects.filter(is_active=True)
    return render(request, 'ai/itinerary_form.html', {'destinations': destinations})


@login_required
def cost_estimator(request):
    """Travel cost estimation tool."""
    result = None
    if request.method == 'POST':
        destination_id = request.POST.get('destination')
        duration = int(request.POST.get('duration', 3))
        travelers = int(request.POST.get('travelers', 1))
        hotel_stars = int(request.POST.get('hotel_stars', 3))
        try:
            destination = Destination.objects.get(id=destination_id, is_active=True)
            result = calculate_travel_cost(destination, duration, travelers, hotel_stars)
            result['destination'] = destination
            result['duration'] = duration
            result['travelers'] = travelers
        except Destination.DoesNotExist:
            messages.error(request, "Destination not found.")

    destinations = Destination.objects.filter(is_active=True)
    return render(request, 'ai/cost_estimator.html', {
        'destinations': destinations,
        'result': result,
    })


@login_required
def weather_info(request):
    """Fetch weather for a destination."""
    weather_data = None
    city = request.GET.get('city', '')
    if city:
        weather_data = get_weather_info(city)

    destinations = Destination.objects.filter(is_active=True)
    return render(request, 'ai/weather.html', {
        'weather_data': weather_data,
        'city': city,
        'destinations': destinations,
    })


@login_required
def nearby_attractions(request):
    """Find nearby attractions based on coordinates."""
    attractions = []
    lat = request.GET.get('lat', '')
    lng = request.GET.get('lng', '')
    radius = float(request.GET.get('radius', 10))

    if lat and lng:
        try:
            attractions = get_nearby_attractions(float(lat), float(lng), radius)
        except ValueError:
            messages.error(request, "Invalid coordinates.")

    return render(request, 'ai/nearby_attractions.html', {
        'attractions': attractions,
        'lat': lat,
        'lng': lng,
    })


@login_required
def ai_chat(request):
    """AI Chat Assistant page."""
    session_id = request.session.get('chat_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['chat_session_id'] = session_id

    chat_history = ChatMessage.objects.filter(
        user=request.user, session_id=session_id
    ).order_by('created_at')

    return render(request, 'ai/chat.html', {
        'chat_history': chat_history,
        'session_id': session_id,
    })


@login_required
@require_POST
def ai_chat_message(request):
    """Process AI chat message via AJAX."""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', request.session.get('chat_session_id', ''))

        if not user_message:
            return JsonResponse({'error': 'Empty message'}, status=400)

        # Save user message
        ChatMessage.objects.create(
            user=request.user,
            session_id=session_id,
            role='user',
            content=user_message
        )

        # Get chat history for context (all messages except the one just saved)
        all_messages = list(ChatMessage.objects.filter(
            user=request.user, session_id=session_id
        ).values('role', 'content').order_by('created_at'))
        history = all_messages[:-1]  # exclude the current user message

        # Get AI response and clean markdown formatting
        ai_response = chat_with_ai(user_message, history)
        ai_response = _clean_markdown(ai_response)

        # Save assistant response
        ChatMessage.objects.create(
            user=request.user,
            session_id=session_id,
            role='assistant',
            content=ai_response
        )

        return JsonResponse({'response': ai_response})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def recommendation_history(request):
    """View recommendation history."""
    history = RecommendationHistory.objects.filter(user=request.user)
    return render(request, 'ai/history.html', {'history': history})


@login_required
def clear_chat(request):
    """Clear chat history for current session."""
    session_id = request.session.get('chat_session_id', '')
    if session_id:
        ChatMessage.objects.filter(user=request.user, session_id=session_id).delete()
        del request.session['chat_session_id']
    messages.success(request, "Chat history cleared.")
    return redirect('ai_chat')
