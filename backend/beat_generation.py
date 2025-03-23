import mido
import pygame
import time
import subprocess
import threading

# Paths to Fluidsynth and SoundFont
SOUNDFONT_PATH = "C:/Users/PC/Downloads/fluidsynth-2.4.3-win10-x64/bin/FluidR3_GM.sf2"
FLUIDSYNTH_PATH = "C:/Users/PC/Downloads/fluidsynth-2.4.3-win10-x64/bin/fluidsynth.exe"

# Global variable to store the Fluidsynth process
fluidsynth_process = None


def generate_beat(tempo):
    """Generate a dynamic drum beat as a MIDI file."""
    print("🥁 Generating a richer Beat...")

    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    tick_time = max(120 - int(tempo), 10)  # Ensures valid timing values

    for i in range(4):  # 4 beats per measure
        # Bass Drum
        track.append(mido.Message('note_on', note=36, velocity=110, time=tick_time))
        track.append(mido.Message('note_off', note=36, velocity=110, time=tick_time))

        # Snare Drum
        track.append(mido.Message('note_on', note=38, velocity=100, time=tick_time))
        track.append(mido.Message('note_off', note=38, velocity=100, time=tick_time))

        # Hi-Hat
        track.append(mido.Message('note_on', note=42, velocity=80, time=tick_time))
        track.append(mido.Message('note_off', note=42, velocity=80, time=tick_time))

        # Crash Cymbal (only on beat 1)
        if i == 0:
            track.append(mido.Message('note_on', note=49, velocity=120, time=tick_time))
            track.append(mido.Message('note_off', note=49, velocity=120, time=tick_time))

    midi_path = "beat.mid"
    mid.save(midi_path)

    print(f"✅ Beat saved as '{midi_path}'")

    return midi_path  # Return the MIDI file path


def play_midi(midi_file):
    """Plays a MIDI file using Fluidsynth."""
    global fluidsynth_process
    try:
        fluidsynth_process = subprocess.Popen([
            FLUIDSYNTH_PATH,
            "-m", "winmidi",
            "-o", "midi.winmidi.device=HarmonyBot_MIDI",
            SOUNDFONT_PATH,
            midi_file
        ])
        print(f"🎶 Playing {midi_file}...")

    except Exception as e:
        print(f"❌ Error playing beat: {e}")


def play_midi_loop(midi_file):
    """Plays a MIDI file in a loop using Fluidsynth."""
    global fluidsynth_process
    try:
        while True:
            play_midi(midi_file)
            time.sleep(10)  # Adjust to match beat duration

    except KeyboardInterrupt:
        stop_midi()


def stop_midi():
    """Stops any playing MIDI by terminating Fluidsynth process."""
    global fluidsynth_process
    if fluidsynth_process:
        fluidsynth_process.terminate()
        fluidsynth_process = None
        print("⏹️ Stopped MIDI playback")
    else:
        print("⚠️ No active MIDI playback to stop.")
