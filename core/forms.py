from django import forms
from django.contrib.auth.forms import UserCreationForm as UCF
from .models import User

class CreationUserForm(UCF):
    class Meta:
        model = User
        fields = ("email", "full_name")
        field_classes = {'email': forms.EmailField}