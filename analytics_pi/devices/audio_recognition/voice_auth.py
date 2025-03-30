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
SILENCE_THRESHOLD = 0.2
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
    """
    Applies a Butterworth bandpass filter to keep frequencies between lowcut and highcut.
    """
    nyq = 0.5 * sr
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], btype='band', output='sos')
    return sosfilt(sos, data)

def record_audio(duration=SAMPLE_DURATION, sr=TARGET_SR):
    try:
        input_device = sd.default.device[0]  # or use `sd.query_devices(kind='input')` to explore
        info = sd.query_devices(input_device, 'input')
        channels = info['max_input_channels']
        if channels < 1:
            raise ValueError(f"Device {input_device} does not support input channels.")

        audio = sd.rec(int(sr * duration), samplerate=sr, channels=1, dtype="float32", device=input_device)
        sd.wait()
        return audio.flatten()
    except Exception as e:
        print(f"[ERROR] Failed to record audio: {e}")
        return np.array([])

def compute_embedding(audio, sr=TARGET_SR):
    # Apply bandpass filter to reduce static noise before preprocessing
    filtered_audio = bandpass_filter(audio, sr, lowcut=300, highcut=3400, order=5)
    wav = preprocess_wav(filtered_audio, source_sr=sr)
    emb = encoder.embed_utterance(wav)
    return emb

def is_voice_detected(audio, threshold=0.25):
    filtered = bandpass_filter(audio, sr=TARGET_SR, lowcut=300, highcut=3400)
    energy = np.sqrt(np.mean(np.square(filtered)))
    print(f"[DEBUG] Filtered RMS energy: {energy:.5f}")
    return energy > threshold




def authenticate_multi_attempt(num_attempts=3):
    collected_embeddings = []

    for attempt in range(num_attempts):
        print(f"[VOICE LOOP] Recording attempt {attempt + 1}/{num_attempts}...")
        audio = record_audio(duration=SAMPLE_DURATION)
        if audio.size == 0 or not is_voice_detected(audio):
            print("[INFO] No valid voice detected. Skipping this attempt.")
            continue

        emb = compute_embedding(audio)
        collected_embeddings.append(emb)
        time.sleep(0.5)  # slight pause between attempts

    if not collected_embeddings:
        print("[WARN] No usable recordings captured.")
        return None

    return np.mean(collected_embeddings, axis=0)


def voice_loop():
    print("[VOICE LOOP] Listening for voice activity...")
    while True:
        chunk = record_audio(duration=0.5)

        if chunk.size == 0:
            continue

        if is_voice_detected(chunk):
            print("[VOICE LOOP] Voice detected! Performing multi-attempt auth...")

            avg_emb = authenticate_multi_attempt(num_attempts=3)
            if avg_emb is None:
                continue  # Skip if no usable attempts

            # Compare to reference embeddings
            similarities = {
                user: cosine_similarity(avg_emb.reshape(1, -1), ref_emb.reshape(1, -1))[0][0]
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

        time.sleep(0.3)  # small cooldown
