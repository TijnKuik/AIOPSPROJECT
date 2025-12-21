import pika
import time
import random
import os

inference_queue = os.getenv("MODEL_QUEUE", "Letterbox")

def auto_message_received(ch, method, properties, body):
    processing_time = random.randint(1, 6)
    print(f"Received new message: [{body}], will take {processing_time} to process")
    time.sleep(processing_time)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("Finished processing the message")

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

connection = connect_with_broker()
channel = connection.channel()
channel.queue_declare(queue=inference_queue)

# This gives the consumer up to x numver of messages that are not Acked yet.
channel.basic_qos(prefetch_count=1)

channel.basic_consume(inference_queue, on_message_callback=auto_message_received)

print("Starting consuming")
channel.start_consuming()
