from django.core.exceptions import ValidationError
from services.models import Job
from core.models import Professional
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
class Payment(models.Model):
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='payments',
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.SET_NULL,
        related_name='receipts',
        null=True,
    )
    value = models.FloatField()
    job = models.OneToOneField(
        Job,
        on_delete=models.PROTECT
    )
    registration_date = models.DateTimeField(
        auto_now=True,
    )

    def validate_value(self):
        if self.value != self.job.value:
            raise ValidationError(
                'Incorrect payment amount'
            )
    
    def full_clean(self, *args, **kwargs):
        self.validate_value()
        return super(Payment, self).full_clean(*args, **kwargs)