from django import forms
from django.contrib.auth.models import User

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']
