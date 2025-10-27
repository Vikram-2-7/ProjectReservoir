from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('weather.urls')),  # Home and weather app
    path('dam/', include('dam.urls')),  # Dam app including dam_control and hydro_alert views
    path('hydroalert/', include('hydroalert.urls')),
        # Hydroalert app
]
