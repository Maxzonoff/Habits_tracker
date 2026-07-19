from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


from .models import Habit
from .paginations import HabitPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import HabitListSerializer, HabitSerializer
from .services import send_telegram_message


class HabitListCreateView(generics.ListCreateAPIView):
    """
    Список своих привычек + создание новой.
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        habit = serializer.save(owner=self.request.user)

        # Логи для отладки
        user = self.request.user
        print("=== DEBUG: Привычка создана ===")
        print(f"Пользователь: {user.username}")
        print(f"Chat ID: {user.chat_id}")
        print(f"Telegram ID: {user.telegram_id}")

        # Отправляем тестовое сообщение в Telegram
        if user.chat_id:
            message = (
                f"✅ <b>Привычка создана!</b>\n\n"
                f"🎯 {habit.action}\n"
                f"📍 {habit.place}\n"
                f"⏰ {habit.time}\n\n"
                f"Я буду напоминать тебе о ней!"
            )
            result = send_telegram_message(user.chat_id, message)
            print(f"Результат отправки: {result}")
        else:
            print(f"WARNING: У пользователя {user.username} нет chat_id!")

        return habit


class HabitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    CRUD для одной привычки.
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)


class PublicHabitListView(generics.ListAPIView):
    """
    Список публичных привычек.
    """

    serializer_class = HabitListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination
    queryset = Habit.objects.filter(is_public=True)
