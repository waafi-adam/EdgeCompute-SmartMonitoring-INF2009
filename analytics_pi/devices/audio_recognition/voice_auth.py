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
SIMILARITY_THRESHOLD = 0.7
SAMPLE_DURATION = 3
TARGET_SR = 16000
SILENCE_THRESHOLD = 0.01
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# MQTT Setup
mqtt_client = connect_mqtt()

# Voice encoder
print("[INFO] Loading voice encoder model on CPU...")
encoder = VoiceEncoder("cpu")

# Load reference embeddings
reference_embeddings = {}
for user in AUTHORIZED_USERS:
    emb_path = os.path.join(CURRENT_DIR, f"ref_{user}.npy")
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
    filtered_audio = bandpass_filter(audio, sr, lowcut=300, highcut=3400, order=5)
    wav = preprocess_wav(filtered_audio, source_sr=sr)
    return encoder.embed_utterance(wav)

def is_voice_detected(audio, threshold=0.01):
    # Check if energy in the speech range is strong enough
    energy = np.mean(np.square(audio))
    return energy > threshold

def check_voice_auth():
    audio = record_audio()
    if audio.size == 0:
        return

    if not is_voice_detected(audio, threshold=SILENCE_THRESHOLD):
        print("[INFO] No voice detected.")
        return

    emb = compute_embedding(audio)
    similarities = {
        user: cosine_similarity(emb.reshape(1, -1), ref_emb.reshape(1, -1))[0][0]
        for user, ref_emb in reference_embeddings.items()
    }

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
    print("[VOICE LOOP] Listening for voice activity...")
    while True:
        # Short listening window (0.5s)
        chunk_duration = 0.5
        chunk = record_audio(duration=chunk_duration)

        if chunk.size == 0:
            continue

        if is_voice_detected(chunk):
            print("[VOICE LOOP] Voice detected! Capturing 3s sample...")
            audio = record_audio(duration=SAMPLE_DURATION)
            if audio.size == 0:
                continue

            if not is_voice_detected(audio):
                print("[INFO] False trigger, discarded.")
                continue

            # Continue with authentication
            emb = compute_embedding(audio)
            similarities = {
                user: cosine_similarity(emb.reshape(1, -1), ref_emb.reshape(1, -1))[0][0]
                for user, ref_emb in reference_embeddings.items()
            }

            best_user = max(similarities, key=similarities.get)
            best_score = similarities[best_user]

            print(f"[INFO] Highest similarity: {best_user} ({best_score:.3f})")
            msg = (
                f"Recognized voice: {best_user}"
                if best_score >= SIMILARITY_THRESHOLD
                else "Unrecognized voice detected"
            )

            publish_alert(mqtt_client, msg, topic=MQTT_VOICE_ALERT_TOPIC)
            print("[MQTT] Alert published:", msg)

        time.sleep(0.3)  # small cooldown to reduce CPU
