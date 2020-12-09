from django import forms
from django.contrib.auth.forms import (
    UserCreationForm as UCF,
    UserChangeForm as UCHF,
    PasswordResetForm as PRF,
)
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
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

    class Meta:
        model = Professional
        fields = (
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
        if not password1 or not password2 and password1 != password2:
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

    class Meta:
        model = Availability
        fields = [
            'start_datetime',
            'end_datetime',
            'recurrence',
            'weekly_recurrence',
            'professional',
        ]


class CustomerForm(forms.Form):
    cpf = forms.CharField(
        max_length=14,
        required=True,
        validators=[validate_cpf]
    )
    zip_code = forms.CharField(
        max_length=9,
        validators=[RegexValidator(regex='^[0-9]{5}-?[0-9]{3}$')],
        required=True,
    )
    neighborhood = forms.CharField(
        required=True,
    )
    street = forms.CharField(
        required=True,
    )
    street_number = forms.IntegerField(
        required=True
    )


class CardForm(forms.Form):
    card_hash = forms.CharField(required=False)
    card_number = forms.CharField(required=False)
    card_expiration_date = forms.CharField(required=False)
    card_holder_name = forms.CharField(required=False)
    card_cvv = forms.CharField(required=False)

    @property
    def full_cleaned_data(self):
        return dict(filter(
            lambda item: bool(item[1]),
            self.cleaned_data.items()
        ))