from django import forms
from .models import Booking, ExpenseTracker


class HotelBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'number_of_guests', 'special_requests', 'payment_method']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'number_of_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'payment_method': forms.Select(
                attrs={'class': 'form-select'},
                choices=[('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'),
                         ('upi', 'UPI'), ('net_banking', 'Net Banking'), ('cash', 'Cash')]
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        if check_in and check_out:
            if check_out <= check_in:
                raise forms.ValidationError("Check-out date must be after check-in date.")
        return cleaned_data


class TransportBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['travel_date', 'number_of_guests', 'special_requests', 'payment_method']
        widgets = {
            'travel_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'number_of_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'payment_method': forms.Select(
                attrs={'class': 'form-select'},
                choices=[('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'),
                         ('upi', 'UPI'), ('net_banking', 'Net Banking'), ('cash', 'Cash')]
            ),
        }


class PackageBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['travel_date', 'number_of_guests', 'special_requests', 'payment_method']
        widgets = {
            'travel_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'number_of_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'payment_method': forms.Select(
                attrs={'class': 'form-select'},
                choices=[('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'),
                         ('upi', 'UPI'), ('net_banking', 'Net Banking'), ('cash', 'Cash')]
            ),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = ExpenseTracker
        fields = ['title', 'amount', 'category', 'date', 'description', 'destination']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'destination': forms.Select(attrs={'class': 'form-select'}),
        }
