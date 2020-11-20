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
    description = models.TextField()
    accepted = models.BooleanField(null=True, blank=True)
    registration_date = models.DateTimeField(
        auto_now=True,
        editable=False,
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

    def full_clean(self, *args, **kwargs):
        self.validate_end_start()
        self.validate_self_proposal()
        return super(Proposal, self).full_clean(*args, **kwargs)

class CounterProposal(models.Model):
    proposal = models.OneToOneField(
        Proposal,
        related_name='counter_proposal',
        on_delete=models.CASCADE,
    )
    target_value = models.FloatField(
        validators=[MinValueValidator(65)],
        default=models.F('proposal__value'),
    )
    description = models.TextField()
    registration_date = models.DateTimeField(
        auto_now=True,
        editable=False,
    )

    def validate_value(self):
        if (self.target_value > (1.2 * self.proposal.value)):
            raise ValidationError('The counter offer must be a maximum of 20% more than the offer')
        if (self.target_value < (0.8 * self.proposal.value)):
            raise ValidationError('The counter offer must be at least 20% more than the offer')
    
    def full_clean(self, *args, **kwargs):
        self.validate_value()
        return super(CounterProposal, self).full_clean(*args, **kwargs)