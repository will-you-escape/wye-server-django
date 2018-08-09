import urllib

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.test import TestCase

from account.models import WYEUser


class AssertMixin(object):

    def assertUserLoggedIn(self, user, response):
        sessionid = response.cookies['sessionid'].value
        session = Session.objects.get(session_key=sessionid)
        session_user_id = int(session.get_decoded().get('_auth_user_id'))
        self.assertEqual(user.id, session_user_id)

    def assertUserLoggedOut(self, user, response):
        sessionid = response.cookies['sessionid'].value
        self.assertEqual(sessionid, '')


class WYEUserCreation(AssertMixin, TestCase):

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

    def test_send_create_user_mutation_direct_logs_the_user_in(self):
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
        self.assertFalse(Session.objects.exists())

        response = self.client.post(self.graph_url, {'query': mutation})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"data":{"createUser":{"user":{"email":"romain@wye.com","pseudo":"Romain"}}}}')

        created_user = WYEUser.objects.get(email="romain@wye.com", pseudo="Romain")
        self.assertUserLoggedIn(created_user, response)


class WYEUserLogin(AssertMixin, TestCase):

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

        self.assertUserLoggedIn(user, response)


class WYEUserLogOut(AssertMixin, TestCase):

    def setUp(self):
        self.graph_url = '/graphql/'
        self.private_graph_url = '/private_graphql/'

    def test_send_logout_user_mutation_successfully_logs_out_a_user(self):
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
        response = self.client.post(self.graph_url, {'query': mutation})
        self.assertUserLoggedIn(user, response)

        mutation_logout = '''
            mutation {
              logoutUser {
                user {
                  email
                }
              }
            }
        '''

        response = self.client.post(self.private_graph_url, {'query': mutation_logout})

        self.assertEqual(response.content, b'{"data":{"logoutUser":null}}')
        self.assertEqual(response.status_code, 200)
        self.assertUserLoggedOut(user, response)

    def test_cannot_log_out_if_user_is_anonymous(self):
        mutation_logout = '''
            mutation {
              logoutUser {
                user {
                  email
                }
              }
            }
        '''

        response = self.client.post(self.private_graph_url, {'query': mutation_logout})

        self.assertEqual(response.status_code, 401)


class WYEWhoAmI(AssertMixin, TestCase):

    def setUp(self):
        self.private_graph_url = '/private_graphql/'

    def test_returns_401_if_user_is_anonymous(self):
        query = '''
            {
                whoami
            }
        '''

        response = self.client.get(self.private_graph_url, {'query': query})

        self.assertEqual(response.status_code, 401)

    def test_returns_200_if_user_is_authenticated(self):
        user = get_user_model().objects.create_user(
            email="romain@wye.com",
            pseudo="Romain",
            password="pass")

        query = '''
            {
                whoami
            }
        '''

        self.client.login(email="romain@wye.com", password="pass")
        response = self.client.get(self.private_graph_url, {'query': query})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"data":{"whoami":"I am romain@wye.com"}}')
