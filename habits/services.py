import requests
from django.conf import settings


def send_telegram_message(chat_id, message):
    """
    Отправка сообщения в Telegram через Bot API.
    """


    if not settings.TELEGRAM_BOT_TOKEN:
        print("WARNING: TELEGRAM_BOT_TOKEN не настроен!")
        return None

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Не удалось отправить сообщение: {e}")
        return None


def format_habit_reminder(habit):
    """
    Форматирует напоминание о привычке.
    """

    message = (
        f"⏰ <b>Напоминание о привычке!</b>\n\n"
        f"🎯 <b>{habit.action}</b>\n"
        f"📍 Место: {habit.place}\n"
        f"⏱ Время выполнения: {habit.duration} сек\n"
    )

    if habit.reward:
        message += f"🎁 Вознаграждение: {habit.reward}\n"

    if habit.linked_habit:
        message += f"🔗 Связанная привычка: {habit.linked_habit.action}\n"

    message += "\n<i>Удачи! Ты справишься! 💪</i>"

    return message
