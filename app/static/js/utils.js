// Function to set the menu offset based on the header height
// export function setMenuOffset() {
//     const header = document.getElementById('siteHeader');
//     const menuOverlay = document.getElementById('menuOverlay');

//     if (header && menuOverlay) {
//         const headerHeight = header.offsetHeight;
//         menuOverlay.style.top = `${headerHeight}px`;
//     }
// }

// // Function to set the iframe height based on the viewport
// export function setIframeHeight() {
//     const iframe = document.querySelector('iframe');
//     if (iframe) {
//         const viewportHeight = window.innerHeight;
//         const newHeight = Math.max(viewportHeight * 0.6, 500); // Minimum 500px
//         iframe.style.height = `${newHeight}px`;
//     }
// }

export function setupInputListeners() {
    const emailInput = document.getElementById('floatingInput');
    const passwordInput = document.getElementById('floatingPassword');

    if (emailInput) {
        emailInput.addEventListener('input', hideTooltipOnInput);
    }
    if (passwordInput) {
        passwordInput.addEventListener('input', hideTooltipOnInput);
    }
}


export function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

export function hideTooltipOnInput(event) {
    var tooltipInstance = bootstrap.Tooltip.getInstance(event.target);
    if (tooltipInstance) {
        tooltipInstance.hide();
    }
}

export function blurButtonsOnMouseUp() {
    document.querySelectorAll("button").forEach(btn => {
        btn.addEventListener("mouseup", () => {
            btn.blur();
        });
    });
}

