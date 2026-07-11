from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserTests(APITestCase):
    """
    Тесты для пользователей.
    """

    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.profile_url = reverse("profile")

        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "password_confirm": "testpassword123",
        }

        self.login_data = {
            "username": "testuser",
            "password": "testpassword123",
        }

    def test_user_registration(self):
        """Тест регистрации пользователя."""
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["username"], "testuser")
        self.assertEqual(User.objects.count(), 1)

    def test_user_registration_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями."""
        data = self.user_data.copy()
        data["password_confirm"] = "wrongpassword"
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_short_password(self):
        """Тест регистрации с коротким паролем."""
        data = self.user_data.copy()
        data["password"] = "short"
        data["password_confirm"] = "short"
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Тест авторизации."""
        self.client.post(self.register_url, self.user_data, format="json")
        response = self.client.post(self.login_url, self.login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "testuser")

    def test_user_login_wrong_password(self):
        """Тест авторизации с неверным паролем."""
        self.client.post(self.register_url, self.user_data, format="json")
        data = self.login_data.copy()
        data["password"] = "wrongpassword"
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_profile_get(self):
        """Тест получения профиля."""
        register_response = self.client.post(
            self.register_url, self.user_data, format="json"
        )
        token = register_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.profile_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")

    def test_user_profile_update(self):
        """Тест обновления профиля."""
        register_response = self.client.post(
            self.register_url, self.user_data, format="json"
        )
        token = register_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        update_data = {"first_name": "Test", "last_name": "User"}
        response = self.client.patch(self.profile_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Test")

    def test_user_profile_unauthorized(self):
        """Тест доступа к профилю без авторизации."""
        response = self.client.get(self.profile_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
