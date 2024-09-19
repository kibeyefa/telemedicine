from django import forms
from .models import *


class PatientProfileForm(forms.ModelForm):
    
    class Meta:
        model = PatientProfile
        fields = ("email", "name", "phone", "date_of_birth", "gender", "address")


class DoctorProfileForm(forms.ModelForm):
    
    class Meta:
        model = DoctorProfile
        fields = ("email", "name", "phone", "date_of_birth", "gender", "address", "bio")
