import librosa
import os
import numpy as np
import soundfile as sf

def extract_audio_features(audio_path):
    audio_path = os.path.abspath(audio_path)
    print(f"📂 Loading audio file: {audio_path}...")
    
    try:
        # Validate the WAV file
        with sf.SoundFile(audio_path) as f:
            print(f"✅ Valid WAV file detected! Format: {f.format}, Channels: {f.channels}, Samplerate: {f.samplerate}")
        
        # Load audio
        y, sr = sf.read(audio_path)
        y = preprocess_audio(y)
        
        if np.max(np.abs(y)) == 0:
            print("⚠️ Audio signal is silent. Skipping feature extraction.")
            return 0, None
        
        tempo, key = analyze_audio(y, sr)
        return tempo, key
        
    except Exception as e:
        print(f"❌ Error in feature extraction: {e}")
        return 0, None


def preprocess_audio(y):
    """Preprocess audio by converting to float32, normalizing, and ensuring mono format."""
    if y.dtype != np.float32:
        y = y.astype(np.float32) / np.max(np.abs(y))  # Normalize if it's int16
    
    if y.ndim > 1:
        y = librosa.to_mono(y.T)  # Convert to mono if needed
    
    y = np.nan_to_num(y, nan=0.0, posinf=1.0, neginf=-1.0)  # Clean NaN/Inf values
    
    max_val = np.max(np.abs(y))
    if max_val > 0 and max_val < 0.999:
        y /= max_val  # Scale to [-1, 1]
    
    return librosa.util.normalize(y) if max_val < 0.999 else y


def analyze_audio(y, sr):
    """Analyze tempo and key from the given audio signal."""
    try:
        energy = np.sum(y ** 2)
        if energy < 1e-4:
            print("⚠️ Energy too low, likely silent or very quiet audio.")
            return 0, None
        
        y_harm, y_perc = harmonic_percussive_separation(y)
        onset_env = librosa.onset.onset_strength(y=y_perc, sr=sr)
        tempo = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)[0] if np.any(onset_env) else 0
        
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        key = chroma.mean(axis=1).argmax()
        
        print(f"🎵 Detected Tempo: {tempo}")
        print(f"🎹 Estimated Key: {key}")
        
        return tempo, key
    
    except Exception as e:
        print(f"❌ Error during feature extraction: {e}")
        return 0, None


def harmonic_percussive_separation(y):
    """Perform harmonic-percussive source separation."""
    try:
        if len(y) < 2048:
            print("⚠️ Audio is too short for HPSS. Skipping separation.")
            return y, y
        
        S = librosa.stft(y, n_fft=1024)
        S_harm, S_perc = librosa.decompose.hpss(S, margin=(1.0, 1.0))
        return librosa.istft(S_harm), librosa.istft(S_perc)
    
    except Exception as e:
        print(f"⚠️ HPSS failed: {e}. Using original signal instead.")
        return y, y
