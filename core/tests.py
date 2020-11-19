from django.test import TestCase
from django.test import client
from .models import User, Professional, Rating
class TestUser(TestCase):

    def test_creation(self):
        user = User(
            email='teste@teste.com',
            full_name='Guido Rossum',
            celphone='32999198822',
            password='tetris2',
        )
        user.save()
    
    def test_professional_creation(self):
        user = User(
            email='teste1@teste.com',
            full_name='Linuz Torvalds',
            celphone='31988776655',
            password='senha',
        )
        user.save()
        professional = Professional(
            user=user,
            state='MG',
            city='Belo Horizonte',
            address='Centro',
            zip_code='36200-000',
            cpf="601.554.960-26",
            rg='mg3434032',
            skills=['CI', 'AE', 'EM'],
            occupation='CI',
            coren='10.000'
        )
        professional.save()
        assert user.professional == professional
        assert user.is_professional

class TestRating(TestCase):

    def setUp(self):
        self.client = User(
            email='teste2@teste.com',
            full_name='Bill Gates',
            celphone='31988776655',
            password='senha',
        )
        self.client.save()
        self.user = User(
            email='teste3@teste.com',
            full_name='Steve Jobs',
            celphone='31988776655',
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
            rg='mg343402',
            skills=['CI', 'AE', 'EM'],
            occupation='CI',
            coren='10.001'
        )
        self.professional.save()

    def test_rate(self):
        rate = Rating(
            client=self.client,
            professional=self.professional,
            grade=3
        )
        rate.save()
        self.assertEqual(self.professional.avg_rating, 3)