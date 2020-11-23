from django.test import TestCase
from .models import Message, User
from core.models import Professional
from services.models import Job, Proposal
from django.utils import timezone


TODAY = timezone.now()
timedelta = timezone.timedelta
class TestChat(TestCase):

    def setUp(self):
        self.client = User(
            email='teste4@teste.com',
            full_name='Tom Cruise',
            celphone='31988776455',
            password='senha',
        )
        self.client.save()
        self.user = User(
            email='teste5@teste.com',
            full_name='Tom Jobim',
            celphone='31988776615',
            password='senha',
        )
        self.user.save()
        self.professional = Professional(
            user=self.user,
            state='MG',
            city='Belo Horizonte',
            address='Centro',
            zip_code='36200-000',
            cpf="752.861.710-52",
            rg='mg343403',
            skills=['CI', 'AE', 'EM'],
            occupation='CI',
            coren='10.002'
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
        self.job = Job(
            proposal=self.proposal,
            client=self.client,
            professional=self.professional,
            value=300,
            start_datetime=TODAY + timedelta(days=1)
        )
        self.job.save()

    def test_send_message(self):
        message = Message(
            sender=self.client,
            receiver=self.user,
            content='Hello! How are you?',
            job=self.job,
        )
        message.save()
        self.assertEqual(
            self.client.messages_sent.all()[0],
            self.user.received_messages.all()[0]
        )