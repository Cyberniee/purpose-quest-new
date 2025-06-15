// static/js/journal_entry.js

let autosaveTimer = null;
let lastSavedContent = "";
let characterBuffer = "";
let saveStatusTimeout = null;


export function loadJournalEntryFromDOM() {
    const textarea = document.getElementById("journal-textarea");
    const entryDateLabel = document.getElementById("entry-date");
    const meta = document.getElementById("journal-metadata");

    if (!meta || !textarea) return;

    const entryId = meta.dataset.entryId;
    const entryDateDisplay = meta.dataset.entryDateDisplay;
    const content = meta.dataset.entryContent || "";

    textarea.disabled = false;
    textarea.value = content;
    lastSavedContent = content;
    textarea.dataset.entryId = entryId;

    if (entryDateLabel) {
        entryDateLabel.innerText = entryDateDisplay;
    }

    initAutosave(textarea);
    setupManualSave(textarea);
    setupBackButton(textarea);

}



function initAutosave(textarea) {
    textarea.addEventListener("input", (event) => {
        characterBuffer += event.data || "";

        if (characterBuffer.length >= 100) {
            saveJournalContent(textarea);
            characterBuffer = "";
        }

        resetAutosaveTimer(textarea);
    });
}

function resetAutosaveTimer(textarea) {
    clearTimeout(autosaveTimer);
    autosaveTimer = setTimeout(() => {
        saveJournalContent(textarea);
    }, 10000);
}

export async function saveJournalContent(textarea) {
    const currentContent = textarea.value.trim();
    const entryId = textarea.dataset.entryId;

    if (!entryId || currentContent === lastSavedContent) return;

    try {
        const response = await fetch(`/api/journal/${entryId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: currentContent }),
        });

        if (response.ok) {
            lastSavedContent = currentContent;
            characterBuffer = "";
            showSaveStatus("Saved ✅");
        } else {
            showSaveStatus("Failed to save ❌", true);
        }
    } catch (err) {
        console.error("Save error:", err);
        showSaveStatus("Error saving ❌", true);
    }
}

function setupManualSave(textarea) {
    const button = document.getElementById("save-button");
    if (!button) return;

    button.addEventListener("click", () => {
        saveJournalContent(textarea);
    });
}

function showSaveStatus(message, isError = false) {
    let statusEl = document.getElementById("save-status");

    if (!statusEl) {
        statusEl = document.createElement("small");
        statusEl.id = "save-status";
        statusEl.classList.add("text-muted", "d-block", "mt-2", "text-end");
        document.getElementById("save-button")?.parentNode?.appendChild(statusEl);
    }

    statusEl.innerText = message;
    statusEl.style.color = isError ? "red" : "green";
    statusEl.style.opacity = "1";

    // Clear existing timeout if any
    if (saveStatusTimeout) clearTimeout(saveStatusTimeout);

    // Only hide if success
    if (!isError) {
        saveStatusTimeout = setTimeout(() => {
            statusEl.style.opacity = "0";
        }, 3000);
    }
}

function setupBackButton(textarea) {
    const backButton = document.getElementById("back-to-dashboard");
    if (!backButton || !textarea) return;

    backButton.addEventListener("click", async (e) => {
        e.preventDefault();

        const currentContent = textarea.value.trim();

        const entryId = textarea.dataset.entryId;

        // Only save if changed
        if (entryId && currentContent !== lastSavedContent) {
            try {
                await saveJournalContent(textarea);
            } catch (err) {
                console.warn("Autosave failed before back nav:", err);
            }
        }

        // Navigate back safely
        const fallback = "/dashboard";
        const previous = document.referrer;

        // Avoid reloading same page or broken navigation
        if (previous && previous !== window.location.href) {
            window.location.href = previous;
        } else {
            window.location.href = fallback;
        }
    });
}

