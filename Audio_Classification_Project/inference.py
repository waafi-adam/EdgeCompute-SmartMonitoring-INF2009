import numpy as np
import sounddevice as sd
import time
from resemblyzer import VoiceEncoder, preprocess_wav
from sklearn.metrics.pairwise import cosine_similarity
from scipy.signal import butter, sosfilt

AUTHORIZED_USERS = ["claire", "claris", "gavin", "waafi", "vianiece"]

SIMILARITY_THRESHOLD = 0.75 #threshold for similarity to identify an authorized user
SAMPLE_DURATION = 3          # time to record audio in seconds
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
    print(f"\nRecording {duration}s of audio. Please speak...")

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

def authenticate_multi_attempt(num_attempts=3):
    collected_embeddings = []
    
    for attempt in range(num_attempts):
        audio = record_audio()  # already applies bandpass filtering in compute_embedding()
        if np.max(np.abs(audio)) < SILENCE_THRESHOLD:
            print("Audio too silent! Please speak louder.")
            continue
        
        emb = compute_embedding(audio)
        collected_embeddings.append(emb)
        time.sleep(0.5)  # slight pause between attempts
    
    if not collected_embeddings:
        print("No valid recordings captured.")
        return "UNKNOWN"
    
    # Average the embeddings from multiple attempts
    avg_emb = np.mean(collected_embeddings, axis=0)
    
    # Compare the average embedding with each reference embedding
    similarities = {}
    for user, ref_emb in reference_embeddings.items():
        sim = cosine_similarity(avg_emb.reshape(1, -1), ref_emb.reshape(1, -1))[0][0]
        similarities[user] = sim
        print(f"Cosine similarity with {user}: {sim:.3f}")
    
    best_user = max(similarities, key=similarities.get)
    best_sim = similarities[best_user]
    print(f"Highest similarity: {best_sim:.3f}")
    
    if best_sim >= SIMILARITY_THRESHOLD:
        print(f"AUTHORIZED USER (Similarity: {best_sim:.3f})")
        return "AUTHORIZED"
    else:
        print("UNKNOWN user.")
        return "UNKNOWN"

if __name__ == "__main__":
    result = authenticate_multi_attempt(num_attempts=3)
    print("Final Result:", result)



