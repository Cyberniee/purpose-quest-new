// static/js/voice_control.js
export function setupVoiceControl({
    micButtonId = "mic-btn",
    providerDropdownId = "providerDropdown",
    providerItemsSelector = "[data-provider]",
    statusId = "voice-status",
    instructionsId = "voice-instructions",
    textareaId = "journal-textarea"
} = {}) {
    console.log(`[VoiceControl] Network status: ${navigator.onLine ? "online ✅" : "offline ❌"}`);
    window.addEventListener("online", () => console.log("[VoiceControl] Network reconnected ✅"));
    window.addEventListener("offline", () => console.warn("[VoiceControl] Network disconnected ❌"));

    const micBtn = document.getElementById(micButtonId);
    const providerItems = document.querySelectorAll(providerItemsSelector);
    const status = document.getElementById(statusId);
    const textarea = document.getElementById(textareaId);
    const instructionBox = document.getElementById(instructionsId);
    const providerDropdown = document.getElementById(providerDropdownId);
    const langItems = document.querySelectorAll("#language-options .dropdown-item");
    const langDropdownBtn = document.getElementById("languageDropdown");
    const languageWrapper = document.getElementById("language-options")?.parentElement;
    const maxRestarts = 15;
    let noSpeechTimer = null;
    const noSpeechTimeoutDuration = 60_000; // 60 seconds

    let isListening = false;
    let restartAttempts = 0;
    let restartTimer = null;


    let currentProvider = "webspeech";
    providerDropdown.textContent = "Provider: Web Speech";
    langDropdownBtn.textContent = "Language: English (US)";
    let selectedLanguage = "English (US)";
    let finalTranscript = ""; // buffer for confirmed text

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = SpeechRecognition ? new SpeechRecognition() : null;

    // Handle language changes
    langItems.forEach(item => {
        item.addEventListener("click", (e) => {
            console.log(`[VoiceControl] Language set to: ${selectedLanguage}`);
            e.preventDefault();
            selectedLanguage = item.dataset.lang;
            langDropdownBtn.textContent = `Language: ${item.textContent}`;
            status.textContent = `Language set to ${item.textContent}`;
        });
    });

    if (recognition) {
        recognition.lang = selectedLanguage;
        recognition.interimResults = true;

        recognition.onstart = () => {
            finalTranscript = textarea.value.trim(); // store existing content
            recognition.lang = selectedLanguage;
            status.textContent = `Provider: Web Speech | 🎙 Listening (${selectedLanguage})...`;
            textarea.focus();
        };

        recognition.onresult = (event) => {
            resetNoSpeechTimer(); // ✅ restart inactivity timer

            let interim = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += " " + transcript;
                    console.log(`[VoiceControl] ✅ Final transcript: "${transcript}"`);
                } else {
                    interim += transcript;
                }
            }
            if (interim) {
                console.log(`[VoiceControl] ✏️ Interim transcript: "${interim}"`);
            }
            textarea.value = (finalTranscript + " " + interim).trim();
        };

        recognition.onerror = (event) => {
            console.error(`[VoiceControl] ❌ Recognition error: ${event.error}`);
            status.textContent = `❌ Error: ${event.error}`;
        };


        recognition.onend = () => {
            if (!isListening) return;

            console.warn("[VoiceControl] 🔁 Recognition ended — restarting...");
            status.textContent = `🔁 Listening again...`;

            restartTimer = setTimeout(() => {
                if (isListening) {
                    try {
                        console.log("[VoiceControl] 🔄 Restarting recognition");
                        recognition.start();
                    } catch (e) {
                        console.error("[VoiceControl] ❌ Restart failed:", e);
                        stopRecognition();
                    }
                }
            }, 100);
        };

    }

    providerItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            currentProvider = item.dataset.provider;
            providerDropdown.textContent = `Provider: ${item.textContent}`;
            status.textContent = `Provider: ${item.textContent} | Status: Idle`;

            console.log(`[VoiceControl] Switched to provider: ${currentProvider}`);
            if (currentProvider === "webspeech") {
                instructionBox.classList.add("d-none");
                langDropdownBtn.textContent = `Language: ${selectedLanguage}`;
                languageWrapper?.classList.remove("d-none");
            } else if (currentProvider === "osnative") {
                const platform = navigator.userAgent.toLowerCase();
                let tip = "💡 Use the mic button on your keyboard or mobile keyboard.";
                if (platform.includes("win")) tip = "💡 Press <strong>Win + H</strong> for Windows dictation.";
                else if (platform.includes('mac')) tip = "💡 Press <strong>Fn</strong> twice to start macOS dictation.";
                instructionBox.innerHTML = tip;
                instructionBox.classList.remove("d-none");
                langDropdownBtn.textContent = `Language: Device-specific`;
                languageWrapper?.classList.add("d-none");
                textarea?.focus();
            }
        });
    });


    micBtn.addEventListener("click", () => {
        if (currentProvider !== "webspeech") {
            status.textContent = "ℹ️ Use OS-native voice input shortcut.";
            return;
        }

        if (!recognition) {
            status.textContent = "❌ Web Speech not supported in this browser.";
            return;
        }

        if (isListening) {
            stopRecognition();
        } else {
            startRecognition();
        }
    });

    function startRecognition() {
        console.log(`[VoiceControl] Starting recognition with language: ${selectedLanguage}`);
        try {
            finalTranscript = textarea.value.trim();
            recognition.lang = selectedLanguage;
            recognition.start();
            isListening = true;
            updateMicButton(true);
            resetNoSpeechTimer(); // ✅ start inactivity window
            console.log(`[VoiceControl] 🎙 Recognition started`);

        } catch (e) {
            console.error("Failed to start recognition:", e);
            status.textContent = "❌ Failed to start microphone.";
            stopRecognition();
        }
    }


    function stopRecognition() {
        console.log("[VoiceControl] 🛑 Stopping recognition");
        recognition.stop();
        isListening = false;
        clearTimeout(restartTimer);
        clearTimeout(noSpeechTimer);
        updateMicButton(false);
        status.textContent = "🛑 Stopped";
    }



    function updateMicButton(active) {
        micBtn.classList.toggle("btn-danger", active);
        micBtn.classList.toggle("btn-secondary", !active);
    }

    function resetNoSpeechTimer() {
        clearTimeout(noSpeechTimer);
        noSpeechTimer = setTimeout(() => {
            console.warn("[VoiceControl] ⏱ No speech detected for 60 seconds. Auto-stopping mic.");
            status.textContent = "⏱ No speech detected for 60 seconds. Stopping.";
            stopRecognition();
        }, noSpeechTimeoutDuration);
    }


}


