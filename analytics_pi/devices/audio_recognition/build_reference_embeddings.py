import os
import numpy as np
import librosa
from resemblyzer import VoiceEncoder, preprocess_wav
from scipy.signal import butter, sosfilt

AUTHORIZED_USERS = ["claire", "claris", "gavin", "waafi", "vianiece"]
NUM_SAMPLES = 15         # number of recordings per user
RECORDINGS_DIR = "recordings"  # folder containing recordings
OUTPUT_DIR = "."         # folder to save the reference embeddings
TARGET_SR = 16000        # Resemblyzer works well with 16kHz

# Initialize VoiceEncoder in CPU mode.
encoder = VoiceEncoder("cpu")

def bandpass_filter(data, sr, lowcut=300, highcut=3400, order=5):
    """
    Applies a Butterworth bandpass filter to keep frequencies between lowcut and highcut.
    This helps reduce static noise outside the speech frequency range.
    """
    nyq = 0.5 * sr
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], btype='band', output='sos')
    return sosfilt(sos, data)

def build_reference_embedding(user, num_samples):
    embeddings = []
    for i in range(1, num_samples + 1):
        wav_path = os.path.join(RECORDINGS_DIR, f"{user}_sample{i}.wav")
        if not os.path.isfile(wav_path):
            print(f"Warning: missing file: {wav_path}")
            continue
        # Load audio at the target sample rate
        audio, sr = librosa.load(wav_path, sr=TARGET_SR)
        # Apply bandpass filter to reduce static noise before processing
        audio_filtered = bandpass_filter(audio, sr, lowcut=300, highcut=3400, order=5)
        # Preprocess the filtered audio for the voice encoder
        wav = preprocess_wav(audio_filtered, source_sr=TARGET_SR)
        emb = encoder.embed_utterance(wav)
        embeddings.append(emb)
    if not embeddings:
        return None
    return np.mean(embeddings, axis=0)

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
