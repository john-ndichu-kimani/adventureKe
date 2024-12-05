from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.

@login_required(login_url='login')
def dashboard(request):
    return render(request,'dashboard.html')

@login_required(login_url='login')
def user_profile(request):
    return render(request,'profile.html')

@login_required(login_url='login')
def clients_manage(request):
    return render(request,'clients_manage.html')

@login_required(login_url='login')
def guides_manage(request):
    return render(request,'guides_manage.html')

@login_required(login_url='login')
def bookings(request):
    return render(request,'bookings.html')

@login_required(login_url='login')
def reviews(request):
    return render(request,'reviews.html')

@login_required(login_url='login')
def tours_manage(request):
    return render(request,'tours_manage.html')

@login_required(login_url='login')
def analytics(request):
    return render(request,'analytics.html')

@login_required(login_url='login')
def logout(request):
    return render(request,'logout.html')