from rest_framework.exceptions import ValidationError


def validate_habit(data, instance=None):
    """
    Валидация привычки при создании/обновлении.

    Правила:
    1. Нельзя одновременно указать вознаграждение и связанную привычку
    2. Время выполнения ≤ 120 секунд
    3. Связанная привычка может быть только приятной
    4. У приятной привычки не может быть вознаграждения или связанной привычки
    5. Нельзя выполнять реже 1 раза в 7 дней
    """

    # Получаем значения из данных (или из instance, если обновление)
    is_pleasant = data.get("is_pleasant", getattr(instance, "is_pleasant", False))
    linked_habit = data.get("linked_habit", getattr(instance, "linked_habit", None))
    reward = data.get("reward", getattr(instance, "reward", None))
    duration = data.get("duration", getattr(instance, "duration", 60))
    period = data.get("period", getattr(instance, "period", 1))

    # --- Правило 1: Нельзя одновременно вознаграждение и связанную привычку ---
    if linked_habit and reward:
        raise ValidationError(
            "Нельзя одновременно указать связанную привычку и вознаграждение. "
            "Выберите что-то одно."
        )

    # --- Правило 2: Время выполнения ≤ 120 секунд ---
    if duration and duration > 120:
        raise ValidationError(
            "Время выполнения привычки не должно превышать 120 секунд."
        )

    # --- Правило 3: Связанная привычка должна быть приятной ---
    if linked_habit and not linked_habit.is_pleasant:
        raise ValidationError(
            "В связанные привычки могут попадать только привычки "
            "с признаком приятной привычки."
        )

    # --- Правило 4: У приятной привычки не может быть вознаграждения или связанной привычки ---
    if is_pleasant:
        if reward:
            raise ValidationError("У приятной привычки не может быть вознаграждения.")
        if linked_habit:
            raise ValidationError(
                "У приятной привычки не может быть связанной привычки."
            )

    # --- Правило 5: Периодичность не реже 1 раза в 7 дней ---
    if period and period > 7:
        raise ValidationError("Нельзя выполнять привычку реже, чем 1 раз в 7 дней.")

    return data
