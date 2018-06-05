import urllib

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.test import TestCase

from account.models import WYEUser


class WYEUserCreation(TestCase):

    def setUp(self):
        self.graph_url = '/graphql/'

    def test_send_create_user_mutation_successfully_creates_a_user(self):
        mutation = '''
            mutation {
              createUser(email: "romain@wye.com", pseudo: "Romain", password: "pass") {
                user {
                  email,
                  pseudo
                }
              }
            }
        '''

        response = self.client.post(self.graph_url, {'query': mutation})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"data":{"createUser":{"user":{"email":"romain@wye.com","pseudo":"Romain"}}}}')
        self.assertTrue(WYEUser.objects.filter(email="romain@wye.com", pseudo="Romain").exists())


class WYEUserLogin(TestCase):

    def setUp(self):
        self.graph_url = '/graphql/'

    def test_send_login_user_mutation_successfully_logs_a_user(self):
        user = get_user_model().objects.create_user(
            email="romain@wye.com",
            pseudo="Romain",
            password="pass")

        mutation = '''
            mutation {
              loginUser(email: "romain@wye.com", password: "pass") {
                user {
                  email,
                  pseudo
                }
              }
            }
        '''

        self.assertFalse(Session.objects.exists())

        response = self.client.post(self.graph_url, {'query': mutation})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"data":{"loginUser":{"user":{"email":"romain@wye.com","pseudo":"Romain"}}}}')

        sessionid = response.cookies['sessionid'].value
        session = Session.objects.get(session_key=sessionid)
        session_user_id = int(session.get_decoded().get('_auth_user_id'))
        self.assertEqual(user.id, session_user_id)
