import music21
import numpy as np
import subprocess
import time

# Paths to Fluidsynth and SoundFont
SOUNDFONT_PATH = "C:/Users/PC/Downloads/fluidsynth-2.4.3-win10-x64/bin/FluidR3_GM.sf2"
FLUIDSYNTH_PATH = "C:/Users/PC/Downloads/fluidsynth-2.4.3-win10-x64/bin/fluidsynth.exe"

# MIDI Key Mapping
KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Global variable for Fluidsynth process
fluidsynth_process = None


def generate_piano_progression(key_index):
    """Generate a chord progression in MIDI and return the file path."""
    print("🎹 Generating Piano Progression...")

    # Ensure key_index is an integer
    try:
        key_index = int(key_index)
    except ValueError:
        print(f"⚠️ Invalid key_index: {key_index}, defaulting to C major (0)")
        key_index = 0  # Default to C major

    # Validate key index
    if key_index < 0 or key_index >= len(KEYS):
        print("⚠️ Invalid key index detected. Defaulting to C major.")
        key_index = 0  # Default to C major

    base_key = KEYS[key_index]

    try:
        root_note = music21.pitch.Pitch(base_key)

        # Create a harmonic chord progression
        progression = [
            [root_note, root_note.transpose(4), root_note.transpose(7)],
            [root_note.transpose(5), root_note.transpose(9), root_note.transpose(12)],
            [root_note.transpose(7), root_note.transpose(11), root_note.transpose(14)],
            [root_note, root_note.transpose(4), root_note.transpose(7)]
        ]

        print("✅ Chord progression generated.")

        # Convert to music21 format
        stream = music21.stream.Stream()
        for chord_notes in progression:
            chord = music21.chord.Chord(chord_notes, quarterLength=2)
            stream.append(chord)

        # Save as MIDI
        midi_filename = "piano_progression.mid"
        stream.write('midi', fp=midi_filename)
        print(f"✅ MIDI file saved: {midi_filename}")

        return midi_filename  # Return MIDI file path

    except Exception as e:
        print(f"❌ Error in generating piano progression: {e}")
        return None


def play_midi(midi_file):
    """Play a MIDI file using Fluidsynth."""
    global fluidsynth_process
    try:
        fluidsynth_process = subprocess.Popen([
            FLUIDSYNTH_PATH,
            "-m", "winmidi",
            "-o", "midi.winmidi.device=HarmonyBot_MIDI",
            SOUNDFONT_PATH,
            midi_file
        ])
        print(f"🎶 Playing {midi_file} with Fluidsynth...")

    except Exception as e:
        print(f"❌ Error playing {midi_file}: {e}")


def play_midi_loop(midi_file):
    """Plays a MIDI file in a loop using Fluidsynth."""
    global fluidsynth_process
    try:
        while True:
            play_midi(midi_file)
            time.sleep(10)  # Adjust to match progression duration

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
