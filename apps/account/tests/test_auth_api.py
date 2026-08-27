from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.test import APIClient


User = get_user_model()


class AuthAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="auth.test@taxigo.test",
            username="auth_test",
            first_name="Auth",
            last_name="Test",
            phone="+22673000001",
            role="CLIENT",
            password="TaxiGo1234!",
            email_verified_at=timezone.now(),
        )
    def test_verified_user_can_login(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "auth.test@taxigo.test",
                "password": "TaxiGo1234!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_login_cookie_authenticates_me_endpoint(self):
        login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "auth.test@taxigo.test",
                "password": "TaxiGo1234!",
            },
            format="json",
        )

        self.assertEqual(
            login_response.status_code,
            200
        )

        response = self.client.get(
            "/api/v1/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["email"],
            self.user.email
        )


    def test_unverified_user_cannot_login(self):
        unverified_user = User.objects.create_user(
            email="unverified@taxigo.test",
            username="unverified_user",
            password="TaxiGo1234!",
            phone="+22673000002",
            role="CLIENT",
        )

        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": unverified_user.email,
                "password": "TaxiGo1234!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )


    def test_wrong_password_cannot_login(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": self.user.email,
                "password": "WrongPassword!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            401
        )


    def test_unauthenticated_user_cannot_access_me(self):
        response = self.client.get(
            "/api/v1/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            401
        )


    def test_refresh_works_with_refresh_cookie(self):
        login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": self.user.email,
                "password": "TaxiGo1234!",
            },
            format="json",
        )

        self.assertEqual(
            login_response.status_code,
            200
        )

        refresh_response = self.client.post(
            "/api/v1/auth/refresh/"
        )

        self.assertEqual(
            refresh_response.status_code,
            200
        )

        # Vérifier qu'on peut toujours accéder à une route protégée
        me_response = self.client.get(
            "/api/v1/auth/me/"
        )

        self.assertEqual(
            me_response.status_code,
            200
        )

        self.assertEqual(
            me_response.data["email"],
            self.user.email
        )


    def test_logout_removes_authentication(self):
        login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": self.user.email,
                "password": "TaxiGo1234!",
            },
            format="json",
        )

        self.assertEqual(
            login_response.status_code,
            200
        )

        logout_response = self.client.post(
            "/api/v1/auth/logout/"
        )

        self.assertEqual(
            logout_response.status_code,
            204
        )

        me_response = self.client.get(
            "/api/v1/auth/me/"
        )

        self.assertEqual(
            me_response.status_code,
            401
        )
        