from django.test import TestCase

from .models import CustomUser, Session

USER_CREDENTIALS = ("testuser", "testuser@moviements.ru", "testpassword")
SUPERUSER_CREDENTIALS = ("superuser", "superuser@moviements.ru", "superpassword")

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10 10_15) AppleWebKit/537.36 (KHTML, like Gecko)"
REMOTE_IP = "127.0.0.1"


class CustomUserTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username=USER_CREDENTIALS[0], email=USER_CREDENTIALS[1]
        )
        self.user.set_password(USER_CREDENTIALS[2])

    def test_create_user(self):
        self.assertEqual(self.user.username, USER_CREDENTIALS[0])
        self.assertEqual(self.user.email, USER_CREDENTIALS[1])
        self.assertFalse(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertTrue(self.user.check_password(USER_CREDENTIALS[2]))

    def test_create_superuser(self):
        superuser = CustomUser.objects.create_superuser(
            username=SUPERUSER_CREDENTIALS[0], email=SUPERUSER_CREDENTIALS[1]
        )
        superuser.set_password(SUPERUSER_CREDENTIALS[2])
        self.assertEqual(superuser.username, SUPERUSER_CREDENTIALS[0])
        self.assertEqual(superuser.email, SUPERUSER_CREDENTIALS[1])
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.check_password(SUPERUSER_CREDENTIALS[2]))

    def tearDown(self):
        self.user.delete()


class SessionsTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username=USER_CREDENTIALS[0], email=USER_CREDENTIALS[1]
        )
        self.user.set_password(USER_CREDENTIALS[2])

        self.session = Session.objects.create(
            user=self.user, user_agent=USER_AGENT, ip_address=REMOTE_IP
        )
        self.session2 = Session.objects.create(
            user=self.user, user_agent=USER_AGENT, ip_address=REMOTE_IP + "2"
        )

    def test_create_session(self):
        self.assertEqual(self.session.user, self.user)
        self.assertEqual(self.session.user_agent, USER_AGENT)
        self.assertEqual(self.session.ip_address, REMOTE_IP)
        self.assertIsNotNone(self.session.created_at)
        self.assertIsNotNone(self.session.updated_at)

    def test_user_session(self):
        self.assertEqual(self.user.sessions.count(), 2)

        self.assertEqual(self.session.user, self.user)
        self.assertEqual(self.session.user_agent, USER_AGENT)
        self.assertEqual(self.session.ip_address, REMOTE_IP)
        self.assertIsNotNone(self.session.created_at)
        self.assertIsNotNone(self.session.updated_at)

        self.assertEqual(self.session2.user, self.user)
        self.assertEqual(self.session2.user_agent, USER_AGENT)
        self.assertEqual(self.session2.ip_address, REMOTE_IP + "2")
        self.assertIsNotNone(self.session2.created_at)
        self.assertIsNotNone(self.session2.updated_at)

    def tearDown(self):
        self.user.delete()
        self.session.delete()
        self.session2.delete()
