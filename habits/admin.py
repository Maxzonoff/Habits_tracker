from django.contrib import admin

from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """
    Настройка отображения привычек в админке.
    """


    list_display = (
        "action",
        "owner",
        "place",
        "time",
        "is_pleasant",
        "period",
        "duration",
        "is_public",
        "created_at",
    )


    list_filter = ("is_pleasant", "is_public", "period", "created_at")


    search_fields = ("action", "place", "owner__username")


    readonly_fields = ("created_at",)

    fieldsets = (
        ("Основная информация", {"fields": ("owner", "action", "place", "time")}),
        ("Тип привычки", {"fields": ("is_pleasant",)}),
        (
            "Вознаграждение",
            {
                "fields": ("linked_habit", "reward"),
                "description": "Выберите либо связанную привычку, либо вознаграждение",
            },
        ),
        ("Настройки", {"fields": ("period", "duration", "is_public")}),
        (
            "Служебные",
            {"fields": ("created_at", "last_completed"), "classes": ("collapse",)},
        ),
    )
