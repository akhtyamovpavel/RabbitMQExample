# 🚀 Быстрая Справка - RabbitMQ + Celery Project

## 📋 Все Сервисы и Порты

| Сервис | URL | Логин | Описание |
|--------|-----|-------|----------|
| **Веб-приложение** | http://localhost:8080 | - | Основной интерфейс для отправки задач |
| **Flower** 🌸 | http://localhost:5555 | - | Мониторинг Celery задач |
| **RabbitMQ Management** | http://localhost:15672 | student/qwerty | Управление очередями |

---

## 🎯 Быстрые Команды

### Запуск и Остановка

```bash
# Запуск всех сервисов
docker compose up -d

# Быстрый запуск с помощью скрипта
./run_celery.sh

# Остановка
docker compose stop

# Полное удаление
docker compose down -v
```

### Масштабирование

```bash
# Увеличить Celery Worker'ы
docker compose up -d --scale celery_worker=3

# Увеличить старые Consumer'ы
docker compose up -d --scale consumer=2
```

### Логи

```bash
# Все логи
docker compose logs -f

# Только Celery
docker compose logs -f celery_worker

# Только Flower
docker compose logs -f flower

# Только API
docker compose logs -f api
```

### Мониторинг Celery

```bash
# Активные задачи
docker compose exec celery_worker celery -A celery_app inspect active

# Статистика
docker compose exec celery_worker celery -A celery_app inspect stats

# Зарегистрированные задачи
docker compose exec celery_worker celery -A celery_app inspect registered
```

---

## 🔄 Методы Отправки Задач

| Метод | Технология | Когда использовать | Сложность |
|-------|------------|-------------------|-----------|
| **Celery** ✨ | Celery + RabbitMQ | Рекомендуется для большинства задач | Низкая |
| **RabbitMQ** 📨 | Pika + RabbitMQ | Нужен полный контроль над очередями | Средняя |
| **Синхронное** 📋 | HTTP | Быстрые операции (< 100ms) | Очень низкая |
| **Синхронное долгое** ⏱️ | HTTP | Только для демонстрации проблем | Очень низкая |

---

## 📁 Структура Проекта

```
RabbitMQExample/
├── api/                        # API сервис
│   ├── celery_app.py          # Конфигурация Celery
│   ├── celery_tasks.py        # Задачи Celery
│   ├── gui/
│   │   └── home_view.py       # Веб-интерфейс
│   ├── main.py                # Точка входа API
│   └── templates/
│       └── home.html          # HTML интерфейс
├── consumer/                   # Старый consumer (для сравнения)
│   └── main.py
├── rmq/                        # Конфигурация RabbitMQ
│   ├── Dockerfile
│   └── definitions.json
├── docker-compose.yml          # Оркестрация сервисов
├── requirements.txt            # Python зависимости
├── run_celery.sh              # Скрипт быстрого запуска
├── README.md                   # Полная документация
├── CELERY_GUIDE.md            # Руководство по Celery
├── FLOWER_GUIDE.md            # Руководство по Flower
└── QUICK_REFERENCE.md         # Эта справка
```

---

## 🧪 Быстрые Тесты

### Тест 1: Базовая Работа Celery (30 секунд)

```bash
# 1. Запустите проект
docker compose up -d

# 2. Откройте http://localhost:8080

# 3. Отправьте задачу через Celery (timeout=5)

# 4. Откройте Flower http://localhost:5555

# 5. Проверьте задачу в Tasks → Success
```

### Тест 2: Масштабирование (2 минуты)

```bash
# 1. Масштабируйте worker'ы
docker compose up -d --scale celery_worker=3

# 2. Отправьте 10 задач (timeout=10)

# 3. В Flower → Workers увидите 3 worker'а

# 4. В Flower → Monitor наблюдайте распределение
```

### Тест 3: Сравнение Методов (1 минута)

```bash
# 1. Отправьте задачу через "Синхронное долгое" (7 сек)
#    → Браузер зависнет

# 2. Отправьте через "Celery" (5 сек)
#    → Моментальный ответ

# 3. Сравните результаты в таблице задач
```

---

## 📊 Полезные URL

| Что нужно | URL |
|-----------|-----|
| Отправить задачу | http://localhost:8080 |
| Посмотреть задачи Celery | http://localhost:5555/tasks |
| Посмотреть worker'ов | http://localhost:5555/workers |
| Графики производительности | http://localhost:5555 (Dashboard) |
| Мониторинг в реальном времени | http://localhost:5555/monitor |
| Очереди RabbitMQ | http://localhost:15672/#/queues |

---

## 🎓 Учебные Сценарии

### Для Студентов: "Celery vs Синхронный"

1. **Синхронный долгий запрос:**
   - Отправьте через "Синхронное долгое" (ID=10)
   - Засеките время → ~7 секунд
   - Попробуйте отправить второй → будет ждать

2. **Celery асинхронный:**
   - Отправьте через "Celery" (timeout=7)
   - Засеките время → < 1 секунда
   - Отправьте ещё 5 задач → все моментально

3. **Вывод:**
   - Асинхронная обработка = лучше UX
   - API не блокируется
   - Масштабируется горизонтально

### Для Преподавателей: Демонстрация

```bash
# 1. Покажите пустой Flower Dashboard
open http://localhost:5555

# 2. Отправьте 20 задач через веб-интерфейс
# (timeout=10 секунд каждая)

# 3. Покажите Flower → Monitor
# (задачи обрабатываются в реальном времени)

# 4. Масштабируйте
docker compose up -d --scale celery_worker=5

# 5. Покажите, как задачи распределились
# Flower → Workers (5 worker'ов активны)

# 6. Объясните метрики в Dashboard
```

---

## 🔧 Конфигурация Celery

### Ключевые Параметры

| Параметр | Значение | Описание |
|----------|----------|----------|
| `broker` | `amqp://student:qwerty@rmq:5672/` | RabbitMQ URL |
| `backend` | `rpc://` | Backend для результатов |
| `task_serializer` | `json` | Формат сериализации |
| `task_track_started` | `True` | Отслеживание старта задач |
| `worker_prefetch_multiplier` | `3` | Задач на worker |
| `concurrency` | `3` | Параллельных процессов |

### Переменные Окружения

```bash
RMQ_URL=amqp://student:qwerty@rmq:5672/
API_URL=http://api:8080/update_task_status_api/
```

---

## 🐛 Быстрое Решение Проблем

| Проблема | Решение |
|----------|---------|
| Flower не открывается | `docker compose logs flower` → Подождите 15 сек |
| Задачи не выполняются | `docker compose logs celery_worker` → Проверьте worker'ы |
| RabbitMQ недоступен | `docker compose restart rmq` → Перезапустите |
| API не отвечает | `docker compose restart api` |
| Порт занят | Измените порт в `docker-compose.yml` |

### Полный Рестарт

```bash
# Если что-то пошло не так
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 📚 Документация

- **[README.md](README.md)** - Полная документация проекта
- **[CELERY_GUIDE.md](CELERY_GUIDE.md)** - Руководство по Celery
- **[FLOWER_GUIDE.md](FLOWER_GUIDE.md)** - Руководство по Flower

---

## 💡 Советы

1. **Используйте Flower для всего**
   - Лучше, чем логи
   - Наглядно и удобно

2. **Начните с малого**
   - 1 worker для начала
   - Потом масштабируйте

3. **Смотрите на графики**
   - Dashboard показывает проблемы
   - Следите за error rate

4. **Тестируйте масштабирование**
   - 1 → 3 → 5 worker'ов
   - Сравните производительность

5. **Читайте документацию**
   - Celery очень гибкий
   - Много возможностей

---

## 🎉 Готово!

Теперь у вас есть:
- ✅ Celery для асинхронных задач
- ✅ Flower для мониторинга
- ✅ RabbitMQ как брокер
- ✅ Красивый веб-интерфейс
- ✅ Полная документация

**Начните с:** http://localhost:8080

**Удачи! 🚀**

