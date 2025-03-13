import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt
import time
import base64
from devices.camera_feed import get_camera_frame
from mqtt.mqtt_config import BROKER_IP, BROKER_PORT, BROKER_TOPIC_AI_ALERTS
import json 

# Define Threat Objects
THREAT_OBJECTS = {"knife", "hammer", "gun", "bat", "screwdriver"}

# Initialize MQTT Client
client = mqtt.Client("ObjectDetector")
client.connect(BROKER_IP, BROKER_PORT, 60)

# Initialize MediaPipe Object Detection
mp_objectron = mp.solutions.objectron
objectron = mp_objectron.Objectron(static_image_mode=False, max_num_objects=5, model_name='Shoe')

def detect_threats():
    while True:
        frame = get_camera_frame()
        if frame is None:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = objectron.process(rgb_frame)

        detected_objects = []
        if results.detected_objects:
            for obj in results.detected_objects:
                obj_name = obj.label.lower()
                if obj_name in THREAT_OBJECTS:
                    detected_objects.append(obj_name)

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

    return json.dumps(alert_data)  # ✅ Fix: Convert to JSON format

if __name__ == "__main__":
    detect_threats()
