from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import json
import pika
import time
import random
import os

# Get the queues from the compose files
inference_queue = os.getenv("MODEL_QUEUE", "Letterbox")

BASE_DIR = Path(__file__).resolve().parent  # api/src

# To convert the data from web to JSON-ish with pydantic
class AddRequest(BaseModel):
    v1: float
    v2: float

# Tries to make connection with broker
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


# Set up the channel and queues when starting up the API/WEB and closing the connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = connect_with_broker()
    print("Connection succesful!")
    channel = connection.channel()
    channel.queue_declare(queue=inference_queue)

    app.state.rabbit_conn = connection
    app.state.rabbit_ch = channel

    yield # Closing the connection
    connection = getattr(app.state, "rabbit_conn", None)
    if connection and connection.is_open:
        connection.close()
        print("Connection closed!")

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
    # Get the channel
    channel = app.state.rabbit_ch

    # Make a dictionairy of the data.
    payload = {"v1": req.v1, "v2": req.v2}

    # Sends the data to the broker
    channel.basic_publish(
        exchange="",
        routing_key=inference_queue,
        body=json.dumps(payload).encode("utf-8"), # Makes the dict. to json, then to bytes for RabbitMQ
        properties=pika.BasicProperties(content_type="api/addition/json")
    )
    print("Data sent to broker!")
    
    return {"Status:": "Queued"}