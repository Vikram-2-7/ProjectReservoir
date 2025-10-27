from django.urls import path
from . import views

urlpatterns = [
    path('', views.dam_control, name='dam_control'),
    path('hydroalert/', views.hydroalert, name='hydroalert'),
]
