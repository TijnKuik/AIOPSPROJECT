import pika
import time
import json
import inference_consumer as consumer
import inference_producer as producer
import os


connection_producer = producer.connect_with_broker()
connection_consumer = consumer.connect_with_broker()

consumer.consume_message_inference(connection_consumer)


def send_result_to_api(value):
    global connection_producer
    producer.send_message_api(connection_producer)

