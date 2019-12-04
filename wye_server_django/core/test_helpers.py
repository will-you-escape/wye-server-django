from django.contrib.sessions.models import Session


class AssertMixin(object):
    def assertUserLoggedIn(self, user, response):
        sessionid = response.cookies["sessionid"].value
        session = Session.objects.get(session_key=sessionid)
        session_user_id = int(session.get_decoded().get("_auth_user_id"))
        self.assertEqual(user.id, session_user_id)

    def assertUserLoggedOut(self, user, response):
        sessionid = response.cookies["sessionid"].value
        self.assertEqual(sessionid, "")
