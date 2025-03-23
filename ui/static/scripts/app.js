document.addEventListener("DOMContentLoaded", () => {
    const recordBtn = document.getElementById("recordBtn");
    const generateBtn = document.getElementById("generateBtn");
    const stopBtn = document.getElementById("stopBtn");
    const statusText = document.getElementById("status");

    const songDetails = document.getElementById("song-details");
    const tempoText = document.getElementById("tempo");
    const keyText = document.getElementById("key");

    let tempo = null;
    let key = null;

    // Function to update status text
    function updateStatus(message, isError = false) {
        statusText.innerText = message;
        statusText.style.color = isError ? "red" : "#0f0f0f";
    }

    // Disable or enable buttons
    function setButtonsState({ record = false, generate = false, stop = false }) {
        recordBtn.disabled = record;
        generateBtn.disabled = generate;
        stopBtn.disabled = stop;
    }

    // Record & Analyze Audio
    recordBtn.addEventListener("click", async () => {
        updateStatus("🎤 Listening...");
        setButtonsState({ record: true });

        try {
            const response = await fetch("/record-analyze", { method: "POST" });
            const data = await response.json();
            
            if (data.success) {
                tempo = data.tempo;
                key = data.key;

                tempoText.innerText = tempo;
                keyText.innerText = key;
                songDetails.classList.remove("hidden");

                updateStatus("✅ Audio analyzed!");
                setButtonsState({ generate: false });
            } else {
                updateStatus("❌ Error: " + data.error, true);
                setButtonsState({ record: false });
            }
        } catch (error) {
            updateStatus("❌ Failed to connect to backend!", true);
            setButtonsState({ record: false });
        }
    });

    // Generate Music
    generateBtn.addEventListener("click", async () => {
        if (!tempo || !key) return;

        updateStatus("🎶 Generating Music...");
        setButtonsState({ generate: true });

        try {
            const response = await fetch("/generate-music", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tempo, key })
            });

            const data = await response.json();
            
            if (data.success) {
                updateStatus("🎵 Playing Generated Music...");
                setButtonsState({ stop: false });
            } else {
                updateStatus("❌ Error: " + data.error, true);
                setButtonsState({ generate: false });
            }
        } catch (error) {
            updateStatus("❌ Failed to connect to backend!", true);
            setButtonsState({ generate: false });
        }
    });

    // Stop Music
    stopBtn.addEventListener("click", async () => {
        updateStatus("⏹️ Stopping Music...");
        setButtonsState({ stop: true });

        try {
            await fetch("/stop-music", { method: "POST" });
            updateStatus("⏹️ Music Stopped!");
        } catch (error) {
            updateStatus("❌ Failed to stop playback!", true);
        }

        setButtonsState({ record: false, generate: false });
    });
});