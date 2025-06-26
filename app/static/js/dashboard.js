// static/js/dashboard.js
export async function initializeJournalDashboard() {
    const button = document.getElementById("start-writing-btn");
    // const container = document.getElementById("today-entry-container");
    console.log(button)

    if (!button) return;

    try {
        // const res = await fetch("/api/journal/recent");
        // const { entries } = await res.json();
        console.log("init dashboard")

        // container.innerHTML = "";

        // entries.forEach((entry, index) => {
        //     // Update start button if today's entry is found first
        //     if (index === 0 && entry.label === "Today’s Entry") {
        //         button.innerText = "Continue today’s entry";
        //         button.dataset.entryId = entry.id;
        //         button.onclick = () => {
        //             window.location.href = `/journal/${entry.id}`;
        //         };
        //     }

        //     const div = document.createElement("div");
        //     div.classList.add("mb-3");

        //     div.innerHTML = `
        //         <a href="/journal/${entry.id}" class="text-decoration-none text-dark">
        //             <div class="border-start border-4 ps-3" data-label="reflection-entry">
        //                 <strong>${entry.label}</strong>
        //                 <p class="mb-0">${entry.preview}</p>
        //             </div>
        //         </a>
        //     `;

        //     container.appendChild(div);
        // });

        // // If no today entry found, fallback
        // if (!entries.some(e => e.label === "Today’s Entry")) {
        //     button.innerText = "Start writing";
        //     button.onclick = () => {
        //         window.location.href = "/journal/today";
        //     };
        // }
        const dates_res = await fetch("/api/journal/all_dates");
        const { dates } = await dates_res.json();
        const dateSet = new Set(dates);

        // Total entries
        const totalEntries = dates.length;
        console.log("entries etc:", totalEntries, dateSet);

        // Calculate streak
        let streak = 0;
        let currentDate = new Date();
        const formatDate = d => d.toISOString().split("T")[0];

        while (true) {
            const dateStr = formatDate(currentDate);
            if (dateSet.has(dateStr)) {
                streak++;
                currentDate.setDate(currentDate.getDate() - 1);
            } else {
                break;
            }
        }

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

