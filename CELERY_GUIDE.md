# 🚀 Краткое Руководство по Celery

## Что было добавлено

В проект добавлена поддержка **Celery** - популярного фреймворка для асинхронной обработки задач в Python.

### Новые файлы:
- `celery_app.py` - конфигурация Celery приложения
- `celery_tasks.py` - определение задач для обработки
- Обновлён `docker-compose.yml` - добавлен сервис `celery_worker`
- Обновлён интерфейс с современным дизайном

---

## 🏃 Быстрый Старт

### 1. Пересоберите контейнеры

```bash
docker compose build
```

### 2. Запустите все сервисы

```bash
docker compose up -d
```

Теперь запущены:
- **api** - веб-интерфейс на http://localhost:8080
- **rmq** - RabbitMQ Management на http://localhost:15672
- **celery_worker** - Celery worker для обработки задач
- **consumer** - старый consumer (для сравнения)

### 3. Откройте веб-интерфейс

Перейдите на http://localhost:8080

Вы увидите обновлённый интерфейс с тремя методами:
- ✨ **Celery** (рекомендуется) - современный подход
- 📨 **RabbitMQ** (напрямую) - старый подход для сравнения
- 📋 **Синхронное получение** - для демонстрации

---

## 📊 Просмотр Логов

### Логи Celery Worker

```bash
docker compose logs -f celery_worker
```

Вы увидите:
```
[2025-01-01 12:00:00] celery.worker.strategy: Received task: process_task[...]
[2025-01-01 12:00:00] Celery Worker celery: Начало обработки задачи 1
[2025-01-01 12:00:05] Celery Worker celery: Задача 1 завершена успешно
```

### Логи всех сервисов

```bash
docker compose logs -f
```

---

## 🔧 Масштабирование

### Запустить 3 Celery Worker'а

```bash
docker compose up -d --scale celery_worker=3
```

### Проверить статус Worker'ов

```bash
docker compose exec celery_worker celery -A celery_app inspect active
```

### Просмотреть зарегистрированные задачи

```bash
docker compose exec celery_worker celery -A celery_app inspect registered
```

Вывод:
```json
{
  "celery@hostname": {
    "process_task": {
      "name": "process_task",
      "exchange": null,
      "routing_key": "celery",
      "rate_limit": null
    },
    "process_data": {
      "name": "process_data",
      ...
    }
  }
}
```

---

## 🧪 Тестирование

### 1. Отправьте задачу через Celery

1. Откройте http://localhost:8080
2. В разделе "✨ Celery (Рекомендуется)" введите: `5` секунд
3. Нажмите "🚀 Отправить через Celery"
4. Наблюдайте в таблице "Статус задач":
   - Badge "Celery" в колонке "Метод"
   - Статус меняется: PENDING → IN_PROGRESS → DONE

### 2. Сравните с RabbitMQ

1. В разделе "📨 RabbitMQ (Напрямую)" введите: `5` секунд
2. Нажмите "📤 Отправить через RabbitMQ"
3. Обратите внимание:
   - Badge "RabbitMQ" в колонке "Метод"
   - Обработка происходит аналогично, но через старый consumer

### 3. Нагрузочное тестирование

Отправьте 10 задач через Celery с timeout=10 секунд:
```bash
# В другом терминале запустите мониторинг
docker compose logs -f celery_worker

# Отправляйте задачи через веб-интерфейс
# Наблюдайте распределение между worker'ами
```

---

## 💻 Разработка Локально

### Запуск Celery Worker на локальной машине

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Убедитесь, что RabbitMQ запущен
docker compose up -d rmq

# 3. Установите переменные окружения
export RMQ_URL=amqp://student:qwerty@localhost:5672/
export API_URL=http://localhost:8080/update_task_status_api/

# 4. Запустите worker
celery -A celery_app worker --loglevel=info --concurrency=3
```

Теперь вы можете:
- Менять код в `celery_tasks.py`
- Перезапускать worker (Ctrl+C и снова запустить)
- Отлаживать задачи

---

## 📝 Структура Кода

### celery_app.py
```python
from celery import Celery

celery_app = Celery(
    'tasks',
    broker='amqp://student:qwerty@rmq:5672/',
    backend='rpc://',
    include=['celery_tasks']
)
```

### celery_tasks.py
```python
from celery_app import celery_app

@celery_app.task(bind=True, name='process_task')
def process_task(self, task_num, timeout, worker_id='celery'):
    # Ваша логика обработки
    task_id = self.request.id
    ...
    return {'status': 'success', 'task_num': task_num}
```

### Отправка задачи из API
```python
from celery_tasks import process_task

# Асинхронная отправка
celery_task = process_task.delay(task_num, timeout, 'celery')
task_id = celery_task.id

# Получение результата (если нужно)
result = celery_task.get(timeout=30)
```

---

## 🔍 Мониторинг в RabbitMQ Management

1. Откройте http://localhost:15672
2. Логин: `student`, пароль: `qwerty`
3. Перейдите на вкладку **Queues**
4. Найдите очередь `celery` - там будут задачи Celery

---

## 🛑 Остановка

```bash
# Остановить все сервисы
docker compose stop

# Или удалить контейнеры
docker compose down

# Удалить с volumes (очистка данных RabbitMQ)
docker compose down -v
```

---

## ❓ Troubleshooting

### Celery Worker не запускается

Проверьте логи:
```bash
docker compose logs celery_worker
```

Возможные причины:
- RabbitMQ ещё не инициализировался (подождите 10-15 сек)
- Ошибка импорта в `celery_tasks.py`

### Задачи не обрабатываются

```bash
# Проверьте, что worker запущен
docker compose ps

# Проверьте активные задачи
docker compose exec celery_worker celery -A celery_app inspect active

# Проверьте статус worker'ов
docker compose exec celery_worker celery -A celery_app inspect stats
```

### RabbitMQ переполнен

```bash
# Очистите очередь (будьте осторожны!)
docker compose exec celery_worker celery -A celery_app purge
```

---

## 🎯 Следующие Шаги

1. **Добавьте свои задачи** в `celery_tasks.py`
2. **Настройте retry** для задач:
   ```python
   @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
   def my_task(self):
       try:
           # код
       except Exception as exc:
           raise self.retry(exc=exc)
   ```
3. **Добавьте периодические задачи** с Celery Beat
4. **Интегрируйте с вашим проектом**

---

## 📚 Полезные Ссылки

- [Celery Documentation](https://docs.celeryproject.org/)
- [RabbitMQ Management](http://localhost:15672)
- [Основной README](README.md)

---

**Успехов в изучении асинхронной обработки задач! 🚀**

