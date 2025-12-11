# app/tests/test_app.py
import pytest
import sys
import os

# Добавляем путь для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app


@pytest.fixture
def client():
    """Фикстура для тестового клиента"""
    with app.test_client() as client:
        yield client


def test_health_endpoint(client, mocker):
    """Тест эндпоинта /health с моком Redis"""
    # Мокаем Redis, чтобы он всегда был доступен
    mock_redis = mocker.patch('app.main.redis_client')
    mock_redis.ping.return_value = True

    response = client.get('/health')
    assert response.status_code == 200
    assert b'healthy' in response.data.lower() or b'ok' in response.data.lower()


def test_main_page(client, mocker):
    """Тест главной страницы"""
    # Мокаем Redis
    mock_redis = mocker.patch('app.main.redis_client')
    mock_redis.incr.return_value = 42

    response = client.get('/')
    assert response.status_code == 200
    # Проверяем, что visits есть в ответе
    data = response.get_json()
    assert 'visits' in data
    assert data['visits'] == 42


def test_main_page_json_format(client, mocker):
    """Тест JSON формата ответа"""
    mock_redis = mocker.patch('app.main.redis_client')
    mock_redis.incr.return_value = 123

    response = client.get('/')
    assert response.status_code == 200
    # Проверяем, что это JSON
    assert response.is_json
    data = response.get_json()
    assert 'visits' in data
    assert 'hostname' in data
    assert 'server_time' in data
    assert 'environment' in data


def test_redis_connection_error(client, mocker):
    """Тест обработки ошибки Redis"""
    # Мокаем ошибку подключения
    mock_redis = mocker.patch('app.main.redis_client')
    mock_redis.incr.side_effect = Exception("Redis connection failed")

    response = client.get('/')
    # Приложение должно вернуть 500 при ошибке Redis - это корректное поведение!
    assert response.status_code == 500
    # Проверяем, что в ответе есть информация об ошибке
    # (Flask по умолчанию возвращает HTML при 500, можно проверить текст)
    assert b'Error' in response.data or b'500' in response.data