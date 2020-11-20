from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, validate_email, RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.contrib.postgres.fields import ArrayField
from functools import reduce
import re

STATES = (
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goías'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraíma'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
)

OCCUPATIONS = (
    ('CI', 'Cuidadora de idosos'),
    ('AE', 'Auxiliar de enfermagem'),
    ('TE', 'Técnico em enfermagem'),
    ('EM', 'Enfermeiro'),
)


SERVICES = (
    ('AC', 'Hospital Escort'),
    ('AD', 'Home Escort'),
    ('CV', 'Dressings / Vaccines'),
    ('HC', 'Home Care'),
)

@deconstructible
class ValidateChoices(object):
    def __init__(self, choices):
        self.choices = choices

    def __call__(self, value):
        if value.upper() not in map(lambda el: el[0].upper(), self.choices):
            raise ValidationError(
                '%(value) is not a valid option',
                params={'value': value})


def invalid_cpf(value):
    raise ValidationError(
        '%(value) is not a valid CPF',
        params={'value', value}
    )


def verify_sum(cpf: list[int], last_index: int):
    cut_cpf = cpf[0:last_index]
    cut_cpf.reverse()
    multipliers = list(range(2, last_index + 2))
    sum_all = lambda total, el: total + (el[0] * el[1])
    grouped_factors = list(zip(cut_cpf, multipliers))
    return reduce(sum_all, grouped_factors, 0)


def verify_rest(sum: int, digit: int):
    rest = (sum * 10) % 11
    new_rest = 0 if ((rest == 10) or (rest == 11)) else rest
    return new_rest == digit


def validate_cpf(value: str):
    unmasked_cpf = re.sub('[^0-9]', '', value)
    RegexValidator('^[0-9]{11}$')(unmasked_cpf)
    list_cpf = list(map(lambda el: int(el), unmasked_cpf))
    first_sum = verify_sum(list_cpf, 9)
    second_sum = verify_sum(list_cpf, 10)
    if not (verify_rest(first_sum, list_cpf[9]) and verify_rest(second_sum, list_cpf[10])):
        invalid_cpf(value)


class User(AbstractUser):
    email = models.CharField(
        unique=True,
        validators=[validate_email],
        max_length=200,
    )
    username = None
    full_name = models.CharField(
        max_length=200,
    )
    born = models.DateField(
        verbose_name='Birth date',
        null=True,
        blank=True,
    )
    avatar = models.ImageField(
        verbose_name='Avatar',
        upload_to='avatars',
        height_field=300,
        width_field=300,
        null=True,
        blank=True,
    )
    celphone = models.CharField(
        max_length=11,
        null=True,
        blank=True,
    )
    telephone = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['password']

    @property
    def is_professional(self):
        return hasattr(self, 'professional')

    class Meta(AbstractUser.Meta):
        swappable='AUTH_USER_MODEL'


class Availability(models.Model):
    RECURRENCES = (
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly'),
    )
    WEEK_DAYS = (
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    )
    start = models.DateTimeField()
    end = models.DateTimeField()
    recurrence = models.CharField(
        choices=RECURRENCES,
        max_length=1,
        validators=[ValidateChoices(RECURRENCES)],
        null=True,
        blank=True,
    )
    weekly_recurrence=ArrayField(
        models.CharField(
            choices=WEEK_DAYS,
            max_length=3,
            validators=[ValidateChoices(WEEK_DAYS)]
        ),
        null=True,
        blank=True,
    )
    registration_date = models.DateTimeField(
        auto_now=True,
    )
    professional = models.ForeignKey(
        'Professional',
        on_delete = models.CASCADE,
        related_name='availabilities',
    )

    def validate_start(self):
        if self.start < self.registration_date:
            raise ValidationError('The start date has passed')

    def validate_end(self):
        if self.end < self.start:
            raise ValidationError(
                'The end date cannot be before the start date')

    def full_clean(self, *args, **kwargs) -> None:
        self.validate_end()
        self.validate_start()
        return super(Availability, self).full_clean(*args, **kwargs)

class Professional(models.Model):
    user = models.OneToOneField(
        User,
        related_name='professional',
        on_delete = models.CASCADE,
    )
    about = models.TextField(
        verbose_name='About text',
        null=True,
        max_length=1000,
        blank=True,
    )
    avg_price = models.FloatField(
        verbose_name='Average Price',
        validators=[MinValueValidator(65)],
        default=0,
    )
    state = models.CharField(
        choices=STATES,
        validators=[ValidateChoices(STATES)],
        max_length=2,
    )
    city = models.CharField(
        max_length=100,
    )
    address = models.CharField(
        max_length=200,
    )
    zip_code = models.CharField(
        max_length=9,
        validators=[RegexValidator(regex='^[0-9]{5}-?[0-9]{3}$')],
    )
    cpf = models.CharField(
        max_length=14,
        validators=[validate_cpf]
    )
    rg = models.CharField(
        max_length=12,
    )
    occupation = models.CharField(
        max_length=2,
        choices=OCCUPATIONS,
        validators=[ValidateChoices(OCCUPATIONS)]
    )
    skills=ArrayField(
        models.CharField(
            max_length=15,
            choices=SERVICES,
            validators=[ValidateChoices(SERVICES)]
        ),
        size=3,
        null=True,
        blank=True,
    )
    coren = models.CharField(
        max_length=6,
        validators=[RegexValidator('^[0-9]{2}\.?[0-9]{3}$')],
    )

    @property
    def avg_rating(self):
        return self.rates.all().aggregate(models.Avg('grade'))['grade__avg']


class Rating(models.Model):
    client = models.ForeignKey(
        User,
        on_delete = models.DO_NOTHING,
        related_name='rates',
    )
    professional = models.ForeignKey(
        Professional,
        on_delete = models.CASCADE,
        related_name='rates',
    )
    grade = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )

    def validate_user(self):
        if self.client == self.professional.user:
                raise ValidationError(
                    'It is not possible to rate yourself'
                )

    def full_clean(self, *args, **kwargs) -> None:
        self.validate_user()
        return super(Rating, self).full_clean(*args, **kwargs)
    class Meta:
        unique_together = ('client', 'professional')
