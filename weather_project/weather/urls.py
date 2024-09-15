# weather/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('get_weather/', views.get_weather, name='get_weather'),  # Fetch weather data
    path('weather_info/', views.weather_info, name='weather_info'),  # Display weather info
    path('dam_control/', views.dam_control, name='dam_control'),  # Placeholder for Dam Control Center
    path('hydro_alert/', views.hydro_alert, name='hydro_alert'),  # Placeholder for Hydro Alert
    path('', views.dam_control, name='dam_control'),
    
     # Placeholder for
]



