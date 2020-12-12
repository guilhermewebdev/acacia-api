from functools import reduce
import re
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
import pagarme
from pagarme.resources import handler_request
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
        'services.Job',
        on_delete=models.CASCADE,
        related_name='payment',
    )
    registration_date = models.DateTimeField(
        auto_now=True,
    )
    paid = models.BooleanField(
        default=False,
    )
    pagarme_id = models.IntegerField(
        null=True,
        blank=True,
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

    def validate_recipient(self):
        if not self.professional.recipient:
            raise ValidationError('The professional should create a recipient account')

    def pay(self, card_index=0):
        self.client.validate_customer()
        self.client.validate_cards()
        self.validate_recipient()
        if not hasattr(self.client, 'address'):
            raise ValidationError('The user address is required')
        if not self.paid:
            billing_fields = ['zipcode', 'street', 'street_number', 'state', 'city', 'neighborhood']
            address = model_to_dict(instance=self.client.address, fields=billing_fields)
            address['zipcode'] = re.sub('[^0-9]', '', address.get('zipcode'))
            default_recipient = pagarme.recipient.default_recipient()
            recipient_status = 'live' if settings.PRODUCTION else 'test'
            comission = settings.PLATFORM_COMMISSION or 0
            customer = {
                'external_id': str(self.client.uuid),
                'name': self.client.full_name,
                'email': self.client.email,
                'country': 'br',
                'type': 'individual',
                'phone_numbers': self.client.customer['phone_numbers'],
                'documents': [{
                    'type': 'cpf',
                    'number': self.client.unmasked_cpf
                }],
            }
            data = {
                'amount': int(self.value * 100),
                'card_id': self.client.cards[card_index]['id'],
                'customer': customer,
                'payment_method': 'credit_card',
                'async': False,
                'postback_url': self.postback_url,
                'soft_descriptor': settings.PAYMENT_DESCRIPTION,
                'billing': {
                    'name': self.client.full_name,
                    'address': {
                        **address,
                        'country': 'br'
                    }
                },
                'items': [{
                    'id': str(self.job.uuid),
                    'title': self.job.proposal.description,
                    'unit_price': int(self.value * 100),
                    'quantity': 1,
                    'tangible': False,
                    'category': 'Services',
                    'date': self.job.start_datetime.date().isoformat()
                }],
                'metadata': {
                    'payment': str(self.uuid),
                    'job': str(self.job.uuid),
                    'professional': self.professional.user.full_name,
                    'client': self.client.full_name,
                },
                'split_rules': [
                    {
                        'recipient_id': default_recipient.get(recipient_status),
                        'charge_processing_fee': True,
                        'percentage': comission,
                        'charge_remainder_fee': True,
                    },
                    {
                        'recipient_id': self.professional.recipient['id'],
                        'charge_processing_fee': False,
                        'percentage': (100 - (comission)),
                        'charge_remainder_fee': False,
                    },
                ]
            }
            self.__transaction = transaction.create(data)
            if self.__transaction.get('status', None) == 'paid':
                self.paid = True
                self.pagarme_id = self.__transaction.get('id')
                self.save(update_fields=['paid', 'pagarme_id'])
        return self.transaction

    def validate_value(self):
        if self.value != self.job.value:
            raise ValidationError(
                'Incorrect payment amount'
            )
    
    def full_clean(self, *args, **kwargs):
        self.validate_value()
        return super(Payment, self).full_clean(*args, **kwargs)

class CashOut(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    professional = models.ForeignKey(
        'core.Professional',
        on_delete=models.CASCADE,
        related_name='cash_outs'
    )
    value = models.FloatField()
    registration_date = models.DateTimeField(
        auto_now=True,
    )
    was_withdrawn = models.BooleanField(
        default=False,
    )
    pagarme_id = models.CharField(
        max_length=6,
        null=True,
        blank=True,
    )
    __transfer = {}

    @property
    def transfer(self):
        if not self.__transfer and self.pagarme_id:
            self.__transfer = handler_request.get(f'https://api.pagar.me/1/transfers/{self.pagarme_id}')
        return self.__transfer

    @classmethod
    def create_withdraw(cls, professional:Professional):
        withdraw = cls(
            professional=professional,
            value=professional.cash,
        )
        withdraw.full_clean()
        withdraw.save()
        withdraw.to_withdraw()
        return withdraw

    def cancel_withdraw(self):
        if self.was_withdrawn and self.pagarme_id:
            self.__transfer = transfer.cancel(self.pagarme_id)
            if self.__transfer['status'] == 'canceled':
                self.was_withdrawn = False
        return self.__transfer

    def to_withdraw(self):
        if not self.was_withdrawn and not self.pagarme_id:
            data = dict(
                amount=int(self.value * (100 - settings.CASH_OUT_COMMISSION)),
                recipient_id=self.professional.pagarme_id
            )
            self.__transfer = transfer.create(data)
            if 'id' in self.__transfer:
                self.pagarme_id = self.__transfer['id']
                self.was_withdrawn = True
        return self.__transfer

    def validate_value(self):
        if self.value != self.professional.cash:
            raise ValidationError(
                'It is only possible to withdraw all the cash'
            )

    def full_clean(self, *args, **kwargs):
        self.validate_value()
        return super(CashOut, self).full_clean(*args, **kwargs)