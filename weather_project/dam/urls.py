# dam/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dam_control, name='dam_control'),
    path('',views.fetch_weather_data,name="fetch_weather_data"),   # Dam control page

]