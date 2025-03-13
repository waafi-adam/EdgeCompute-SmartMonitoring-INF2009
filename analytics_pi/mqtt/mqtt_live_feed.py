import cv2
import paho.mqtt.client as mqtt
import time
import base64
from devices.camera_feed import get_camera_frame
from mqtt.mqtt_config import BROKER_IP, BROKER_PORT, BROKER_TOPIC_LIVE_FEED

# Initialize MQTT client
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1, client_id="AnalyticsPiLiveFeed")
client.connect(BROKER_IP, BROKER_PORT, 60)

def start_live_feed():
    print("📡 Starting Live Feed...")
    while True:
        frame = get_camera_frame()
        if frame is None:
            print("🚨 ERROR: No frame detected. Skipping frame...")
            continue

        # Encode frame as JPEG
        _, buffer = cv2.imencode(".jpg", frame)
        encoded_frame = base64.b64encode(buffer).decode()

        # Publish frame to MQTT
        client.publish(BROKER_TOPIC_LIVE_FEED, encoded_frame)
        print("📡 Sent frame to MQTT.")
        time.sleep(0.1)

if __name__ == "__main__":
    start_live_feed()
