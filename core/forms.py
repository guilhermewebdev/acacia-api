from django import forms
from django.contrib.auth.forms import UserCreationForm as UCF, UserChangeForm as UCHF, PasswordResetForm as PRF
from .models import User, account_activation_token
from django.conf import settings
class UserCreationForm(UCF):
    class Meta:
        model = User
        fields = ("email", "full_name")
        field_classes = {'email': forms.EmailField}

class UserChangeForm(UCHF):
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

class PasswordResetForm(PRF):
    
    def save(self, *args, **kwargs):
        email = self.cleaned_data['email']
        user = User.objects.get(email=email)
        return user.recover_password()