# build_reference_embeddings.py
import os
import numpy as np
import librosa
from resemblyzer import VoiceEncoder, preprocess_wav

AUTHORIZED_USERS = ["claire", "claris", "gavin", "waafi", "vianiece"]
NUM_SAMPLES = 15         # no of recordings per user
RECORDINGS_DIR = "recordings"  # folder containing recordings
OUTPUT_DIR = "."         # folder to save the reference embeddings
TARGET_SR = 16000        # Resemblyzer works well with 16kHz

# initialize VoiceEncoder in cpu mode
encoder = VoiceEncoder("cpu")

def build_reference_embedding(user, num_samples):
    embeddings = []
    for i in range(1, num_samples + 1):
        wav_path = os.path.join(RECORDINGS_DIR, f"{user}_sample{i}.wav")
        if not os.path.isfile(wav_path):
            print(f"Warning: missing file: {wav_path}")
            continue
        audio, sr = librosa.load(wav_path, sr=TARGET_SR)
        wav = preprocess_wav(audio, source_sr=TARGET_SR)
        emb = encoder.embed_utterance(wav)
        embeddings.append(emb)
    if not embeddings:
        return None
    return np.mean(embeddings, axis=0) \

def main():
    for user in AUTHORIZED_USERS:
        print(f"Processing user: {user}")
        ref_emb = build_reference_embedding(user, NUM_SAMPLES)
        if ref_emb is None:
            print(f"No valid audio found for user {user}. Skipping.")
            continue
        out_path = os.path.join(OUTPUT_DIR, f"ref_{user}.npy")
        np.save(out_path, ref_emb)
        print(f"Saved reference embedding for '{user}' at: {out_path}\n")

if __name__ == "__main__":
    main()
