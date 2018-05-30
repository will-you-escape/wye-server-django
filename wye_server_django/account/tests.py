import urllib

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
        query='''
            query TestQuery { test }
            mutation TestMutation { writeTest { test } }
        '''

        response = self.client.post(self.graph_url, {'query': mutation})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"data":{"createUser":{"user":{"email":"romain@wye.com","pseudo":"Romain"}}}}')
        self.assertTrue(WYEUser.objects.filter(email="romain@wye.com", pseudo="Romain").exists())
