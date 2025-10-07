# RabbitMQ + Celery Example: Паттерны Межсервисного Взаимодействия

## 📋 Описание Проекта

Демонстрационный проект, иллюстрирующий различные подходы к взаимодействию между микросервисами в распределённых системах. Проект создан для образовательных целей и демонстрирует:

- **Синхронное взаимодействие** (Request-Response)
- **Асинхронное взаимодействие** через Celery (рекомендуемый подход)
- **Асинхронное взаимодействие** через очереди сообщений (RabbitMQ напрямую)
- **Паттерн Producer-Consumer** с RabbitMQ и Celery
- **Dead Letter Queue** для обработки ошибок
- **Горизонтальное масштабирование** обработчиков
- **Celery** для удобного управления задачами

---

## 🏗️ Архитектура Системы

Система состоит из четырёх основных компонентов:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Браузер (UI)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP (8080)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Service (aiohttp)                        │
│  • Веб-интерфейс для демонстрации                               │
│  • Publisher задач в RabbitMQ                                   │
│  • REST API для обновления статусов                             │
└───────────┬──────────────────────────────────┬──────────────────┘
            │ AMQP (5672)                      │ HTTP Callback
            ▼                                  │
┌──────────────────────────────────┐           │
│       RabbitMQ Message Broker    │           │
│  • Exchange: to_direct (fanout)  │           │
│  • Queue: test_direct            │           │
│  • DLQ: test_direct_rejected     │           │
└───────────┬──────────────────────┘           │
            │ AMQP                             │
            ▼                                  │
┌──────────────────────────────────────────────┴──────────────────┐
│              Consumer Service (Workers)                         │
│  • Обработка задач из очереди                                   │
│  • Масштабируемость (N экземпляров)                             │
│  • Prefetch control для балансировки нагрузки                   │
└─────────────────────────────────────────────────────────────────┘
```

### Компоненты

#### 1. **API Service** (`api/`)
- **Фреймворк**: aiohttp (асинхронный веб-сервер на Python)
- **Порт**: 8080
- **Функции**:
  - Веб-интерфейс с тремя режимами взаимодействия
  - Публикация задач в RabbitMQ через Exchange
  - REST API endpoint для обратной связи от Consumer'ов
  - In-memory хранилище состояния задач

#### 2. **Celery Worker** (`celery_worker`)
- **Количество экземпляров**: масштабируемое (по умолчанию 1, concurrency=3)
- **Функции**:
  - Получение и обработка задач через Celery
  - Использование RabbitMQ в качестве брокера
  - Автоматическая балансировка нагрузки
  - Мониторинг статуса задач
  - Повторные попытки при ошибках

#### 3. **Consumer Service** (`consumer/`)
- **Количество экземпляров**: масштабируемое (по умолчанию 1)
- **Функции**:
  - Получение задач из очереди `test_direct` (старый способ для сравнения)
  - Обработка с настраиваемым timeout
  - Отправка обновлений статуса в API Service
  - Обработка ошибок с перенаправлением в DLQ

#### 4. **RabbitMQ** (`rmq/`)
- **Порты**: 
  - 5672 (AMQP протокол)
  - 15672 (Management UI)
- **Настройки**:
  - Exchange: `to_direct` (тип: fanout)
  - Queue: `test_direct` (durable, с DLX)
  - Dead Letter Queue: `test_direct_rejected`
  - Prefetch Count: 3 (одновременно обрабатывает до 3 задач на worker)

---

## 🚀 Быстрый Старт

### Предварительные Требования

- Docker >= 20.10
- Docker Compose >= 1.29

### 1. Сборка Проекта

```bash
docker compose build
```

Эта команда создаёт Docker образы для всех сервисов (API, Consumer, RabbitMQ, Celery Worker).

### 2. Запуск Всех Сервисов

```bash
docker compose up -d
```

Флаг `-d` запускает контейнеры в фоновом режиме (detached mode).

### 3. Проверка Доступности

После запуска доступны следующие интерфейсы:

- **Веб-приложение**: http://localhost:8080
- **RabbitMQ Management**: http://localhost:15672
  - Логин: `student`
  - Пароль: `qwerty`

### 4. Запуск Celery Worker

Celery Worker запускается автоматически при старте всех сервисов. Для просмотра логов:

```bash
docker compose logs -f celery_worker
```

Для масштабирования Celery Worker:

```bash
docker compose up -d --scale celery_worker=3
```

---

## 🎯 Демонстрируемые Паттерны

Веб-интерфейс позволяет протестировать три сценария взаимодействия:

### 1. Асинхронное Взаимодействие через Celery (Рекомендуется) ✨

**Описание**: Современный подход к обработке задач с использованием Celery. Клиент отправляет задачу через API, которая немедленно попадает в Celery, а обработка происходит в фоновом режиме.

**Преимущества**:
- ✅ Простота использования - минимальный boilerplate код
- ✅ Автоматическая сериализация/десериализация данных
- ✅ Встроенная поддержка повторных попыток (retry)
- ✅ Мониторинг задач из коробки (task states, progress)
- ✅ Горизонтальное масштабирование (просто добавьте больше worker'ов)
- ✅ Интеграция с RabbitMQ как брокером сообщений
- ✅ Поддержка периодических задач (через Celery Beat)
- ✅ Chainable tasks и workflows

**Как работает**:
1. Пользователь отправляет задачу через веб-форму
2. API вызывает `process_task.delay()` для отправки задачи в Celery
3. Celery маршрутизирует задачу в RabbitMQ
4. Свободный Celery Worker забирает и выполняет задачу
5. Worker обновляет статус через API (`PENDING` → `IN_PROGRESS` → `DONE/ERROR`)
6. Результат можно получить через `AsyncResult` по ID задачи

**Когда использовать Celery**:
- Долгие операции (обработка файлов, генерация отчётов)
- Фоновые задачи (отправка email, уведомления)
- Периодические задачи (cron-like операции)
- Batch-обработка данных
- Интеграции с внешними API

### 2. Асинхронное Взаимодействие через RabbitMQ (Напрямую)

**Описание**: Прямая работа с RabbitMQ через библиотеку Pika. Подходит для более низкоуровнего контроля над очередями.

**Преимущества**:
- ✅ Полный контроль над структурой сообщений
- ✅ Настройка exchanges, queues, bindings
- ✅ Поддержка Dead Letter Queues
- ✅ Гибкость в routing patterns

**Когда использовать**:
- Нужен полный контроль над RabbitMQ топологией
- Специфические требования к маршрутизации
- Интеграция с legacy системами
- Обучение основам работы с очередями

### 3. Синхронное Взаимодействие

**Описание**: Классический Request-Response паттерн. Клиент отправляет запрос и немедленно получает ответ.

**Когда использовать**:
- Требуется немедленный ответ
- Операция выполняется быстро (< 100ms)
- Простая логика без сложных зависимостей

**Недостатки**:
- Блокирующая операция
- Низкая отказоустойчивость (если сервис недоступен - ошибка)
- Не подходит для долгих операций

### 4. Синхронное с Долгим Ответом

**Описание**: Тот же Request-Response, но с искусственной задержкой 7 секунд для демонстрации проблем блокирующих операций.

**Демонстрируемая проблема**: 
Пока один запрос обрабатывается, API сервер не может эффективно обрабатывать другие запросы (даже с async/await, т.к. здесь используется `asyncio.sleep()`).

**Урок**: Долгие синхронные операции блокируют ресурсы и снижают throughput системы.


---

## 📊 Управление и Мониторинг

### Просмотр Логов

```bash
# Логи всех сервисов в реальном времени
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f api
docker-compose logs -f consumer
docker-compose logs -f rmq
```

### Запуск Отдельного Сервиса

```bash
# Полезно для отладки
docker-compose up api
```

### Остановка Сервисов

```bash
# Graceful shutdown с таймаутом 1 секунда
docker-compose stop -t 1
```

### Удаление Контейнеров

```bash
# Удаление остановленных контейнеров
docker-compose rm -f
```

### Масштабирование Воркеров

#### Celery Worker (рекомендуемый подход)

```bash
# Увеличить количество Celery Worker'ов до 3
docker-compose up -d --scale celery_worker=3

# Или увеличить до 5
docker-compose up -d --scale celery_worker=5
```

**Эффект**: Celery автоматически распределит задачи между всеми worker'ами. Каждый worker может обрабатывать до 3 задач одновременно (concurrency=3).

#### Consumer (старый подход)

```bash
# Увеличить количество обработчиков до 2
docker-compose up -d --scale consumer=2
```

**Эффект**: RabbitMQ автоматически распределит задачи между всеми Consumer'ами по алгоритму Round-Robin с учётом Prefetch Count.

### Запуск Celery Worker Локально (для разработки)

```bash
# Установите зависимости
pip install -r requirements.txt

# Установите переменные окружения
export RMQ_URL=amqp://student:qwerty@localhost:5672/
export API_URL=http://localhost:8080/update_task_status_api/

# Запустите worker
celery -A celery_app worker --loglevel=info --concurrency=3
```

### Мониторинг Celery

Для просмотра логов Celery Worker:

```bash
docker-compose logs -f celery_worker
```

Для проверки статуса worker'ов:

```bash
docker-compose exec celery_worker celery -A celery_app inspect active
```

Для просмотра зарегистрированных задач:

```bash
docker-compose exec celery_worker celery -A celery_app inspect registered
```

---

## 🔧 Конфигурация

### Переменные Окружения

#### API Service
```yaml
RMQ_URL: amqp://student:qwerty@rmq:5672/
```

#### Consumer Service
```yaml
RMQ_URL: amqp://student:qwerty@rmq:5672/
API_URL: http://api:8080/update_task_status_api/
QUEUE_NAME: test_direct
EXCHANGE_NAME: to_direct
```

### RabbitMQ Settings

**Prefetch Count**: `3`
- Каждый Consumer одновременно обрабатывает максимум 3 задачи
- Предотвращает перегрузку медленных Consumer'ов
- Обеспечивает более равномерное распределение нагрузки

**Dead Letter Exchange (DLX)**:
- При ошибке обработки (`basic_reject` с `requeue=False`) задача попадает в `test_direct_rejected`
- Позволяет анализировать проблемные задачи
- Можно настроить алерты или повторную обработку

---

## 🧪 Сценарии Тестирования

### 1. Проверка Базовой Работы с Celery

1. Откройте http://localhost:8080
2. В разделе "Celery (Рекомендуется)" введите время выполнения: `5`
3. Нажмите "🚀 Отправить через Celery"
4. Наблюдайте в таблице "Задачи":
   - Статус сразу становится `PENDING`
   - Через несколько мс: `IN_PROGRESS`
   - Через ~5 секунд: `DONE`
   - В колонке "Метод" будет badge "Celery"

### 2. Демонстрация Масштабирования Celery

```bash
# Запустите 3 Celery Worker'а
docker-compose up -d --scale celery_worker=3

# Откройте веб-интерфейс
# Отправьте 10 задач через Celery с timeout=10 секунд
# Наблюдайте в таблице задач, как они распределяются

# Просмотрите логи для проверки распределения
docker-compose logs -f celery_worker
```

### 3. Сравнение Celery и RabbitMQ

**Через Celery**:
- Отправьте 5 задач через "Celery" с timeout=5
- API моментально отвечает на все запросы
- Задачи автоматически распределяются между Celery Worker'ами
- Удобный мониторинг через Celery inspect

**Через RabbitMQ напрямую**:
- Отправьте 5 задач через "RabbitMQ (Напрямую)" с timeout=5
- API также моментально отвечает
- Задачи обрабатываются через Consumer'ов
- Требуется больше кода для управления

### 4. Тестирование Dead Letter Queue

```bash
# Измените код consumer/main.py для симуляции ошибки
# Например, добавьте: raise Exception("Simulated error")
# Пересоберите: docker-compose build consumer
# Перезапустите: docker-compose up -d

# Отправьте задачу через UI
# Проверьте в RabbitMQ Management → Queues
# Задача должна попасть в test_direct_rejected
```

---

## 🎓 Образовательные Цели

Проект демонстрирует ключевые концепции:

### 1. Celery для Асинхронных Задач
- **Простая интеграция**: минимальный код для запуска задач
- **Task States**: автоматическое отслеживание статусов (PENDING, STARTED, SUCCESS, FAILURE)
- **Retry механизм**: встроенная поддержка повторных попыток
- **Result backends**: получение результатов выполнения задач
- **Масштабирование**: горизонтальное масштабирование через добавление worker'ов

### 2. Message Queue Patterns
- **Producer-Consumer**: разделение ответственности
- **Fanout Exchange**: broadcast сообщений
- **Work Queue**: распределение задач между workers
- **RabbitMQ как брокер**: Celery использует RabbitMQ для передачи сообщений

### 3. Асинхронная Архитектура
- Decoupling сервисов
- Буферизация нагрузки
- Горизонтальное масштабирование
- Неблокирующие операции

### 4. Reliability Patterns
- **Acknowledgments**: гарантия обработки (manual ack)
- **Dead Letter Queues**: обработка ошибок
- **Durable Queues**: персистентность (переживает рестарт RabbitMQ)
- **Task retries**: автоматические повторные попытки в Celery

### 5. Performance Optimization
- **Prefetch Count**: контроль нагрузки на worker
- **Concurrency**: параллельная обработка задач
- **Connection Pooling**: эффективное использование ресурсов
- **Load Balancing**: автоматическое распределение RabbitMQ

---

## 🐛 Troubleshooting

### Проблема: "Consumer не забирает задачи"

**Диагностика**:
```bash
docker-compose logs consumer
```

**Возможные причины**:
- RabbitMQ еще не готов (добавьте `depends_on` с health check)
- Неверные credentials
- Queue не был объявлен (consumer объявляет при запуске)

### Проблема: "API не может подключиться к RabbitMQ"

**Решение**: Убедитесь, что RabbitMQ полностью инициализирован
```bash
docker-compose logs rmq | grep "Server startup complete"
```

Если API запустился раньше - перезапустите:
```bash
docker-compose restart api
```

### Проблема: "Задачи остаются в состоянии IN_PROGRESS"

**Причина**: Consumer упал или завис

**Диагностика**:
```bash
# Проверьте запущенные consumer'ы
docker-compose ps consumer

# Проверьте логи на ошибки
docker-compose logs consumer | tail -50
```

### Проблема: "Management UI недоступен"

**Решение**: Дождитесь полной инициализации RabbitMQ (~10-15 сек)
```bash
docker-compose logs rmq -f
```

---

## 📚 Полезные Ресурсы

### RabbitMQ
- [Official Documentation](https://www.rabbitmq.com/documentation.html)
- [Getting Started Tutorial](https://www.rabbitmq.com/getstarted.html)
- [Reliability Guide](https://www.rabbitmq.com/reliability.html)

### Python Libraries
- [Pika Documentation](https://pika.readthedocs.io/) - RabbitMQ клиент для Python
- [aiohttp Documentation](https://docs.aiohttp.org/) - Асинхронный веб-фреймворк

### Архитектурные Паттерны
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)
- [Microservices Patterns](https://microservices.io/patterns/index.html)

---

## 🔒 Security Note

⚠️ **Внимание**: Этот проект предназначен ТОЛЬКО для образовательных целей и локальной разработки.

**НЕ используйте в продакшене** без следующих изменений:
- Смените дефолтные credentials (`student/qwerty`)
- Используйте переменные окружения для секретов
- Настройте TLS для RabbitMQ
- Добавьте аутентификацию для API endpoints
- Настройте rate limiting
- Реализуйте proper logging и мониторинг

---

## 💡 Преимущества Celery перед Прямой Работой с RabbitMQ

| Характеристика | Celery | RabbitMQ напрямую (Pika) |
|----------------|--------|--------------------------|
| **Простота использования** | ✅ Высокая - декораторы, простой API | ⚠️ Средняя - требует больше кода |
| **Сериализация** | ✅ Автоматическая (JSON, pickle, msgpack) | ❌ Ручная |
| **Мониторинг задач** | ✅ Встроенный (task states, inspect) | ❌ Нужно реализовывать |
| **Retry механизм** | ✅ Встроенный с экспоненциальной задержкой | ❌ Нужно реализовывать |
| **Периодические задачи** | ✅ Celery Beat | ❌ Нужен внешний планировщик |
| **Task chains/workflows** | ✅ chain, group, chord | ❌ Нужно реализовывать |
| **Result backend** | ✅ Встроенный | ❌ Нужно реализовывать |
| **Контроль топологии** | ⚠️ Ограниченный | ✅ Полный контроль |
| **Размер overhead** | ⚠️ Больше зависимостей | ✅ Минимальный |

**Вывод**: Используйте **Celery** для большинства задач асинхронной обработки. Используйте **RabbitMQ напрямую** только если нужен полный контроль над топологией очередей или специфическая маршрутизация.

---

## 📚 Дополнительные Материалы

### Документация Celery
- [Официальная документация Celery](https://docs.celeryproject.org/)
- [Celery - First Steps](https://docs.celeryproject.org/en/stable/getting-started/first-steps-with-celery.html)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/tasks.html#task-best-practices)

### Структура Проекта с Celery

```
RabbitMQExample/
├── celery_app.py         # Конфигурация Celery
├── celery_tasks.py       # Определение задач
├── api/
│   ├── gui/
│   │   └── home_view.py  # Отправка задач через .delay()
│   └── main.py
├── consumer/             # Старый способ (для сравнения)
│   └── main.py
└── docker-compose.yml    # celery_worker сервис
```

---

## 📄 Лицензия

Проект создан в образовательных целях для курса "Промышленная Разработка" (PromDa).

---

## 👤 Автор

Учебный материал подготовлен для курса PromDa 2025, Fall 2025.

---

## 🤝 Вопросы и Feedback

Если у вас возникли вопросы или предложения по улучшению примера, создайте issue в репозитории или обратитесь к преподавателю курса.
