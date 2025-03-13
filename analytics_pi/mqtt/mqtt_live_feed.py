import cv2
import paho.mqtt.client as mqtt
import time
import base64
from devices.camera_feed import get_camera_frame
from mqtt_config import BROKER_IP, BROKER_PORT, BROKER_TOPIC_LIVE_FEED

# Initialize MQTT client
client = mqtt.Client(client_id="AnalyticsPiLiveFeed")
client.connect(BROKER_IP, BROKER_PORT, 60)

def start_live_feed():
    while True:
        frame = get_camera_frame()
        if frame is None:
            continue

        # Encode frame as JPEG
        _, buffer = cv2.imencode(".jpg", frame)
        encoded_frame = base64.b64encode(buffer).decode()

        # Publish frame to MQTT
        client.publish(BROKER_TOPIC_LIVE_FEED, encoded_frame)
        time.sleep(0.1)

if __name__ == "__main__":
    start_live_feed()
