from django.core.exceptions import ValidationError
from django.db.models import query
from django.test import TestCase
from .models import User, Professional, account_activation_token
from graphql_jwt.testcases import JSONWebTokenTestCase
import json
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
        user = User(
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

class LoginTest(JSONWebTokenTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@tst.com',
            password='abda1234',
            is_active=True,
        )
        self.client.authenticate(self.user)

    def execute(self, query, variables):
        return json.loads(json.dumps(self.client.execute(
            query, variables
        ).to_dict(dict_class=dict)))

    def test_activation_user(self):
        self.client.logout()
        self.user.is_active = False
        self.user.save()
        self.assertEqual(self.user.is_active, False)
        query = '''
            mutation ActivateUser($input: UserActivationInput!){
                activateUser(input: $input) {
                    isActive
                }
            }
        '''
        result = self.execute(query, {
            'input': {
                'token': account_activation_token.make_token(self.user),
                'uuid': str(self.user.uuid)
            }
        })
        self.assertNotIn('errors', result)
        self.assert_(result['data']['activateUser']['isActive'])
        user = User.objects.get(email=self.user.email)
        self.assert_(user.is_active)

    def test_get_user(self):
        query = '''
            mutation Login($email: String!, $password: String!) {
                tokenAuth(email: $email, password: $password) {
                    payload
                    refreshExpiresIn
                }
            }
        '''

        variables = {
            'email': self.user.email,
            'password': 'abda1234'
        }

        result = self.execute(query, variables)
        assert result['data']['tokenAuth']['payload']['email'] == self.user.email

    def test_sign_up(self):
        query = '''
            mutation SignUp($credentials: UserCreationInput!){
                createUser(input: $credentials) {
                    user {
                        fullName
                        uuid
                    }
                }
            }
        '''

        result = self.execute(query, dict(credentials={
            "fullName": "Teste Da Silva",
            "email": "ttt@ggg.com",
            "password1": "avg12340",
            "password2": "avg12340"
        }))

        assert not 'error' in result
        assert 'data' in result
        assert not 'password' in result['data']['createUser']['user']

    def test_update_user(self):
        self.client.authenticate(self.user)
        query = '''
            mutation UpdateUser($data: UserUpdateInput!){
                updateUser(input: $data){
                    user {
                        fullName
                        uuid
                        email
                    }
                }
            }
        '''
        result = self.execute(query, {
            'data': {
                'fullName': "Nerso da Capitinga",
                'email': self.user.email
            }
        })
        self.assertEqual(result, {
            'data': {
                'updateUser': {
                    'user': {
                        'fullName': 'Nerso da Capitinga',
                        'uuid': str(self.user.uuid),
                        'email': self.user.email,
                    }
                }
            }
        })
    
    def test_update_user_without_login(self):
        self.client.logout()
        query = '''
            mutation UpdateUser($data: UserUpdateInput!){
                updateUser(input: $data){
                    user {
                        fullName
                        uuid
                        email
                    }
                }
            }
        '''
        result = self.execute(query, {
            'data': {
                'fullName': "Nerso da Capitinga",
                'email': self.user.email
            }
        })
        self.assertEqual(result['errors'][0]['message'], 'You do not have permission to perform this action')

    def test_reset_password(self):
        self.client.logout()
        query = '''
            mutation ResetPassword($input: PasswordResetInput!){
                resetPassword(input: $input){
                    email
                }
            }
        '''
        result = self.execute(query, {
            'input': {
                'email': self.user.email
            }
        })
        self.assertEqual(result, {
            'data': {
                'resetPassword': {
                    'email': self.user.email
                }
            }
        })
