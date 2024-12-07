from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_dashboard, name='user-dashboard'),
    path('profile/', views.profile_management, name='profile'),
    path('reviews/', views.reviews, name='reviews'),
    path('payment-history/', views.payment_history, name='payment-history'),
    path('single-tour/<int:tour_id>/',views.single_package,name='single-tour'),
    path('book-tour/<int:tour_id>/', views.book_tour, name='book-tour'),
    path('my-bookings/', views.my_bookings, name='my-bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel-booking'),


]