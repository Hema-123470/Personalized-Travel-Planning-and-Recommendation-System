"""
AI Engine for Travel Recommendations
Provides AI-powered recommendations without requiring external API keys by default.
Falls back to built-in recommendation logic when OpenAI is not configured.
"""
import json
import random
from django.conf import settings
from travel.models import Destination, Hotel, Attraction, TourPackage


def get_destinations_by_budget(budget, num=5):
    """Filter destinations by budget range."""
    destinations = Destination.objects.filter(
        is_active=True,
        average_budget__lte=float(budget) * 1.2
    ).order_by('-rating')[:num]
    return list(destinations)


def get_budget_recommendations(budget, duration, travelers=1):
    """Generate budget-based recommendations."""
    from decimal import Decimal
    per_person_budget = float(budget) / travelers if travelers > 0 else float(budget)
    destinations = Destination.objects.filter(
        is_active=True,
        average_budget__lte=per_person_budget
    ).order_by('-rating')[:30]

    recommendations = []
    for dest in destinations:
        hotels = Hotel.objects.filter(destination=dest, is_active=True).order_by('price_per_night').first()
        packages = TourPackage.objects.filter(destination=dest, is_active=True).order_by('price_per_person').first()
        hotel_cost = float(hotels.price_per_night) * duration if hotels else 0
        package_cost = float(packages.get_discounted_price()) * travelers if packages else float(dest.average_budget) * travelers

        recommendations.append({
            'destination': dest,
            'estimated_cost': min(package_cost, float(budget)),
            'fits_budget': float(dest.average_budget) * travelers * (duration / 3) <= float(budget),
            'cheapest_hotel': hotels,
            'best_package': packages,
        })
    return recommendations


def generate_itinerary(destination, duration_days, budget=None):
    """Generate a varied day-wise itinerary for a destination."""
    attractions = list(Attraction.objects.filter(destination=destination, is_active=True))
    hotels = Hotel.objects.filter(destination=destination, is_active=True).first()
    packages = TourPackage.objects.filter(destination=destination, is_active=True).first()

    city = destination.city
    name = destination.name
    climate = destination.climate or 'temperate'
    category_name = destination.category.name.lower() if destination.category else ''

    # ── curated activity pools by destination type (no hardcoded place names) ──
    beach_activities = [
        (f"Visit {name}'s most popular beach and enjoy the sunrise",
         f"Water sports — try parasailing, jet skiing, or snorkeling at {city} beach",
         f"Beachside seafood dinner and evening stroll along the shore"),
        (f"Explore the local fishing village and fresh fish market in {city}",
         f"Sunset boat cruise along the {city} coastline",
         f"Visit beach shacks, enjoy live music and local seafood"),
        (f"Visit nearby secluded beaches and hidden coves around {name}",
         f"Dolphin spotting tour or kayaking trip near {city}",
         f"Bonfire night on the beach with BBQ dinner"),
        (f"Heritage and architecture walk through old {city} town",
         f"Shopping at {city} local markets — spices, cashews, handicrafts",
         f"Local cuisine tasting dinner at a popular restaurant in {city}"),
        (f"Day trip to a nearby island or scenic coastal spot near {name}",
         f"Visit {city} lighthouse and enjoy panoramic coastal views",
         f"Spa and relaxation evening at your resort"),
    ]
    mountain_activities = [
        (f"Arrive in {city} — acclimatize with a short walk around town",
         f"Visit the {city} main market and explore a local monastery",
         f"Bonfire evening at the hotel with mountain views"),
        (f"Sunrise trek to the {name} viewpoint",
         f"Visit a historic temple or cultural heritage site in {city}",
         f"River rafting or zip-lining adventure near {city}"),
        (f"Day trip to a nearby snow point or hill station around {name}",
         f"Snow or nature activities — hiking, photography, or skiing",
         f"Hot beverage and local mountain cuisine dinner in {city}"),
        (f"Visit local orchards, farms, and a nearby village near {city}",
         f"Photography walk through {name} valleys, rivers, and peaks",
         f"Camping or bonfire under the stars near {city}"),
        (f"Explore {city} old town and a Tibetan or Buddhist monastery",
         f"Shopping for woolens, shawls, and local handicrafts in {city}",
         f"Farewell dinner with a mountain view"),
    ]
    heritage_activities = [
        (f"Visit the main fort or palace of {name}",
         f"Explore {city} local bazaar — textiles, jewellery, and spices",
         f"Cultural show or folk dance performance in {city}"),
        (f"Visit the city museum and palace complex of {name}",
         f"Camel or elephant safari / heritage vehicle ride in {city}",
         f"Rooftop dinner overlooking {city} old town"),
        (f"Day trip to a nearby historic monument or stepwell around {name}",
         f"Guided heritage walk through old lanes of {city}",
         f"Try authentic local cuisine at a traditional restaurant in {city}"),
        (f"Visit art galleries and handicraft workshops in {city}",
         f"Explore the most iconic monument of {name}",
         f"Sunset at a nearby lake or garden in {city}"),
        (f"Morning yoga session at your heritage hotel in {city}",
         f"Shopping for souvenirs, gems, and local handicrafts",
         f"Farewell royal dinner in {city}"),
    ]
    spiritual_activities = [
        (f"Arrive in {city} — attend the famous evening aarti ceremony",
         f"Walk along the sacred ghats and explore the old town of {city}",
         f"Spiritual discourse or classical music performance in {city}"),
        (f"Sunrise boat ride on the sacred river at {city}",
         f"Visit the main temples, ashrams, and meditation centers of {name}",
         f"Local street food tour in {city} — chaat, lassi, and sweets"),
        (f"Yoga and meditation session at sunrise in {city}",
         f"Explore the sacred ghats and attend a morning prayer ceremony",
         f"Evening aarti ceremony at the main ghat of {city}"),
        (f"Day trip to a nearby pilgrimage site or ancient temple near {name}",
         f"Explore local workshops — silk weaving, brasswork, or crafts in {city}",
         f"Evening cultural show and dinner in {city}"),
        (f"Final temple darshan and blessing ceremony in {city}",
         f"Shopping for religious items, incense, and local handicrafts",
         f"Farewell dinner at a rooftop restaurant in {city}"),
    ]
    nature_activities = [
        (f"Arrive in {city} — check in and evening nature walk",
         f"Visit a botanical garden, tea garden, or spice plantation near {name}",
         f"Local cuisine dinner in {city}"),
        (f"Houseboat or backwater cruise near {city}",
         f"Village visit and cultural interaction near {name}",
         f"Sunset over the backwaters or valley near {city}"),
        (f"Wildlife safari or bird watching at a sanctuary near {name}",
         f"Jungle or nature trek with a local guide near {city}",
         f"Bonfire and folk music night at the camp"),
        (f"Visit a waterfall and hilltop viewpoint near {name}",
         f"Ayurvedic spa and wellness session in {city}",
         f"Traditional local cuisine dinner in {city}"),
        (f"Tea garden or coffee plantation visit near {name}",
         f"Shopping for local spices, teas, and handicrafts in {city}",
         f"Farewell dinner and evening in {city}"),
    ]
    default_activities = [
        (f"Arrive in {city} — check in, freshen up and explore the neighbourhood",
         f"Visit the main market and key landmarks of {city}",
         f"Dinner at a popular local restaurant in {city}"),
        (f"Morning sightseeing — major monuments and heritage sites of {name}",
         f"Visit a museum or art gallery in {city}",
         f"Evening cultural show or walk in {city}"),
        (f"Day trip to a nearby attraction or scenic spot around {name}",
         f"Photography walk and street food tour in {city}",
         f"Relax at hotel"),
        (f"Local village or nature walk near {city}",
         f"Shopping for local handicrafts and souvenirs in {city}",
         f"Special local cuisine dinner"),
        (f"Final sightseeing around {name}",
         f"Last-minute shopping in {city}",
         f"Farewell dinner and departure preparations"),
    ]

    # Pick the right activity pool based on category then destination name
    n = name.lower()
    if any(w in category_name for w in ['beach', 'coastal', 'sea', 'island']):
        pool = beach_activities
    elif any(w in category_name for w in ['mountain', 'hill', 'adventure', 'trek', 'snow']):
        pool = mountain_activities
    elif any(w in category_name for w in ['heritage', 'culture', 'historic', 'royal', 'fort']):
        pool = heritage_activities
    elif any(w in category_name for w in ['spiritual', 'pilgrimage', 'religious', 'temple', 'devotion']):
        pool = spiritual_activities
    elif any(w in category_name for w in ['nature', 'wildlife', 'forest', 'backwater', 'tea', 'eco']):
        pool = nature_activities
    elif any(w in n for w in ['goa', 'beach', 'puri', 'kovalam', 'varkala', 'andaman']):
        pool = beach_activities
    elif any(w in n for w in ['manali', 'shimla', 'darjeeling', 'mussoorie', 'ooty', 'nainital', 'munnar', 'coorg', 'leh', 'ladakh']):
        pool = mountain_activities
    elif any(w in n for w in ['jaipur', 'agra', 'delhi', 'mysore', 'hampi', 'udaipur', 'jodhpur']):
        pool = heritage_activities
    elif any(w in n for w in ['varanasi', 'rishikesh', 'haridwar', 'tirupati', 'amritsar', 'mathura', 'vrindavan']):
        pool = spiritual_activities
    elif any(w in n for w in ['kerala', 'alleppey', 'kodaikanal', 'wayanad', 'coorg']):
        pool = nature_activities
    else:
        pool = default_activities

    # Build itinerary using real attractions first, then pool
    itinerary = []
    attraction_idx = 0

    for day in range(1, duration_days + 1):
        # Use pool entry for this day (cycle if duration > pool size)
        pool_entry = pool[(day - 1) % len(pool)]
        morning_base, afternoon_base, evening_base = pool_entry

        day_cost = 800  # food & misc base

        # Day 1: always arrival
        if day == 1:
            morning = f"Arrive in {city} — check in at {hotels.name if hotels else 'your hotel'} and freshen up"
            afternoon = afternoon_base
            evening = evening_base
        # Last day: always departure
        elif day == duration_days:
            morning = morning_base
            afternoon = f"Last-minute shopping and packing"
            evening = f"Farewell dinner at a local restaurant and departure from {city}"
        else:
            morning = morning_base
            afternoon = afternoon_base
            evening = evening_base

        # Override morning with a real attraction if available
        if day > 1 and attraction_idx < len(attractions):
            a = attractions[attraction_idx]
            morning = f"Visit {a.name}" + (f" (Entry: ₹{a.entry_fee:.0f})" if float(a.entry_fee) > 0 else " (Free entry)")
            day_cost += float(a.entry_fee)
            attraction_idx += 1

        # Override afternoon with another real attraction if available
        if attraction_idx < len(attractions):
            a = attractions[attraction_idx]
            afternoon = f"Explore {a.name}" + (f" (Entry: ₹{a.entry_fee:.0f})" if float(a.entry_fee) > 0 else " (Free entry)")
            day_cost += float(a.entry_fee)
            attraction_idx += 1

        if hotels:
            day_cost += float(hotels.price_per_night)

        itinerary.append({
            'day': day,
            'morning': morning,
            'afternoon': afternoon,
            'evening': evening,
            'estimated_cost': round(day_cost, 2),
        })

    return itinerary


def calculate_travel_cost(destination, duration_days, travelers, hotel_stars=3):
    """Estimate total travel cost breakdown."""
    hotels = Hotel.objects.filter(
        destination=destination, is_active=True, stars__lte=hotel_stars
    ).order_by('-stars').first()

    hotel_cost = float(hotels.price_per_night) * duration_days * travelers if hotels else float(destination.average_budget) * 0.4 * duration_days

    attractions = Attraction.objects.filter(destination=destination, is_active=True)
    attraction_cost = sum(float(a.entry_fee) for a in attractions) * travelers

    food_cost = 800 * duration_days * travelers
    misc_cost = 500 * duration_days * travelers

    total = hotel_cost + food_cost + attraction_cost + misc_cost
    cost_breakdown = {
        'accommodation': round(hotel_cost, 2),
        'food': round(food_cost, 2),
        'attractions': round(attraction_cost, 2),
        'miscellaneous': round(misc_cost, 2),
        'total': round(total, 2),
        'per_person': round(total / travelers if travelers > 0 else total, 2),
    }
    return cost_breakdown


def get_personalized_recommendations(user, limit=6):
    """Get personalized recommendations based on user history."""
    from booking.models import Booking
    from ai_recommendations.models import RecommendationHistory

    # Get previously visited/booked destinations
    booked_destinations = Destination.objects.filter(
        hotels__bookings__user=user
    ).distinct()

    # Get favorite destinations
    favorite_categories = user.favorites.values_list(
        'destination__category', flat=True
    ).distinct()

    # Recommend similar destinations
    if favorite_categories:
        recommended = Destination.objects.filter(
            category__in=favorite_categories,
            is_active=True
        ).exclude(
            id__in=booked_destinations.values_list('id', flat=True)
        ).order_by('-rating', '-is_featured')[:limit]
    else:
        recommended = Destination.objects.filter(
            is_active=True, is_featured=True
        ).order_by('-rating')[:limit]

    return list(recommended)


def get_nearby_attractions(latitude, longitude, radius_km=10):
    """Get attractions near given coordinates."""
    import math
    attractions = Attraction.objects.filter(
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False
    )
    nearby = []
    for attraction in attractions:
        if attraction.latitude and attraction.longitude:
            lat1, lon1 = float(latitude), float(longitude)
            lat2, lon2 = float(attraction.latitude), float(attraction.longitude)
            R = 6371
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            distance = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            if distance <= radius_km:
                nearby.append({'attraction': attraction, 'distance': round(distance, 2)})
    nearby.sort(key=lambda x: x['distance'])
    return nearby[:10]


def get_weather_info(city):
    """Fetch current weather using Open-Meteo (free, no API key required).
    Steps: geocode city name → fetch weather from Open-Meteo."""
    import requests

    try:
        # Step 1: Geocode city name to coordinates using Open-Meteo geocoding API
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url, timeout=10)
        geo_data = geo_resp.json()

        if not geo_data.get('results'):
            return {'error': f'City "{city}" not found. Please check the spelling and try again.', 'city': city}

        result = geo_data['results'][0]
        lat = result['latitude']
        lon = result['longitude']
        city_name = result['name']
        country = result.get('country', '')
        timezone = result.get('timezone', 'auto')

        # Step 2: Fetch current weather from Open-Meteo
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
            f"wind_speed_10m,weather_code,visibility"
            f"&timezone={timezone}"
        )
        w_resp = requests.get(weather_url, timeout=10)
        w_data = w_resp.json()

        current = w_data.get('current', {})

        # Map WMO weather code to description and icon
        wmo_code = current.get('weather_code', 0)
        description, icon = _wmo_to_description(wmo_code)

        visibility_m = current.get('visibility', 0)
        visibility_km = round(visibility_m / 1000, 1) if visibility_m else 0

        return {
            'city': city_name,
            'country': country,
            'temperature': current.get('temperature_2m', 0),
            'feels_like': current.get('apparent_temperature', 0),
            'humidity': current.get('relative_humidity_2m', 0),
            'description': description,
            'icon': icon,
            'wind_speed': round(current.get('wind_speed_10m', 0) / 3.6, 1),  # km/h → m/s
            'visibility': visibility_km,
        }

    except Exception as e:
        return {'error': f'Weather service unavailable: {str(e)}', 'city': city}


def _wmo_to_description(code):
    """Convert WMO weather code to human-readable description and an OWM-style icon code."""
    wmo_map = {
        0:  ('Clear Sky', '01d'),
        1:  ('Mainly Clear', '01d'),
        2:  ('Partly Cloudy', '02d'),
        3:  ('Overcast', '04d'),
        45: ('Foggy', '50d'),
        48: ('Icy Fog', '50d'),
        51: ('Light Drizzle', '09d'),
        53: ('Moderate Drizzle', '09d'),
        55: ('Dense Drizzle', '09d'),
        61: ('Slight Rain', '10d'),
        63: ('Moderate Rain', '10d'),
        65: ('Heavy Rain', '10d'),
        71: ('Slight Snow', '13d'),
        73: ('Moderate Snow', '13d'),
        75: ('Heavy Snow', '13d'),
        77: ('Snow Grains', '13d'),
        80: ('Slight Showers', '09d'),
        81: ('Moderate Showers', '09d'),
        82: ('Violent Showers', '09d'),
        85: ('Snow Showers', '13d'),
        86: ('Heavy Snow Showers', '13d'),
        95: ('Thunderstorm', '11d'),
        96: ('Thunderstorm with Hail', '11d'),
        99: ('Thunderstorm with Heavy Hail', '11d'),
    }
    return wmo_map.get(code, ('Unknown', '01d'))


def chat_with_ai(user_message, chat_history=None, user_context=None):
    """Chat with AI travel assistant.
    Priority: Gemini → OpenAI → rule-based fallback."""
    gemini_key = getattr(settings, 'GEMINI_API_KEY', '')
    openai_key = getattr(settings, 'OPENAI_API_KEY', '')

    if gemini_key and gemini_key != 'your_gemini_api_key_here':
        return _gemini_chat(user_message, chat_history, user_context)
    if openai_key and openai_key != 'your_openai_api_key_here':
        return _openai_chat(user_message, chat_history, user_context)
    return _rule_based_chat(user_message, user_context)


def _build_system_prompt():
    """Build a rich system prompt with live destination data from the database."""
    destinations = Destination.objects.filter(is_active=True).values(
        'name', 'city', 'country', 'average_budget', 'rating', 'best_time_to_visit', 'climate'
    )
    dest_info = "\n".join([
        f"- {d['name']} ({d['city']}, {d['country']}): avg budget ₹{d['average_budget']}, "
        f"rating {d['rating']}/5, best time: {d['best_time_to_visit'] or 'all year'}, climate: {d['climate']}"
        for d in destinations
    ])

    return f"""You are an expert AI Travel Assistant for 'AI Travel Planner', an Indian travel platform.

You help users with:
- Destination recommendations across India and the world
- Day-wise trip itinerary planning
- Budget estimation and cost breakdowns
- Hotel, transport, and package suggestions
- Weather and best time to visit advice
- General travel tips, visa info, packing lists, safety tips

Our available destinations and their details:
{dest_info}

Guidelines:
- Always be friendly, helpful, and conversational like a knowledgeable travel expert
- Give specific, actionable advice — real place names, estimated costs in Indian Rupees (₹)
- For Indian destinations, include cultural tips, local food recommendations, and transport options
- Format responses clearly with line breaks, bullet points, and emojis where appropriate
- If asked about budget, always give a rough cost breakdown (accommodation, food, transport, activities)
- If asked for itinerary, give a proper day-by-day plan
- Keep responses concise but complete — not too long, not too short
- You can answer ANY travel-related question, not just about our listed destinations
"""


def _gemini_chat(user_message, chat_history=None, user_context=None):
    """Use Google Gemini for intelligent travel chat (new google-genai SDK)."""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        system_prompt = _build_system_prompt()

        # Build conversation contents
        contents = []
        if chat_history:
            for msg in chat_history[-10:]:
                role = 'user' if msg['role'] == 'user' else 'model'
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part(text=msg['content'])]
                ))
        contents.append(types.Content(
            role='user',
            parts=[types.Part(text=user_message)]
        ))

        # Try models in order of availability
        for model_name in ['models/gemini-3.1-flash-lite', 'models/gemini-3.1-flash-image', 'models/gemini-flash-latest']:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.7,
                        max_output_tokens=800,
                    )
                )
                return response.text
            except Exception as model_err:
                if '429' in str(model_err) or 'RESOURCE_EXHAUSTED' in str(model_err):
                    continue  # try next model
                raise  # re-raise other errors

        # All models exhausted quota
        return "⚠️ Gemini API quota reached for today. Using built-in responses.\n\n" + _rule_based_chat(user_message)

    except Exception as e:
        error_msg = str(e)
        if 'API_KEY_INVALID' in error_msg or 'invalid' in error_msg.lower():
            return "⚠️ Gemini API key is invalid. Please check GEMINI_API_KEY in .env.\n\n" + _rule_based_chat(user_message)
        if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
            return "⚠️ Gemini API daily quota reached. Using built-in responses.\n\n" + _rule_based_chat(user_message)
        return _rule_based_chat(user_message)


def _openai_chat(user_message, chat_history=None, user_context=None):
    """Use OpenAI GPT for intelligent chat (fallback if no Gemini key)."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        messages = [{"role": "system", "content": _build_system_prompt()}]
        if chat_history:
            for msg in chat_history[-10:]:
                messages.append({"role": msg['role'], "content": msg['content']})
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=600,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return _rule_based_chat(user_message)


def _rule_based_chat(message, user_context=None):
    """Smart rule-based AI chat — extracts destination, duration, and budget from the message."""
    import re
    message_lower = message.lower()

    # ── helpers ──────────────────────────────────────────────────────────────

    def extract_destination(text):
        """Return a Destination object if any destination name is mentioned."""
        all_dests = Destination.objects.filter(is_active=True)
        for dest in all_dests:
            if dest.name.lower() in text or dest.city.lower() in text:
                return dest
        return None

    def extract_days(text):
        """Return number of days mentioned (e.g. '5 days', '3-day')."""
        match = re.search(r'(\d+)\s*[-\s]?\s*day', text)
        if match:
            return int(match.group(1))
        return None

    def extract_budget(text):
        """Return budget amount mentioned (handles ₹30,000 / 30000 / 30k)."""
        # ₹30,000 or 30,000 or 30000
        match = re.search(r'[₹rs\.]*\s*(\d[\d,]+)', text.replace(' ', ''))
        if match:
            val = int(match.group(1).replace(',', ''))
            return val
        # 30k / 50k
        match = re.search(r'(\d+)\s*k', text)
        if match:
            return int(match.group(1)) * 1000
        return None

    # ── greetings ─────────────────────────────────────────────────────────────
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'help', 'start']):
        return (
            "Hello! 👋 I'm your AI Travel Assistant 🌍\n\n"
            "I can help you with:\n"
            "• 🗺️ Destination recommendations\n"
            "• 💰 Budget estimation for any destination\n"
            "• 📅 Day-wise itinerary planning\n"
            "• 🏨 Hotel & transport suggestions\n"
            "• ☁️ Weather information\n\n"
            "Try asking me: *'Budget for Goa for 5 days'* or *'Best beach destinations under ₹30,000'*"
        )

    # ── extract key info from message ─────────────────────────────────────────
    dest = extract_destination(message_lower)
    days = extract_days(message_lower)
    budget = extract_budget(message_lower)

    # ── budget/cost for a specific destination ────────────────────────────────
    if dest and any(word in message_lower for word in ['budget', 'cost', 'price', 'how much', 'expensive', 'cheap', 'afford', 'spend', 'know']):
        duration = days or 3
        travelers = 1
        cost = calculate_travel_cost(dest, duration, travelers)
        lines = [
            f"💰 Estimated cost for {dest.name} ({duration} days, {travelers} person):\n",
            f"🏨 Accommodation: ₹{cost['accommodation']:,.0f}",
            f"🍽️ Food & Dining: ₹{cost['food']:,.0f}",
            f"🎯 Attractions: ₹{cost['attractions']:,.0f}",
            f"🛍️ Miscellaneous: ₹{cost['miscellaneous']:,.0f}",
            f"━━━━━━━━━━━━━━━━━━",
            f"💵 Total: ₹{cost['total']:,.0f}",
            f"👤 Per person: ₹{cost['per_person']:,.0f}",
        ]
        if dest.best_time_to_visit:
            lines.append(f"\n📅 Best time to visit: {dest.best_time_to_visit}")
        lines.append(f"\nWant a detailed day-by-day itinerary for {dest.name}? Just ask!")
        return "\n".join(lines)

    # ── itinerary for a specific destination ──────────────────────────────────
    if dest and any(word in message_lower for word in ['itinerary', 'plan', 'trip', 'visit', 'day', 'schedule', 'tour']):
        duration = days or 3
        itinerary = generate_itinerary(dest, duration)
        cost = calculate_travel_cost(dest, duration, 1)
        lines = [f"📅 {duration}-Day Itinerary for {dest.name}\n"]
        for day in itinerary:
            lines.append(f"🗓️ Day {day['day']}:")
            if day['morning']:
                lines.append(f"  🌅 Morning: {day['morning']}")
            if day['afternoon']:
                lines.append(f"  ☀️ Afternoon: {day['afternoon']}")
            if day['evening']:
                lines.append(f"  🌙 Evening: {day['evening']}")
            lines.append(f"  💸 Est. daily cost: ₹{day['estimated_cost']:,.0f}\n")
        lines.append(f"💰 Total estimated cost: ₹{cost['total']:,.0f}")
        if dest.best_time_to_visit:
            lines.append(f"📅 Best time to visit: {dest.best_time_to_visit}")
        return "\n".join(lines)

    # ── best time to visit a specific destination ─────────────────────────────
    if dest and any(word in message_lower for word in ['best time', 'when to visit', 'season', 'when should', 'month']):
        btv = dest.best_time_to_visit or "October to March (pleasant weather)"
        climate_tips = {
            'tropical': "🌴 Tropical climate — avoid monsoon (Jun–Sep). Best Nov–Feb.",
            'temperate': "🌤️ Temperate climate — Spring (Mar–May) and Autumn (Sep–Nov) are ideal.",
            'arid': "🌵 Arid/Desert climate — visit Oct–Feb to avoid extreme heat.",
            'continental': "❄️ Continental climate — Summer (May–Aug) is best for sightseeing.",
        }
        tip = climate_tips.get(dest.climate, "")
        return (
            f"📅 Best time to visit {dest.name}:\n\n"
            f"✅ {btv}\n\n"
            f"{tip}\n\n"
            f"🌡️ Climate type: {dest.get_climate_display() if hasattr(dest, 'get_climate_display') else dest.climate.title()}\n"
            f"💰 Average budget: ₹{dest.average_budget:,.0f} per person\n\n"
            f"Want me to plan a trip itinerary or estimate costs for {dest.name}?"
        )

    # ── hotels for a specific destination ─────────────────────────────────────
    if dest and any(word in message_lower for word in ['hotel', 'stay', 'accommodation', 'resort', 'lodge']):
        hotels = Hotel.objects.filter(destination=dest, is_active=True).order_by('price_per_night')[:4]
        if hotels:
            lines = [f"🏨 Hotels in {dest.name}:\n"]
            for h in hotels:
                lines.append(f"⭐ {h.stars}★ {h.name} — ₹{h.price_per_night:,.0f}/night")
            lines.append(f"\nWant to book one? Visit the Hotels section or ask me for an itinerary!")
            return "\n".join(lines)
        return f"No hotels listed for {dest.name} yet. Check our Hotels section for options!"

    # ── weather for a specific destination ────────────────────────────────────
    if dest and any(word in message_lower for word in ['weather', 'climate', 'temperature', 'rain', 'snow', 'hot', 'cold']):
        weather = get_weather_info(dest.city)
        if 'error' not in weather:
            return (
                f"☁️ Current weather in {dest.city}:\n\n"
                f"🌡️ Temperature: {weather['temperature']}°C (feels like {weather['feels_like']}°C)\n"
                f"🌤️ Condition: {weather['description']}\n"
                f"💧 Humidity: {weather['humidity']}%\n"
                f"💨 Wind: {weather['wind_speed']} m/s\n\n"
                f"📅 Best time to visit: {dest.best_time_to_visit or 'October to March'}"
            )
        return f"For {dest.name}, the best time to visit is: {dest.best_time_to_visit or 'October to March (cool and dry)'}."

    # ── budget-filtered recommendations ───────────────────────────────────────
    if budget and any(word in message_lower for word in ['beach', 'mountain', 'hill', 'heritage', 'adventure', 'destination', 'recommend', 'suggest', 'under', 'within', 'less than']):
        climate_filter = None
        if any(w in message_lower for w in ['beach', 'coastal', 'sea', 'goa', 'kerala']):
            climate_filter = 'tropical'
        elif any(w in message_lower for w in ['hill', 'mountain', 'manali', 'darjeeling']):
            climate_filter = 'temperate'

        qs = Destination.objects.filter(is_active=True, average_budget__lte=budget)
        if climate_filter:
            qs = qs.filter(climate=climate_filter)
        dests = qs.order_by('-rating')[:4]

        if dests:
            lines = [f"🗺️ Top destinations under ₹{budget:,}:\n"]
            for d in dests:
                lines.append(f"📍 {d.name} — avg ₹{d.average_budget:,.0f}/person | ⭐ {d.rating}")
            lines.append(f"\nWant a detailed itinerary or cost breakdown for any of these?")
            return "\n".join(lines)
        return f"No destinations found under ₹{budget:,}. Try increasing your budget a bit!"

    # ── general budget travel (no specific destination) ────────────────────────
    if any(word in message_lower for word in ['cheap', 'affordable', 'budget', 'low cost']):
        dests = Destination.objects.filter(is_active=True).order_by('average_budget')[:4]
        if dests:
            lines = ["💰 Most affordable destinations:\n"]
            for d in dests:
                lines.append(f"📍 {d.name} — avg ₹{d.average_budget:,.0f}/person | ⭐ {d.rating}")
            lines.append("\nTell me your budget and I'll find the perfect match!")
            return "\n".join(lines)

    # ── general destination recommendations ───────────────────────────────────
    if any(word in message_lower for word in ['recommend', 'suggest', 'where', 'destination', 'popular', 'top', 'best place']):
        dests = Destination.objects.filter(is_active=True, is_featured=True).order_by('-rating')[:4]
        if dests:
            lines = ["🌟 Top recommended destinations:\n"]
            for d in dests:
                lines.append(f"📍 {d.name}, {d.country} — ⭐ {d.rating} | Avg ₹{d.average_budget:,.0f}")
            lines.append("\nShare your preferences (beach/mountain/heritage/adventure) for personalized suggestions!")
            return "\n".join(lines)

    # ── general weather question ───────────────────────────────────────────────
    if any(word in message_lower for word in ['weather', 'climate', 'temperature']):
        return "☁️ I can check live weather for any destination! Just mention the city — e.g. 'Weather in Manali' or 'How is the weather in Goa?'"

    # ── general hotel question ─────────────────────────────────────────────────
    if any(word in message_lower for word in ['hotel', 'accommodation', 'stay', 'resort']):
        return "🏨 I can suggest hotels! Which destination are you planning to visit? E.g. 'Hotels in Jaipur' or 'Stay options in Manali'."

    # ── general itinerary question ─────────────────────────────────────────────
    if any(word in message_lower for word in ['itinerary', 'plan', 'schedule', 'days']):
        return "📅 I'd love to plan your trip! Just tell me the destination and number of days — e.g. '5 day itinerary for Goa' or 'Plan a trip to Manali for 3 days'."

    # ── default ───────────────────────────────────────────────────────────────
    all_dests = list(Destination.objects.filter(is_active=True).values_list('name', flat=True)[:6])
    dest_list = ', '.join(all_dests) if all_dests else 'Goa, Manali, Jaipur, Kerala'
    return (
        f"I can help you plan your perfect trip! 🌍\n\n"
        f"Try asking me:\n"
        f"• 'Budget for Goa for 5 days'\n"
        f"• '3 day itinerary for Manali'\n"
        f"• 'Best time to visit Kerala'\n"
        f"• 'Beach destinations under ₹30,000'\n"
        f"• 'Hotels in Jaipur'\n\n"
        f"Available destinations: {dest_list}"
    )
