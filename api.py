from flask import Flask, request, jsonify, render_template
import sys
import os
import ui.main as main
import numpy as np
import time

# Ensure backend and UI paths are accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "ui")))

app = Flask(__name__, template_folder="ui/templates", static_folder="ui/static")

@app.route("/")
def home():
    """Serves the main UI page."""
    return render_template("index.html")

@app.route("/record-analyze", methods=["POST"])
def record_and_analyze_api():
    """Records audio, extracts tempo & key, and returns results using main.py."""
    try:
        tempo, key = main.record_audio_and_extract_features()
        if tempo is None or key is None:
            return jsonify({"success": False, "error": "No valid music detected."})

        # 🔥 Ensure tempo is a standard Python int
        tempo = int(tempo) if isinstance(tempo, (np.integer, np.int64, np.int32)) else tempo
        key = str(key)  # Ensure key is a string

        return jsonify({"success": True, "tempo": tempo, "key": key})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/generate-music", methods=["POST"])
def generate_music_api():
    """Generates beat and piano progression and plays them."""
    try:
        data = request.json
        tempo = data.get("tempo")
        key = data.get("key")

        if tempo is None or key is None:
            return jsonify({"success": False, "error": "Missing tempo or key"})

        # ✅ Convert NumPy int64 to standard Python int
        tempo = int(tempo) if isinstance(tempo, (np.integer, np.int64, np.int32)) else tempo
        key = str(key)  # Ensure key is a string

        beat_file, piano_file = main.generate_music_files(tempo, key)

        if not beat_file or not piano_file:
            return jsonify({"success": False, "error": "Music generation failed."})

        # ✅ Play the generated MIDI files
        print(f"🎵 Playing generated MIDI files: {beat_file}, {piano_file}")
        main.piano_generation.play_midi(piano_file) # Play the piano progression
        time.sleep(1)  # Small delay to ensure playback starts
        main.piano_generation.play_midi(beat_file)  # Play the beat

        return jsonify({"success": True, "beat": beat_file, "piano": piano_file})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/play-music", methods=["POST"])
def play_music_api():
    """Starts music playback using main.py."""
    try:
        data = request.json
        beat_file = data.get("beat")
        piano_file = data.get("piano")

        if not beat_file or not piano_file:
            return jsonify({"success": False, "error": "Missing music files."})

        main.play_music_in_loop(beat_file, piano_file)
        return jsonify({"success": True, "message": "Music is playing."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/stop-music", methods=["POST"])
def stop_music_api():
    """Stops music playback using main.py."""
    try:
        main.stop_music()
        return jsonify({"success": True, "message": "Music playback stopped."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
