from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin-dashboard'),
    path('profile/', views.user_profile, name='profile'),  # Assuming there's a separate profile view
    path('clients/', views.clients_manage, name='clients-manage'),
    path('user-bookings/', views.user_bookings, name='user-bookings'),
    path('tour-guides/', views.guides_manage, name='guides-manage'),
    path('reviews/', views.reviews, name='reviews'),
    path('create/', views.create_tour, name='create'),
    path('tours/', views.tours_manage, name='tours-manage'),
    path('analytics/', views.analytics, name='analytics'),
]