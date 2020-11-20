from django.utils import timezone
from django.utils.timezone import timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from core.models import Professional
from .models import Proposal

User = get_user_model()
TODAY = timezone.now()

class TestProposal(TestCase):

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
            state='MG',
            city='Belo Horizonte',
            address='Centro',
            zip_code='36200-000',
            cpf="529.982.247-25",
            rg='mg3434032',
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
            start=TODAY + timedelta(days=1),
            end=TODAY + timedelta(days=3),
            value=300.00,
        )
        self.proposal.save()

    def test_past_date(self):
        self.proposal.start = TODAY - timedelta(days=2)
        self.proposal.end = TODAY - timedelta(days=1)
        self.assertRaises(ValidationError, self.proposal.full_clean)

    def test_end_before_start(self):
        self.proposal.start = TODAY + timedelta(days=4)
        self.proposal.end = TODAY + timedelta(days=2)
        self.assertRaises(ValidationError, self.proposal.full_clean)

    def test_self_proposal(self):
        self.proposal.client = self.professional.user
        self.proposal.professional = self.professional
        self.assertRaises(ValidationError, self.proposal.full_clean)

    