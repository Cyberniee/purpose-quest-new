// static/js/archive_page.js
import { initCalendar } from '/static/js/calendar.js';
import { setupMobileSidebar } from '/static/js/mobile_ui.js';

let journalDates = [];       // for calendar
let journalListCache = [];   // for list view

async function fetchJournalDates() {
    try {
        const res = await fetch('/api/journal/all_dates');
        const { dates } = await res.json();
        journalDates = dates;
        console.log('[Archive] Loaded journal dates:', journalDates);
    } catch (err) {
        console.error("[Archive] Failed to fetch journal dates", err);
    }
}

async function fetchPaginatedEntries() {
    try {
        const res = await fetch('/api/journal/paginated?page=1&limit=10');
        const { entries } = await res.json();
        journalListCache = entries;
    } catch (err) {
        console.error("[Archive] Failed to fetch paginated entries", err);
    }
}

function loadJournalEntry(dateKey) {
    const match = journalListCache.find(entry => entry.entry_date === dateKey);
    const container = document.getElementById("entry-preview-container");
    const dateTitle = document.getElementById("entry-date-title");
    const summary = document.getElementById("entry-summary-text");
    const excerpt = document.getElementById("entry-excerpt-text");
    const wordCount = document.getElementById("entry-word-count");
    const viewBtn = document.getElementById("view-entry-btn");
    const editBtn = document.getElementById("edit-entry-btn");

    const todayKey = new Date().toISOString().split("T")[0];

    if (match) {
        dateTitle.innerText = match.label;
        summary.innerText = match.summary || '';
        excerpt.innerText = match.preview || '';
        wordCount.innerText = match.word_count ? `${match.word_count} words` : '';

        viewBtn.href = `/journal/${match.id}`;
        viewBtn.textContent = "👁 View Entry";
        viewBtn.classList.remove("d-none");

        if (dateKey === todayKey) {
            editBtn.href = `/journal/${match.id}`;
            editBtn.textContent = "✏️ Continue";
            editBtn.classList.remove("d-none");
        } else {
            editBtn.classList.add("d-none");
        }
    } else {
        dateTitle.innerText = new Date(dateKey).toDateString();
        summary.innerText = '';
        excerpt.innerText = "No journal entry found for this date.";
        wordCount.innerText = '';

        if (dateKey === todayKey) {
            viewBtn.href = "/journal/today";
            viewBtn.textContent = "✍️ Start Writing";
            viewBtn.classList.remove("d-none");
        } else {
            viewBtn.classList.add("d-none");
        }

        editBtn.classList.add("d-none");
    }

    container.classList.remove("d-none");
}

function renderListView() {
    const container = document.getElementById("entry-list-container");
    container.innerHTML = "";

    journalListCache.forEach(entry => {
        const card = document.createElement("div");
        card.className = "bg-light p-4 rounded mb-4 shadow-sm";

        card.innerHTML = `
            <h5 class="mb-1">${entry.label}</h5>
            <p class="text-muted fw-semibold">${entry.summary || ''}</p>
            <p class="mb-2">${entry.preview}</p>
            <div class="d-flex justify-content-between align-items-center">
                <small>${entry.word_count || 0} words</small>
                <div class="d-flex gap-2">
                    <a href="/journal/${entry.id}" class="btn btn-secondary btn-sm">👁 View</a>
                    <a href="/journal/${entry.id}" class="btn btn-primary btn-sm">✏️ Edit</a>
                </div>
            </div>`;

        container.appendChild(card);
    });
}

function setupViewToggles() {
    const calendarBtn = document.getElementById("calendar-view-btn");
    const listBtn = document.getElementById("list-view-btn");

    calendarBtn.addEventListener("click", () => {
        document.getElementById("calendar-container-wrapper").classList.remove("d-none");
        document.getElementById("archive-list-view").classList.add("d-none");

        calendarBtn.classList.add("btn-primary", "active");
        calendarBtn.classList.remove("btn-secondary");
        listBtn.classList.remove("btn-primary", "active");
        listBtn.classList.add("btn-secondary");
    });

    listBtn.addEventListener("click", () => {
        document.getElementById("calendar-container-wrapper").classList.add("d-none");
        document.getElementById("archive-list-view").classList.remove("d-none");

        listBtn.classList.add("btn-primary", "active");
        listBtn.classList.remove("btn-secondary");
        calendarBtn.classList.remove("btn-primary", "active");
        calendarBtn.classList.add("btn-secondary");

        renderListView();
    });
}

export async function initArchivePage() {
    setupMobileSidebar();
    await Promise.all([fetchJournalDates(), fetchPaginatedEntries()]);

    // show the calendar by default
    document.getElementById("calendar-container-wrapper").classList.remove("d-none");
    document.getElementById("archive-list-view").classList.add("d-none");

    initCalendar({
        displaySelector: ".display",
        daysContainerSelector: ".days",
        leftArrowSelector: ".left",
        rightArrowSelector: ".right",
        selectedOutputSelector: ".selected",
        onDateSelect: loadJournalEntry,
        journalEntryDates: journalDates
    });

    setupViewToggles();

    // Default to today's entry preview
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const todayKey = `${yyyy}-${mm}-${dd}`;
    loadJournalEntry(todayKey);
}
