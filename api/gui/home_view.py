import os
import aiohttp_jinja2
import time
import pika
from aiohttp import web
import asyncio
import json
from collections import OrderedDict

import logging


RMQ_URL = os.environ.get('RMQ_URL')
MAX_TASKS_DISPLAY = 20


DATA = [
    {'id': 10, 'title': 'Тарелка'},
    {'id': 11, 'title': 'Ложка'},
    {'id': 12, 'title': 'Стакан'},
    {'id': 13, 'title': 'Чашка'},
    {'id': 14, 'title': 'Кастрюля'},
    {'id': 15, 'title': 'Вилка'},
    {'id': 16, 'title': 'Стол'},
]

TASKS = OrderedDict()

LAST_TASK_NUM = 0


def _get_last_tasks():
    return list(TASKS.values())[:-MAX_TASKS_DISPLAY:-1]


@aiohttp_jinja2.template('home.html')
async def home_view(request):
    return {'data': DATA, 'tasks': _get_last_tasks()}


@aiohttp_jinja2.template('home.html')
async def get_sync_data(request):
    print("[get_sync_data]")
    data_id = request.rel_url.query.get('data_id')
    res = None
    if data_id:
        res = [i for i in DATA if i['id'] == int(data_id)]
    return {'data': DATA, 'tasks': _get_last_tasks(), 'get_sync_result': res[0] if res else res}


@aiohttp_jinja2.template('home.html')
async def get_sync_long_data(request):
    print("[get_sync_long_data]")
    # эта функция сделана специально синхронной, что бы показать работу простого однопоточного сервиса
    data_id = request.rel_url.query.get('data_id')
    res = None
    if data_id:
        res = [i for i in DATA if i['id'] == int(data_id)]
    await asyncio.sleep(7)

    return {'data': DATA, 'tasks': _get_last_tasks(), 'get_sync_long_data': res[0] if res else res}


@aiohttp_jinja2.template('home.html')
async def send_rmq_direct(request):
    print("[send_rmq_direct]")
    post_data = await request.post()
    processing_timeout = post_data.get('processing_timeout', '1') or '1'
    routing_key = post_data.get('routing_key', '')
    worker_id = post_data.get('worker_id', 'Unknown')
    task_num = increase_last_task_num()

    with pika.BlockingConnection(pika.URLParameters(RMQ_URL)) as connection:
        with connection.channel() as channel:
            data = {'timeout': processing_timeout,
                    'task_num': task_num,
                    'routing_key': routing_key,
                    'task_status': 'PENDING',
                    'worker_id': worker_id}
            channel.basic_publish(exchange='to_direct', routing_key=routing_key, body=json.dumps(data).encode())
            TASKS[task_num] = data

    return {'data': DATA, 'tasks': _get_last_tasks(), 'rmq_direct_id': task_num}


async def update_task_status_api(request):
    print("[update_task_status_api]")
    post_data = await request.json()
    task_num = post_data.get('task_num')
    task_status = post_data.get('task_status')
    worker_id = post_data.get('worker_id', 'Unknown')

    task = TASKS.get(task_num)
    if task:
        task['task_status'] = task_status
        task['worker_id'] = worker_id
        return web.json_response(data={'result': 'ok'})

    return web.json_response(data={'result': 'not found'}, status=404)


def increase_last_task_num():
    global LAST_TASK_NUM
    LAST_TASK_NUM += 1
    return LAST_TASK_NUM
