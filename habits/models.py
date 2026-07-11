from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Habit(models.Model):
    """
    Модель привычки.

    В книге привычка описывается формулой:
    "Я буду [ДЕЙСТВИЕ] в [ВРЕМЯ] в [МЕСТО]"

    Полезная привычка: действие, которое нужно выполнить.
    Приятная привычка: действие, которое можно прикрепить к полезной как вознаграждение.
    """

    # --- Владелец привычки ---
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Владелец",
    )

    # --- Основные поля (формула из книги) ---
    place = models.CharField(
        max_length=255, verbose_name="Место", help_text="Где выполнять привычку?"
    )

    time = models.TimeField(
        verbose_name="Время", help_text="Во сколько выполнять привычку?"
    )

    action = models.CharField(
        max_length=255,
        verbose_name="Действие",
        help_text="Что конкретно нужно сделать?",
    )

    # --- Признак приятной привычки ---
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
        help_text="True = приятная привычка (без вознаграждения), False = полезная привычка",
    )

    # --- Связанная привычка (только для полезных) ---
    linked_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_to",
        verbose_name="Связанная привычка",
        help_text="Приятная привычка, которая будет вознаграждением за выполнение",
    )

    # --- Вознаграждение (только для полезных) ---
    reward = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Вознаграждение",
        help_text="Чем себя порадовать после выполнения?",
    )

    # --- Периодичность ---
    PERIOD_CHOICES = [
        (1, "Каждый день"),
        (2, "Раз в 2 дня"),
        (3, "Раз в 3 дня"),
        (4, "Раз в 4 дня"),
        (5, "Раз в 5 дней"),
        (6, "Раз в 6 дней"),
        (7, "Раз в 7 дней"),
    ]

    period = models.PositiveSmallIntegerField(
        choices=PERIOD_CHOICES,
        default=1,
        verbose_name="Периодичность",
        help_text="Как часто выполнять привычку (в днях)",
    )

    # --- Время на выполнение ---
    duration = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        verbose_name="Время на выполнение (сек)",
        help_text="Сколько секунд займёт выполнение (макс. 120)",
    )

    # --- Признак публичности ---
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
        help_text="True = видна всем пользователям",
    )

    # --- Дата создания ---
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    # --- Дата последнего выполнения ---
    last_completed = models.DateTimeField(
        null=True, blank=True, verbose_name="Последнее выполнение"
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]

    def __str__(self):
        habit_type = "Приятная" if self.is_pleasant else "Полезная"
        return f"{habit_type}: {self.action} в {self.time} в {self.place}"

    def is_linked_pleasant(self):
        """
        Проверяет, является ли связанная привычка приятной.
        """
        if self.linked_habit:
            return self.linked_habit.is_pleasant
        return False
