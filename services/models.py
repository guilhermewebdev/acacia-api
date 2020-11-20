from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from core.models import OCCUPATIONS, Professional, STATES, SERVICES, ValidateChoices
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def future_validator(date_time):
    if timezone.now() > date_time:
        raise ValidationError(
            'This date has passed'
        )

class Proposal(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='proposals',
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='proposals',
    )
    city = models.CharField(
        max_length=100,
    )
    state = models.CharField(
        max_length=2,
        choices=STATES,
        validators=[ValidateChoices(STATES)],
    )
    professional_type = models.CharField(
        max_length=2,
        choices=OCCUPATIONS,
        validators=[ValidateChoices(OCCUPATIONS)],
    )
    service_type = models.CharField(
        max_length=2,
        choices=SERVICES,
        validators=[ValidateChoices(SERVICES)],
    )
    start = models.DateTimeField(
        validators=[future_validator],
    )
    end = models.DateTimeField(
        validators=[future_validator]
    )
    value = models.FloatField(
        validators=[MinValueValidator(65)],
    )

    def validate_end_start(self):
        if self.start > self.end:
            raise ValidationError(
                'The start must be before the end'
            )

    def validate_self_proposal(self):
        if self.client == self.professional.user:
            raise ValidationError(
                "You cannot make a proposal for yourself"
            )

    def full_clean(self, *args, **kwargs) -> None:
        self.validate_end_start()
        self.validate_self_proposal()
        return super(Proposal, self).full_clean(*args, **kwargs)