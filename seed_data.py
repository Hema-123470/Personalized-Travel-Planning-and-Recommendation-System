"""
Seed script to populate the database with sample data.
Run: python seed_data.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_project.settings')
django.setup()

from travel.models import Category, Destination, Hotel, Attraction, Transport, TourPackage
from decimal import Decimal

print("Seeding database...")

# ─── Categories ────────────────────────────────────────────────────────────────
cats_data = [
    ('Beach', 'fas fa-umbrella-beach'),
    ('Mountains', 'fas fa-mountain'),
    ('Heritage & Culture', 'fas fa-landmark'),
    ('Adventure', 'fas fa-hiking'),
    ('Wildlife', 'fas fa-paw'),
    ('Spiritual', 'fas fa-pray'),
    ('Hill Stations', 'fas fa-cloud'),
    ('City Tours', 'fas fa-city'),
]
cat_objs = {}
for name, icon in cats_data:
    c, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon, 'is_active': True})
    cat_objs[name] = c
print(f"  Categories: {Category.objects.count()}")

# ─── Destinations ──────────────────────────────────────────────────────────────
destinations_data = [
    dict(name='Goa', country='India', state='Goa', city='Panaji',
         cat='Beach',
         description='Goa is India smallest state and a top tourist destination known for its stunning beaches, vibrant nightlife, Portuguese heritage, and delicious seafood. With golden sands and crystal-clear waters, Goa is perfect for every traveler.',
         short_description='India beach paradise with golden sands and vibrant nightlife.',
         climate='tropical', best_time_to_visit='November to February',
         average_budget=15000, latitude=15.2993, longitude=74.1240,
         is_featured=True, rating=4.7),
    dict(name='Manali', country='India', state='Himachal Pradesh', city='Manali',
         cat='Mountains',
         description='Manali is a high-altitude Himalayan resort town in Himachal Pradesh. It is a gateway to trekking in the Pir Panjal and the Kullu Valley, perfect for adventure sports and snow activities.',
         short_description='Himalayan adventure hub with snow-capped peaks and scenic valleys.',
         climate='continental', best_time_to_visit='October to June',
         average_budget=12000, latitude=32.2396, longitude=77.1887,
         is_featured=True, rating=4.8),
    dict(name='Jaipur', country='India', state='Rajasthan', city='Jaipur',
         cat='Heritage & Culture',
         description='Known as the Pink City, Jaipur is the capital of Rajasthan and is famous for its palaces, forts, and vibrant culture. The city is a treasure trove of history, arts, and crafts.',
         short_description='The Pink City famous for royal palaces, forts and Rajasthani culture.',
         climate='arid', best_time_to_visit='October to March',
         average_budget=10000, latitude=26.9124, longitude=75.7873,
         is_featured=True, rating=4.6),
    dict(name='Kerala Backwaters', country='India', state='Kerala', city='Alleppey',
         cat='Wildlife',
         description='Kerala Backwaters is a network of interconnected canals, rivers and lakes. A houseboat cruise through the backwaters is one of the most relaxing experiences in India.',
         short_description='Serene backwaters with houseboat cruises through lush green landscapes.',
         climate='tropical', best_time_to_visit='September to March',
         average_budget=18000, latitude=9.4981, longitude=76.3388,
         is_featured=True, rating=4.9),
    dict(name='Agra', country='India', state='Uttar Pradesh', city='Agra',
         cat='Heritage & Culture',
         description='Agra is home to the iconic Taj Mahal, one of the Seven Wonders of the World. The city also boasts Agra Fort and Fatehpur Sikri, both UNESCO World Heritage Sites.',
         short_description='Home to the iconic Taj Mahal and magnificent Mughal architecture.',
         climate='temperate', best_time_to_visit='October to March',
         average_budget=8000, latitude=27.1767, longitude=78.0081,
         is_featured=True, rating=4.5),
    dict(name='Darjeeling', country='India', state='West Bengal', city='Darjeeling',
         cat='Hill Stations',
         description='Darjeeling is a hill station in the Himalayas, famous for its tea plantations, view of Kangchenjunga, and the Darjeeling Himalayan Railway, a UNESCO World Heritage Site.',
         short_description='Famous hill station known for tea gardens and Himalayan views.',
         climate='temperate', best_time_to_visit='March to May, September to November',
         average_budget=9000, latitude=27.0360, longitude=88.2627,
         is_featured=False, rating=4.6),
    dict(name='Rishikesh', country='India', state='Uttarakhand', city='Rishikesh',
         cat='Adventure',
         description='Rishikesh is known as the Yoga Capital of the World and a hub for adventure sports like white-water rafting, bungee jumping, and camping by the banks of the Ganges River.',
         short_description='Yoga capital of the world and adventure sports hub on the Ganges.',
         climate='temperate', best_time_to_visit='September to June',
         average_budget=7000, latitude=30.0869, longitude=78.2676,
         is_featured=False, rating=4.7),
    dict(name='Varanasi', country='India', state='Uttar Pradesh', city='Varanasi',
         cat='Spiritual',
         description='Varanasi, also known as Kashi, is one of the oldest living cities in the world and the spiritual capital of India. The Ganges ghats, aarti ceremonies and ancient temples make it a deeply spiritual experience.',
         short_description='Ancient spiritual city on the Ganges with iconic ghats and temples.',
         climate='temperate', best_time_to_visit='October to March',
         average_budget=6000, latitude=25.3176, longitude=82.9739,
         is_featured=False, rating=4.6),
]

dest_objs = {}
for d in destinations_data:
    cat_key = d.pop('cat')
    if not Destination.objects.filter(name=d['name']).exists():
        obj = Destination.objects.create(category=cat_objs.get(cat_key), **d)
    else:
        obj = Destination.objects.get(name=d['name'])
    dest_objs[d['name']] = obj
print(f"  Destinations: {Destination.objects.count()}")

# ─── Hotels ────────────────────────────────────────────────────────────────────
hotels_data = [
    dict(destination='Goa', name='Taj Holiday Village Resort', stars=5,
         description='A luxurious 5-star resort on Candolim Beach with world-class amenities.',
         address='Sinquerim, Bardez, Goa 403515', phone='+91-832-6683000',
         price_per_night=15000, amenities='WiFi,Pool,Spa,Restaurant,Beach Access,Gym',
         is_featured=True, rating=4.8, total_rooms=142, available_rooms=50),
    dict(destination='Goa', name='Hotel Baga Beach Resort', stars=3,
         description='Budget-friendly hotel near the famous Baga Beach with modern amenities.',
         address='Baga Road, Calangute, Goa 403516', phone='+91-832-2277777',
         price_per_night=3500, amenities='WiFi,Pool,Restaurant,Bar',
         is_featured=False, rating=4.0, total_rooms=45, available_rooms=20),
    dict(destination='Manali', name='Span Resort & Spa', stars=5,
         description='Luxury resort on the banks of Beas River with mountain views.',
         address='NH-21, Kullu-Manali Highway, Himachal Pradesh 175131',
         phone='+91-1902-250881', price_per_night=12000,
         amenities='WiFi,Spa,Restaurant,River View,Bonfire,Trekking',
         is_featured=True, rating=4.7, total_rooms=80, available_rooms=30),
    dict(destination='Jaipur', name='Rambagh Palace Hotel', stars=5,
         description='A former royal palace turned luxury hotel, offering a royal Rajasthani experience.',
         address='Bhawani Singh Rd, Rambagh, Jaipur 302005', phone='+91-141-2211919',
         price_per_night=20000, amenities='WiFi,Pool,Spa,Restaurant,Heritage Tour,Gardens',
         is_featured=True, rating=4.9, total_rooms=78, available_rooms=15),
    dict(destination='Agra', name='The Oberoi Amarvilas', stars=5,
         description='Every room in this luxury hotel has a view of the Taj Mahal.',
         address='Taj East Gate Road, Agra 282001', phone='+91-562-2231515',
         price_per_night=25000, amenities='WiFi,Pool,Spa,Restaurant,Taj View,Butler',
         is_featured=True, rating=4.9, total_rooms=102, available_rooms=20),
    dict(destination='Kerala Backwaters', name='Punnamada Lake Resort', stars=4,
         description='Beautiful resort on Punnamada Lake with traditional Kerala architecture.',
         address='Punnamada Lake, Alleppey 688006', phone='+91-477-2232900',
         price_per_night=8000, amenities='WiFi,Pool,Restaurant,Houseboat,Ayurveda',
         is_featured=True, rating=4.6, total_rooms=60, available_rooms=25),
]

for h in hotels_data:
    dest_name = h.pop('destination')
    dest = dest_objs.get(dest_name)
    if dest and not Hotel.objects.filter(name=h['name']).exists():
        Hotel.objects.create(destination=dest, is_active=True, **h)
print(f"  Hotels: {Hotel.objects.count()}")

# ─── Attractions ───────────────────────────────────────────────────────────────
attractions_data = [
    dict(destination='Goa', name='Baga Beach', attraction_type='beach',
         description='One of the most popular beaches in Goa, famous for water sports, shacks, and nightlife.',
         entry_fee=0, opening_hours='Open 24 hours', rating=4.5),
    dict(destination='Goa', name='Basilica of Bom Jesus', attraction_type='temple',
         description='A UNESCO World Heritage Site and one of the finest examples of Baroque architecture in India.',
         entry_fee=0, opening_hours='9:00 AM - 6:30 PM', rating=4.7),
    dict(destination='Manali', name='Rohtang Pass', attraction_type='mountain',
         description='A high mountain pass on the eastern Pir Panjal Range offering spectacular views of glaciers.',
         entry_fee=500, opening_hours='Open seasonally May-Nov', rating=4.8),
    dict(destination='Manali', name='Hadimba Temple', attraction_type='temple',
         description='An ancient cave temple dedicated to Hadimba Devi surrounded by cedar forest.',
         entry_fee=0, opening_hours='8:00 AM - 6:00 PM', rating=4.6),
    dict(destination='Jaipur', name='Hawa Mahal', attraction_type='monument',
         description='The Palace of Winds is a stunning 5-floor palace with 953 small windows decorated with intricate latticework.',
         entry_fee=50, opening_hours='9:30 AM - 5:00 PM', rating=4.6),
    dict(destination='Jaipur', name='Amber Fort', attraction_type='monument',
         description='A magnificent fort-palace complex built in 1592 by Raja Man Singh I, known for its artistic style.',
         entry_fee=200, opening_hours='8:00 AM - 5:30 PM', rating=4.8),
    dict(destination='Agra', name='Taj Mahal', attraction_type='monument',
         description='The iconic white marble mausoleum built by Mughal Emperor Shah Jahan in memory of his wife Mumtaz Mahal. UNESCO World Heritage Site.',
         entry_fee=1100, opening_hours='6:00 AM - 6:30 PM (Closed Friday)', rating=5.0,
         latitude=27.1751, longitude=78.0421),
    dict(destination='Agra', name='Agra Fort', attraction_type='monument',
         description='A UNESCO World Heritage Site, this massive red sandstone fort served as the main residence of Mughal emperors.',
         entry_fee=650, opening_hours='6:00 AM - 6:00 PM', rating=4.5),
    dict(destination='Kerala Backwaters', name='Alleppey Backwaters Cruise', attraction_type='other',
         description='A houseboat cruise through the peaceful backwaters of Kerala, surrounded by lush paddy fields and coconut palms.',
         entry_fee=3000, opening_hours='6:00 AM - 6:00 PM', rating=4.9),
    dict(destination='Rishikesh', name='River Rafting on Ganges', attraction_type='entertainment',
         description='Thrilling white-water rafting experience on the holy Ganges River with rapids of varying difficulty.',
         entry_fee=600, opening_hours='8:00 AM - 4:00 PM', rating=4.8),
]

for a in attractions_data:
    dest_name = a.pop('destination')
    dest = dest_objs.get(dest_name)
    if dest and not Attraction.objects.filter(name=a['name']).exists():
        Attraction.objects.create(destination=dest, is_active=True, **a)
print(f"  Attractions: {Attraction.objects.count()}")

# ─── Transport ─────────────────────────────────────────────────────────────────
transports_data = [
    dict(destination='Goa', transport_type='flight', name='Mumbai to Goa Flight',
         from_location='Mumbai (BOM)', to_location='Goa (GOI)',
         duration='1 hour 10 mins', price=3500),
    dict(destination='Goa', transport_type='bus', name='Mumbai to Goa Volvo Bus',
         from_location='Mumbai', to_location='Panaji, Goa',
         duration='10-12 hours', price=800),
    dict(destination='Manali', transport_type='bus', name='Delhi to Manali HRTC Bus',
         from_location='Delhi ISBT', to_location='Manali Bus Stand',
         duration='14-16 hours', price=1200),
    dict(destination='Jaipur', transport_type='train', name='Delhi to Jaipur Express',
         from_location='New Delhi Railway Station', to_location='Jaipur Junction',
         duration='4 hours 30 mins', price=450),
    dict(destination='Agra', transport_type='train', name='Gatimaan Express',
         from_location='Hazrat Nizamuddin, Delhi', to_location='Agra Cantt',
         duration='1 hour 40 mins', price=755),
    dict(destination='Kerala Backwaters', transport_type='flight', name='Delhi to Cochin Flight',
         from_location='Delhi (DEL)', to_location='Cochin (COK)',
         duration='3 hours', price=5500),
]

for t in transports_data:
    dest_name = t.pop('destination')
    dest = dest_objs.get(dest_name)
    if dest and not Transport.objects.filter(name=t['name']).exists():
        Transport.objects.create(destination=dest, is_active=True, **t)
print(f"  Transport options: {Transport.objects.count()}")

# ─── Tour Packages ─────────────────────────────────────────────────────────────
packages_data = [
    dict(destination='Goa', name='Goa Beach & Nightlife Package', duration_days=4,
         description='Enjoy 4 days of sun, sand and surf in Goa. Includes beach tours, water sports, and vibrant nightlife experience.',
         price_per_person=12000, discount_percent=10, max_group_size=15,
         includes='Hotel (3 nights), Breakfast, Water sports, City tour, Airport transfers',
         excludes='Flights, Lunch, Dinner, Personal expenses',
         itinerary='Day 1: Arrival, check-in, evening at Baga Beach\nDay 2: North Goa beaches - Calangute, Anjuna\nDay 3: South Goa - Palolem, Old Goa churches\nDay 4: Water sports, shopping, departure',
         difficulty='easy', is_featured=True, rating=4.7),
    dict(destination='Manali', name='Manali Snow Adventure Package', duration_days=5,
         description='Experience the snow-capped Himalayas with adventure activities like skiing, snow trek, and paragliding in Manali.',
         price_per_person=18000, discount_percent=5, max_group_size=12,
         includes='Hotel (4 nights), Breakfast, Rohtang Pass visit, Skiing, Guide',
         excludes='Flights, Dinner, Personal expenses, Entry tickets',
         itinerary='Day 1: Arrival Manali, check-in\nDay 2: Solang Valley, snow activities\nDay 3: Rohtang Pass excursion\nDay 4: Old Manali, Hadimba Temple\nDay 5: Departure',
         difficulty='moderate', is_featured=True, rating=4.8),
    dict(destination='Jaipur', name='Royal Rajasthan Heritage Tour', duration_days=3,
         description='Explore the royal heritage of Jaipur with visits to magnificent forts, palaces and experience authentic Rajasthani culture.',
         price_per_person=9000, discount_percent=0, max_group_size=20,
         includes='Hotel (2 nights), Breakfast, Guide, Fort entries, Cultural show',
         excludes='Flights, Lunch, Dinner, Shopping',
         itinerary='Day 1: City Palace, Jantar Mantar, Hawa Mahal\nDay 2: Amber Fort, Jal Mahal, bazaar shopping\nDay 3: Nahargarh Fort, departure',
         difficulty='easy', is_featured=True, rating=4.6),
    dict(destination='Agra', name='Taj Mahal Golden Triangle Tour', duration_days=2,
         description='A focused tour of Agra to experience the magnificent Taj Mahal and other Mughal era monuments.',
         price_per_person=6500, discount_percent=0, max_group_size=25,
         includes='Hotel (1 night), Breakfast, Taj Mahal sunrise visit, Agra Fort, Guide',
         excludes='Flights/Train, Lunch, Dinner',
         itinerary='Day 1: Arrive Agra, Taj Mahal (evening view), Agra Fort\nDay 2: Taj Mahal sunrise, Fatehpur Sikri, departure',
         difficulty='easy', is_featured=True, rating=4.7),
    dict(destination='Kerala Backwaters', name='Kerala Houseboat Backwater Package', duration_days=3,
         description='Cruise through the enchanting backwaters of Kerala on a traditional houseboat and experience authentic village life.',
         price_per_person=14000, discount_percent=8, max_group_size=8,
         includes='Houseboat (1 night), Hotel (1 night), All meals on houseboat, Transfers',
         excludes='Flights, Lunch/Dinner at hotel, Ayurveda treatments',
         itinerary='Day 1: Arrive Alleppey, houseboat check-in, afternoon cruise\nDay 2: Morning cruise, village walk, hotel transfer\nDay 3: Departure',
         difficulty='easy', is_featured=True, rating=4.9),
]

for p in packages_data:
    dest_name = p.pop('destination')
    dest = dest_objs.get(dest_name)
    if dest and not TourPackage.objects.filter(name=p['name']).exists():
        TourPackage.objects.create(destination=dest, is_active=True, **p)
print(f"  Tour packages: {TourPackage.objects.count()}")

print("\nSeed data loaded successfully!")
print("\nLogin credentials:")
print("  Admin:    username=admin    password=Admin@1234")
print("  App URL:  http://127.0.0.1:8000/")
