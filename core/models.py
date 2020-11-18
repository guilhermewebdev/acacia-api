from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email, RegexValidator, validate_slug
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from functools import reduce
import re

STATES = (
  ( 'AC', 'Acre' ),
  ( 'AL', 'Alagoas' ),
  ( 'AP', 'Amapá' ),
  ( 'AM', 'Amazonas' ),
  ( 'BA', 'Bahia' ),
  ( 'CE', 'Ceará' ),
  ( 'DF', 'Distrito Federal' ),
  ( 'ES', 'Espírito Santo' ),
  ( 'GO', 'Goías' ),
  ( 'MA', 'Maranhão' ),
  ( 'MT', 'Mato Grosso' ),
  ( 'MS', 'Mato Grosso do Sul' ),
  ( 'MG', 'Minas Gerais' ),
  ( 'PA', 'Pará' ),
  ( 'PB', 'Paraíba' ),
  ( 'PR', 'Paraná' ),
  ( 'PE', 'Pernambuco' ),
  ( 'PI', 'Piauí' ),
  ( 'RJ', 'Rio de Janeiro' ),
  ( 'RN', 'Rio Grande do Norte' ),
  ( 'RS', 'Rio Grande do Sul' ),
  ( 'RO', 'Rondônia' ),
  ( 'RR', 'Roraíma' ),
  ( 'SC', 'Santa Catarina' ),
  ( 'SP', 'São Paulo' ),
  ( 'SE', 'Sergipe' ),
  ( 'TO', 'Tocantins' ),
)

OCCUPATIONS = (
    ('CI', 'Cuidadora de idosos'),
    ('AE', 'Auxiliar de enfermagem'),
    ('TE', 'Técnico em enfermagem'),
    ('EM', 'Enfermeiro'),
)

@deconstructible
class ValidateChoices(object):
    def __init__(self, choices):
        self.choices = choices
    
    def __call__(self,value):
        if value.upper() not in map(lambda el: el[0], choices):
            raise ValidationError(
                '%(value) is not a valid Brazil state',
                params={'value': value}
            )

def invalid_cpf(value):
    raise ValidationError(
        '%(value) is not a valid CPF',
        params={'value', value}
    )

verify_sum = lambda cpf, last_index: reduce(
        lambda total, el, index: total + (el * (index + 2)),
        cpf.reverse()[0:last_index], 0)
def verify_rest(sum: int, digit: int):
    rest = (sum * 10) % 11
    new_rest = 0 if ((rest == 10) or (rest == 11)) else rest
    return new_rest == digit

def validate_cpf(value: str):
    unmasked_cpf = re.sub('[\s.-]*', '', value)
    array_cpf = map(lambda el: int(el), value.split(''))
    RegexValidator('(\d)\1{10}')(unmasked_cpf)
    if (not unmasked_cpf or unmasked_cpf.length != 11): 
        invalid_cpf(value)
    first_sum = verify_sum(array_cpf, 9)
    second_sum = verify_sum(array_cpf, 10)
    if not verify_rest(first_sum, array_cpf[9]) and verify_rest(second_sum, array_cpf[10]):
        invalid_cpf(value)

class User(AbstractUser):
    email = models.CharField(
        unique=True,
        validators=[validate_email],
        max_length=200,
    )
    username = models.CharField(
        null=True,
        validators=[validate_slug],
        unique=True,
        max_length=100,
    )
    full_name = models.CharField(
        max_length=200,
    )

class Professional(models.Model):
    user = models.OneToOneField(
        User,
        related_name='professional',
        on_delete=models.CASCADE,
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
        max_length=15,
        choices=OCCUPATIONS,
        validators=[ValidateChoices(OCCUPATIONS)]
    )
    coren = models.CharField(
        max_length=6,
        validators=[RegexValidator('^[0-9]{2}\.?[0-9]{3}$')],
    )