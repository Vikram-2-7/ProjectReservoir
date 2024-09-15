from django import forms

class HydroAlertForm(forms.Form):
    dam_name = forms.CharField(
        max_length=100,
        label='Dam or Reservoir Name',
        widget=forms.TextInput(attrs={
            'class': 'border border-gray-300 rounded p-2 w-full',
            'placeholder': 'Enter the name of the dam or reservoir',
        })
    )
    high_rainfall_threshold = forms.FloatField(
        label='High Rainfall Threshold (mm)',
        initial=50,
        widget=forms.NumberInput(attrs={
            'class': 'border border-gray-300 rounded p-2 w-full',
            'placeholder': 'Enter high rainfall threshold',
        })
    )
    high_inflow_threshold = forms.FloatField(
        label='High Inflow Threshold (cubic feet/sec)',
        initial=200,
        widget=forms.NumberInput(attrs={
            'class': 'border border-gray-300 rounded p-2 w-full',
            'placeholder': 'Enter high inflow threshold',
        })
    )
    low_water_level_threshold = forms.FloatField(
        label='Low Water Level Threshold (mcft)',
        initial=600,
        widget=forms.NumberInput(attrs={
            'class': 'border border-gray-300 rounded p-2 w-full',
            'placeholder': 'Enter low water level threshold',
        })
    )
    low_inflow_threshold = forms.FloatField(
        label='Low Inflow Threshold (cubic feet/sec)',
        initial=50,
        widget=forms.NumberInput(attrs={
            'class': 'border border-gray-300 rounded p-2 w-full',
            'placeholder': 'Enter low inflow threshold',
        })
    )