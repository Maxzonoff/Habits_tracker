from celery import shared_task
from django.utils import timezone

from .models import Habit
from .services import format_habit_reminder, send_telegram_message


@shared_task
def send_habit_reminder(habit_id):
    """
    Celery-задача: отправить напоминание о привычке.
    """
    try:
        habit = Habit.objects.get(id=habit_id)
    except Habit.DoesNotExist:
        print(f"Привычка с ID {habit_id} не найдена")
        return

    user = habit.owner
    if not user.chat_id:
        print(f"У пользователя {user.username} не привязан Telegram")
        return

    message = format_habit_reminder(habit)
    result = send_telegram_message(user.chat_id, message)

    if result and result.get("ok"):
        print(f"Напоминание отправлено пользователю {user.username}")
    else:
        print(f"Не удалось отправить напоминание пользователю {user.username}")


@shared_task
def check_and_send_reminders():
    """
    Периодическая задача Celery Beat:
    Проверяет, какие привычки нужно выполнить сейчас,
    и отправляет напоминания.
    """
    current_time = timezone.now().time()

    habits = Habit.objects.filter(is_pleasant=False)

    sent_count = 0

    for habit in habits:

        habit_time = habit.time
        if (
            habit_time.hour == current_time.hour
            and habit_time.minute == current_time.minute
        ):

            if habit.last_completed:
                days_since = (timezone.now() - habit.last_completed).days
                if days_since < habit.period:
                    continue

            send_habit_reminder.delay(habit.id)
            sent_count += 1

    print(f"Проверено привычек: {habits.count()}, отправлено напоминаний: {sent_count}")
    return sent_count
