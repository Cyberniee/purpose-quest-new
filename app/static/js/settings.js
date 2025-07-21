export async function loadSettings() {
    const res = await fetch('/users/settings');
    const data = await res.json();

    // Profile
    document.getElementById('first-name').value = data.first_name || "";
    document.getElementById('last-name').value = data.last_name || "";
    document.getElementById('email').value = data.email || "";

    if (data.whatsapp_linked) {
        document.getElementById("wa-link-status").innerHTML = `<span class="text-success">✅ Linked</span>`;
        const btn = document.getElementById("link-whatsapp");
        btn.classList.add("d-none");

    }

    // Notifications
    document.getElementById('notif-daily').checked = data.notifications.daily;
    document.getElementById('notif-ai-insights').checked = data.notifications.ai_insights;
    document.getElementById('notif-streaks').checked = data.notifications.streaks;

    // Privacy
    document.getElementById('security-encrypt').checked = data.privacy.encrypt;
    document.getElementById('security-ai').checked = data.privacy.ai_analysis;

    // Appearance
    // document.getElementById(`theme-${data.appearance.theme}`).checked = true;
    document.getElementById(`font-${data.appearance.font_size}`).checked = true;

}

export async function saveAllSettings() {
    const statusEl = document.getElementById('save-profile-status');

    const payload = {
        first_name: document.getElementById('first-name').value.trim(),
        last_name: document.getElementById('last-name').value.trim(),

        notifications: {
            daily: document.getElementById('notif-daily').checked,
            ai_insights: document.getElementById('notif-ai-insights').checked,
            streaks: document.getElementById('notif-streaks').checked
        },

        privacy: {
            encrypt: document.getElementById('security-encrypt').checked,
            ai_analysis: document.getElementById('security-ai').checked
        },

        appearance: {
            theme: document.querySelector('input[name="theme"]:checked')?.value || "auto",
            font_size: document.querySelector('input[name="fontsize"]:checked')?.value || "medium"
        }
    };

    const res = await fetch('/users/settings/update_preferences', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    if (statusEl) {
        if (res.ok) {
            statusEl.textContent = "✔ Saved";
            statusEl.classList.remove("text-danger");
            statusEl.classList.add("text-success");
        } else {
            statusEl.textContent = "❌ Failed to save";
            statusEl.classList.remove("text-success");
            statusEl.classList.add("text-danger");
        }

        statusEl.classList.remove("d-none");

        setTimeout(() => {
            statusEl.classList.add("d-none");
        }, 3000);
    }
}

export function setupWhatsappLinking() {
    const btn = document.getElementById("link-whatsapp");
    if (!btn) return;

    btn.addEventListener("click", async () => {
        try {
            const res = await fetch("/users/settings/link-token", { method: "POST" });
            const data = await res.json();

            document.getElementById("wa-link-url").href = data.wa_link;
            document.getElementById("wa-link-url").textContent = data.wa_link;
            document.getElementById("wa-token-display").textContent = data.token;
            document.getElementById("wa-link-container").classList.remove("d-none");
        } catch (err) {
            console.error("Failed to generate WhatsApp token", err);
            alert("❌ Could not generate token");
        }
    });
}

