# consumer
import pika
import time
import random

def auto_message_received(ch, method, properties, body):
    processing_time = random.randint(1, 6)
    print(f"Received new message: [{body}], will take {processing_time} to process")


connection_parameters = pika.ConnectionParameters('localhost')
connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()

channel.queue_declare(queue="Letterbox")

channel.basic_qos(prefetch_size=1)

channel.basic_consume(queue="Letterbox", on_message_callback=auto_message_received)

print("Starting consuming")
channel.start_consuming()
