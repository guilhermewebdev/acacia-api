from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import User, Professional, account_activation_token
from django.utils.timezone import now, timedelta

class TestUser(TestCase):

    def test_creation(self):
        user = User.objects.create_user(
            email='teste@teste.com',
            full_name='Guido Rossum',
            celphone='32999198822',
            password='tetris2',
        )
        user.full_clean()
        user.save()
    
    def test_professional_creation(self):
        user = User.objects.create_user(
            email='teste1@teste.com',
            full_name='Linuz Torvalds',
            celphone='31988776655',
            password='senha',
        )
        user.full_clean()
        user.save()
        professional = Professional(
            user=user,
            state='MG',
            city='Belo Horizonte',
            address='Centro',
            zip_code='36200-000',
            cpf="529.982.247-25",
            rg='mg3434032',
            skills=['AC', 'AD', 'HC'],
            occupation='CI',
            avg_price=80,
            coren='10.000'
        )
        professional.full_clean()
        professional.save()
        assert user.professional == professional
        assert user.is_professional

    def test_invalid_cpf(self):
        user = User(
            email='teste10@teste.com',
            full_name='Chimbinha',
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
            avg_price=99,
            cpf="601.554.963-56",
            rg='mg343402',
            skills=['CI', 'AE', 'EM'],
            occupation='CI',
            coren='10.040'
        )
        self.assertRaises(ValidationError, professional.full_clean)

    def test_invalid_coren(self):
        user = User(
            email='teste10@teste.com',
            full_name='Chimbinha',
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
            avg_price=99,
            cpf="529.982.247-25",
            rg='mg343402',
            skills=['CI', 'AE', 'EM'],
            occupation='CI',
            coren='1040'
        )
        self.assertRaises(ValidationError, professional.full_clean)

    def test_invalid_state(self):
        user = User(
            email='teste10@teste.com',
            full_name='Chimbinha',
            celphone='31988776655',
            password='senha',
        )
        user.save()
        professional = Professional(
            user=user,
            state='My',
            city='Belo Horizonte',
            address='Centro',
            zip_code='36200-000',
            avg_price=99,
            cpf="529.982.247-25",
            rg='mg343402',
            skills=['CI', 'AE', 'EM'],
            occupation='CI',
            coren='10.400'
        )
        self.assertRaises(ValidationError, professional.full_clean)

class ProfessionalTestREST(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@tst.com',
            password='abda1234',
            is_active=True,
        )
        self.professional = Professional.objects.create(
            user=User.objects.create_user(
                email='test@tstd.com',
                password='abda1234',
                is_active=True,
                full_name='Bernardo Lagosta'
            ),
            state='MG',
            city='Belo Horizonte',
            address='Centro',
            zip_code='36200-000',
            avg_price=99,
            cpf="529.982.247-25",
            rg='mg343402',
            skills=['CI', 'AE', 'EM'],
            occupation='CI',
            coren='10.400'
        )
        self.professional.user.save()
        self.professional.save()

    def test_list_professionals(self):
        response = self.client.get('/professionals/')
        self.assertEqual(response.json(), [{
            'user': {
                'full_name': self.professional.user.full_name,
                'uuid': str(self.professional.user.uuid),
                'email': self.professional.user.email,
                'avatar': None,
                'is_active': self.professional.user.is_active,
            },
            'about': self.professional.about,
            'avg_price': self.professional.avg_price,
            'state': 'MG',
            'city': self.professional.city,
            'occupation': self.professional.occupation,
            'skills': self.professional.skills,
            'avg_rating': self.professional.avg_rating,
            'availabilities': [],
        }])