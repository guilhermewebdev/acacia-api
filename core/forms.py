from django import forms
from django.contrib.auth.forms import UserCreationForm as UCF, UserChangeForm as UCHF
from .models import User

class UserCreationForm(UCF):
    class Meta:
        model = User
        fields = ("email", "full_name")
        field_classes = {'email': forms.EmailField}

class UserChangeForm(UCHF):
    email = forms.EmailField(
        required=False,
    )
    full_name = forms.CharField(
        required=False,
    )
    class Meta:
        model = User
        fields = (
            'full_name',
            'email',
            'born',
            'avatar',
            'celphone_ddd',
            'celphone',
            'telephone_ddd',
            'telephone',
        )
