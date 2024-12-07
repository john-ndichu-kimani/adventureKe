from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import UserRegistrationForm
from .models import User, Tour, Booking, Destination


# Create your views here.

def index(request):
    return render(request,'index.html')

def about(request):
    return render(request,'about.html')

def booking(request):
    return render(request,'booking.html')

def contact(request):
    return render(request,'contact.html')

def destination(request):
    return render(request,'destination.html')

def package(request):
    return render(request,'package.html')

def service(request):
    return render(request,'service.html')

def team(request):
    return render(request,'team.html')

def testimonial(request):
    return render(request,'testimonial.html')
def not_found(request):
    return render(request,'404.html')


def is_admin(user):
    return user.is_authenticated and user.role == 'ADMIN'

def user_register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Check for duplicate email
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
            else:
                form.save()
                messages.success(request, "Registered successfully! Please log in.")
        else:
            messages.error(request, "Please fix the input errors below")
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})



def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request,'Login successful!')
            return render(request, 'login.html', {'user_role': user.role})
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')




