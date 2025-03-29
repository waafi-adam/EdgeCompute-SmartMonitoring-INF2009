import face_recognition
import cv2
import numpy as np
import time
import pickle
import os
from mqtt.mqtt_live_feed import publish_alert
from mqtt.mqtt_config import connect_mqtt

print("[INFO] facial_recognition module loaded")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENCODINGS_FILE = os.path.join(CURRENT_DIR, "encodings.pickle")

known_face_encodings = []
known_face_names = []
mqtt_client = None

def load_face_data():
    global known_face_encodings, known_face_names
    if not os.path.exists(ENCODINGS_FILE):
        raise FileNotFoundError(f"encodings.pickle not found at {ENCODINGS_FILE}")

    with open(ENCODINGS_FILE, "rb") as f:
        data = pickle.load(f)
    known_face_encodings = data["encodings"]
    known_face_names = data["names"]


def setup_mqtt():
    global mqtt_client
    mqtt_client = connect_mqtt()


def process_frame(frame, model='small', cv_scaler=2):
    if not known_face_encodings or not known_face_names:
        raise RuntimeError("[ERROR] Face data not loaded. Call load_face_data() first.")

    # Downscale for performance
    small_frame = cv2.resize(frame, (0, 0), fx=(1/cv_scaler), fy=(1/cv_scaler))
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect faces and compute encodings
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations, model=model)

    face_names = []
    scaled_locations = []

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        if face_distances.size > 0:
            best_index = np.argmin(face_distances)
            if matches[best_index]:
                name = known_face_names[best_index]
        face_names.append(name)

        # Scale face coordinates back up to original size
        scaled_locations.append((top * cv_scaler, right * cv_scaler, bottom * cv_scaler, left * cv_scaler))

    # Draw annotations on original frame
    annotated_frame = draw_results(frame.copy(), scaled_locations, face_names)
    return annotated_frame, face_names


def draw_results(frame, face_locations, face_names):
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        cv2.rectangle(frame, (left, top), (right, bottom), (244, 42, 3), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        label = name
        font_scale = 1.0
        thickness = 1
        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
        padding_x, padding_y = 10, 5
        label_width = text_width + 2 * padding_x
        label_height = text_height + 2 * padding_y
        center_x = (left + right) // 2
        label_left = center_x - label_width // 2
        label_right = center_x + label_width // 2
        label_bottom = top - 5
        label_top = label_bottom - label_height

        cv2.rectangle(frame, (label_left, label_top), (label_right, label_bottom), (244, 42, 3), cv2.FILLED)
        text_x = label_left + (label_width - text_width) // 2
        text_y = label_top + (label_height + text_height) // 2 - baseline + 10
        cv2.putText(frame, label, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
    return frame


def send_alert(message):
    if mqtt_client is None:
        setup_mqtt()
    publish_alert(mqtt_client, message)
