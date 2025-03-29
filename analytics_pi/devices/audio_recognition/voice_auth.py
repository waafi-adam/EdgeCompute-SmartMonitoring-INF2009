# File: /analytics_pi/devices/voice_recognition/voice_auth.py

import numpy as np
import sounddevice as sd
import time
from resemblyzer import VoiceEncoder, preprocess_wav
from sklearn.metrics.pairwise import cosine_similarity
from scipy.signal import butter, sosfilt
import os
from mqtt.mqtt_live_feed import publish_alert
from mqtt.mqtt_config import connect_mqtt, MQTT_VOICE_ALERT_TOPIC

AUTHORIZED_USERS = ["claire", "claris", "gavin", "waafi", "vianiece"]
SIMILARITY_THRESHOLD = 0.8
SAMPLE_DURATION = 3
TARGET_SR = 16000
SILENCE_THRESHOLD = 0.01

# MQTT Setup
mqtt_client = connect_mqtt()

# Voice encoder
print("[INFO] Loading voice encoder model on CPU...")
encoder = VoiceEncoder("cpu")

# Load reference embeddings
reference_embeddings = {}
for user in AUTHORIZED_USERS:
    emb_path = f"ref_{user}.npy"
    if os.path.isfile(emb_path):
        reference_embeddings[user] = np.load(emb_path)
        print(f"[INFO] Loaded reference for {user}")
    else:
        print(f"[WARN] Missing reference embedding: {emb_path}")

if not reference_embeddings:
    raise RuntimeError("[ERROR] No reference embeddings available!")

def bandpass_filter(data, sr, lowcut=300, highcut=3400, order=5):
    nyq = 0.5 * sr
    sos = butter(order, [lowcut / nyq, highcut / nyq], btype='band', output='sos')
    return sosfilt(sos, data)

def record_audio(duration=SAMPLE_DURATION, sr=TARGET_SR):
    try:
        input_device = sd.default.device[0]
        info = sd.query_devices(input_device, 'input')
        if info['max_input_channels'] < 1:
            raise ValueError("Input device has no channels")
        audio = sd.rec(int(sr * duration), samplerate=sr, channels=1, dtype="float32", device=input_device)
        sd.wait()
        return audio.flatten()
    except Exception as e:
        print(f"[ERROR] Audio recording failed: {e}")
        return np.array([])

def compute_embedding(audio, sr=TARGET_SR):
    filtered_audio = bandpass_filter(audio, sr)
    wav = preprocess_wav(filtered_audio, source_sr=sr)
    return encoder.embed_utterance(wav)

def check_voice_auth():
    audio = record_audio()
    if np.max(np.abs(audio)) < SILENCE_THRESHOLD:
        print("[INFO] Silent or too soft.")
        return

    emb = compute_embedding(audio)
    similarities = {user: cosine_similarity(emb.reshape(1, -1), ref_emb.reshape(1, -1))[0][0]
                    for user, ref_emb in reference_embeddings.items()}

    best_user = max(similarities, key=similarities.get)
    best_score = similarities[best_user]

    print(f"[INFO] Highest similarity: {best_user} ({best_score:.3f})")
    if best_score >= SIMILARITY_THRESHOLD:
        msg = f"Recognized voice: {best_user}"
    else:
        msg = "Unrecognized voice detected"

    publish_alert(mqtt_client, msg, topic=MQTT_VOICE_ALERT_TOPIC)
    print("[MQTT] Alert published:", msg)

def voice_loop():
    while True:
        check_voice_auth()
        time.sleep(5)  # slight delay between checks