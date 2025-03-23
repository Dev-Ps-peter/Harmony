from flask import Flask, render_template, request, jsonify
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import backend.audio_analysis as audio_analysis
import backend.beat_generation as beat_generator
import backend.piano_generation as piano_generator
import backend.real_time_processing as real_time_processing
import backend.utils as utils
import threading

app = Flask(__name__)

# Global variables to store generated music files
current_beat = None
current_piano = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/record-analyze", methods=["POST"])
def record_and_analyze():
    try:
        audio = real_time_processing.record_audio()
        normalized_audio = utils.normalize_audio(audio)

        # Save temp audio file
        audio_path = "temp_audio.wav"
        utils.save_audio(audio_path, normalized_audio)

        tempo, key = audio_analysis.extract_audio_features(audio_path)
        tempo = tempo[0] if isinstance(tempo, list) else tempo

        return jsonify({"success": True, "tempo": round(tempo, 2), "key": key})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/generate-music", methods=["POST"])
def generate_music():
    global current_beat, current_piano
    try:
        data = request.json
        tempo = int(data["tempo"])
        key = data["key"]

        current_beat = beat_generator.generate_beat(tempo)
        current_piano = piano_generator.generate_piano_progression(key)

        # Start playing in a separate thread
        threading.Thread(target=beat_generator.play_midi_loop, args=(current_beat,)).start()
        threading.Thread(target=piano_generator.play_midi_loop, args=(current_piano,)).start()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/stop-music", methods=["POST"])
def stop_music():
    try:
        beat_generator.stop_midi()
        piano_generator.stop_midi()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
