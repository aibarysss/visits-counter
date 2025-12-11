# Используем один файл вместо двух
FROM python:3.11-alpine

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY app/ ./app/

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5000/health || exit 1

# Переменные окружения
ENV FLASK_APP=app/main.py
ENV FLASK_ENV=${FLASK_ENV:-production}

# Пользователь для безопасности
RUN adduser -D myuser
USER myuser

# Запуск приложения
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app.main:app"]