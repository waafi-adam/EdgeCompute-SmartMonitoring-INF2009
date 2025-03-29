import threading
import cv2
import base64
import time
import json
import smbus
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from scipy.fft import fft

from mqtt.mqtt_config import connect_mqtt
from mqtt.mqtt_live_feed import publish_feed, publish_alert
from mqtt.mqtt_gesture import publish_gesture_alert
from mqtt.mqtt_config import MQTT_FACE_ALERT_TOPIC, MQTT_OBJECT_ALERT_TOPIC, MQTT_GESTURE_ALERT_TOPIC

from devices.camera_feed import facial_recognition as fr
from devices.camera_feed import object_detection as od
from devices.gesturerecognition import gesture as gesture
from devices.audio_recognition.voice_auth import voice_loop

fr.load_face_data()
fr.setup_mqtt()

# ---------- Video Stream Class ----------
class VideoStream:
    def __init__(self, src=0, width=640, height=480):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.ret, self.frame = self.cap.read()
        self.running = True
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.running = False
        self.cap.release()

# ---------- Async MQTT Publishing ----------
def async_publish(jpg_text):
    threading.Thread(target=publish_feed, args=(mqtt_client, jpg_text), daemon=True).start()

# ---------- MQTT Setup ----------
mqtt_client = connect_mqtt()
mqtt_thread = threading.Thread(target=mqtt_client.loop_forever)
mqtt_thread.daemon = True
mqtt_thread.start()

# ---------- Webcam Setup ----------
video_stream = VideoStream()
if not video_stream.ret:
    print("[ERROR] Unable to access the webcam.")
    exit()

# ---------- Alert Settings ----------
alert_interval = 30  # seconds
last_alert_time = 0
frame_count = 0

# ---------- Detection Thread ----------
detection_lock = threading.Lock()
latest_annotated_frame = None
latest_face_names = []
latest_object_alerts = []

# ---------- Gesture Alert Handling ----------
def on_gesture_alert(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
    except Exception as e:
        print("[ERROR] Failed to handle gesture MQTT message:", e)

mqtt_client.subscribe(MQTT_GESTURE_ALERT_TOPIC)
mqtt_client.message_callback_add(MQTT_GESTURE_ALERT_TOPIC, on_gesture_alert)

def detection_worker():
    global latest_annotated_frame, latest_face_names, latest_object_alerts
    while True:
        ret, frame = video_stream.read()
        if not ret:
            continue

        try:
            annotated_frame, face_names = fr.process_frame(frame, model='small', cv_scaler=3)
            object_annotated, object_alerts = od.detect_objects(frame)
            composite_frame = cv2.addWeighted(object_annotated, 0.6, annotated_frame, 0.4, 0)

            with detection_lock:
                latest_annotated_frame = composite_frame.copy()
                latest_face_names = face_names
                latest_object_alerts = object_alerts

            for msg in object_alerts:
                try:
                    publish_alert(mqtt_client, msg, topic=MQTT_OBJECT_ALERT_TOPIC)
                except Exception as e:
                    print("[ERROR] Failed to publish object alert immediately:", e)

        except Exception as e:
            print(f"[ERROR] Detection thread exception: {e}")
            continue

# Start detection in background
detection_thread = threading.Thread(target=detection_worker, daemon=True)
detection_thread.start()
# Start voice authentication in background
voice_thread = threading.Thread(target=voice_loop, daemon=True)
voice_thread.start()
# # In your main loop or in a thread:
# threading.Thread(target=voice_loop_worker, daemon=True).start()


# ---------- Main Loop (MQTT Publishing) ----------
frame_count = 0

while True:
    frame_count += 1
    time.sleep(0.05)  # ~20 FPS max render loop
    
    with detection_lock:
        display_frame = latest_annotated_frame.copy() if latest_annotated_frame is not None else None
        face_names = latest_face_names[:]
        object_alerts = latest_object_alerts[:]
        
    gesture.process_next(mqtt_client)


    if display_frame is None:
        continue

    # Encode and publish every 5th frame
    if frame_count % 5 == 0:
        stream_frame = cv2.resize(display_frame, (320, 240))
        ret2, buffer = cv2.imencode('.jpg', stream_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if ret2:
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            async_publish(jpg_as_text)

    # Publish face alerts if needed
    current_time = time.time()
    if (current_time - last_alert_time) > alert_interval:
        for name in face_names:
            try:
                msg = "Unrecognized face detected" if name == "Unknown" else f"Recognized: {name}"
                publish_alert(mqtt_client, msg, topic=MQTT_FACE_ALERT_TOPIC)
            except Exception as e:
                print("[ERROR] Failed to publish face alert:", e)

        last_alert_time = current_time
    



video_stream.stop()
mqtt_client.disconnect()




