from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.test import Client

from adventureApp.models import TourGuide, User, Tour


# Create your views here.

@login_required(login_url='login')
def dashboard(request):
    return render(request,'dashboard.html')

@login_required(login_url='login')
def user_profile(request):
    user = request.user
    context = {'user': user}
    return render(request,'profile.html',context)

@login_required(login_url='login')
def clients_manage(request):
    users = User.objects.all()
    context = {'clients': users}
    return render(request,'clients_manage.html',context)


def guides_manage(request):
    guides = TourGuide.objects.all()
    context = {'guides':guides}
    return render(request,'guides_manage.html',context)

@login_required(login_url='login')
def bookings(request):
    user_bookings = TourGuide.objects.all()
    context = {'bookings':user_bookings}
    return render(request,'bookings.html',context)

@login_required(login_url='login')
def reviews(request):
    user_reviews = User.objects.all()
    context = {'reviews':user_reviews}
    return render(request,'reviews.html',context)

@login_required(login_url='login')
def tours_manage(request):
    tours = Tour.objects.all()
    context = {'tours':tours}
    return render(request,'tours_manage.html',context)

@login_required(login_url='login')
def analytics(request):
    return render(request,'analytics.html')

@login_required(login_url='login')
def logout(request):
    return render(request,'logout.html')



