// static/js/dashboard.js
export async function initializeJournalDashboard() {
    const button = document.getElementById("start-writing-btn");
    // const container = document.getElementById("today-entry-container");
    console.log(button)

    if (!button) return;

    try {
        console.log("init dashboard")
        const dates_res = await fetch("/api/journal/all_dates");
        const { dates } = await dates_res.json();
        const dateSet = new Set(dates);

        // Total entries
        const now = new Date();
        const thisMonth = now.getMonth();
        const thisYear = now.getFullYear();

        const datesThisMonth = dates.filter(dateStr => {
            const d = new Date(dateStr);
            return d.getMonth() === thisMonth && d.getFullYear() === thisYear;
        });

        const totalEntries = datesThisMonth.length;
        console.log("entries etc:", totalEntries, dateSet);

        // Calculate streak
        let streak = 0;
        let currentDate = new Date();
        const formatDate = d => d.toISOString().split("T")[0];

        // if today not written, step back to yesterday to start checking
        const todayStr = formatDate(currentDate);
        if (!dateSet.has(todayStr)) {
            currentDate.setDate(currentDate.getDate() - 1);
        }

        // now count backwards as long as dates are present
        while (true) {
            const dateStr = formatDate(currentDate);
            if (dateSet.has(dateStr)) {
                streak++;
                currentDate.setDate(currentDate.getDate() - 1);
            } else {
                break;
            }
        }

        // render
        document.querySelectorAll("#total-entries-count").forEach(el => {
            el.textContent = totalEntries;
        });

        document.querySelectorAll("#streak-count").forEach(el => {
            el.textContent = `${streak} day${streak === 1 ? "" : "s"}`;
        });


    } catch (err) {
        console.error("Failed to initialize journal dashboard", err);
    }
}


export function setupMockButton() {
    const button = document.getElementById("generate-mock-entries");
    if (!button) return;

    button.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/journal/mock/dev", { method: "POST" });
            if (res.ok) {
                alert("Mock entries created!");
                window.location.reload(); // refresh to see updated reflections
            } else {
                alert("Error generating entries.");
            }
        } catch (err) {
            console.error("Error creating mock entries:", err);
        }
    });
}

