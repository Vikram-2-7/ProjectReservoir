# dam/forms.py
from django import forms

class DamPredictForm(forms.Form):
    name = forms.CharField(
        required=True,
        label="Reservoir / Dam / City",
        widget=forms.TextInput(attrs={"placeholder": "Enter reservoir/dam/city name", "class":"w-full p-2 border rounded"})
    )
    temperature = forms.FloatField(required=False, label="Temperature (°C)")
    humidity = forms.FloatField(required=False, label="Humidity (%)")
    wind_speed = forms.FloatField(required=False, label="Wind Speed (km/h)")
    rainfall = forms.FloatField(required=False, label="Rainfall (mm)")
