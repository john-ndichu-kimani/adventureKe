
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('adventureApp.urls')),
    path('admin-dashboard/',include('admin_dashboard_app.urls')),
    path('user-dashboard/',include('user_dashboard_app.urls')),
]

if settings.DEBUG:  # Serve media files only during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)