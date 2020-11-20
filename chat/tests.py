from django.test import TestCase
from .models import Message, User
from core.models import Professional

class TestChat(TestCase):

    def setUp(self) -> None:
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

    def test_send_message(self):
        message = Message(
            sender=self.client,
            receiver=self.user,
            content='Hello! How are you?',
        )
        message.save()
        self.assertEqual(
            self.client.messages_sent.all()[0],
            self.user.received_messages.all()[0]
        )