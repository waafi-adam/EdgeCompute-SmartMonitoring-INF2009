import os
import time
import numpy as np
import sounddevice as sd
from resemblyzer import VoiceEncoder, preprocess_wav
from sklearn.metrics.pairwise import cosine_similarity
from mqtt.mqtt_live_feed import publish_alert
from mqtt.mqtt_config import connect_mqtt, MQTT_ALERT_TOPIC

AUTHORIZED_USERS = ["claire", "claris", "gavin", "waafi", "vianiece"]
SIMILARITY_THRESHOLD = 0.7
SAMPLE_DURATION = 3
TARGET_SR = 16000
SILENCE_THRESHOLD = 0.01
COOLDOWN_SECONDS = 10  # to avoid spamming alerts

encoder = VoiceEncoder("cpu")
mqtt_client = connect_mqtt()

reference_embeddings = {}
for user in AUTHORIZED_USERS:
    emb_path = f"analytics_pi/devices/audio_recognition/ref_{user}.npy"
    if os.path.exists(emb_path):
        reference_embeddings[user] = np.load(emb_path)
    else:
        print(f"[WARN] Missing embedding: {emb_path}")

if not reference_embeddings:
    raise ValueError("[ERROR] No voice reference embeddings loaded!")

def record_audio():
    try:
        input_device = sd.default.device[0]
        audio = sd.rec(int(TARGET_SR * SAMPLE_DURATION), samplerate=TARGET_SR,
                       channels=1, dtype="float32", device=input_device)
        sd.wait()
        return audio.flatten()
    except Exception as e:
        print(f"[ERROR] Recording failed: {e}")
        return np.array([])

def voice_loop():
    last_alert = 0
    while True:
        audio = record_audio()
        if np.max(np.abs(audio)) < SILENCE_THRESHOLD:
            continue  # skip if silent

        wav = preprocess_wav(audio, source_sr=TARGET_SR)
        emb = encoder.embed_utterance(wav)

        similarities = {
            user: cosine_similarity(emb.reshape(1, -1), ref.reshape(1, -1))[0][0]
            for user, ref in reference_embeddings.items()
        }

        best_user = max(similarities, key=similarities.get)
        best_score = similarities[best_user]

        if best_score >= SIMILARITY_THRESHOLD:
            msg = f"Voice recognized: {best_user}"
        else:
            msg = "Unrecognized voice detected"

        # prevent spamming alerts
        if time.time() - last_alert > COOLDOWN_SECONDS:
            print(f"[VOICE] {msg}")
            publish_alert(mqtt_client, msg, topic=MQTT_ALERT_TOPIC)
            last_alert = time.time()

        time.sleep(0.5)  # small delay to reduce CPU usage
