from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    Пароль шифруется автоматически.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="Минимум 8 символов",
    )
    password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}, label="Подтверждение пароля"
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "password_confirm",
            "telegram_id",
            "chat_id",
        )

    def validate(self, data):
        """
        Проверяем, что пароли совпадают.
        """
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают.")
        return data

    def create(self, validated_data):
        """
        Создаём пользователя. Убираем password_confirm, т.к. его нет в модели.
        """
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотра и редактирования профиля.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "telegram_id",
            "chat_id",
            "first_name",
            "last_name",
        )
        read_only_fields = ("id", "username", "email")
