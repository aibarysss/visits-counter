# app/main.py
from flask import Flask, jsonify
import redis
import os
import socket
from datetime import datetime

app = Flask(__name__)

# Конфигурация Redis
redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_password = os.getenv('REDIS_PASSWORD', '')

# Подключение к Redis
redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password if redis_password else None,
    decode_responses=True
)


# В app/main.py обновите функцию index:
@app.route('/')
def index():
    """Главная страница со счётчиком посещений"""
    try:
        # Увеличиваем счётчик
        visits = redis_client.incr('visits')

        # Получаем информацию о хосте
        hostname = socket.gethostname()
        server_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        response_data = {
            'message': 'Welcome to Visits Counter!',
            'visits': visits,
            'hostname': hostname,
            'server_time': server_time,
            'environment': os.getenv('APP_ENV', 'development'),
            'version': os.getenv('APP_VERSION', '1.0.0')
        }

        return jsonify(response_data)

    except redis.ConnectionError as e:
        # Возвращаем 200 даже при ошибке Redis, но с сообщением
        return jsonify({
            'message': 'Welcome to Visits Counter!',
            'error': 'Redis temporarily unavailable',
            'visits': 'N/A',
            'hostname': socket.gethostname(),
            'environment': os.getenv('APP_ENV', 'development'),
            'version': os.getenv('APP_VERSION', '1.0.0')
        }), 200


@app.route('/health')
def health():
    """Health check для мониторинга"""
    try:
        # Проверяем соединение с Redis
        redis_client.ping()

        return jsonify({
            'status': 'healthy',
            'redis': 'connected',
            'timestamp': datetime.now().isoformat()
        }), 200

    except redis.ConnectionError:
        return jsonify({
            'status': 'unhealthy',
            'redis': 'disconnected',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/stats')
def stats():
    """Статистика (можно расширить)"""
    try:
        visits = redis_client.get('visits') or 0
        uptime = redis_client.get('app_start_time')

        if not uptime:
            uptime = datetime.now().isoformat()
            redis_client.set('app_start_time', uptime)

        return jsonify({
            'total_visits': int(visits),
            'uptime_since': uptime,
            'current_time': datetime.now().isoformat()
        })

    except redis.ConnectionError:
        return jsonify({'error': 'Redis unavailable'}), 500


@app.route('/api/reset', methods=['POST'])
def reset_counter():
    """Сброс счётчика (требует аутентификации в реальном приложении)"""
    # В реальном приложении здесь должна быть аутентификация!
    redis_client.set('visits', 0)
    return jsonify({'message': 'Counter reset successfully'}), 200


if __name__ == '__main__':
    # Сохраняем время старта приложения
    redis_client.set('app_start_time', datetime.now().isoformat())

    # Запускаем Flask
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=(os.getenv('FLASK_DEBUG', 'False') == 'True')
    )