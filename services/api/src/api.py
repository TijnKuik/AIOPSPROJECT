from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel
from pathlib import Path
import threading
import src.api_producer as producer
import src.api_consumer as consumer
import json
import pika
import time
import random
import os
# Get the queues from the compose files
inference_queue = os.getenv("MODEL_QUEUE", "Letterbox")

BASE_DIR = Path(__file__).resolve().parent  # api/src

connection_producer = None
connection_consumer = None
consumer_thread = None

# To convert the data from web to JSON-ish with pydantic
class AddRequest(BaseModel):
    v1: float
    v2: float


def start_consuming(connection):
    consumer.consume_message_inference(connection)

# Set up the channel and queues when starting up the API/WEB and closing the connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    global connection_producer, connection_consumer, consumer_thread

    connection_producer = producer.connect_with_broker()
    connection_consumer = consumer.connect_with_broker()

    if connection_producer is None or connection_consumer is None:
        raise RuntimeError("Could not connect to RabbitMQ")

    print("- [API] Connection successful!")

    # start consumer in background
    consumer_thread = threading.Thread(
        target=start_consuming,
        args=(connection_consumer,),
        daemon=True
    )
    consumer_thread.start()

    yield # Closing the connection
    producer.close_connection(connection_producer)
    consumer.close_connection(connection_consumer)


# Set up the fastapi app
app = FastAPI(lifespan=lifespan)


# Serve static files (css, js, images)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Setting up the home page
@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")
    

@app.post("/add")
def add(req: AddRequest):
    global connection_producer; global connection_consumer
    job_id = random.randint(10000, 99999)
    # Make a dictionairy of the data.
    payload = {"job_id": job_id, "v1": req.v1, "v2": req.v2}
    producer.send_message_inference(connection_producer, payload)
    data = consumer.retrieve_job(job_id)
    print(data)
    return {"Status:": "Queued"}


