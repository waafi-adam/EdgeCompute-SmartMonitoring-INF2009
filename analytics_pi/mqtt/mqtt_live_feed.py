import cv2
import paho.mqtt.client as mqtt
import time
import base64
import numpy as np
from mqtt_config import BROKER_IP, BROKER_PORT, BROKER_TOPIC_LIVE_FEED, BROKER_CLIENT_ID

# Initialize MQTT client
client = mqtt.Client(BROKER_CLIENT_ID)
client.connect(BROKER_IP, BROKER_PORT, 60)

# Initialize camera
cap = cv2.VideoCapture(0)  # Use the first available camera

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Encode frame as JPEG
    _, buffer = cv2.imencode(".jpg", frame)
    encoded_frame = base64.b64encode(buffer).decode()

    # Publish frame to MQTT
    client.publish(BROKER_TOPIC_LIVE_FEED, encoded_frame)
    time.sleep(0.1)  # Adjust for FPS control
