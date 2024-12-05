
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin_dashboard_app/', admin.site.urls),
    path('', include('adventureApp.urls')),
    path('admin-dashboard/',include('admin_dashboard_app.urls')),
]
