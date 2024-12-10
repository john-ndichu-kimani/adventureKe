from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin-dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('clients/', views.clients_manage, name='clients-manage'),
    path('ban-user/<int:user_id>/', views.ban_user, name='ban_user'),
    path('user-bookings/', views.user_bookings, name='user-bookings'),
    path('tour-guides/', views.guides_manage, name='guides-manage'),
    path('reviews/', views.reviews, name='reviews'),
    path('tours/create/', views.create_or_update_tour, name='create_tour'),
    path('tours/update/<int:tour_id>/', views.create_or_update_tour, name='update_tour'),
    path('tours/delete/<int:tour_id>/', views.delete_tour, name='delete_tour'),
    path('tours/', views.tours_manage, name='tours-manage'),
]