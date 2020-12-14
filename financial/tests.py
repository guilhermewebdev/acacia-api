from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import Payment
from django.contrib.auth import get_user_model
from core.models import Professional
from services.models import Job, Proposal
from django.utils import timezone

User = get_user_model()
TODAY = timezone.now()
timedelta = timezone.timedelta

class TestPayment(TestCase):

    def setUp(self):
        self.client = User(
            email='tete@tete.com',
            password='senha',
            full_name='Fulano de tal',
        )
        self.client.save()
        self.user = User(
            email='tet2e@tete.com',
            password='senha',
            full_name='Fulano de tal',
        )
        self.user.save()
        self.professional = Professional(
            user=self.user,
            skills=['CI', 'AE', 'EM'],
            occupation='CI',
            avg_price=80,
            coren='10.000'
        )
        self.professional.save()
        self.proposal = Proposal(
            client=self.client,
            professional=self.professional,
            city='Curitiba',
            state='PR',
            professional_type='AE',
            service_type='AC',
            start_datetime=TODAY + timedelta(days=1),
            end_datetime=TODAY + timedelta(days=3),
            value=300.00,
            description='Lorem Ipsum dolores'
        )
        self.proposal.save()
        self.proposal.accept()
        self.job = self.proposal.job
        self.payment = Payment(
            client=self.client,
            professional=self.professional,
            value=300,
            job=self.job
        )
        self.payment.full_clean()
        self.payment.save()
    
    def test_payment(self):
        self.payment.full_clean()

    def test_wrong_payment_value(self):
        self.payment.value = 100
        self.assertRaises(ValidationError, self.payment.full_clean)

    def test_cash(self):
        self.assertEqual(self.professional.cash, 300)
        