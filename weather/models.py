from django.db import models
from django.contrib.auth.models import User
import json


class WeatherData(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=50, blank=True)
    temperature = models.FloatField()
    feels_like = models.FloatField()
    humidity = models.IntegerField()
    pressure = models.FloatField()
    wind_speed = models.FloatField()
    wind_deg = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=10)
    visibility = models.FloatField(null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['city', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.city} - {self.temperature}°C at {self.timestamp}"


class WeatherForecast(models.Model):
    weather_data = models.ForeignKey(WeatherData, on_delete=models.CASCADE, related_name='forecasts')
    date = models.DateField()
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=10)
    min_temp = models.FloatField()
    max_temp = models.FloatField()
    
    class Meta:
        ordering = ['date']
        unique_together = ['weather_data', 'date']
    
    def __str__(self):
        return f"{self.weather_data.city} - {self.date}: {self.min_temp}°C to {self.max_temp}°C"


class UserSearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    city = models.CharField(max_length=100)
    search_timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-search_timestamp']
        indexes = [
            models.Index(fields=['user', '-search_timestamp']),
            models.Index(fields=['city']),
        ]
    
    def __str__(self):
        return f"{self.user or 'Anonymous'} searched for {self.city} at {self.search_timestamp}"
