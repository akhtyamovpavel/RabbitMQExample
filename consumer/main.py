import os
import time
import pika
import json
import requests
from uuid import uuid4


RMQ_URL = os.environ.get('RMQ_URL')
API_URL = os.environ.get('API_URL', 'http://0.0.0.0:8080/update_task_status_api/')
QUEUE_NAME = os.environ.get('QUEUE_NAME', 'test_direct')
EXCHANGE_NAME = os.environ.get('EXCHANGE_NAME', 'to_direct')
PREFETCH_COUNT = 3


def main():
    worker_id = uuid4().hex[:4]

    connection = pika.BlockingConnection(pika.URLParameters(RMQ_URL))
    channel = connection.channel()

    channel.queue_declare(queue=f'{QUEUE_NAME}_rejected', durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True,
                          arguments={'x-dead-letter-exchange': '',
                                     'x-dead-letter-routing-key': f'{QUEUE_NAME}_rejected'})

    channel.queue_bind(queue=QUEUE_NAME, exchange=EXCHANGE_NAME, routing_key='direct_out')
    channel.basic_qos(prefetch_count=PREFETCH_COUNT)

    def callback(ch, method, properties, body):
        print(f">>> start processing message {body}")
        task_num = 0
        try:
            data = json.loads(body)
            task_num = data.get('task_num')
            requests.post(API_URL, json={'task_num': task_num, 'task_status': 'IN_PROGRESS', 'worker_id': worker_id})
            time.sleep(int(data.get('timeout', 0)))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            requests.post(API_URL, json={'task_num': task_num, 'task_status': 'DONE', 'worker_id': worker_id})
            print(f"<<< end processing message {body}")
        except Exception as ex:
            print(f"Error occurred: {ex}")
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            requests.post(API_URL, json={'task_num': task_num, 'task_status': 'ERROR'})

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False, consumer_tag=worker_id)
    channel.start_consuming()


if __name__ == '__main__':
    main()
