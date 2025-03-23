import sounddevice as sd
import numpy as np

def record_audio(duration=10, sample_rate=44100):
    try:
        print(f"🎙️ Recording for {duration} seconds...")
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.float32)
        sd.wait()  # Wait until recording is finished
        print("✅ Recording complete.")
        return audio.flatten()  # Return as a 1D NumPy array
    except Exception as e:
        print(f"❌ Error recording audio: {e}")
        return None
