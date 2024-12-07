from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Booking


class UserRegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'password',
            'required': 'required',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'required': 'required',
            'id': 'confirm_password'
        })
    )

    class Meta:
        model = User
        fields = ['fullname', 'email', 'phone_number', 'password1', 'password2']
        widgets = {
            'fullname': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'required': 'required',
                'id': 'fullname'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'required': 'required',
                'id': 'email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'id': 'phone_number',
                'required': 'required',
                'type': 'tel'  # Changed from number to tel for better mobile experience
            }),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Add phone number validation
        if not phone_number.isdigit():
            raise forms.ValidationError("Phone number must contain only digits")
        return phone_number

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['slots_booked']
        widgets = {
            'slots_booked': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            })
        }

    def __init__(self, *args, **kwargs):
        self.tour = kwargs.pop('tour', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_slots_booked(self):
        slots = self.cleaned_data['slots_booked']
        if not self.tour:
            raise forms.ValidationError("Tour information is missing.")

        available_slots = self.tour.max_group_size - self.tour.get_booked_slots()
        if slots > available_slots:
            raise forms.ValidationError(f"Only {available_slots} slots are available for this tour.")

        return slots

    def save(self, commit=True):
        # Create booking instance
        booking = super().save(commit=False)
        booking.tour = self.tour
        booking.user = self.user

        if commit:
            booking.save()
        return booking

class TourSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control py-3 rounded-3  w-75',
            'placeholder': 'Search packages by destination,...'
        })
    )
