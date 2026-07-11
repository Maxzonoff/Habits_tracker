from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Наследуемся от AbstractUser — она уже содержит:
    - username
    - email
    - password
    - first_name, last_name
    - is_active, is_staff, is_superuser
    - date_joined, last_login

    Добавляем поля для Telegram-интеграции.
    """

    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Обязательное поле. Уникальный email.",
    )

    telegram_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Telegram ID",
        help_text="ID пользователя в Telegram для отправки напоминаний",
    )

    chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Chat ID",
        help_text="ID чата в Telegram для отправки сообщений",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username or self.email
