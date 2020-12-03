from django import forms
from django.contrib.auth.forms import (
    UserCreationForm as UCF,
    UserChangeForm as UCHF,
    PasswordResetForm as PRF,
)
from django.core.exceptions import ValidationError
from django.utils.text import capfirst
from .models import Availability, User, Professional, validate_cpf
from django.utils.translation import gettext as _
import re


ERROR_MESSAGES = {
    'invalid_login': _(
        "Please enter a correct %(email)s and password. Note that both "
        "fields may be case-sensitive."
    ),
    'inactive': _("This account is inactive."),
    'password_mismatch': _('The two password fields didn’t match.'),
}
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
            'cellphone_ddd',
            'cellphone',
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
        user.activate(self.cleaned_data['token'])
        return user

class UserDeletionForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'autofocus': True}),
        max_length=254,
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )


    def clean_password(self):
        if not self.instance.check_password(self.cleaned_data.get('password')):
            raise ValidationError(ERROR_MESSAGES['invalid_login'])
        return self.cleaned_data.get('password')

    def clean_email(self):
        if not self.instance.email == self.cleaned_data.get('email'):
            raise ValidationError(_('Invalid email'))
        return self.cleaned_data['email']

    def save(self):
        return self.instance.delete()[0] != 0

    class Meta:
        model = User
        fields = []

class ProfessionalCreationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=200,
        required=True,
    )
    email = forms.EmailField(
        max_length=200,
        required=True,
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                ERROR_MESSAGES['password_mismatch'],
                code='password_mismatch',
            )
        return password2
    
    def clean_cpf(self):
        validate_cpf(self.cleaned_data.get('cpf'))
        return re.sub('[^0-9]', '', self.cleaned_data.get('cpf'))

    def clean(self):
        cleaned_data = super(ProfessionalCreationForm, self).clean()
        if(cleaned_data['password1'] == cleaned_data['password2']):
            cleaned_data.pop('password2')
            if not self.instance.id:
                self.instance.user = User.objects.create_user(
                    email=cleaned_data.pop('email'),
                    password=cleaned_data.pop('password1'),
                    full_name=cleaned_data.pop('full_name'),
                )
                self.instance.user.full_clean()
            for attr, value in cleaned_data.items():
                setattr(self.instance, attr, value)
            self.instance.full_clean()
        return self.cleaned_data
    
    def save(self):
        self.instance.user.save()
        self.instance.save()
        self.instance.user.confirm_email()
        return self.instance
    class Meta:
        model = Professional
        fields = (
            "state",
            "city",
            "address",
            "zip_code",
            "cpf",
            "rg",
            "occupation",
            "coren",
        )

class ProfessionalUpdateForm(forms.ModelForm):

    def clean_cpf(self):
        validate_cpf(self.cleaned_data.get('cpf'))
        return re.sub('[^0-9]', '', self.cleaned_data.get('cpf'))

    class Meta:
        model = Professional
        fields = (
            "state",
            "city",
            "address",
            "zip_code",
            "cpf",
            "rg",
            "occupation",
            "coren",
            "skills",
            "avg_price",
            "about",
        )

class ProfessionalDeletionForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'autofocus': True}),
        max_length=254,
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    def clean_password(self):
        if not self.instance.user.check_password(self.cleaned_data.get('password')):
            raise ValidationError(_('The password fields didn’t match.'))
        return self.cleaned_data.get('password')

    def clean_email(self):
        if not self.instance.user.email == self.cleaned_data.get('email'):
            raise ValidationError(_('The email fields didn’t match.'))

    def save(self):
        return self.instance.delete()[0] != 0

    class Meta:
        model = Professional
        fields = []

class PasswordChangeForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                ERROR_MESSAGES['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def clean_password(self):
        if not self.instance.check_password(self.cleaned_data.get('password')):
            raise ValidationError(ERROR_MESSAGES['invalid_login'])
        return self.cleaned_data.get('password')

    def save(self):

        self.instance.set_password(self.cleaned_data['password1'])
        self.instance.save(update_fields=['password'])
        return self.instance

    class Meta:
        model = User
        fields = [
            'password',
        ]

class AvailabilityForm(forms.ModelForm):
    uuid = forms.UUIDField(required=False)

    class Meta:
        model = Availability
        fields = [
            'start_datetime',
            'end_datetime',
            'recurrence',
            'weekly_recurrence',
        ]
