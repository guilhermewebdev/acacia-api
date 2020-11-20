from django.utils import timezone
from django.utils.timezone import timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from core.models import Professional
from .models import CounterProposal, Proposal, Rating

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
            start_datetime=TODAY + timedelta(days=1),
            end_datetime=TODAY + timedelta(days=3),
            value=300.00,
            description='Lorem Ipsum dolores'
        )
        self.proposal.save()

    def test_past_date(self):
        self.proposal.start_datetime = TODAY - timedelta(days=2)
        self.proposal.end_datetime = TODAY - timedelta(days=1)
        self.assertRaises(ValidationError, self.proposal.full_clean)

    def test_end_before_start(self):
        self.proposal.start_datetime = TODAY + timedelta(days=4)
        self.proposal.end_datetime = TODAY + timedelta(days=2)
        self.assertRaises(ValidationError, self.proposal.full_clean)

    def test_self_proposal(self):
        self.proposal.client = self.professional.user
        self.proposal.professional = self.professional
        self.assertRaises(ValidationError, self.proposal.full_clean)

    def test_accept_proposal(self):
        self.proposal.accept()
        self.assertEqual(self.proposal.job.value, self.proposal.value)

    def test_other_user_get_job(self):
        impostor = User(
            email='impostor@ts.com',
        )
        impostor.save()
        self.proposal.accept()
        self.proposal.job.client = impostor
        self.assertRaises(ValidationError, self.proposal.job.full_clean)


    def test_counter_proposal(self):
        counter_proposal = CounterProposal(
            proposal=self.proposal,
            value=320,
            description='Teste',
        )
        counter_proposal.full_clean()
        counter_proposal.value = 500
        self.assertRaises(ValidationError, counter_proposal.full_clean)
        counter_proposal.value = 100
        self.assertRaises(ValidationError, counter_proposal.full_clean)


class TestRating(TestCase):

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
            start_datetime=TODAY + timedelta(days=1),
            end_datetime=TODAY + timedelta(days=3),
            value=300.00,
            description='Lorem Ipsum dolores'
        )
        self.proposal.save()
        self.proposal.accept()

    def test_rating(self):
        rating = Rating(
            client=self.client,
            job=self.proposal.job,
            grade=4,
        )
        rating.full_clean()
        rating.save()
        self.assertEqual(self.professional.avg_rating, 4)