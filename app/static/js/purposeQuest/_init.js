//_init.js
import { fetchPreviousData, onInputKeyPress, debounce, autosave } from "./saveData.js";
import { updateWordCount } from "./_utils.js";
import { setVersionFlag, loadSimpleSection, loadElaborateSection, loadLiteSection, prefillFormData, collectFormData } from "./formHandlers.js";
import { showPart, getCurrentPartNumber } from './productNav.js';
import { simpleFormDataTemplate, elaborateFormDataTemplate, liteFormDataTemplate } from './formDataTemplates.js';
import { validateForm, submitForm } from './validation.js';
import { btnLoader } from '../addLoader.js';

export let formData = {};
export let formType = '';


//local helper functions
function getFormParts() {
    const parts = Array.from(document.querySelectorAll('.form-part'));
    const totalParts = parts.length;
    return { parts, totalParts };
}

// Ensure to update the setTextAreaSize function with a minimum height check
export function setTextAreaSize(textarea) {
    const minHeight = 50; // Minimum height for textarea in pixels
    textarea.style.height = 'auto';
    textarea.style.height = Math.max(textarea.scrollHeight, minHeight) + 'px';
}

export async function initializeProduct() {
    // Determine form type from URL and set formDataTemplate accordingly
    setFormTypeFromURL();
    console.log(formType)
    let formDataTemplate
    if (formType === 'elaborate') {
        formDataTemplate = elaborateFormDataTemplate;
    } else if (formType === 'lite') {
        formDataTemplate = liteFormDataTemplate;
    } else {  // assuming 'simple' is the default or fallback
        formDataTemplate = simpleFormDataTemplate;
    }
    console.log(formDataTemplate)
    document.getElementById('welcomeModal').classList.add('show');

    // Fetch previous data
    const result = await fetchPreviousData(formDataTemplate);
    console.log("result after fetching prev data: ", result)
    // Initialize formData with the selected template and any pre-filled data
    formData = { ...formDataTemplate, ...result.formData };
    console.log("formdata after fetch prev data is: ", formData)



    // Load the relevant section and pre-fill form data
    loadRelevantSection(result.versionFlag, () => prefillFormData(formData));
}

export function setFormTypeFromURL() {
    const currentURL = window.location.href;
    const urlPath = new URL(currentURL).pathname;

    if (urlPath.includes('lite')) {
        formType = 'lite';
    } else if (urlPath.includes('purpose-journey')) {
        formType = 'elaborate';
    } else if (urlPath.includes('purpose-quest')) {
        formType = 'simple';
    } else {
        console.error("Invalid URL path for selection. Neither 'purpose-quest' nor 'purpose-journey' found.");
    }
}


export function progress(currentPartNumber) {
    const { totalParts } = getFormParts();
    const percentage = (100 / (totalParts - 1)) * (currentPartNumber - 1);
    document.getElementsByClassName('progress-bar')[0].style.width = `${percentage}%`;
}

export function initializeCommonElements() {
    const { parts, totalParts } = getFormParts();
    parts.forEach((part, index) => {
        // Next Button
        const nextBtn = part.querySelector('.nextBtn');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                const currentPartNumber = getCurrentPartNumber();
                if (currentPartNumber < totalParts) {
                    showPart(currentPartNumber + 1);
                    progress(currentPartNumber + 1);
                }
            });
        }
        // Previous Button
        const prevBtn = part.querySelector('.prevBtn');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                const currentPartNumber = getCurrentPartNumber();
                if (currentPartNumber > 1) {
                    showPart(currentPartNumber - 1);
                    progress(currentPartNumber - 1);
                }
            });
        }
    });

    // Handle form submission, we need to collect all written user input and fill it into the set formData template
    const form = document.getElementById('userForm');
    const submitButton = form.querySelector('[type="submit"]');
    //btnLoader(submitButton);

    let isSubmitting = false;

    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent default form submission behavior

        // Prevent double submission
        if (isSubmitting) {
            console.log("Already submitting, please wait...");
            return;
        }

        // Collect data from the form
        formData = collectFormData();

        // Validate the form
        const isValid = validateForm(formData);
        if (isValid) {
            console.log("submission valid ", isValid);

            // Set the flag to prevent further submission attempts
            isSubmitting = true;

            // Disable the button to prevent multiple submissions
            submitButton.disabled = true;

            // Create the spinner element
            const spinner = document.createElement('span');
            spinner.className = 'spinner-border spinner-border-sm';
            spinner.setAttribute('role', 'status');
            spinner.setAttribute('aria-hidden', 'true');

            // Optionally, you could add some space between the spinner and the button text
            const space = document.createTextNode(' ');

            // Append the spinner and space to the button
            submitButton.prepend(spinner);
            submitButton.prepend(space);

            // Attempt to submit the form
            await submitForm(formData);

            // Once the form has been submitted, you might want to remove the spinner
            // and re-enable the button, depending on the outcome of submitForm
            submitButton.removeChild(spinner);
            submitButton.removeChild(space);
            submitButton.disabled = false;
            isSubmitting = false;
        } else {
            console.log("Form is not valid.");
            // If the form is not valid, no need to remove the spinner or re-enable the button
            // because they were never added or disabled in the first place.
        }
    });


    document.querySelectorAll('textarea').forEach(textarea => {
        setTextAreaSize(textarea);
        updateWordCount(textarea.id); // Initialize word count display
        const debouncedAutosave = debounce(() => autosave(), 1000);  // Create debounced function once
        textarea.addEventListener('input', function (event) {
            setTextAreaSize(this);
            updateWordCount(this.id); // Update word count display on input
            onInputKeyPress(event, debouncedAutosave);
        });
    });

    showPart(1);
}

export function initSection() {
    productBody.classList.add('bodyPurposeQuest');
    initializeCommonElements()
}

export function initSelectionSection() {
    // Get current URL and path
    const currentURL = window.location.href;
    const urlPath = new URL(currentURL).pathname;

    // Load the corresponding section based on the URL
    if (urlPath.includes('lite')) {
        setVersionFlag('lite');
        loadLiteSection();
        formData = { ...simpleFormDataTemplate };  // Update formData to simple template
        formType = 'lite';
    } else if (urlPath.includes('purpose-journey')) {
        setVersionFlag('elaborate');
        loadElaborateSection();
        formData = { ...elaborateFormDataTemplate };  // Update formData to elaborate template
        formType = 'elaborate';
    } else if (urlPath.includes('purpose-quest')) {
        setVersionFlag('simple');
        loadSimpleSection();
        formData = { ...liteFormDataTemplate };  // Update formData to elaborate template
        formType = 'simple';
    } else {
        // You can handle the case where neither condition is met, perhaps by displaying an error or redirecting the user
        console.error("Invalid URL path for selection. Neither 'purpose-quest' nor 'purpose-journey' found.");
    }
    console.log(formType)
}


export function loadRelevantSection(versionFlag, prefillCallback) {
    console.log("loadRelevantSections data: ", versionFlag, prefillCallback);

    // Helper function to execute prefillCallback if it's provided
    function handlePrefill() {
        if (prefillCallback) prefillCallback();
    }
    console.log("load relevant section, versionFlag: ", versionFlag)

    if (versionFlag === null || versionFlag === false) {
        // Load selection section
        initSelectionSection();
    } else if (versionFlag === 'elaborate') {
        // Load elaborate section
        loadHTMLModule('purpose-quest-elaborate.html', 'dynamicContent', () => {
            initSection();
            handlePrefill();
        });
    } else if (versionFlag === 'simple') {
        // Load simple section
        loadHTMLModule('purpose-quest-simple.html', 'dynamicContent', () => {
            initSection();
            handlePrefill();
        });
    } else if (versionFlag === 'lite') {
        loadHTMLModule('purpose-quest-lite-content.html', 'dynamicContent', () => {
            initSection();
            handlePrefill();
        });
    } else {
        console.log("An error occured loading the form content");
    }
}

export function loadHTMLModule(path, targetId, initFunction) {
    console.log("loadHtmlModule: ", path, "targetId: ", targetId, "initfunct: ", initFunction)
    fetch(`/report/section/${path}`)
        .then(response => response.text())
        .then(html => {
            const targetElement = document.getElementById(targetId);

            // Remove existing event listeners from target element's textareas
            const existingTextareas = targetElement.querySelectorAll('textarea');
            existingTextareas.forEach(textarea => {
                textarea.removeEventListener('input', textarea._inputHandler);
            });

            // Update HTML content
            targetElement.innerHTML = html;

            // Call the initFunction to set up new event listeners, if provided
            if (initFunction) {
                initFunction();
            }
        })
        .catch(error => {
            console.warn('Something went wrong.', error);
        });
}