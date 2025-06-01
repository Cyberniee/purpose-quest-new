// Function to set the menu offset based on the header height
export function setMenuOffset() {
    const header = document.getElementById('siteHeader');
    const menuOverlay = document.getElementById('menuOverlay');

    if (header && menuOverlay) {
        const headerHeight = header.offsetHeight;
        menuOverlay.style.top = `${headerHeight}px`;
    }
}

// Function to set the iframe height based on the viewport
export function setIframeHeight() {
    const iframe = document.querySelector('iframe');
    if (iframe) {
        const viewportHeight = window.innerHeight;
        const newHeight = Math.max(viewportHeight * 0.6, 500); // Minimum 500px
        iframe.style.height = `${newHeight}px`;
    }
}

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

export function quickNavInit() {
    const path = window.location.pathname;
    console.log(path);

    const buttons = document.querySelectorAll('.status-button');

    buttons.forEach(function(button) {
        const buttonHref = button.getAttribute('href');
        const normalizedButtonHref = buttonHref.startsWith('.') ? buttonHref.substring(1) : buttonHref;

        if (path.endsWith(normalizedButtonHref)) {
            button.classList.add('active');
            button.classList.add('disabled'); // Add 'disabled' class
        } else {
            button.classList.remove('active');
            button.classList.remove('disabled'); // Remove 'disabled' class if it's not a match
        }
    });
}

export function addSpinnerLoader(message, parentElement) {
    const loadingContainer = document.createElement('div');
    loadingContainer.classList.add('d-flex', 'justify-content-center', 'align-items-center', 'my-5');
    const spinner = document.createElement('div');
    spinner.classList.add('spinner-border');
    spinner.setAttribute('role', 'status');
    const loadingText = document.createElement('span');
    loadingText.classList.add('ms-2');
    loadingText.textContent = message;
    loadingContainer.appendChild(spinner);
    loadingContainer.appendChild(loadingText);
    parentElement.appendChild(loadingContainer);
    
    // Return the loading container for later reference
    return loadingContainer;
}
