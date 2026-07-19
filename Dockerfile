# Базовый образ: официальный Python 3.12, облегчённая версия
FROM python:3.12-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Настройки Python внутри контейнера:
# не создавать .pyc-файлы и сразу выводить логи в консоль
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем только файлы зависимостей (отдельным слоем — для кэша)
COPY pyproject.toml poetry.lock ./

# Ставим зависимости в системный Python контейнера
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Копируем весь код проекта
COPY . .

# Порт, который слушает Django
EXPOSE 8000

# Команда по умолчанию (в docker-compose переопределим для каждого сервиса)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]