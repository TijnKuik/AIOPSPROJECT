import pika
import time
import random
import os



connection_parameters = pika.ConnectionParameters('localhost')
connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()

channel.queue_declare(queue="Letterbox")

messageId = 1 

while(True):
    message = f"Hello this is the first message, MSGID: {messageId}"
    channel.basic_publish(exchange='', routing_key="Letterbox", body=message)
    print(f"Sent message: [{message}]")
    time.sleep(random.randint(1, 4))

    messageId += 1