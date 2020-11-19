from django.test import TestCase
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
            occupation=['CI', 'AE', 'EM'],
            coren='10.000'
        )
        professional.save()
        assert user.professional == professional
        assert user.is_professional