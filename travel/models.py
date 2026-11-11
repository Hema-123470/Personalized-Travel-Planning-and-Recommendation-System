from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-tag', help_text='Font Awesome icon class')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Destination(models.Model):
    CLIMATE_CHOICES = [
        ('tropical', 'Tropical'),
        ('temperate', 'Temperate'),
        ('arid', 'Arid'),
        ('continental', 'Continental'),
        ('polar', 'Polar'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='destinations')
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='destinations/')
    gallery_image1 = models.ImageField(upload_to='destinations/gallery/', blank=True, null=True)
    gallery_image2 = models.ImageField(upload_to='destinations/gallery/', blank=True, null=True)
    gallery_image3 = models.ImageField(upload_to='destinations/gallery/', blank=True, null=True)
    climate = models.CharField(max_length=20, choices=CLIMATE_CHOICES, default='temperate')
    best_time_to_visit = models.CharField(max_length=200, blank=True)
    average_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    total_reviews = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'destinations'
        ordering = ['-is_featured', '-rating']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.country}"


class Attraction(models.Model):
    ATTRACTION_TYPE = [
        ('museum', 'Museum'),
        ('beach', 'Beach'),
        ('mountain', 'Mountain'),
        ('temple', 'Temple/Religious'),
        ('park', 'National Park'),
        ('monument', 'Monument/Historical'),
        ('shopping', 'Shopping'),
        ('entertainment', 'Entertainment'),
        ('restaurant', 'Restaurant'),
        ('other', 'Other'),
    ]
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='attractions')
    name = models.CharField(max_length=200)
    attraction_type = models.CharField(max_length=20, choices=ATTRACTION_TYPE, default='other')
    description = models.TextField()
    image = models.ImageField(upload_to='attractions/', blank=True, null=True)
    entry_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    opening_hours = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attractions'
        ordering = ['-rating']

    def __str__(self):
        return f"{self.name} - {self.destination.name}"


class Hotel(models.Model):
    STAR_CHOICES = [(i, f'{i} Star') for i in range(1, 6)]
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='hotels')
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='hotels/')
    stars = models.IntegerField(choices=STAR_CHOICES, default=3)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.TextField(blank=True, help_text='Comma separated amenities')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    total_rooms = models.IntegerField(default=10)
    available_rooms = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hotels'
        ordering = ['-stars', '-rating']

    def __str__(self):
        return f"{self.name} ({self.stars}★) - {self.destination.name}"

    def get_amenities_list(self):
        return [a.strip() for a in self.amenities.split(',') if a.strip()]


class Transport(models.Model):
    TRANSPORT_TYPE = [
        ('flight', 'Flight'),
        ('train', 'Train'),
        ('bus', 'Bus'),
        ('car', 'Car/Taxi'),
        ('ferry', 'Ferry/Boat'),
        ('other', 'Other'),
    ]
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='transports')
    transport_type = models.CharField(max_length=20, choices=TRANSPORT_TYPE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    from_location = models.CharField(max_length=200)
    to_location = models.CharField(max_length=200)
    duration = models.CharField(max_length=100, blank=True, help_text='e.g. 2 hours 30 mins')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transports'
        ordering = ['transport_type', 'price']

    def __str__(self):
        return f"{self.name} ({self.transport_type}) - {self.from_location} to {self.to_location}"


class TourPackage(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='packages')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='packages')
    description = models.TextField()
    image = models.ImageField(upload_to='packages/')
    duration_days = models.IntegerField()
    max_group_size = models.IntegerField(default=15)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.IntegerField(default=0)
    includes = models.TextField(blank=True, help_text='What is included')
    excludes = models.TextField(blank=True, help_text='What is excluded')
    itinerary = models.TextField(blank=True, help_text='Day-wise itinerary')
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='easy')
    hotels = models.ManyToManyField(Hotel, blank=True, related_name='packages')
    transports = models.ManyToManyField(Transport, blank=True, related_name='packages')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    total_bookings = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tour_packages'
        ordering = ['-is_featured', '-rating']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_discounted_price(self):
        if self.discount_percent > 0:
            from decimal import Decimal
            discount = Decimal(str(self.discount_percent)) / Decimal('100')
            return self.price_per_person * (1 - discount)
        return self.price_per_person


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        unique_together = ['user', 'destination']

    def __str__(self):
        return f"{self.user.username} ❤ {self.destination.name}"


class TripPlan(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trip_plans')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    number_of_travelers = models.IntegerField(default=1)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='planning')
    notes = models.TextField(blank=True)
    itinerary = models.TextField(blank=True, help_text='JSON formatted itinerary')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trip_plans'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s trip to {self.destination.name}"

    def duration_days(self):
        return (self.end_date - self.start_date).days


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s review ({self.rating}★)"
