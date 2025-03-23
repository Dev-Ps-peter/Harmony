import os
import pygame
import subprocess
import time
import numpy as np

# Initialize pygame mixer only if not already initialized
if not pygame.mixer.get_init():
    pygame.mixer.init()

# Paths for Fluidsynth and SoundFont
SOUNDFONT_PATH = os.path.abspath("C:/Users/PC/Downloads/fluidsynth-2.4.3-win10-x64/bin/FluidR3_GM.sf2")
FLUIDSYNTH_PATH = os.path.abspath("C:/Users/PC/Downloads/fluidsynth-2.4.3-win10-x64/bin/fluidsynth.exe")

# Global variables for MIDI playback control
stop_flag = False
midi_processes = []  # Stores active MIDI processes


def save_audio(filepath, audio_data=None):
    """
    Save recorded audio data to a file.
    :param filepath: Path to save the audio file.
    :param audio_data: Binary audio data (optional).
    :return: The saved file path.
    """
    try:
        with open(filepath, "wb") as f:
            f.write(audio_data if audio_data else b"")  # Save actual or empty data
        return filepath
    except Exception as e:
        print(f"❌ Error saving audio file: {e}")
        return None


def play_audio(file_path):
    """
    Play an audio file using pygame.
    :param file_path: Path to the audio file.
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found")
        return

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        print(f"▶️ Playing: {file_path}")
    except pygame.error as e:
        print(f"❌ Audio playback error: {e}")


def stop_audio():
    """Stop any currently playing audio."""
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        print("⏹️ Audio playback stopped.")
    else:
        print("⚠️ No audio is currently playing.")


def normalize_audio(audio):
    """
    Normalizes audio to have a consistent volume.
    :param audio: NumPy array of audio data.
    :return: Normalized NumPy array.
    """
    if audio is None or len(audio) == 0:
        print("⚠️ Cannot normalize empty audio.")
        return None

    max_val = np.max(np.abs(audio))
    if max_val == 0:
        print("⚠️ Audio is silent! Normalization skipped.")
        return audio  # Return original to avoid division by zero

    return audio / max_val  # Normalize to [-1, 1]


def play_midi_loop(midi_file):
    """
    Plays a MIDI file in a loop using Fluidsynth until stopped.
    :param midi_file: Path to the MIDI file.
    """
    global stop_flag, midi_processes

    while not stop_flag:
        try:
            process = subprocess.Popen([FLUIDSYNTH_PATH, "-ni", SOUNDFONT_PATH, midi_file])
            midi_processes.append(process)  # Track process
            process.wait()  # Wait for playback completion before looping
        except Exception as e:
            print(f"❌ Error playing MIDI: {e}")
            break

    print(f"🔁 Looping {midi_file} stopped.")


def stop_midi():
    """
    Stops MIDI playback by setting stop flag and terminating Fluidsynth processes.
    """
    global stop_flag, midi_processes
    stop_flag = True  # Prevent new loops

    print("⏹️ Stopping MIDI playback...")

    # Terminate all active Fluidsynth processes
    for process in midi_processes:
        try:
            if process.poll() is None:  # If still running
                process.terminate()  # Graceful termination
                time.sleep(1)  # Allow time to close
                process.kill()  # Force kill if necessary
        except Exception as e:
            print(f"⚠️ Error stopping MIDI process: {e}")

    midi_processes.clear()  # Clear process list
    print("✅ MIDI playback stopped.")
