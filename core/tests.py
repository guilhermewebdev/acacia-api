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
    