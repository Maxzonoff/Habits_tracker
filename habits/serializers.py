from rest_framework import serializers

from .models import Habit
from .validators import validate_habit


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для привычек.
    Включает валидацию из validators.py.
    """

    owner_name = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Habit
        fields = (
            "id",
            "owner",
            "owner_name",
            "place",
            "time",
            "action",
            "is_pleasant",
            "linked_habit",
            "reward",
            "period",
            "duration",
            "is_public",
            "created_at",
            "last_completed",
        )
        read_only_fields = ("id", "owner", "created_at", "last_completed")

    def validate(self, data):
        """
        Запускаем кастомную валидацию из validators.py.
        Передаём instance для корректной работы при обновлении.
        """
        return validate_habit(data, instance=getattr(self, "instance", None))


class HabitListSerializer(serializers.ModelSerializer):
    """
    Упрощённый сериализатор для списка привычек.
    Меньше полей — быстрее загружается.
    """

    owner_name = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Habit
        fields = (
            "id",
            "action",
            "place",
            "time",
            "is_pleasant",
            "is_public",
            "owner_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
