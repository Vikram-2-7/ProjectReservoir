# dam/forms.py
from django import forms

class DamDataForm(forms.Form):
    inflow = forms.FloatField(label='Inflow (cubic feet/sec)', required=True)
    outflow = forms.FloatField(label='Outflow (cubic feet/sec)', required=True)
    water_flow = forms.FloatField(label='Water Flow (cubic feet/sec)', required=True)
    city = forms.CharField(label='City', required=True)
    start_date = forms.DateField(label='Start Date (YYYY-MM-DD)', required=True)
    end_date = forms.DateField(label='End Date (YYYY-MM-DD)', required=True)