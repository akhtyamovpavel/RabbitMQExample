import os
import time
import requests
from celery_app import celery_app

# URL для отправки обновлений статуса задачи в API
API_URL = os.environ.get('API_URL', 'http://api:8080/update_task_status_api/')


@celery_app.task(bind=True, name='process_task')
def process_task(self, task_num, timeout, worker_id='celery'):
    """
    Задача Celery для обработки данных.
    
    Args:
        task_num: Номер задачи
        timeout: Время выполнения в секундах
        worker_id: Идентификатор воркера (по умолчанию 'celery')
    
    Returns:
        dict: Результат обработки задачи
    """
    task_id = self.request.id
    print(f"[Celery Worker {worker_id}] Начало обработки задачи {task_num} (Celery ID: {task_id})")
    
    try:
        # Обновляем статус на IN_PROGRESS
        requests.post(API_URL, json={
            'task_num': task_num,
            'task_status': 'IN_PROGRESS',
            'worker_id': f'{worker_id}-{task_id[:8]}'
        })
        
        # Имитируем работу
        time.sleep(int(timeout))
        
        # Обновляем статус на DONE
        requests.post(API_URL, json={
            'task_num': task_num,
            'task_status': 'DONE',
            'worker_id': f'{worker_id}-{task_id[:8]}'
        })
        
        print(f"[Celery Worker {worker_id}] Задача {task_num} завершена успешно")
        return {'status': 'success', 'task_num': task_num, 'task_id': task_id}
        
    except Exception as ex:
        print(f"[Celery Worker {worker_id}] Ошибка при обработке задачи {task_num}: {ex}")
        
        # Обновляем статус на ERROR
        requests.post(API_URL, json={
            'task_num': task_num,
            'task_status': 'ERROR',
            'worker_id': f'{worker_id}-{task_id[:8]}'
        })
        
        raise


@celery_app.task(bind=True, name='process_data')
def process_data(self, data_id):
    """
    Задача для обработки данных по ID (демонстрационная).
    
    Args:
        data_id: ID данных для обработки
    
    Returns:
        dict: Результат обработки
    """
    task_id = self.request.id
    print(f"[Celery Worker] Обработка данных с ID {data_id} (Celery ID: {task_id})")
    
    # Имитируем работу
    time.sleep(2)
    
    return {'status': 'success', 'data_id': data_id, 'task_id': task_id}
