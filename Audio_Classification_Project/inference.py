# authenticate.py
import numpy as np
import sounddevice as sd
import time
from resemblyzer import VoiceEncoder, preprocess_wav
from sklearn.metrics.pairwise import cosine_similarity

AUTHORIZED_USERS = ["claire", "claris", "gavin", "waafi", "vianiece"]

SIMILARITY_THRESHOLD = 0.75
SAMPLE_DURATION = 3          #time to record audio
TARGET_SR = 16000            # Resemblyzer default sample rate (16kHz)
SILENCE_THRESHOLD = 0.01     # minimum audio amplitude to consider as speech


print("Loading voice encoder model on CPU...")
encoder = VoiceEncoder("cpu")

reference_embeddings = {}
for user in AUTHORIZED_USERS:
    emb_path = f"ref_{user}.npy"
    try:
        reference_embeddings[user] = np.load(emb_path)
        print(f"Loaded reference for {user} from {emb_path}")
    except FileNotFoundError:
        print(f"Missing reference embedding for {user}. Please run build_reference_embeddings.py.")

if not reference_embeddings:
    raise ValueError("No reference embeddings available!")


def record_audio(duration=SAMPLE_DURATION, sr=TARGET_SR):
    print(f"\nRecording {duration}s of audio. Please speak...")

    try:
        input_device = sd.default.device[0]  # Get system's default input device
        audio = sd.rec(int(sr * duration), samplerate=sr, channels=1, dtype="float32", device=input_device)
        sd.wait()
        return audio.flatten()
    except Exception as e:
        print(f"[ERROR] Failed to record audio: {e}")
        return np.array([])


def compute_embedding(audio, sr=TARGET_SR):
    # preprocess_wav accepts a raw numpy array.
    wav = preprocess_wav(audio, source_sr=sr)
    emb = encoder.embed_utterance(wav)
    return emb

def authenticate():
    max_attempts = 3
    attempt = 0
    while attempt < max_attempts:
        audio = record_audio()
        if np.max(np.abs(audio)) < SILENCE_THRESHOLD:
            print("Audio too silent! Please speak louder.\n")
            attempt += 1
            continue

        new_emb = compute_embedding(audio)
        similarities = {}
        # compute cosine similarity with each authorized user
        for user, ref_emb in reference_embeddings.items():
            sim = cosine_similarity(new_emb.reshape(1, -1), ref_emb.reshape(1, -1))[0][0]
            similarities[user] = sim
            print(f"Cosine similarity with {user}: {sim:.3f}")

        # get the highest similarity value and corresponding user
        best_user = max(similarities, key=similarities.get)
        best_sim = similarities[best_user]
        print(f"Highest similarity: {best_sim:.3f}")

        # binary decision: if the best similarity exceeds the threshold, accept as authorized.
        if best_sim >= SIMILARITY_THRESHOLD:
            print(f"AUTHORIZED USER (Similarity: {best_sim:.3f})")
            return "AUTHORIZED"
        else:
            print("UNKNOWN user. Try again...\n")
            attempt += 1
            time.sleep(1)
    
    print("Failed to authenticate after 3 attempts.")
    return "UNKNOWN"

if __name__ == "__main__":
    result = authenticate()
    print("Final Result:", result)
