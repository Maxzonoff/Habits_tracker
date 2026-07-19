import time

import requests
from django.core.management.base import BaseCommand
from django.conf import settings

from users.models import User


class Command(BaseCommand):
    """
    Команда для запуска Telegram-бота.

    Запуск: python manage.py bot

    Бот работает в режиме long-polling:
    - Получает обновления от Telegram
    - Когда пользователь пишет /start — сохраняет его chat_id
    """

    help = "Запуск Telegram-бота для привычек"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Запуск Telegram-бота..."))

        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(self.style.ERROR("TELEGRAM_BOT_TOKEN не настроен!"))
            self.stdout.write(
                self.style.WARNING(
                    "1. Напиши @BotFather в Telegram\n"
                    "2. Создай бота командой /newbot\n"
                    "3. Получи токен и добавь в .env файл"
                )
            )
            return

        offset = 0

        self.stdout.write(self.style.SUCCESS("Бот запущен! Ожидаю сообщения..."))

        while True:
            try:
                url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
                params = {"offset": offset, "limit": 100}

                response = requests.get(url, params=params, timeout=30)
                data = response.json()

                if not data.get("ok"):
                    self.stdout.write(self.style.ERROR(f"Ошибка API: {data}"))
                    time.sleep(5)
                    continue

                updates = data.get("result", [])

                for update in updates:
                    self.process_update(update)
                    offset = update["update_id"] + 1

                time.sleep(1)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
                time.sleep(5)

    def process_update(self, update):
        """
        Обрабатывает одно обновление от Telegram.
        """

        if "message" not in update:
            return

        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        username = message["from"].get("username", "unknown")

        self.stdout.write(f"Сообщение от @{username}: {text}")

        if text == "/start":
            self.handle_start(chat_id, username, message["from"])
        elif text == "/help":
            self.handle_help(chat_id)
        else:
            self.handle_unknown(chat_id)

    def handle_start(self, chat_id, username, user_data):
        """
        Обработка команды /start.
        Сохраняет chat_id пользователя.
        """

        try:
            user = User.objects.get(username=username)
            user.chat_id = str(chat_id)
            user.telegram_id = str(user_data.get("id", ""))
            user.save()

            self.send_message(
                chat_id,
                f"Привет, {user.first_name or username}! 👋\n\n"
                f"Твой Telegram успешно привязан к аккаунту.\n"
                f"Теперь ты будешь получать напоминания о привычках!",
            )
            self.stdout.write(self.style.SUCCESS(f"Пользователь @{username} привязан"))

        except User.DoesNotExist:
            self.send_message(
                chat_id,
                "Привет! 👋\n\n"
                "Я бот для трекера привычек.\n"
                f"Твой username: @{username}\n"
                "Чтобы получать напоминания, зарегистрируйся на сайте "
                "с таким же username и напиши мне /start снова.",
            )

    def handle_help(self, chat_id):
        """
        Обработка команды /help.
        """
        self.send_message(
            chat_id,
            "📋 <b>Доступные команды:</b>\n\n"
            "/start — Привязать Telegram к аккаунту\n"
            "/help — Показать это сообщение\n\n"
            "Я буду присылать напоминания о твоих привычках!",
        )

    def handle_unknown(self, chat_id):
        """
        Обработка неизвестных сообщений.
        """
        self.send_message(
            chat_id,
            "Я не понимаю это сообщение 😅\n"
            "Напиши /help, чтобы увидеть доступные команды.",
        )

    def send_message(self, chat_id, text):
        """
        Отправляет сообщение через Telegram API.
        """
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }

        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Не удалось отправить сообщение: {e}"))
