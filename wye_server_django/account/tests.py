import datetime
import pytz
import urllib

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.test import TestCase

from account.models import WYEUser
from rooms.models import EscapeRoomSession


class AssertMixin(object):
    def assertUserLoggedIn(self, user, response):
        sessionid = response.cookies["sessionid"].value
        session = Session.objects.get(session_key=sessionid)
        session_user_id = int(session.get_decoded().get("_auth_user_id"))
        self.assertEqual(user.id, session_user_id)

    def assertUserLoggedOut(self, user, response):
        sessionid = response.cookies["sessionid"].value
        self.assertEqual(sessionid, "")


class WYEUserCreation(AssertMixin, TestCase):
    def setUp(self):
        self.graph_url = "/graphql/"

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

        response = self.client.post(self.graph_url, {"query": mutation})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'{"data":{"createUser":{"user":{"email":"romain@wye.com","pseudo":"Romain"}}}}',
        )
        self.assertTrue(
            WYEUser.objects.filter(email="romain@wye.com", pseudo="Romain").exists()
        )

    def test_send_create_user_mutation_direct_logs_the_user_in(self):
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
        self.assertFalse(Session.objects.exists())

        response = self.client.post(self.graph_url, {"query": mutation})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'{"data":{"createUser":{"user":{"email":"romain@wye.com","pseudo":"Romain"}}}}',
        )

        created_user = WYEUser.objects.get(email="romain@wye.com", pseudo="Romain")
        self.assertUserLoggedIn(created_user, response)


class WYEUserLogin(AssertMixin, TestCase):
    def setUp(self):
        self.graph_url = "/graphql/"

    def test_send_login_user_mutation_successfully_logs_a_user(self):
        user = get_user_model().objects.create_user(
            email="romain@wye.com", pseudo="Romain", password="pass"
        )

        mutation = """
            mutation {
              loginUser(email: "romain@wye.com", password: "pass") {
                user {
                  email,
                  pseudo
                }
              }
            }
        """

        self.assertFalse(Session.objects.exists())

        response = self.client.post(self.graph_url, {"query": mutation})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'{"data":{"loginUser":{"user":{"email":"romain@wye.com","pseudo":"Romain"}}}}',
        )

        self.assertUserLoggedIn(user, response)

    def test_send_login_user_mutation_does_not_log_a_user_on_wrong_credentials(self):
        user = get_user_model().objects.create_user(
            email="romain@wye.com", pseudo="Romain", password="pass"
        )

        mutation = """
            mutation {
              loginUser(email: "romain@wye.com", password: "wrong_password") {
                user {
                  email,
                  pseudo
                }
              }
            }
        """

        self.assertFalse(Session.objects.exists())

        response = self.client.post(self.graph_url, {"query": mutation})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"data":{"loginUser":{"user":null}}}')

        self.assertFalse(Session.objects.exists())


class WYEUserLogOut(AssertMixin, TestCase):
    def setUp(self):
        self.graph_url = "/graphql/"
        self.private_graph_url = "/private_graphql/"

    def test_send_logout_user_mutation_successfully_logs_out_a_user(self):
        user = get_user_model().objects.create_user(
            email="romain@wye.com", pseudo="Romain", password="pass"
        )

        mutation = """
            mutation {
              loginUser(email: "romain@wye.com", password: "pass") {
                user {
                  email,
                  pseudo
                }
              }
            }
        """
        response = self.client.post(self.graph_url, {"query": mutation})
        self.assertUserLoggedIn(user, response)

        mutation_logout = """
            mutation {
              logoutUser {
                user {
                  email
                }
              }
            }
        """

        response = self.client.post(self.private_graph_url, {"query": mutation_logout})

        self.assertEqual(response.content, b'{"data":{"logoutUser":null}}')
        self.assertEqual(response.status_code, 200)
        self.assertUserLoggedOut(user, response)

    def test_cannot_log_out_if_user_is_anonymous(self):
        mutation_logout = """
            mutation {
              logoutUser {
                user {
                  email
                }
              }
            }
        """

        response = self.client.post(self.private_graph_url, {"query": mutation_logout})

        self.assertEqual(response.status_code, 401)


class WYEWhoAmI(AssertMixin, TestCase):
    def setUp(self):
        self.private_graph_url = "/private_graphql/"

    def test_returns_401_if_user_is_anonymous(self):
        query = """
            {
                whoami
            }
        """

        response = self.client.get(self.private_graph_url, {"query": query})

        self.assertEqual(response.status_code, 401)

    def test_returns_200_if_user_is_authenticated(self):
        user = get_user_model().objects.create_user(
            email="romain@wye.com", pseudo="Romain", password="pass"
        )

        query = """
            {
                whoami
            }
        """

        self.client.login(email="romain@wye.com", password="pass")
        response = self.client.get(self.private_graph_url, {"query": query})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"data":{"whoami":"I am romain@wye.com"}}')


class WYEEscapeRoomSessions(AssertMixin, TestCase):
    def setUp(self):
        self.private_graph_url = "/private_graphql/"
        self.user = get_user_model().objects.create_user(
            email="romain@wye.com", pseudo="Romain", password="pass"
        )

        self.client.login(email="romain@wye.com", password="pass")

    def test_returns_nothing_if_no_escape_rooms(self):

        query = """
            {
                roomSessions {
                  name
                  playedDatetime
                  durationTime
                  numberOfHints
                }
            }
        """

        response = self.client.get(self.private_graph_url, {"query": query})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"data":{"roomSessions":[]}}')

    def test_returns_all_escape_rooms_for_a_given_user(self):
        EscapeRoomSession.objects.create(
            name="Escape Room Toulouse",
            played_datetime=datetime.datetime(2001, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
            duration_time=datetime.timedelta(minutes=50, seconds=00),
            number_of_hints=2,
            user=self.user,
        )

        query = """
            {
                roomSessions {
                  name
                  playedDatetime
                  durationTime
                  numberOfHints
                }
            }
        """

        response = self.client.get(self.private_graph_url, {"query": query})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'{"data":{"roomSessions":[{"name":"Escape Room Toulouse","playedDatetime":"2001-01-01T12:00:00+00:00","durationTime":3000.0,"numberOfHints":2}]}}',
        )

    def test_does_not_return_room_sessions_for_a_different_user(self):

        new_user = get_user_model().objects.create_user(
            email="new-user@wye.com", pseudo="NewUser", password="NewUser"
        )
        EscapeRoomSession.objects.create(
            name="Escape Room Toulouse",
            played_datetime=datetime.datetime(2001, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
            duration_time=datetime.timedelta(minutes=50, seconds=00),
            number_of_hints=2,
            user=new_user,
        )

        query = """
            {
                roomSessions {
                  name
                  playedDatetime
                  durationTime
                  numberOfHints
                }
            }
        """

        response = self.client.get(self.private_graph_url, {"query": query})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"data":{"roomSessions":[]}}')

    def test_can_create_room_session(self):
        mutation = """
            mutation {
              createRoomSession(name: "Escape room Youkidea", playedDatetime:"2012-11-23T13:32:00+00:00", durationTime:1200.0, numberOfHints:0) {
                roomSession {
                  name
                }
              }
            }
        """
        self.assertFalse(EscapeRoomSession.objects.exists())

        response = self.client.post(self.private_graph_url, {"query": mutation})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            EscapeRoomSession.objects.filter(
                name="Escape room Youkidea",
                played_datetime=datetime.datetime(
                    2012, 11, 23, 13, 32, tzinfo=pytz.UTC
                ),
                duration_time=datetime.timedelta(seconds=1200),
                number_of_hints=0,
                user=self.user,
            ).exists()
        )

