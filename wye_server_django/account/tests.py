import urllib

from django.test import TestCase

from account.models import WYEUser


class WYEUserCreation(TestCase):

    def setUp(self):
        self.graph_url = '/graphql'

    def test_send_create_user_mutation_successfully_creates_a_user(self):
        mutation = """
            mutation {
              createUser(email: "romain@wye.com", pseudo: "Romain", password: "pass") {
                user {
                  email,
                  pseudo
                }
              }
            }
        """
        encodedMutation = urllib.parse.quote(mutation)
        print(encodedMutation)
        response = self.client.get(self.graph_url, {'mutation': encodedMutation})

        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WYEUser.objects.count(), 1)
