from django import forms
from .models import Station

class SearchBusForm(forms.Form):
    source = forms.ModelChoiceField(queryset=Station.objects.all(), empty_label="Select Source", widget=forms.Select(attrs={'class': 'form-select'}))
    destination = forms.ModelChoiceField(queryset=Station.objects.all(), empty_label="Select Destination", widget=forms.Select(attrs={'class': 'form-select'}))
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

class PassengerForm(forms.Form):
    passenger_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    passenger_phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    seat_numbers = forms.CharField(widget=forms.HiddenInput())
