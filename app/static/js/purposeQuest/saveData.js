//saveData.js
import { getTokenId } from './tokenModule.js';
import { collectFormData } from './formHandlers.js';
import { formType } from "./_init.js";

let keystrokes = 0;

//text area
let debouncedShowSaveMessage = debounce(showSaveMessage, 60000);  // Debounce showSaveMessage for 1 minute


export function debounce(func, delay) {
  let debounceTimer;
  return function (...args) {
    const context = this;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => func.apply(context, ...args), delay);
  }
}

export function autosave() {
  let payload;
  const tokenId = getTokenId();
  const userData = collectFormData();
  payload = {
    story: userData,
    token_id: tokenId
  };

  console.log("autosave filled with: ", payload);

  fetch("/report/autosave_story", {
    method: "POST",
    body: JSON.stringify(payload),
    headers: {
      'Content-Type': 'application/json'
    }
  });

  debouncedShowSaveMessage();  // Call the debounced version of showSaveMessage

}

export function onInputKeyPress(event, debouncedAutosave) {
  keystrokes++;
  if (keystrokes >= 10) {
    debouncedAutosave();
    keystrokes = 0;
  }
}

// fetch previous data looks at previous data. If none is present, it does nothing. If data is present, it prefills the form.
export function fetchPreviousData() {
  const tokenId = getTokenId();
  console.log("fetchPrevData gets token: ", tokenId)
  return new Promise((resolve, reject) => {
    console.log(tokenId)
    fetch("/report/fetch_prev_data", {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'TokenId': tokenId,
      }
    }).then(response => {
      console.log("resp for fetchPrevData: ", response);
      if (response.status === 204) {
        return null;
      }
      return response.json();
    })
      .then(data => {
        if (data) {
          console.log("previous data recovered: ", data);
          resolve({
            formData: data.data || {},
            versionFlag: data.versionFlag
          });
        } else {
          resolve({
            formData: {},
            versionFlag: formType === 'elaborate'  // Default to the formType from URL
          });
        }
      })
      .catch(err => reject(err));
  });
}

function showSaveMessage() {
  const safeIcon = document.getElementById('safeIcon');
  safeIcon.textContent = 'Progress saved!'; // Add the text
  safeIcon.style.display = 'block'; // Make the element a block to show it

  // Fade in
  safeIcon.style.animation = 'fadeIn 0.2s';
  safeIcon.style.opacity = '1';

  setTimeout(() => {
    // Start the fade-out after 1.6s (2s total - 0.2s for fade-in - 0.2s for fade-out)
    safeIcon.style.animation = 'fadeOut 0.2s';
    safeIcon.style.opacity = '0';

    // Hide the element after fade-out
    setTimeout(() => {
      safeIcon.style.display = 'none';
    }, 200); // Wait 0.2s for the fade-out to finish

  }, 1600); // 1.6s is the delay for the text to be visible before fading out
}