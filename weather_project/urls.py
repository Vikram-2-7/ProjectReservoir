from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('weather.urls')),   # Default routes go to weather app
    path('dam/', include('dam.urls')),   # Routes for dam control app
]
