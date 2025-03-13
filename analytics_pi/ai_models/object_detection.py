import torch
import cv2
import numpy as np
import paho.mqtt.client as mqtt
import time
import base64
import json
from devices.camera_feed import get_camera_frame
from mqtt.mqtt_config import BROKER_IP, BROKER_PORT, BROKER_TOPIC_AI_ALERTS

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Define Threat Objects (Common dangerous items)
THREAT_OBJECTS = {"knife", "hammer", "gun", "bat", "screwdriver"}

# Initialize MQTT Client
client = mqtt.Client(client_id="ObjectDetector")
client.connect(BROKER_IP, BROKER_PORT, 60)

def detect_threats():
    while True:
        frame = get_camera_frame()
        if frame is None:
            print("🚨 ERROR: No camera frame detected. Skipping detection...")
            continue

        results = model(frame)
        detected_objects = [obj for obj in results.pandas().xyxy[0]['name'] if obj in THREAT_OBJECTS]

        if detected_objects:
            print(f"⚠️ Threat Detected: {detected_objects}")
            alert_data = send_alert(frame, detected_objects)
            client.publish(BROKER_TOPIC_AI_ALERTS, alert_data)

        time.sleep(0.5)

def send_alert(frame, detected_objects):
    _, buffer = cv2.imencode(".jpg", frame)
    encoded_image = base64.b64encode(buffer).decode()

    alert_data = {
        "timestamp": int(time.time()),
        "objects": detected_objects,
        "image": encoded_image
    }

    return json.dumps(alert_data)

if __name__ == "__main__":
    detect_threats()
