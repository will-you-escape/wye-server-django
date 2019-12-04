import datetime
import pytz

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.test_helpers import AssertMixin
from rooms.models import EscapeRoomSession

# Create your tests here.
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
