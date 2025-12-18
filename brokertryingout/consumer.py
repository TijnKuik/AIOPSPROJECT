# consumer
import pika
import time
import random

def auto_message_received(ch, method, properties, body):
    processing_time = random.randint(1, 6)
    print(f"Received new message: [{body}], will take {processing_time} to process")
    time.sleep(processing_time)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("Finished processing the message")


connection_parameters = pika.ConnectionParameters('localhost')
connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()

channel.queue_declare(queue="Letterbox")

# This gives the consumer up to x numver of messages that are not Acked yet.
channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue="Letterbox", on_message_callback=auto_message_received)

print("Starting consuming")
channel.start_consuming()
