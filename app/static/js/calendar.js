// calendar.js
export function initCalendar({
    displaySelector,
    daysContainerSelector,
    leftArrowSelector,
    rightArrowSelector,
    selectedOutputSelector,
    onDateSelect = () => { },
    journalEntryDates = [] // e.g. ["2025-06-14", "2025-06-02"]
}) {
    const display = document.querySelector(displaySelector);
    const days = document.querySelector(daysContainerSelector);
    const previous = document.querySelector(leftArrowSelector);
    const next = document.querySelector(rightArrowSelector);
    const selected = document.querySelector(selectedOutputSelector);

    let date = new Date();
    let year = date.getFullYear();
    let month = date.getMonth();

    function renderCalendar() {
        days.innerHTML = "";
        selected.innerHTML = "";

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);

        const firstDayIndex = firstDay.getDay();
        const numberOfDays = lastDay.getDate();

        let formattedDate = date.toLocaleString("en-US", {
            month: "long",
            year: "numeric"
        });

        if (display) display.innerHTML = `${formattedDate}`;

        for (let x = 0; x < firstDayIndex; x++) {
            const filler = document.createElement("div");
            days.appendChild(filler);
        }

        for (let i = 1; i <= numberOfDays; i++) {
            const dayDiv = document.createElement("div");
            const currentDate = new Date(year, month, i);
            const dateString = currentDate.toDateString(); // for display
            const isoString = currentDate.getFullYear()
                + "-" + String(currentDate.getMonth() + 1).padStart(2, '0')
                + "-" + String(currentDate.getDate()).padStart(2, '0');

            dayDiv.dataset.date = isoString;
            dayDiv.textContent = i;

            const today = new Date();
            today.setHours(0, 0, 0, 0); // strip time
            currentDate.setHours(0, 0, 0, 0);

            // Disable future days
            const isFuture = currentDate > today;
            if (isFuture) {
                dayDiv.classList.add("disabled-date");
                dayDiv.classList.add("text-muted");
                dayDiv.style.pointerEvents = "none";
            } else {
                // Highlight today
                if (currentDate.toDateString() === new Date().toDateString()) {
                    dayDiv.classList.add("current-date");
                }

                // Highlight entry dates
                if (journalEntryDates.includes(isoString)) {
                    dayDiv.classList.add("has-entry");
                }

                // Click listener
                dayDiv.addEventListener("click", () => {
                    document.querySelectorAll(".days div.selected-date").forEach(el => {
                        el.classList.remove("selected-date");
                    });

                    dayDiv.classList.add("selected-date");

                    if (selected) selected.innerHTML = `Selected Date : ${dateString}`;
                    onDateSelect(isoString);
                });
            }

            days.appendChild(dayDiv);
        }


    }

    function goToPreviousMonth() {
        if (month <= 0) {
            month = 11;
            year -= 1;
        } else {
            month -= 1;
        }
        date.setMonth(month);
        renderCalendar();
    }

    function goToNextMonth() {
        if (month >= 11) {
            month = 0;
            year += 1;
        } else {
            month += 1;
        }
        date.setMonth(month);
        renderCalendar();
    }

    if (previous) previous.addEventListener("click", goToPreviousMonth);
    if (next) next.addEventListener("click", goToNextMonth);

    renderCalendar();
}
