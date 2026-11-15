from django import forms
from .models import Vehicle


class VehicleSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label="Szukaj",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Marka, model lub nr rejestracyjny...'
        })
    )
    status = forms.ChoiceField(
        required=False,
        label="Status",
        choices=[('', 'Wszystkie statusy')] + Vehicle.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )