import smbus
import pandas as pd
import numpy as np
import joblib
import time
from scipy.fft import fft

# Load trained model and scaler
model = joblib.load("gesture_model.pkl")
scaler = joblib.load("scaler.pkl")

# I2C Configuration
bus = smbus.SMBus(1)
ACC_ADDRESS = 0x19  # Accelerometer I2C address

def read_accelerometer():
    """Read accelerometer values from I2C"""
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
    """Extract features for real-time classification."""
    window = np.array(window)
    features = []
    
    for i in range(3):  # x, y, z axes
        axis_data = window[:, i]
        
        features.append(np.mean(axis_data))
        features.append(np.std(axis_data))
        features.append(np.min(axis_data))
        features.append(np.max(axis_data))
        features.append(np.mean(np.abs(axis_data - np.mean(axis_data))))
        features.append(np.sum(axis_data ** 2) / len(axis_data))
    
    for i in range(3):
        fft_vals = np.abs(fft(window[:, i]))[:len(window) // 2]
        freq_max = np.argmax(fft_vals)
        spectral_entropy = -np.sum((fft_vals / np.sum(fft_vals)) * np.log2(fft_vals / np.sum(fft_vals) + 1e-10))
        
        features.append(freq_max)
        features.append(spectral_entropy)

    return np.array(features).reshape(1, -1)

# Real-time gesture recognition
window_size = 10
data_window = []

print("Starting real-time gesture recognition...")
while True:
    acc_x, acc_y, acc_z = read_accelerometer()
    data_window.append([acc_x, acc_y, acc_z])

    if len(data_window) == window_size:
        # Extract features from the window
        features = extract_features(data_window)

        # Load feature names
        feature_names = joblib.load("feature_names.pkl")

        # Convert extracted features to DataFrame with correct column names
        features_df = pd.DataFrame(features, columns=feature_names)

        # Normalize using the same feature names
        features = scaler.transform(features_df)

        # Predict gesture
        prediction = model.predict(features)[0]
        print(f"Detected Gesture: {prediction}")

        # Maintain sliding window
        data_window.pop(0)

    time.sleep(0.05)  # Sampling rate (20Hz)

