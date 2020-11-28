from django.core.exceptions import ValidationError
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
                login(email: $email, password: $password) {
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
        assert result['data']['login']['payload']['email'] == self.user.email

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

    def test_delete_user(self):
        user = User.objects.create_user(
            email='test@tsdt.com',
            password='abda1234',
            is_active=True,
        )
        user.save()
        self.client.authenticate(user)
        query = '''
            mutation DeleteUser($input: UserDeletionInput!){
                deleteUser(input: $input){
                    deleted
                }
            }
        '''
        result = self.execute(query, {
            'input': {
                'password': 'abda1234',
                'email': user.email
            }
        })
        self.assertEqual(result,{
            'data': {
                'deleteUser': {
                    'deleted': True,
                }
            }
        })

    def test_change_password(self):
        self.client.authenticate(self.user)
        query = '''
            mutation ChangePassword($input: PasswordChangeInput!){
                changePassword(input: $input){
                    changed
                }
            }
        '''
        variables = {
            'input': {
                'password': 'abda1234',
                'password1': 'xicotico',
                'password2': 'xicotico',
            }
        }
        result = self.execute(query, variables)
        self.assertEqual(result, {
            'data': {
                'changePassword': {
                    'changed': True,
                }
            }
        })
        user = User.objects.get(email=self.user.email)
        self.assert_(user.check_password('xicotico'))


class ProfessionalTest(JSONWebTokenTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@tst.com',
            password='abda1234',
            is_active=True,
        )
        self.client.authenticate(self.user)
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

    def execute(self, query, variables):
        return json.loads(json.dumps(self.client.execute(query, variables).to_dict(dict_class=dict)))

    def test_creation_professional(self):
        query = '''
            mutation CreateProfessional($input: ProfessionalCreationInput!) {
                createProfessional(input: $input) {
                    professional {
                        user {
                            fullName
                        }
                    }
                }
            }
        '''
        variables = {
            'input': {
                'fullName': 'Fulano de Tal',
                'email': 'gru@ted.com',
                'password1': 'vd34560',
                'password2': 'vd34560',
                'state': 'MG',
                'city': 'Belo Horizonte',
                'address': 'Any local',
                'zipCode': '36200-000',
                'rg': 'rj46565',
                'occupation': 'CI',
                'coren': '20.000',
                'cpf': '661.034.190-77',
            }
        }
        result = self.execute(query, variables)
        self.assertEqual(result, {
            'data': {
                'createProfessional': {
                    'professional': {
                        'user': {
                            'fullName': variables['input']['fullName']
                        }
                    }
                }
            }
        })

    def test_professional_update(self):
        self.client.authenticate(self.professional.user)
        query = '''
            mutation UpdateProfessional($input: ProfessionalUpdateInput!){
                updateProfessional(input: $input){
                    professional {
                        state
                    }
                }
            }
        '''
        variables = {
            'input': {
                'state': 'MG',
                'city': 'Belo Horizonte',
                'address': 'Any local',
                'zipCode': '36200-000',
                'rg': 'rj46565',
                'occupation': 'CI',
                'coren': '20.000',
                'cpf': '661.034.190-77',
            }
        }
        result = self.execute(query, variables)
        self.assertEqual(result, {
            'data': {
                'updateProfessional': {
                    'professional': {
                        'state': variables['input']['state'],
                    }
                }
            }
        })

    def test_professional_deletion(self):
        self.client.authenticate(self.professional.user)
        query = '''
            mutation DeleteProfessional($input: ProfessionalDeletionInput!){
                deleteProfessional(input: $input){
                    deleted
                }
            }
        '''
        variables = {
            'input': {
                'email': self.professional.user.email,
                'password': 'abda1234',
            }
        }
        result = self.execute(query, variables)
        self.assertEqual(result, {
            'data': {
                'deleteProfessional': {
                    'deleted': True,
                }
            }
        })

    def test_list_professionals(self):
        self.client.logout()
        query = '''
            {
                professionals {
                    data {
                        coren
                    }
                }
            }
        '''
        result = self.execute(query, {})
        self.assertEqual(result, {
            'data': {
                'professionals': {
                    'data': [
                        {
                            'coren': self.professional.coren
                        }
                    ]
                }
            }
        })

    def test_filter_professional(self):
        self.client.logout()
        query = '''
            query FindProfessionals($filters: FilterProfessionalInput){
                professionals {
                    data(filters: $filters) {
                        coren
                    }
                }
            }
        '''
        variables = {
            'filters': {
                'state': self.professional.state
            }
        }
        result = self.execute(query, variables)
        self.assertEqual(result, {
            'data': {
                'professionals': {
                    'data': [
                        {
                            'coren': self.professional.coren
                        }
                    ]
                }
            }
        })
