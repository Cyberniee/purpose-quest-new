//btnloader.js

export function activateLoader(btn) {
    // Disable the button
    btn.disabled = true;

    // Create the spinner element
    const spinner = document.createElement('span');
    spinner.className = 'spinner-border spinner-border-sm';
    spinner.setAttribute('role', 'status');
    spinner.setAttribute('aria-hidden', 'true');

    const existingSpinner = btn.querySelector('.spinner-border');
    if (existingSpinner) {
        existingSpinner.remove();
    }

    // Append the spinner to the button
    btn.prepend(spinner);

    // Add a small delay before disabling the button to ensure form submission is triggered
    // This might be unnecessary if you're immediately disabling the button, so consider removing this delay if it's not needed
    setTimeout(() => { btn.disabled = true; }, 100);

    // Re-enable the button after 5 seconds
    setTimeout(() => {
        btn.disabled = false; // Re-enable the button
        spinner.remove(); // Remove the spinner element
    }, 5000); // Adjust the time as needed
}

export function deactivateLoader(btn) {
    // Remove the spinner element from the button
    const spinner = btn.querySelector('.spinner-border');
    if (spinner) {
        spinner.remove();
    }
}

export function btnLoader(btns) {
    // Check if btns is a single element, if so, convert it to an array
    if (!NodeList.prototype.isPrototypeOf(btns) && !HTMLCollection.prototype.isPrototypeOf(btns)) {
        btns = [btns];
    }

    // Iterate over the buttons and add the event listener
    btns.forEach(btn => {
        btn.addEventListener('click', function () {
            activateLoader(btn);
        });
    });
}