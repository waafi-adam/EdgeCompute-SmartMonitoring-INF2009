import smbus
import pandas as pd
import numpy as np
import joblib
import os
import time
from scipy.fft import fft
from mqtt.mqtt_gesture import publish_gesture_alert

# Path to model files
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(CURRENT_DIR, "gesture_model.pkl"))
scaler = joblib.load(os.path.join(CURRENT_DIR, "scaler.pkl"))
feature_names = joblib.load(os.path.join(CURRENT_DIR, "feature_names.pkl"))

# I2C Setup
bus = smbus.SMBus(1)
ACC_ADDRESS = 0x19
GESTURE_WINDOW_SIZE = 10

data_window = []
last_gesture_time = 0
last_prediction = None
GESTURE_COOLDOWN = 10  # seconds
VARIANCE_THRESHOLD = 100

def read_accelerometer():
    def read_word(reg_low, reg_high):
        low = bus.read_byte_data(ACC_ADDRESS, reg_low)
        high = bus.read_byte_data(ACC_ADDRESS, reg_high)
        value = (high << 8) | low
        return value if value < 32768 else value - 65536

    x = read_word(0x28, 0x29)
    y = read_word(0x2A, 0x2B)
    z = read_word(0x2C, 0x2D)
    return x, y, z

def extract_features(window):
    window = np.array(window)
    features = []

    for i in range(3):
        axis_data = window[:, i]
        features += [
            np.mean(axis_data),
            np.std(axis_data),
            np.min(axis_data),
            np.max(axis_data),
            np.mean(np.abs(axis_data - np.mean(axis_data))),
            np.sum(axis_data ** 2) / len(axis_data)
        ]

    for i in range(3):
        fft_vals = np.abs(fft(window[:, i]))[:len(window) // 2]
        freq_max = np.argmax(fft_vals)
        spectral_entropy = -np.sum((fft_vals / np.sum(fft_vals)) * np.log2(fft_vals / np.sum(fft_vals) + 1e-10))
        features.append(freq_max)
        features.append(spectral_entropy)

    return np.array(features).reshape(1, -1)

def is_still(window):
    window = np.array(window)
    total_variance = np.sum(np.var(window, axis=0))
    return total_variance < VARIANCE_THRESHOLD

def process_next(mqtt_client):
    global data_window, last_gesture_time, last_prediction
    acc_x, acc_y, acc_z = read_accelerometer()
    data_window.append([acc_x, acc_y, acc_z])

    if len(data_window) == GESTURE_WINDOW_SIZE:
        # Manually override any model prediction if sensor is physically still
        if is_still(data_window):
            data_window.pop(0)
            return  # Completely skip detection and alerting

        features = extract_features(data_window)
        features_df = pd.DataFrame(features, columns=feature_names)
        features_scaled = scaler.transform(features_df)

        prediction = model.predict(features_scaled)[0].lower()

        data_window.pop(0)  # Maintain sliding window

        # Skip any model-predicted stationary gestures (extra guard)
        if prediction == "stationary":
            return

        now = time.time()
        if now - last_gesture_time > GESTURE_COOLDOWN:
#             print(f"[GESTURE] Detected: {prediction}")
            try:
                publish_gesture_alert(mqtt_client, "Movement detected!")
                last_gesture_time = now
                last_prediction = prediction
            except Exception as e:
                print("[ERROR] Failed to publish gesture alert:", e)


time.sleep(3)  # Sampling rate
