from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

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