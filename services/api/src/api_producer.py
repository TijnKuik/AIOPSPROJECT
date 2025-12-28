from pydantic import BaseModel
from pathlib import Path
import json
import asyncio
import pika
import time
import random
import os

# Get the queues from the compose files
inference_queue = os.getenv("MODEL_QUEUE", "Letterbox")


def connect_with_broker(retries=30, delay_s=2):
    # Gets the port from the OS(containers (set in compose))
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port = int(os.getenv("RABBITMQ_PORT", 5672))

    # Sets the connection parameters
    connection_parameters = pika.ConnectionParameters(host=host, port=port)
    last_error = None
    
    # Tries to connect to the broker x amount of time
    for _ in range(retries):
        try:
            return pika.BlockingConnection(connection_parameters)
        except pika.exceptions.AMQPConnectionError as e:
            last_error = e
            time.sleep(delay_s)
    raise RuntimeError("- [API_PRODUCER] Couldn't connect to RabbitMQ") from last_error


# Tries to make connection with broker
def send_message_inference(connection, payload):
    channel_inference = connection.channel()
    channel_inference.queue_declare(queue=inference_queue)

    channel_inference.basic_publish(
        exchange="",
        routing_key=inference_queue,
        body=json.dumps(payload).encode("utf-8"), # Makes the dict. to json, then to bytes for RabbitMQ
        properties=pika.BasicProperties(content_type="api/addition/json")
    )
    print("- [API] Data sent to broker!")

def close_connection(connection):
    if connection and connection.is_open:
        connection.close()
        print("- [API] Connection closed!")