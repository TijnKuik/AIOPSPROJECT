import pika
import time
import json
import random
import os

api_queue = os.getenv("API_QUEUE", "Letterbox")

all_jobs = {}


def retrieve_job(job_id):
    try:
        for _ in range(100):
            if job_id in all_jobs.keys():
                return all_jobs[job_id]
            time.sleep(0.001)
    except:
        print(" - [API_CONSUMER] Job not existing.")

def inference_result(ch, method, properties, body):
    data = json.loads(body.decode("utf-8"))
    job_id = data["job_id"]
    result = data["result"]
    all_jobs.update({job_id: result})
    ch.basic_ack(delivery_tag=method.delivery_tag)

    
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



def consume_message_inference(connection):
    channel_api_inference = connection.channel()
    channel_api_inference.queue_declare(queue=api_queue)

    channel_api_inference.basic_qos(prefetch_count=1)
    channel_api_inference.basic_consume(api_queue, on_message_callback=inference_result)
    print("- [API_INFERENCE] Waiting for messages!")
    channel_api_inference.start_consuming()


def close_connection(connection):
    if connection and connection.is_open:
        connection.close()
        print("- [API] Connection closed!")
