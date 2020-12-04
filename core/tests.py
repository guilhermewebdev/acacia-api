from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import response
from .models import Availability, User, Professional, account_activation_token
from django.utils.timezone import now, timedelta

class TestUser(TestCase):

    def test_creation(self):
        user = User.objects.create_user(
            email='teste@teste.com',
            full_name='Guido Rossum',
            cellphone='32999198822',
            password='tetris2',
        )
        user.full_clean()
        user.save()
    
    def test_professional_creation(self):
        user = User.objects.create_user(
            email='teste1@teste.com',
            full_name='Linuz Torvalds',
            cellphone='31988776655',
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
            cellphone='31988776655',
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
            cellphone='31988776655',
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
            cellphone='31988776655',
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

    def test_confirmation_email(self):
        user = User.objects.create_user(
            email='test@tst.com',
            password='abda1234',
        )
        user.save()
        self.assertNotEqual(settings.SENDER_EMAIL, None)
        self.assert_(user.confirm_email())

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
        response = self.client.get('/professionals.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{
            'uuid': str(self.professional.uuid),
            'about': self.professional.about,
            'full_name': self.professional.user.full_name,
            'email': self.professional.user.email,
            'avatar': None,
            'is_active': self.professional.user.is_active,
            'avg_price': float(self.professional.avg_price),
            'state': 'MG',
            'city': self.professional.city,
            'occupation': self.professional.occupation,
            'skills': self.professional.skills,
            'avg_rating': self.professional.avg_rating,
            'url': f'http://testserver/professionals/{str(self.professional.uuid)}/'
        }])

    def test_create_professional(self):
        data = {
            'state': 'MG',
            'city':   'Belo Horizonte',
            'occupation': 'CI',
            'password1': 'acac333',
            'password2': 'acac333',
            'full_name': 'Pindamonhagaba da Silva',
            'email': 'dudu@google.com',
            'cpf': '567.933.940-45',
            'rg': 'rj343534',
            'address': 'Lá mesmo',
            'zip_code': '33000-334',
            'coren': 39.999
        }
        response = self.client.post('/professionals/', data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.json())
        self.assertIn('uuid', response.json())

    def test_retrieve_professional(self):
        response = self.client.get(f'/professionals/{str(self.professional.uuid)}/')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('uuid', data)
        self.assertEqual(data['occupation'], self.professional.occupation)

    def test_availabilities(self):
        availability = Availability.objects.create(
            professional=self.professional,
            start_datetime=(now() + timedelta(days=1)),
            end_datetime=(now() + timedelta(days=1, hours=2))
        )
        availability.save()
        response = self.client.get(
            f'/professionals/{str(self.professional.uuid)}/availabilities.json',
        )
        json = response.json()
        self.assertEqual(json[0].get('uuid'), str(availability.uuid))


class TestUserREST(TestCase):

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
    
    def test_get_profile(self):
        self.client.login(username=self.user.email, password='abda1234')
        response = self.client.get('/users/profile.json')
        data = response.json()
        self.assertIn('uuid', data)
        self.assertEqual(data['uuid'], str(self.user.uuid))

    def test_create_profile(self):
        self.client.logout()
        data = {
            'email': 'email@gmail.com',
            'full_name': 'Teste da Silva',
            'password1': 'abda1234',
            'password2': 'abda1234',
        }
        response = self.client.post('/users.json', data=data)
        json = response.json()
        self.assertIn('uuid', json)
        self.assertEqual(json['is_active'], False)

    def test_user_deletion(self):
        user = User.objects.create_user(
            email='tes3t@tst.com',
            password='abda1234',
            is_active=True,
        )
        user.save()
        data = {
            'email': user.email,
            'password': 'abda1234'
        }
        self.client.login(username=user.email, password='abda1234')
        response = self.client.delete(
            '/users/profile.json',
            data=data,
            content_type='application/json'
        )
        self.assertEqual(response.json(), {
            'deleted': True
        })

    def test_change_password(self):
        self.client.logout()
        self.client.login(username=self.user.email, password='abda1234')
        data = {
            'password': 'abda1234',
            'password1': 'abda143501',
            'password2': 'abda143501',
        }
        response = self.client.patch(
            '/users/profile.json',
            data=data,
            content_type='application/json'
        )
        json = response.json()
        self.assertIn('uuid', json)
        self.assertEqual(response.status_code, 200)

    def test_activate_user(self):
        user = User.objects.create_user(
            email='testdd@tst.com',
            password='abda1234',
        )
        user.save()
        data = {
            'token': account_activation_token.make_token(user)
        }
        response = self.client.put(
            f'/users/{user.uuid}/',
            data=data,
            content_type='application/json'
        )
        json = response.json()
        self.assertIn('is_active', json)
        self.assertEqual(json['is_active'], True)

    def test_list_self_availabilities(self):
        self.client.login(username=self.professional.user.email, password='abda1234')
        response = self.client.get('/users/profile/availabilities.json')
        json = response.json()
        self.assertIn('uuid', json[0])
        self.assertQuerysetEqual(
            self.professional.availabilities.all(),
            json
        )