export function setupMobileSidebar() {
  const sidebarOverlay = document.getElementById("sidebar-overlay");
  const hamburgerBtn = document.getElementById("hamburger-btn");

  function closeSidebar() {
    sidebarOverlay.classList.add("d-none");
    hamburgerBtn?.classList.remove("hidden");
  }

  if (hamburgerBtn && sidebarOverlay) {
    hamburgerBtn.addEventListener("click", () => {
      sidebarOverlay.classList.remove("d-none");
      hamburgerBtn.classList.add("hidden");
    });

    sidebarOverlay.addEventListener("click", (e) => {
      if (e.target.id === "sidebar-overlay") {
        closeSidebar();
      }
    });

    setTimeout(() => {
      sidebarOverlay.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", closeSidebar);
      });
    }, 0);
  }
}
