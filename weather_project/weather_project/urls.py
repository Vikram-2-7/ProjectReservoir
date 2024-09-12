# weather_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from weather import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('weather/', include('weather.urls')),  # Include weather app URLs
    path('', lambda request: HttpResponseRedirect('/weather/get_weather/')),  # Redirect to weather app
    path('', views.home), 
]

