from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get_weather/', views.get_weather, name='get_weather'),
    path('weather_info/', views.weather_info, name='weather_info'),
]
