# Habits Tracker

Трекер полезных привычек (по мотивам книги «Атомные привычки») с напоминаниями в Telegram.

REST API на Django REST Framework, контейнеризация через Docker, автоматический деплой через GitHub Actions.

## Стек

- Python 3.12, Django 6, Django REST Framework
- PostgreSQL 16, Redis
- Celery + Celery Beat (периодические напоминания)
- Telegram Bot API
- Docker, Docker Compose, Nginx
- GitHub Actions (CI/CD), Docker Hub

## Структура проекта

- `config` — настройки Django, Celery
- `users` — регистрация, авторизация по токену, профиль
- `habits` — привычки, валидаторы, напоминания, Telegram-бот
- `nginx` — конфигурация Nginx
- `.github/workflows` — CI/CD-пайплайн

## Локальный запуск через Docker (рекомендуется)

1. Клонировать репозиторий и перейти в папку проекта.
2. Создать файл `.env` по образцу `.env.example`.
3. Запустить все сервисы одной командой:

   ```bash
   docker compose up -d --build
   ```

4. Проект доступен по адресу http://localhost/
   - Swagger: http://localhost/swagger/
   - Админка: http://localhost/admin/

Поднимаются 7 контейнеров: `web` (Django), `db` (PostgreSQL), `redis`, `celery`, `celery-beat`, `bot` (Telegram), `nginx`.

Остановка: `docker compose down` (данные базы сохраняются в volume `pg_data`).

## Локальный запуск без Docker

1. Установить зависимости: `poetry install`
2. Убедиться, что локально запущены PostgreSQL и Redis; создать базу `habits_tracker`.
3. Создать `.env` по образцу `.env.example`.
4. Применить миграции и запустить сервер:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. При необходимости отдельно запустить:
   - `celery -A config worker --loglevel=INFO`
   - `celery -A config beat --loglevel=INFO`
   - `python manage.py bot` (требуется `TELEGRAM_BOT_TOKEN`)

## CI/CD

Пайплайн (`.github/workflows/ci.yml`) запускается при каждом `push` и `pull request`:

1. **lint** — проверка кода flake8;
2. **test** — тесты Django (PostgreSQL и Redis поднимаются как сервисы GitHub Actions);
3. **build** — проверка сборки Docker-образов и push образа в Docker Hub;
4. **deploy** (только при push) — копирование `docker-compose.yml` и `nginx/nginx.conf` на сервер по SSH, затем `docker compose pull` и `docker compose up -d`.

### Секреты GitHub (Settings → Secrets and variables → Actions)

| Секрет | Описание |
|---|---|
| `SERVER_IP` | Публичный IP сервера |
| `SSH_USER` | Пользователь сервера |
| `SSH_KEY` | Приватный SSH-ключ для деплоя |
| `DEPLOY_DIR` | Папка проекта на сервере |
| `DOCKER_HUB_USERNAME` | Логин Docker Hub |
| `DOCKER_HUB_ACCESS_TOKEN` | Access token Docker Hub |

### Настройка сервера для деплоя

1. Установить Docker и Docker Compose.
2. Открыть порт 80 (группа безопасности / фаервол).
3. Создать папку деплоя (`DEPLOY_DIR`), в ней:
   - файл `.env` по образцу `.env.example` (обязательно указать `DOCKER_HUB_USERNAME` и `CSRF_TRUSTED_ORIGINS=http://&lt;IP-сервера&gt;`);
   - пустую подпапку `nginx`.
4. Добавить публичный SSH-ключ (парный к секрету `SSH_KEY`) в `~/.ssh/authorized_keys`.

После этого каждый push в ветку автоматически разворачивает проект на сервере.