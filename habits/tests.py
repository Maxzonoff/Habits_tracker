from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Habit

User = get_user_model()


class HabitTests(APITestCase):
    """
    Тесты для привычек.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword123"
        )

        self.user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpassword123"
        )

        self.client.force_authenticate(user=self.user)

        self.habit_data = {
            "place": "Дом",
            "time": "07:00:00",
            "action": "Выпить стакан воды",
            "is_pleasant": False,
            "reward": "Чашка кофе",
            "period": 1,
            "duration": 60,
            "is_public": False,
        }

    def test_create_habit(self):
        """Тест создания привычки."""
        response = self.client.post("/habits/", self.habit_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)
        self.assertEqual(Habit.objects.first().owner, self.user)

    def test_create_habit_unauthorized(self):
        """Тест создания привычки без авторизации."""
        self.client.force_authenticate(user=None)
        response = self.client.post("/habits/", self.habit_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_habits(self):
        """Тест списка привычек."""
        Habit.objects.create(owner=self.user, **self.habit_data)
        Habit.objects.create(owner=self.user2, **self.habit_data)

        response = self.client.get("/habits/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_habit_pagination(self):
        """Тест пагинации."""
        for i in range(7):
            data = self.habit_data.copy()
            data["action"] = f"Привычка {i}"
            Habit.objects.create(owner=self.user, **data)

        response = self.client.get("/habits/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])

    def test_retrieve_habit(self):
        """Тест получения одной привычки."""
        habit = Habit.objects.create(owner=self.user, **self.habit_data)
        response = self.client.get(f"/habits/{habit.id}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "Выпить стакан воды")

    def test_update_habit(self):
        """Тест обновления привычки."""
        habit = Habit.objects.create(owner=self.user, **self.habit_data)
        update_data = {"action": "Выпить 2 стакана воды"}
        response = self.client.patch(f"/habits/{habit.id}/", update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "Выпить 2 стакана воды")

    def test_delete_habit(self):
        """Тест удаления привычки."""
        habit = Habit.objects.create(owner=self.user, **self.habit_data)
        response = self.client.delete(f"/habits/{habit.id}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)

    def test_cannot_access_other_user_habit(self):
        """Тест: нельзя получить чужую привычку."""
        habit = Habit.objects.create(owner=self.user2, **self.habit_data)
        response = self.client.get(f"/habits/{habit.id}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_public_habits_list(self):
        """Тест списка публичных привычек."""
        data = self.habit_data.copy()
        data["is_public"] = True
        Habit.objects.create(owner=self.user, **data)
        Habit.objects.create(owner=self.user2, **data)

        response = self.client.get("/habits/public/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_validation_reward_and_linked_habit(self):
        """Тест валидации: нельзя одновременно reward и linked_habit."""
        pleasant_data = self.habit_data.copy()
        pleasant_data["is_pleasant"] = True
        pleasant_data["reward"] = ""
        pleasant_habit = Habit.objects.create(owner=self.user, **pleasant_data)

        data = self.habit_data.copy()
        data["linked_habit"] = pleasant_habit.id
        response = self.client.post("/habits/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validation_duration_max(self):
        """Тест валидации: duration не более 120 сек."""
        data = self.habit_data.copy()
        data["duration"] = 200
        response = self.client.post("/habits/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validation_pleasant_no_reward(self):
        """Тест валидации: у приятной привычки не может быть reward."""
        data = self.habit_data.copy()
        data["is_pleasant"] = True
        response = self.client.post("/habits/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validation_period_max(self):
        """Тест валидации: period не более 7 дней."""
        data = self.habit_data.copy()
        data["period"] = 10
        response = self.client.post("/habits/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_linked_habit_must_be_pleasant(self):
        """Тест: связанная привычка должна быть приятной."""
        not_pleasant = Habit.objects.create(owner=self.user, **self.habit_data)

        data = self.habit_data.copy()
        data["reward"] = ""
        data["linked_habit"] = not_pleasant.id
        response = self.client.post("/habits/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
