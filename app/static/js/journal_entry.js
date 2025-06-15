// static/js/journal_entry.js

let autosaveTimer = null;
let lastSavedContent = "";
let characterBuffer = "";
let saveStatusTimeout = null;


export async function loadJournalEntryFromDOM() {
    const textarea = document.getElementById("journal-textarea");
    const entryDateLabel = document.getElementById("entry-date");
    const meta = document.getElementById("journal-metadata");
    const titleEl = document.getElementById("entry-title");
    const urlPath = window.location.pathname;

    if (!textarea || !titleEl) return;

    let entryId, entryDate, entryDateDisplay, content;

    if (urlPath === "/journal/today") {
        // Dynamically fetch or create today's entry
        try {
            const res = await fetch("/api/journal/today", { method: "POST" });
            const data = await res.json();

            entryId = data.id;
            entryDate = data.entry_date;
            entryDateDisplay = data.entry_date_display;
            content = data.content || "";
        } catch (err) {
            console.error("Failed to fetch/create today's entry", err);
            return;
        }
    } else {
        // Fallback to server-injected metadata
        if (!meta) return;

        entryId = meta.dataset.entryId;
        entryDate = meta.dataset.entryDate;
        entryDateDisplay = meta.dataset.entryDateDisplay;
        content = meta.dataset.entryContent || "";
    }

    // Populate form
    textarea.disabled = false;
    textarea.value = content;
    lastSavedContent = content;
    textarea.dataset.entryId = entryId;

    // Set title based on entry date
    const entryDateObj = new Date(entryDate);

    const isSameDate = (d1, d2) => (
        d1.getFullYear() === d2.getFullYear() &&
        d1.getMonth() === d2.getMonth() &&
        d1.getDate() === d2.getDate()
    );

    const today = new Date();
    const yesterday = new Date();
    yesterday.setDate(today.getDate() - 1);

    if (urlPath === "/journal/today" || isSameDate(today, entryDateObj)) {
        titleEl.innerText = "Today’s Entry";
    } else if (isSameDate(yesterday, entryDateObj)) {
        titleEl.innerText = "Yesterday’s Entry";
    } else {
        const options = { month: 'long', day: 'numeric' };
        const formatted = entryDateObj.toLocaleDateString(undefined, options);
        titleEl.innerText = `Entry from ${formatted}`;
    }

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

