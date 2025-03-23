import sys
import os
import numpy as np
import threading
import soundfile as sf

# Append backend directory to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import backend modules
import backend.audio_analysis as audio_analysis
import backend.beat_generation as beat_generation
import backend.piano_generation as piano_generation
import backend.real_time_processing as real_time_processing
import backend.utils as utils

# Load paths from utils
SOUNDFONT_PATH = utils.SOUNDFONT_PATH
FLUIDSYNTH_PATH = utils.FLUIDSYNTH_PATH

# Global control variable for MIDI playback
stop_flag = False

def record_audio_and_extract_features():
    """
    Records audio, normalizes it, and extracts tempo & key.
    """
    try:
        print("🎤 Recording Audio for 10 seconds...")
        audio = real_time_processing.record_audio()
        
        if audio is None or len(audio) == 0:
            raise ValueError("No audio data recorded! Check microphone input.")

        print(f"🔊 Recorded Audio Shape: {audio.shape}")
        
        print("🔊 Normalizing audio...")
        normalized_audio = utils.normalize_audio(audio)
        
        if normalized_audio is None or len(normalized_audio) == 0:
            raise ValueError("Normalized audio is empty! Skipping feature extraction.")

        audio_path = "temp_audio.wav"
        sf.write(audio_path, normalized_audio, 44100)
        print(f"✅ Audio saved at: {audio_path}")

        print("🎵 Extracting features...")
        tempo, key = audio_analysis.extract_audio_features(audio_path)
        
        # Ensure tempo is a Python int
        tempo = int(tempo[0]) if isinstance(tempo, np.ndarray) else int(tempo)
        
        print(f"✅ Detected Tempo: {tempo} BPM")
        print(f"✅ Detected Key: {key}")
        
        return tempo, key
    except Exception as e:
        print(f"❌ Error during audio processing: {e}")
        return None, None

def generate_music_files(tempo, key):
    try:
        print(f"📌 Initial values -> Tempo: {tempo} ({type(tempo)}), Key: {key} ({type(key)})")

        if isinstance(tempo, str):
            tempo = int(tempo)
        elif isinstance(tempo, (np.int64, np.int32, np.integer)):
            tempo = int(tempo)

        key = str(key)  

        print(f"🎵 Generating music with Tempo: {tempo} ({type(tempo)}), Key: {key} ({type(key)})")

        print("🥁 Generating Beat...")
        beat_file = beat_generation.generate_beat(tempo)
        
        print("🎹 Generating Piano Progression...")
        piano_file = piano_generation.generate_piano_progression(key) 
        
        if not beat_file or not piano_file:
            raise ValueError("Music generation failed.")
        
        return beat_file, piano_file
    except Exception as e:
        print(f"❌ Error during music generation: {e}")
        return None, None

def play_music_in_loop(beat_file, piano_file):
    """
    Plays both beat and piano progression in a loop concurrently.
    Stops playback when the user presses Enter.
    """
    global stop_flag
    if not beat_file or not piano_file:
        print("❌ Error: Could not generate music files.")
        return
    
    print("🎶 Playing Beat and Piano Progression in Loop... (Press Enter to Stop)")
    stop_flag = False
    
    beat_thread = threading.Thread(target=utils.play_midi_loop, args=(beat_file,))
    piano_thread = threading.Thread(target=utils.play_midi_loop, args=(piano_file,))
    
    beat_thread.start()
    piano_thread.start()
    
    input("⏹️ Press Enter to stop playback...\n")
    stop_music()
    
    beat_thread.join()
    piano_thread.join()

def stop_music():
    """
    Stops MIDI playback by setting the stop flag and terminating processes.
    """
    global stop_flag
    stop_flag = True
    utils.stop_midi()
    print("✅ Music Stopped.")

def main():
    """
    Main execution function.
    """
    try:
        tempo, key = record_audio_and_extract_features()
        if tempo is None or key is None:
            print("⚠️ No valid music detected. Exiting.")
            return
        
        beat_file, piano_file = generate_music_files(tempo, key)
        if not beat_file or not piano_file:
            print("⚠️ Music generation failed. Exiting.")
            return
        
        play_music_in_loop(beat_file, piano_file)
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
