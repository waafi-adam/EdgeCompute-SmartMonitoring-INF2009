import smbus
import time
import numpy as np
import csv
import os
from scipy.fft import fft

# I2C Configuration
bus = smbus.SMBus(1)
ACC_ADDRESS = 0x19  # Accelerometer I2C address

# Enable accelerometer (Normal mode, 10Hz, all axes active)
bus.write_byte_data(ACC_ADDRESS, 0x20, 0x27)

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

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
    """Extract features from a window of accelerometer readings."""
    window = np.array(window)
    features = []
    
    # Time-Domain Features
    for i in range(3):  # x, y, z axes
        axis_data = window[:, i]
        
        features.append(np.mean(axis_data))  # Mean
        features.append(np.std(axis_data))   # Standard Deviation
        features.append(np.min(axis_data))   # Min
        features.append(np.max(axis_data))   # Max
        features.append(np.mean(np.abs(axis_data - np.mean(axis_data))))  # Mean Absolute Difference
        features.append(np.sum(axis_data ** 2) / len(axis_data))  # Signal Energy
    
    # Frequency-Domain Features
    for i in range(3):  # x, y, z axes
        fft_vals = np.abs(fft(window[:, i]))[:len(window) // 2]  # Compute FFT and take half spectrum
        freq_max = np.argmax(fft_vals)  # Dominant frequency index
        spectral_entropy = -np.sum((fft_vals / np.sum(fft_vals)) * np.log2(fft_vals / np.sum(fft_vals) + 1e-10))  # Spectral Entropy
        
        features.append(freq_max)
        features.append(spectral_entropy)

    return features

# Collect Data for Multiple Gestures
all_data = []
window_size = 10  # 10 samples per window (~0.5s if sampling at 20Hz)

while True:
    gesture_name = input("\nEnter gesture label (or type 'done' to finish): ")
    if gesture_name.lower() == 'done':
        break  # Stop collecting gestures
    
    print(f"Collecting data for '{gesture_name}' gesture. Move your hand!")

    data_window = []
    start_time = time.time()
    
    while time.time() - start_time < 10:  # Record for 10 seconds
        acc_x, acc_y, acc_z = read_accelerometer()
        data_window.append([acc_x, acc_y, acc_z])
        
        if len(data_window) == window_size:
            features = extract_features(data_window)
            features.append(gesture_name)
            all_data.append(features)
            data_window.pop(0)  # Maintain sliding window
        
        time.sleep(0.05)  # Sampling rate (20Hz)

print("\nAll gestures recorded! Saving to CSV...")

# Check if the file already exists
csv_filename = os.path.join(script_dir, "gestures_dataset.csv")
file_exists = os.path.exists(csv_filename)

# Open the file in append mode
with open(csv_filename, "a", newline="") as file:
    writer = csv.writer(file)

    # If file does not exist, write the header first
    if not file_exists:
        feature_names = [f"mean_{axis}" for axis in ['x', 'y', 'z']] + \
                        [f"std_{axis}" for axis in ['x', 'y', 'z']] + \
                        [f"min_{axis}" for axis in ['x', 'y', 'z']] + \
                        [f"max_{axis}" for axis in ['x', 'y', 'z']] + \
                        [f"mad_{axis}" for axis in ['x', 'y', 'z']] + \
                        [f"energy_{axis}" for axis in ['x', 'y', 'z']] + \
                        [f"freq_max_{axis}" for axis in ['x', 'y', 'z']] + \
                        [f"spectral_entropy_{axis}" for axis in ['x', 'y', 'z']] + \
                        ["gesture"]
        writer.writerow(feature_names)  # Write the header only once

    # Append new data
    writer.writerows(all_data)

print(f"New features appended to {csv_filename}")
