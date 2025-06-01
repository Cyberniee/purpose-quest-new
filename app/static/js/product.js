export async function initializeForm(container, sessionId, reportTypeId, userId, apiBase) {
    const parts = Array.from(container.querySelectorAll(".form-part"));
    let currentIndex = 0;

    function showPart(index) {
        parts.forEach((part, i) => {
            part.classList.toggle("hidden", i !== index);
        });

        const progress = document.querySelector(".progress-bar");
        const percentage = (100 / (parts.length - 1)) * index;
        progress.style.width = `${percentage}%`;
    }

    function updateWordCount(el, text) {
        const count = text.trim().split(/\s+/).filter(Boolean).length;
        el.textContent = `Minimum: ${count}/25 words`;
    }

    const prefilledAnswers = await fetchAnswers(sessionId);

    parts.forEach((part, index) => {
        const textarea = part.querySelector("textarea");
        const status = part.querySelector(".save-status");
        const wordCountEl = part.querySelector(".word-count");
        const questionId = part.getAttribute("data-question-id");
        if (!textarea || !status || !wordCountEl) return;

        // Prefill
        if (prefilledAnswers[questionId]) {
            textarea.value = prefilledAnswers[questionId];
            updateWordCount(wordCountEl, textarea.value);
        }

        // AUTOSAVE — attach only once
        let debounceTimer;
        textarea.addEventListener("input", () => {
            updateWordCount(wordCountEl, textarea.value);
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                fetch(`${apiBase}/answer`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        input_session_id: sessionId,
                        report_type_id: reportTypeId,
                        question_id: questionId,
                        answer_text: textarea.value,
                        user_id: userId
                    })
                })
                    .then(res => res.json())
                    .then(json => {
                        status.textContent = json.status === "ok" ? "✓ Saved" : "✗ Error saving";
                        status.style.color = json.status === "ok" ? "green" : "red";
                    })
                    .catch(() => {
                        status.textContent = "✗ Network error";
                        status.style.color = "red";
                    });
            }, 800);
        });

        // NAVIGATION
        const nextBtn = part.querySelector(".nextBtn");
        const prevBtn = part.querySelector(".prevBtn");

        if (nextBtn) {
            nextBtn.addEventListener("click", () => {
                if (currentIndex < parts.length - 1) {
                    currentIndex++;
                    showPart(currentIndex);
                }
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener("click", () => {
                if (currentIndex > 0) {
                    currentIndex--;
                    showPart(currentIndex);
                }
            });
        }
    });

    // Show modal and first question
    showPart(currentIndex);
    const welcomeModal = document.getElementById("welcomeModal");
    if (welcomeModal) welcomeModal.classList.add("show");
}

async function fetchAnswers(sessionId) {
    try {
        const res = await fetch(${ apiBase } / answers / ${ sessionId });
        const json = await res.json();
        if (json.status === "ok") {
            return json.answers.reduce((map, item) => {
                map[item.question_id] = item.answer_text;
                return map;
            }, {});
        } else {
            console.error("Error loading answers");
            return {};
        }
    } catch (e) {
        console.error("Failed to load saved answers", e);
        return {};
    }
}