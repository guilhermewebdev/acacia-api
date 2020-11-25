from django.core.exceptions import ValidationError
from services.models import Job
from core.models import Professional
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from pagarme import transaction, transfer
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
    paid = models.BooleanField(
        default=False,
    )
    __transaction = None

    @property
    def transaction(self):
        if not self.__transaction:
            self.__transaction = transaction.find_by({
                'metadata': {
                    'payment': self.uuid,
                }
            })
        return self.__transaction

    @property
    def postback_url(self):
        return f'{settings.HOST}/postback/payment/{self.uuid}/'

    def pay(self, card_hash, street, street_number, zipcode, state, city, neighborhood, country='BR', complementary='_'):
        if not self.paid:
            self.__transaction = transaction.create(dict(
                amount=int(self.value * 100),
                card_hash=card_hash,
                customer=self.client.customer,
                payment_method='credit_card',
                postback_url=self.postback_url,
                soft_descriptor=settings.PAYMENT_DESCRIPTION,
                billing=dict(
                    street=street,
                    street_number=street_number,
                    zipcode=zipcode,
                    state=state,
                    city=city,
                    neighborhood=neighborhood,
                    country=country,
                    complementary=complementary,
                ),
                items=[dict(
                    id=self.job.pk,
                    title=self.job.proposal.description,
                    unit_price=self.value,
                    quantity=1,
                    tangible=False,
                    category='Services',
                    date=f'{self.job.start_datetime.year}-{self.job.start_datetime.month}-{self.job.start_datetime.day}'
                )],
                metadata=dict(
                    payment=self.uuid,
                )
            ))
            if self.__transaction.get('status', None) == 'paid':
                self.paid = True
                self.save(update_fields=['paid'])
        return self.paid, self.transaction

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
    withdrawn = models.BooleanField(
        default=False,
    )
    pagerme_id = models.CharField(
        max_length=6,
        null=True,
        blank=True,
    )
    __transfer = {}

    @property
    def transfer(self):
        if (self.__transfer == {}) and self.pagerme_id:
            self.__transfer = transfer.find_by({
                'id': self.pagerme_id
            })
        return self.__transfer

    def cancel_withdraw(self):
        if self.withdraw and self.pagerme_id:
            self.__transfer = transfer.cancel(self.pagerme_id)
            if self.__transfer['status'] == 'canceled':
                self.withdraw = False
        return self.__transfer

    def withdraw(self):
        if not self.withdraw and not self.pagerme_id:
            self.__transfer = transfer.create(dict(
                amount=int(self.value * (100 - settings.CASH_OUT_COMMISSION)),
                recipient_id=self.professional.recipient.get('id', None)
            ))
            if 'id' in self.__transfer:
                self.pagerme_id = self.__transfer['id']
                self.withdraw = True
        return self.__transfer

    def validate_value(self):
        if self.value != self.professional.cash:
            raise ValidationError(
                'It is only possible to withdraw all the cash'
            )

    def full_clean(self, *args, **kwargs):
        self.validate_value()
        return super(CashOut, self).full_clean(*args, **kwargs)