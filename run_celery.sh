#!/bin/bash

# Скрипт для быстрого запуска Celery

echo "🚀 Запуск проекта с Celery..."
echo ""

# Проверка наличия docker-compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

# Остановка старых контейнеров
echo "📦 Остановка старых контейнеров..."
docker compose down

# Сборка образов
echo "🔨 Сборка образов..."
docker compose build

# Запуск всех сервисов
echo "🎬 Запуск сервисов..."
docker compose up -d

# Ожидание запуска
echo "⏳ Ожидание инициализации сервисов (15 секунд)..."
sleep 15

# Проверка статуса
echo ""
echo "✅ Сервисы запущены!"
echo ""
echo "📊 Статус контейнеров:"
docker compose ps

echo ""
echo "🌐 Доступные интерфейсы:"
echo "   - Веб-приложение: http://localhost:8080"
echo "   - Flower (Celery мониторинг): http://localhost:5555 🌸"
echo "   - RabbitMQ Management: http://localhost:15672 (student/qwerty)"
echo ""
echo "📋 Полезные команды:"
echo "   - Логи Celery:           docker compose logs -f celery_worker"
echo "   - Логи всех сервисов:    docker compose logs -f"
echo "   - Масштабирование:       docker compose up -d --scale celery_worker=3"
echo "   - Статус worker'ов:      docker compose exec celery_worker celery -A celery_app inspect active"
echo "   - Остановка:             docker compose stop"
echo ""
echo "🎉 Готово! Откройте http://localhost:8080"

