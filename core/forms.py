from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (
    UserCreationForm as UCF,
    UserChangeForm as UCHF,
    PasswordResetForm as PRF,
    AuthenticationForm,
)
from django.core.exceptions import ValidationError
from django.utils.text import capfirst
from .models import User, account_activation_token
from django.conf import settings
from django.utils.translation import gettext as _
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

class UserActivationForm(forms.Form):
    token = forms.CharField(required=True)
    uuid = forms.UUIDField(required=True)

    def save(self, *args, **kwargs):
        user = User.objects.get(uuid=self.cleaned_data['uuid'])
        return user.activate(self.cleaned_data['token'])

class UserDeletionForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'autofocus': True}),
        max_length=254,
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(email)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)
        self.email_field = User._meta.get_field(User.USERNAME_FIELD)
        if self.fields['email'].label is None:
            self.fields['email'].label = capfirst(self.email_field.verbose_name)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email is not None and password:
            user = User.objects.get(email=email)
            self.user_cache = user if user.check_password(password) else None
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        if not self.user_cache:
            self.clean()
        return self.user_cache

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages['invalid_authentication'],
            code='invalid_authentication',
            params={'email': self.email_field.verbose_name},
        )
    
    def save(self):
        user = self.get_user()
        print(user)
        return user.delete()[0] != 0