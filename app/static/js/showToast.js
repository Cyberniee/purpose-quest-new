export function showToast(title, message, delay = 5000) {
    const toastContainer = document.getElementById('toast-container');

    // Create unique ID for the toast element
    const toastId = `toast-${Date.now()}`;

    // Construct the toast element
    const toastEl = document.createElement('div');
    toastEl.classList.add('toast');
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.setAttribute('id', toastId);
    toastEl.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">${title}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    // Append the toast element to the toast container
    toastContainer.appendChild(toastEl);

    // Initialize and show the toast using Bootstrap's Toast API
    const toast = new bootstrap.Toast(toastEl, {
        delay: delay
    });
    toast.show();

    // Remove the toast element from the DOM after it's hidden
    toastEl.addEventListener('hidden.bs.toast', function() {
        document.getElementById(toastId).remove();
    });
}