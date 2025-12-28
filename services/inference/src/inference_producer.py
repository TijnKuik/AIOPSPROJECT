from pathlib import Path
import json
import pika
import time
import random
import os

# Get the queues from the compose files
api_queue = os.getenv("API_QUEUE", "Letterbox")


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
    raise RuntimeError("Couldn't connect to RabbitMQ") from last_error


# Tries to make connection with broker
def send_message_api(connection, payload):
    channel_inference = connection.channel()
    channel_inference.queue_declare(queue=api_queue)

    channel_inference.basic_publish(
        exchange="",
        routing_key=api_queue,
        body=payload, # Makes the dict. to json, then to bytes for RabbitMQ
        properties=pika.BasicProperties(content_type="api/addition/json")
    )
    print("- [INFERENCE - Prod.] Data sent to broker!")

def close_connection(connection):
    if connection and connection.is_open:
        connection.close()
        print("- [INFERENCE - Prod.] Connection closed!")