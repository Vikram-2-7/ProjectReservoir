# weather_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('weather.urls')),
    path('dam/', include('dam.urls')),
    path('hydroalert/',include('hydroalert.urls')),  # Include weather app URLs
]
