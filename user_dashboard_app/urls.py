from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_dashboard, name='user-dashboard'),
    path('my-profile/', views.view_profile, name='my-profile'),
    path('reviews/', views.reviews, name='reviews'),
    path('booking/payment/<int:booking_id>/', views.initiate_payment, name='initiate_payment'),
    path('mpesa/callback/<int:booking_id>/', views.mpesa_payment_callback, name='mpesa_callback'),
    path('payments/', views.payment_history, name='payments'),
    path('single-tour/<int:tour_id>/',views.single_package,name='single-tour'),
    path('book-tour/<int:tour_id>/', views.book_tour, name='book-tour'),
    path('my-bookings/', views.my_bookings, name='my-bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel-booking'),


]