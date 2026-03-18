from django.db import models
from django.contrib.auth.models import User
import json


class Dam(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    capacity = models.FloatField(help_text="Maximum water capacity in mcft")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['location']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.location}"


class DamMeasurement(models.Model):
    dam = models.ForeignKey(Dam, on_delete=models.CASCADE, related_name='measurements')
    measurement_date = models.DateTimeField()
    upstream_water_level = models.FloatField(help_text="Upstream water level in mcft")
    downstream_water_level = models.FloatField(help_text="Downstream water level in mcft")
    inflow_rate = models.FloatField(help_text="Inflow rate in cubic feet/sec")
    outflow_rate = models.FloatField(help_text="Outflow rate in cubic feet/sec")
    rainfall_amount = models.FloatField(default=0, help_text="Rainfall amount in mm")
    temperature = models.FloatField(null=True, blank=True, help_text="Temperature in Celsius")
    humidity = models.FloatField(null=True, blank=True, help_text="Humidity percentage")
    wind_speed = models.FloatField(null=True, blank=True, help_text="Wind speed km/s")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-measurement_date']
        indexes = [
            models.Index(fields=['dam', '-measurement_date']),
            models.Index(fields=['measurement_date']),
        ]
        unique_together = ['dam', 'measurement_date']
    
    def __str__(self):
        return f"{self.dam.name} - {self.measurement_date}: {self.upstream_water_level} mcft"


class DamAlert(models.Model):
    ALERT_TYPES = [
        ('HIGH', 'High Water Level Alert'),
        ('LOW', 'Low Water Level Alert'),
        ('NORMAL', 'Normal Status'),
        ('CRITICAL', 'Critical Alert'),
    ]
    
    dam = models.ForeignKey(Dam, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPES)
    message = models.TextField()
    water_level = models.FloatField(help_text="Water level at time of alert in mcft")
    inflow_rate = models.FloatField(help_text="Inflow rate at time of alert in cubic feet/sec")
    rainfall_last_3_days = models.FloatField(default=0, help_text="Total rainfall in last 3 days in mm")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dam', '-created_at']),
            models.Index(fields=['alert_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.dam.name} - {self.alert_type}: {self.message[:50]}"


class MLModelPrediction(models.Model):
    dam = models.ForeignKey(Dam, on_delete=models.CASCADE, related_name='predictions')
    prediction_date = models.DateTimeField()
    model_type = models.CharField(max_length=50, default='RandomForest')
    features_used = models.JSONField(help_text="Features used for prediction")
    prediction_result = models.BooleanField(help_text="True for success, False for failure")
    confidence_score = models.FloatField(help_text="Model confidence score")
    actual_result = models.BooleanField(null=True, blank=True, help_text="Actual outcome for validation")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-prediction_date']
        indexes = [
            models.Index(fields=['dam', '-prediction_date']),
            models.Index(fields=['model_type']),
            models.Index(fields=['prediction_date']),
        ]
    
    def __str__(self):
        return f"{self.dam.name} - {self.prediction_date}: {'Success' if self.prediction_result else 'Failure'}"


class DamOperation(models.Model):
    OPERATION_TYPES = [
        ('RELEASE', 'Water Release'),
        ('STORAGE', 'Water Storage'),
        ('MONITOR', 'Monitoring Only'),
        ('EMERGENCY', 'Emergency Operation'),
    ]
    
    dam = models.ForeignKey(Dam, on_delete=models.CASCADE, related_name='operations')
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPES)
    water_release_amount = models.FloatField(null=True, blank=True, help_text="Amount of water released in mcft")
    recommended_release = models.FloatField(help_text="Recommended water release in mcft")
    inflow_capacity = models.FloatField(help_text="Current inflow capacity in cubic feet/sec")
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dam', '-created_at']),
            models.Index(fields=['operation_type']),
        ]
    
    def __str__(self):
        return f"{self.dam.name} - {self.operation_type} at {self.created_at}"
