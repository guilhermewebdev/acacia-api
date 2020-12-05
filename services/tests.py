from django.http.request import HttpRequest
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

class TestProposalREST(TestCase):

    def setUp(self):
        self.professional = Professional.objects.create(
            user=User.objects.create_user(
                email='dance@balance.com',
                password='abda143501',
                is_active=True,
            )
        )
        self.professional.save()
        self.user = User.objects.create_user(
            email='bate@bola.com',
            password='abda1234',
            is_active=True,
        )
        self.user.save()
        self.proposal = Proposal(
            client=self.user,
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

    def test_list_sent_proposals(self):
        self.client.login(request=HttpRequest(), username=self.user.email, password='abda1234')
        response = self.client.get('/proposals/sent.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['uuid'], str(self.proposal.uuid))

    def test_list_received_proposals(self):
        self.client.logout()
        self.client.login(request=HttpRequest(), username=self.professional.user.email, password='abda143501')
        response = self.client.get('/proposals/received.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['uuid'], str(self.proposal.uuid))

    def test_list_proposals(self):
        self.client.login(request=HttpRequest(), username=self.professional.user.email, password='abda143501')
        response = self.client.get('/proposals/?format=json')
        self.assertEqual(response.status_code, 405, msg=response.content)

    def test_sent_proposal(self):
        self.client.login(request=HttpRequest(), username=self.user.email, password='abda1234')
        data = dict(
            client=str(self.user.uuid),
            professional=str(self.professional.uuid),
            city='Curitiba',
            state='PR',
            professional_type='AE',
            service_type='AC',
            start_datetime=(TODAY + timedelta(days=1)).isoformat(),
            end_datetime=(TODAY + timedelta(days=3)).isoformat(),
            value=300.00,
            description='Lorem Ipsum dolores'
        )
        response = self.client.post('/proposals.json', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200, msg=response.content)
        self.assertIn('uuid', response.json())

    def test_update_proposal(self):
        self.client.login(request=HttpRequest(), username=self.user.email, password='abda1234')
        data = dict(
            client=str(self.user.uuid),
            professional=str(self.professional.uuid),
            city='Curitiba',
            state='PR',
            professional_type='AE',
            service_type='AC',
            start_datetime=(TODAY + timedelta(days=1)).isoformat(),
            end_datetime=(TODAY + timedelta(days=3)).isoformat(),
            value=300.00,
            description='Lorem Ipsum dolores'
        )
        response = self.client.put(f'/proposals/{self.proposal.uuid}.json', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200, msg=response.json())
        self.assertIn('uuid', response.json())
        self.assertEqual(str(self.proposal.uuid), response.json()['uuid'])

    