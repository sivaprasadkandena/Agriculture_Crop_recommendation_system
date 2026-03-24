"""
Forms for Crop Recommendation System
Features: N, P, K, temperature, humidity, ph, rainfall
"""

from django import forms
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from .models import UserProfile

class CropPredictionForm(forms.Form):
    """
    Form for single crop prediction based on soil and climate parameters
    """
    
    N = forms.FloatField(
        label='Nitrogen (N) Level',
        min_value=0,
        max_value=150,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter nitrogen level (0-150)',
            'step': '0.1'
        }),
        help_text='Soil nitrogen content in mg/kg'
    )
    
    P = forms.FloatField(
        label='Phosphorus (P) Level',
        min_value=0,
        max_value=150,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phosphorus level (0-150)',
            'step': '0.1'
        }),
        help_text='Soil phosphorus content in mg/kg'
    )
    
    K = forms.FloatField(
        label='Potassium (K) Level',
        min_value=0,
        max_value=150,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter potassium level (0-150)',
            'step': '0.1'
        }),
        help_text='Soil potassium content in mg/kg'
    )
    
    temperature = forms.FloatField(
        label='Temperature (°C)',
        min_value=0,
        max_value=60,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter temperature (0-60°C)',
            'step': '0.1'
        }),
        help_text='Average temperature in degrees Celsius'
    )
    
    humidity = forms.FloatField(
        label='Humidity (%)',
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter humidity (0-100%)',
            'step': '0.1'
        }),
        help_text='Relative humidity percentage'
    )
    
    ph = forms.FloatField(
        label='pH Level',
        min_value=3.5,
        max_value=9.5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter pH level (3.5-9.5)',
            'step': '0.1'
        }),
        help_text='Soil pH level (3.5 = very acidic, 7 = neutral, 9.5 = very alkaline)'
    )
    
    rainfall = forms.FloatField(
        label='Rainfall (mm)',
        min_value=0,
        max_value=350,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter rainfall (0-350mm)',
            'step': '0.1'
        }),
        help_text='Annual rainfall in millimeters'
    )


class CropCSVUploadForm(forms.Form):
    """
    Form for batch crop predictions via CSV upload
    CSV should have columns: N, P, K, temperature, humidity, ph, rainfall
    """
    
    csv_file = forms.FileField(
        label='Upload CSV File',
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv',
        }),
        help_text='CSV file should have columns: N, P, K, temperature, humidity, ph, rainfall'
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        if file:
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('File size must not exceed 5MB.')
        return file


class ProfileCompletionForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'location', 'soil_type', 'farm_size']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'soil_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter soil type'}),
            'farm_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter farm size'}),
        }