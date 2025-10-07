import os
from celery import Celery

# Получаем URL для RabbitMQ из переменных окружения
RMQ_URL = os.environ.get('RMQ_URL', 'amqp://student:qwerty@rmq:5672/')

# Создаём экземпляр Celery с использованием RabbitMQ в качестве брокера и бэкенда результатов
celery_app = Celery(
    'tasks',
    broker=RMQ_URL,
    backend='rpc://',  # Используем RabbitMQ RPC в качестве бэкенда результатов
    include=['celery_tasks']
)

# Настройки Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=3,
)
