//formHandlers.js
import { getTokenId } from './tokenModule.js';
import { formType, loadRelevantSection } from "./_init.js";
import { simpleFormDataTemplate, elaborateFormDataTemplate, liteFormDataTemplate } from './formDataTemplates.js';

function triggerInputEvent(element) {
    const event = new Event('input', {
        'bubbles': true,
        'cancelable': true
    });
    element.dispatchEvent(event);
}

export function prefillFormData(formData) {
    if (formType === 'simple') {
        // Handle simple form
        const keys = Object.keys(formData);
        keys.forEach((key, index) => {
            const formPart = document.getElementById(`part${index + 1}`);
            if (formPart) {
                const textarea = formPart.querySelector('textarea');
                if (textarea && formData[key]) {
                    textarea.value = formData[key];
                    triggerInputEvent(textarea);
                }
            }
        });
    } else if (formType === 'lite') {
        const keys = Object.keys(formData);
        keys.forEach((key, index) => {
            const formPart = document.getElementById(`part${index + 1}`);
            if (formPart) {
                const textarea = formPart.querySelector('textarea');
                if (textarea && formData[key]) {
                    textarea.value = formData[key];
                    triggerInputEvent(textarea);
                }
            }
        });
    } else {
        // Handle elaborate form
        Object.keys(formData).forEach((sectionKey, sectionIndex) => {
            const formPart = document.getElementById(`part${sectionIndex + 1}`);
            if (formPart && formPart.getAttribute("data-key") === sectionKey) {
                Object.keys(formData[sectionKey]).forEach((subSectionKey) => {
                    Object.keys(formData[sectionKey][subSectionKey]).forEach((fieldKey) => {
                        const textarea = formPart.querySelector(`textarea[name="${fieldKey}"]`);
                        if (textarea && formData[sectionKey][subSectionKey][fieldKey]) {
                            textarea.value = formData[sectionKey][subSectionKey][fieldKey];
                            triggerInputEvent(textarea);
                        }
                    });
                });
            }
        });
    }
}

export function collectFormData() {
    // Create a new object to store user data, initialized with the values from the original formData
    let userFormData;
    //console.log("FormType: ", formType)

    if (formType === 'simple') {
        userFormData = { ...simpleFormDataTemplate };  // Initialize from the simple template
    } else if (formType === 'lite') {
        userFormData = { ...liteFormDataTemplate };  // Initialize from the simple template
    } else {
        userFormData = JSON.parse(JSON.stringify(elaborateFormDataTemplate));  // Clone the elaborate template
    }
    //console.log("UserFormData", userFormData)

    const formParts = document.querySelectorAll('.form-part');

    formParts.forEach((formPart) => {
        const sectionKey = formPart.getAttribute('data-key');
        //console.log("Current section key: ", sectionKey);  // Debug line

        const textareas = formPart.querySelectorAll('textarea');

        textareas.forEach((textarea) => {
            const fieldKey = textarea.getAttribute('name');
            //console.log("Current field key: ", fieldKey);  // Debug line

            const value = textarea.value;
            //console.log("Current value: ", value);  // Debug line
            const transformedFieldKey = fieldKey.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');

            if (formType === 'simple' || formType === 'lite') {
                // For the simple form, directly set the value.
                if (sectionKey === transformedFieldKey) {
                    userFormData[sectionKey] = value;
                }
            } else {
                // For the elaborate form, traverse to find the right place to set the value.
                if (userFormData[sectionKey]) {
                    Object.keys(userFormData[sectionKey]).forEach((subSectionKey) => {
                        if (userFormData[sectionKey][subSectionKey][fieldKey] !== undefined) {
                            userFormData[sectionKey][subSectionKey][fieldKey] = value;
                        }
                    });
                }
            }
        });
    });

    console.log("Collected data: ", userFormData);  // Debug line
    return userFormData;
}

export function autoExpand(textarea) {
    const currentScroll = document.documentElement.scrollTop; // Store current scroll position

    // Calculate the minimum height based on line height and rows
    const style = window.getComputedStyle(textarea, null);
    const lineHeight = parseInt(style.getPropertyValue("line-height"), 10);
    const rows = textarea.getAttribute("rows");
    const minHeight = lineHeight * rows;

    // Reset the height
    textarea.style.height = 'auto';

    // Adjust the height to its scroll height, but not less than minHeight
    textarea.style.height = `${Math.max(textarea.scrollHeight, minHeight)}px`;

    document.documentElement.scrollTop = currentScroll; // Restore the scroll position
}

export function setVersionFlag(isElaborate) {
    const tokenId = getTokenId();
    console.log("versionFlag in setVersionFlag: ", isElaborate);
    fetch('/report/set_version', {
        method: 'POST',
        body: JSON.stringify({ version: isElaborate, tokenId: tokenId }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === "failure") {
                console.log("Failed to set elaborate flag");
            }
        })
        .catch(error => {
            console.log('Fetch operation error:', error.message);
        });
}

// the loadSections below have a chain of functions amongst which setting the common elements and eventlisteners
export function loadSimpleSection() {
    const tokenId = getTokenId();
    // Clear the selection section
    const dynamicContent = document.getElementById('dynamicContent');
    dynamicContent.innerHTML = '';

    // Load the simple section
    loadRelevantSection('simple', tokenId, () => {
        // Prefill callback if needed
    });
}

export function loadElaborateSection() {
    const tokenId = getTokenId();
    // Clear the selection section
    const dynamicContent = document.getElementById('dynamicContent');
    dynamicContent.innerHTML = '';

    // Load the elaborate section
    loadRelevantSection('elaborate', tokenId, () => {
        // Prefill callback if needed
    });
}

export function loadLiteSection() {
    const tokenId = getTokenId();
    // Clear the selection section
    const dynamicContent = document.getElementById('dynamicContent');
    dynamicContent.innerHTML = '';

    // Load the elaborate section
    loadRelevantSection('lite', tokenId, () => {
        // Prefill callback if needed
    });
}
