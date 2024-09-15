from django.urls import path
from . import views

urlpatterns = [
    path('', views.hydroalert, name='hydroalert'),
    path('', views.fetch_critical_data, name='fetch_critical_data'),
    path('', views.fetch_dam_location, name='fetch_dam_location'),
    
    path('', views.hydroalert, name='hydroalert'),  # Main page
    path('fetch_critical_data/', views.fetch_critical_data, name='fetch_critical_data'),
    
]
