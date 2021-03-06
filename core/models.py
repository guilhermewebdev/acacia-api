import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as UM
from django.core.validators import validate_email, RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.contrib.postgres.fields import ArrayField
from functools import reduce
from pagarme import customer, recipient
from django.template.loader import render_to_string
import re
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator as dtg
from django.conf import settings
from django.utils.timezone import now
import pagarme
from pagarme.resources import handler_request


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) +
            str(user.is_active)
        )
account_activation_token = TokenGenerator()

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

@deconstructible
class MinOrNullValidator(object):
    def __init__(self, minimum):
        self.min = minimum

    def __call__(self, value):
        if value and value < self.min:
            raise ValidationError(
                '%(value) should be more than %(minimum)',
                params={
                    'value': value,
                    'minimum': self.min
                }
            )

def verify_sum(cpf, last_index):
    cut_cpf = cpf[0:last_index]
    cut_cpf.reverse()
    multipliers = list(range(2, last_index + 2))
    sum_all = lambda total, el: total + (el[0] * el[1])
    grouped_factors = list(zip(cut_cpf, multipliers))
    return reduce(sum_all, grouped_factors, 0)


def verify_rest(sum, digit):
    rest = (sum * 10) % 11
    new_rest = 0 if ((rest == 10) or (rest == 11)) else rest
    return new_rest == digit


def validate_cpf(value):
    unmasked_cpf = re.sub('[^0-9]', '', value)
    RegexValidator('^[0-9]{11}$')(unmasked_cpf)
    list_cpf = list(map(lambda el: int(el), unmasked_cpf))
    first_sum = verify_sum(list_cpf, 9)
    second_sum = verify_sum(list_cpf, 10)
    if not (verify_rest(first_sum, list_cpf[9]) and verify_rest(second_sum, list_cpf[10])):
        raise ValidationError(
            '%(value) is not a valid CPF',
            params={'value', value}
        )


class UserManager(UM):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)



class User(AbstractUser):
    objects = UserManager()
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
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
    cellphone_ddd = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        validators=[RegexValidator('^[0-9]{2}$')]
    )
    cellphone = models.CharField(
        max_length=11,
        null=True,
        blank=True,
    )
    telephone_ddd = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        validators=[RegexValidator('^[0-9]{2}$')]
    )
    telephone = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )
    saved_in_pagarme = models.BooleanField(
        default=False
    )
    is_active = models.BooleanField(
        default=False
    )
    pagarme_id = models.IntegerField(
        null=True,
        blank=True,
        unique=True,
    )
    cpf = models.CharField(
        max_length=14,
        validators=[validate_cpf],
        null=True,
        blank=True,
    )
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['password']

    __customer = None
    __cards = []

    @property
    def is_professional(self):
        return hasattr(self, 'professional')

    @property
    def unmasked_cpf(self):
        return re.sub('[^0-9]', '', self.cpf or '')
    
    @property
    def customer(self):
        if self.saved_in_pagarme and self.__customer == None:
            self.__customer = handler_request.get(f'https://api.pagar.me/1/customers/{self.pagarme_id}', {})
        return self.__customer

    @property
    def cards(self):
        if not self.__cards and self.saved_in_pagarme:
            self.__cards = handler_request.get(
                f'https://api.pagar.me/1/cards?customer_id={self.pagarme_id}'
            )
        return self.__cards

    @property
    def full_cellphone(self):
        if self.cellphone and self.cellphone_ddd:
            return f'+55{self.cellphone_ddd}{self.cellphone}'
        return None

    @property
    def full_telephone(self):
        if self.telephone and self.telephone_ddd:
            return f'+55{self.telephone_ddd}{self.telephone}'
        return None

    @staticmethod
    def get_deleted_user(cls):
        return cls.object.get(email='deleted@user.com')

    def recover_password(self):
        self.email_user(
            'Recuperação de Senha',
            message=render_to_string(
                'recover_password_email.html',
                {
                    'user': self,
                    'token': dtg.make_token(self),
                    'link': settings.CHANGE_PASSWORD_LINK,
                }
            )
        )

    def set_recovered_password(self, token, password):
        if dtg.check_token(self, token):
            self.set_password(password)
            return True
        return False

    def confirm_email(self):
        if not self.is_active:
            self.email_user(
                'Confirmação de E-mail',
                message=render_to_string(
                    'email_template.html',
                    {
                        'user': self,
                        'token': account_activation_token.make_token(self),
                        'link': settings.CONFIRMATION_LINK,
                    }
                ),
                from_email=settings.SENDER_EMAIL,
            )
            return True
        return False

    def activate(self, token):
        if account_activation_token.check_token(self, token):
            self.is_active = True
            self.save(update_fields=['is_active'])
        return self.is_active

    def create_customer(self):
        if not self.saved_in_pagarme:
            data = {
                'name': self.full_name,
                'email': self.email,
                'external_id': str(self.uuid),
                'country': 'br',
                'birthday': self.born.isoformat(),
                'type': 'individual',
                'phone_numbers': [],
                'documents': [{
                    'type': 'cpf',
                    'number': self.unmasked_cpf,
                }]
            }
            if self.full_cellphone:
                data['phone_numbers'].append(self.full_cellphone)
            if self.full_telephone:
                data['phone_numbers'].append(self.full_telephone)
            self.__customer = customer.create(data)
            if 'id' in self.__customer:
                self.saved_in_pagarme = True
                self.pagarme_id = self.__customer['id']
                self.save(update_fields=['saved_in_pagarme', 'pagarme_id'])
        return self.customer

    def create_card(self, card):
        return pagarme.card.create({
            **card,
            'customer_id': self.pagarme_id,
        })

    def validate_customer(self):
        if not self.saved_in_pagarme or not self.pagarme_id:
            raise ValidationError('You need create a customer')


    def validate_cards(self):
        if not self.cards:
            raise ValidationError('You need create a cart')

    class Meta(AbstractUser.Meta):
        swappable='AUTH_USER_MODEL'


class Address(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='address',
    )
    street = models.CharField( 
        max_length=200,
    )
    street_number = models.CharField(
        max_length=30,
    )
    zipcode = models.CharField(
        max_length=9,
        validators=[RegexValidator(regex='^[0-9]{5}-?[0-9]{3}$')],
    )
    state = models.CharField(
        choices=STATES,
        validators=[ValidateChoices(STATES)],
        max_length=2,
    )
    city = models.CharField(
        max_length=100,
    )
    neighborhood = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    complementary = models.CharField(
        max_length=200,
    )


    def __str__(self) -> str:
        return f'{self.street}, {self.street_number}, {self.neighborhood}, {self.city} - {self.state}'

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
    uuid = models.UUIDField(
        unique=True,
        editable=False,
        default=uuid.uuid4
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
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
        if self.start_datetime < now():
            raise ValidationError('The start date has passed')

    def validate_end(self):
        if self.end_datetime < self.start_datetime:
            raise ValidationError(
                'The end date cannot be before the start date')

    def full_clean(self, *args, **kwargs) -> None:
        self.validate_end()
        self.validate_start()
        return super(Availability, self).full_clean(*args, **kwargs)

class Professional(models.Model):
    uuid = models.UUIDField(
        unique=True,
        editable=False,
        default=uuid.uuid4
    )
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
        validators=[MinOrNullValidator(65)],
        default=0,
        blank=True,
        null=True,
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
    saved_in_pagarme = models.BooleanField(
        default=False
    )
    pagarme_id = models.CharField(
        null=True,
        blank=True,
        max_length=100,
    )
    __recipient = {}

    @property
    def recipient(self):
        if self.saved_in_pagarme and not self.__recipient:
            self.__recipient = handler_request.get(
                f'https://api.pagar.me/1/recipients/{self.pagarme_id}'
            )
        return self.__recipient
    
    @property
    def postback_url(self):
        return f'{settings.HOST}/postback/professional/{self.uuid}/'

    @property
    def avg_rating(self):
        return self.jobs.filter(rate__isnull=False).all().aggregate(models.Avg('rate__grade'))['rate__grade__avg']

    @property
    def cash(self):
        cash = Professional.objects.filter(uuid=str(self.uuid)).aggregate(
            cash_in=models.Sum('receipts__value'), cash_out=models.Sum('cash_outs__value'),
        )
        return (cash.get('cash_in', 0) or 0) - (cash.get('cash_out', 0) or 0)

    def create_recipient(self, agency, agency_dv, bank_code, account, account_dv, legal_name):
        if not self.saved_in_pagarme:
            self.__recipient = recipient.create({
                "type": "individual",
                "name": self.user.full_name,
                "email": self.user.email,
                "postback_url": self.postback_url,
                "automatic_anticipation_enabled": True,
                "bank_account": {
                    "agencia": agency, 
                    "agencia_dv": agency_dv, 
                    "bank_code": bank_code, 
                    "conta": account, 
                    "conta_dv": account_dv, 
                    "document_type": 'cpf',
                    "document_number": self.user.unmasked_cpf, 
                    "legal_name": legal_name.upper(), 
                },
                "phone_numbers": [
                    {
                        "ddd": self.user.telephone_ddd,
                        "number": f'{self.user.telephone_ddd}{self.user.telephone}',
                        "type": "phone"
                    },
                    {
                        "ddd": self.user.cellphone_ddd,
                        "number": f'{self.user.cellphone_ddd}{self.user.cellphone}',
                        "type": "mobile"
                    }
                ]
            })
            if self.__recipient.get('id') is not None:
                self.saved_in_pagarme = True
                self.pagarme_id = self.__recipient['id']
                self.save(update_fields=['saved_in_pagarme', 'pagarme_id'])
        return self.recipient
    
    @staticmethod
    def get_deleted_professional(cls):
        return cls.objects.get(user__email='deleted@user.com')