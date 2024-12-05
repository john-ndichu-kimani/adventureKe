from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('booking/', views.booking, name='booking'),
    path('contact/', views.contact, name='contact'),
    path('destinations/', views.destination, name='destination'),
    path('packages/', views.package, name='package'),
    path('services/', views.service, name='service'),
    path('teams/', views.team, name='team'),
    path('testimonials/', views.testimonial, name='testimonial'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('user-dashboard/', views.user_dashboard, name='user-dashboard'),
    path('admin_dashboard_app-dashboard/', views.admin_dashboard, name='admin_dashboard_app-dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('not-found/', views.not_found, name='not_found'),

]
