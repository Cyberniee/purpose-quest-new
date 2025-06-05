//accountutils.js

export function formatProductDate(productId, dateStr) {
    // Extract the date and time from the ISO 8601 format
    const dateTime = dateStr.split('T');
    const datePart = dateTime[0];
    const timePart = dateTime[1].split(':').slice(0, 2).join(':'); // Taking only hour and minute

    // Reformat the date
    const dateParts = datePart.split('-');
    const formattedDate = `${dateParts[2]}-${dateParts[1]}-${dateParts[0]}, ${timePart}`;

    // Update the span with the formatted date
    document.getElementById("formattedDate-" + productId).textContent = formattedDate;
}

function addReportToUI(product) {
    const reportsSection = document.querySelector('.reports-section .row');
    const noReportsMessage = reportsSection.querySelector('.no-reports-message');

    // Remove the "No reports available" message if it exists
    if (noReportsMessage) {
        noReportsMessage.remove();
    }

    const colDiv = document.createElement('div');
    colDiv.classList.add('col-md-4', 'mb-4', 'd-flex', 'justify-content-center');
    colDiv.setAttribute('data-token-id', product.token_id);

    const cardDiv = document.createElement('div');
    cardDiv.classList.add('card', 'product-card', 'invalid-product-card', 'd-flex', 'flex-column');

    // Create an img element
    const imgElement = document.createElement('img');
    imgElement.classList.add('card-img-top', 'image-max-h');
    imgElement.src = product.image; // Set the src to the product's image URL
    imgElement.alt = product.name; // Set the alt text to the product's name

    // Insert the image element at the beginning of the cardDiv
    cardDiv.insertBefore(imgElement, cardDiv.firstChild);

    const cardBodyDiv = document.createElement('div');
    cardBodyDiv.classList.add('card-body', 'd-flex', 'flex-column', 'flex-grow-1');

    const titleH5 = document.createElement('h5');
    titleH5.classList.add('card-title');
    titleH5.textContent = product.name;

    const tokenP = document.createElement('p');
    tokenP.classList.add('card-token');
    tokenP.textContent = product.token_id;

    const descriptionP = document.createElement('p');
    descriptionP.classList.add('card-text');
    descriptionP.textContent = product.description;

    const reportLink = document.createElement('a');
    reportLink.classList.add('btn', 'btn-primary', 'start-btn', 'mt-auto');
    reportLink.href = product.report_link;
    reportLink.dataset.productId = product.product_id;
    reportLink.dataset.tokenId = product.token_id;
    reportLink.textContent = 'Open Report';

    cardBodyDiv.appendChild(titleH5);
    cardBodyDiv.appendChild(tokenP);
    cardBodyDiv.appendChild(descriptionP);
    cardBodyDiv.appendChild(reportLink);

    cardDiv.appendChild(cardBodyDiv);
    colDiv.appendChild(cardDiv);
    reportsSection.appendChild(colDiv);
}

function removeProductFromList(taskId) {
    const progressContainer = document.querySelector(`div[data-task-id="${taskId}"]`);
    if (progressContainer) {
        const productCard = progressContainer.closest('.valid-product-card');
        if (productCard) {
            const ancestorElement = productCard.parentElement;
            if (ancestorElement) {
                ancestorElement.remove();
            }
        }
    }
}

function updateUIBasedOnTaskStatus(tokenId, data) {
    const productElement = document.querySelector(`div[data-token-id="${tokenId}"]`);
    if (productElement) {
        const progressDiv = productElement.querySelector('.progress-container');
        const progressBar = progressDiv.querySelector('.progress-bar');
        const progressLabel = progressDiv.querySelector('.progress-label');
        const statusLabel = productElement.querySelector('.token-status-label');
        const startButton = productElement.querySelector('.start-btn');
        const percentage = Number(data.percentage) || 0;  // Ensure it's a number

        if (data.status === 'PROGRESS' || data.status === 'SUCCESS' || data.status === 'LIMIT' || data.status === 'ERROR') {
            progressDiv.style.display = 'block';
        }

        if (data.status === 'PROGRESS') {
            const progressMessage = `Task Progress: ${data.progress} - ${percentage.toFixed(2)}% (allow up to 15 minutes to complete)`;
            progressLabel.innerText = progressMessage;
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);  // Set aria-valuenow attribute
            statusLabel.innerText = 'Processing...';
            statusLabel.classList.remove('bg-warning');
            statusLabel.classList.remove('bg-success');
            statusLabel.classList.remove('bg-primary');
            statusLabel.classList.add('bg-success');

            // Create the spinner element
            const spinner = document.createElement('span');
            spinner.className = 'spinner-border spinner-border-sm';
            spinner.setAttribute('role', 'status');
            spinner.setAttribute('aria-hidden', 'true');

            // Optionally, you could add some space between the spinner and the button text
            const space = document.createTextNode(' ');

            // Clear existing button text and append the spinner and space
            startButton.innerText = '';
            startButton.appendChild(spinner);
            startButton.appendChild(space);
            startButton.appendChild(document.createTextNode('Processing...'));

            // Disable the button
            startButton.disabled = true;
        } else if (data.status === 'SUCCESS') {
            progressLabel.innerText = 'Task Complete! Generating link...';
            progressBar.style.width = '100%';  // Complete progress bar
            progressBar.setAttribute('aria-valuenow', 100);  // Set aria-valuenow attribute
            statusLabel.innerText = 'Done';
            statusLabel.classList.remove('bg-warning');
            statusLabel.classList.remove('bg-success');
            statusLabel.classList.remove('bg-primary');
            statusLabel.classList.add('bg-success');
            startButton.disabled = true;
            startButton.innerText = 'Done';
        } else if (data.status === 'LIMIT') {
            progressLabel.innerText = '${data.limit}';
            progressBar.style.width = '0%';  // Complete progress bar
            progressBar.setAttribute('aria-valuenow', 0);  // Set aria-valuenow attribute
            statusLabel.innerText = 'Done';
            statusLabel.classList.remove('bg-warning');
            statusLabel.classList.remove('bg-success');
            statusLabel.classList.remove('bg-primary');
            statusLabel.classList.add('bg-error');
            startButton.disabled = false;
            startButton.innerText = 'Open';
        } else if (data.status === 'WAITING') {
            progressLabel.innerText = '${data.progress}';
            statusLabel.innerText = 'Waiting';
            statusLabel.classList.remove('bg-warning');
            statusLabel.classList.remove('bg-success');
            statusLabel.classList.remove('bg-primary');
            statusLabel.classList.add('bg-error');
            startButton.disabled = true;
            startButton.innerText = 'waiting...';
        } else if (data.status === 'CRITICAL') {
            progressLabel.innerText = '${data.progress}';
            statusLabel.innerText = 'Critical error';
            statusLabel.classList.remove('bg-warning');
            statusLabel.classList.remove('bg-success');
            statusLabel.classList.remove('bg-primary');
            statusLabel.classList.add('bg-error');
            startButton.disabled = false;
            startButton.innerText = 'open';
        }
    }
}

export function checkNewUser(userId) {
    const userCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('user_data='));

    if (!userCookie) return;

    try {
        // Extract raw cookie value
        const rawValue = userCookie.split('=').slice(1).join('=');
        // Safely decode and sanitize
        const cleaned = decodeURIComponent(rawValue)
            .replace(/\\n/g, '\\n')
            .replace(/\\'/g, "\\'")
            .replace(/\\"/g, '\\"')
            .replace(/\\&/g, '\\&')
            .replace(/\\r/g, '\\r')
            .replace(/\\t/g, '\\t')
            .replace(/\\b/g, '\\b')
            .replace(/\\f/g, '\\f');

        const userData = JSON.parse(cleaned);

        if (userData.first_login) {
            const modal = document.getElementById('motivatorModal');
            if (modal) {
                modal.classList.add('show');
            }
            updateUserData({ first_login: false });
        }
    } catch (err) {
        console.error("Failed to parse user_data cookie:", err);
    }
}



export async function updateUserData(updates = {}) {
    try {
        const response = await fetch('/user/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include', // ensures cookies like access_token are sent
            body: JSON.stringify(updates)
        });

        const data = await response.json();
        if (response.ok) {
            console.log('✅ Update successful:', data.message);
        } else {
            console.warn('⚠️ Update failed:', data.message);
        }

        return data;
    } catch (error) {
        console.error('🚫 Error updating user:', error);
        return { status: 'error', message: 'Could not update user' };
    }
}


export function getTaskStatus(tokenId, card) {
    const progressContainer = card.querySelector('.progress-container');
    const progressBar = progressContainer.querySelector('.progress-bar');
    const progressLabel = progressContainer.querySelector('.progress-label');
    const statusLabel = card.querySelector('.token-status-label');
    const startButton = card.querySelector('.btn');

    async function checkProgress() {
        try {
            const res = await fetch(`/report/progress/${tokenId}`);
            if (!res.ok) throw new Error("Failed to get progress");
            const data = await res.json();

            const percentage = Math.round((data.progress / data.total) * 100);

            // Show and update the progress bar
            progressContainer.style.display = 'block';
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
            progressLabel.innerText = `Progress: ${percentage}%`;

            // Update badge text
            if (statusLabel) {
                statusLabel.innerText = 'Processing...';
                statusLabel.classList.remove('bg-warning', 'bg-primary');
                statusLabel.classList.add('bg-success');
            }

            // Show spinner on button
            if (startButton && startButton.tagName.toLowerCase() === 'button') {
                startButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...`;
                startButton.disabled = true;
            }

            if (data.status === 'completed') {
                clearInterval(interval);
                card.classList.remove("disabled-card");
                progressContainer.style.display = 'none';

                // Replace button with link
                if (startButton) {
                    startButton.outerHTML = `<a class="btn btn-primary mt-auto" href="/report/${data.report_id}" role="button">To Report</a>`;
                }

                if (statusLabel) {
                    statusLabel.innerText = 'Done';
                    statusLabel.classList.remove('bg-warning');
                    statusLabel.classList.add('bg-success');
                }
            }
        } catch (err) {
            console.error("Progress check error", err);
        }
    }

    const interval = setInterval(checkProgress, 8000);
    checkProgress();
}

