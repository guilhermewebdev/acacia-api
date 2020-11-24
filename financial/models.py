from django.core.exceptions import ValidationError
from services.models import Job
from core.models import Professional
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
import uuid

User = get_user_model()

class Payment(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    client = models.ForeignKey(
        User, 
        on_delete=models.SET(User.get_deleted_user),
        related_name='payments',
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.SET(Professional.get_deleted_professional),
        related_name='receipts',
        null=True,
    )
    value = models.FloatField()
    job = models.OneToOneField(
        Job,
        on_delete=models.CASCADE,
        related_name='payment',
    )
    registration_date = models.DateTimeField(
        auto_now=True,
    )

    @property
    def postback_url(self):
        return f'{settings.HOST}/{self.uuid}'

    def validate_value(self):
        if self.value != self.job.value:
            raise ValidationError(
                'Incorrect payment amount'
            )
    
    def full_clean(self, *args, **kwargs):
        self.validate_value()
        return super(Payment, self).full_clean(*args, **kwargs)

class CashOut(models.Model):
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='cash_outs'
    )
    value = models.FloatField()
    registration_date = models.DateTimeField(
        auto_now=True,
    )

    def validate_value(self):
        if self.value != self.professional.cash:
            raise ValidationError(
                'It is only possible to withdraw all the cash'
            )

    def full_clean(self, *args, **kwargs):
        self.validate_value()
        return super(CashOut, self).full_clean(*args, **kwargs)