from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Настройка отображения пользователя в админке Django.
    Добавляем поля telegram_id и chat_id.
    """

    list_display = (
        "username",
        "email",
        "telegram_id",
        "chat_id",
        "is_staff",
        "is_active",
        "date_joined",
    )

    list_filter = ("is_staff", "is_active", "date_joined")
    search_fields = ("username", "email", "telegram_id")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Telegram",
            {
                "fields": ("telegram_id", "chat_id"),
                "description": "Данные для интеграции с Telegram-ботом",
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Telegram", {"fields": ("telegram_id", "chat_id")}),
    )
