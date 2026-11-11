from django import forms
from .models import Destination, Hotel, Transport, TourPackage, Attraction, Category, TripPlan, Review


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. fas fa-mountain'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ['name', 'country', 'state', 'city', 'category', 'description',
                  'short_description', 'image', 'gallery_image1', 'gallery_image2',
                  'gallery_image3', 'climate', 'best_time_to_visit', 'average_budget',
                  'latitude', 'longitude', 'is_featured', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'gallery_image1': forms.FileInput(attrs={'class': 'form-control'}),
            'gallery_image2': forms.FileInput(attrs={'class': 'form-control'}),
            'gallery_image3': forms.FileInput(attrs={'class': 'form-control'}),
            'climate': forms.Select(attrs={'class': 'form-select'}),
            'best_time_to_visit': forms.TextInput(attrs={'class': 'form-control'}),
            'average_budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['destination', 'name', 'description', 'image', 'stars', 'address',
                  'phone', 'email', 'website', 'price_per_night', 'amenities',
                  'latitude', 'longitude', 'total_rooms', 'available_rooms',
                  'is_featured', 'is_active']
        widgets = {
            'destination': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'stars': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control'}),
            'amenities': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WiFi, Pool, Gym, ...'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'total_rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TransportForm(forms.ModelForm):
    class Meta:
        model = Transport
        fields = ['destination', 'transport_type', 'name', 'description',
                  'from_location', 'to_location', 'duration', 'price', 'is_active']
        widgets = {
            'destination': forms.Select(attrs={'class': 'form-select'}),
            'transport_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'from_location': forms.TextInput(attrs={'class': 'form-control'}),
            'to_location': forms.TextInput(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TourPackageForm(forms.ModelForm):
    class Meta:
        model = TourPackage
        fields = ['name', 'destination', 'category', 'description', 'image',
                  'duration_days', 'max_group_size', 'price_per_person',
                  'discount_percent', 'includes', 'excludes', 'itinerary',
                  'difficulty', 'hotels', 'transports', 'is_featured', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_group_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_person': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control'}),
            'includes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'excludes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'itinerary': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'hotels': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'transports': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AttractionForm(forms.ModelForm):
    class Meta:
        model = Attraction
        fields = ['destination', 'name', 'attraction_type', 'description', 'image',
                  'entry_fee', 'opening_hours', 'latitude', 'longitude', 'is_active']
        widgets = {
            'destination': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'attraction_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'entry_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'opening_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TripPlanForm(forms.ModelForm):
    class Meta:
        model = TripPlan
        fields = ['destination', 'title', 'start_date', 'end_date',
                  'number_of_travelers', 'budget', 'notes']
        widgets = {
            'destination': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'number_of_travelers': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("End date must be after start date.")
        return cleaned_data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'},
                                   choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Review title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your experience...'}),
        }
