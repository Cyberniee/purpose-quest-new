//validation.js
import { getTokenId, getProductSlug } from './tokenModule.js';
import { collectFormData } from './formHandlers.js';
import { showPart } from './productNav.js';
import { progress } from './_init.js';


export function validateForm(data) {
  let isValid = true;
  let firstInvalidPartNumber = null;

  for (let key in data) {
    const value = data[key];
    const words = value.split(' ').filter(Boolean); // split by space and filter out empty strings

    const partNumber = Object.keys(data).indexOf(key) + 1; // Gets the part number from its position in the object
    const textarea = document.querySelector(`#part${partNumber} textarea`);
    const tooltip = document.querySelector(`#tooltip-part${partNumber}`);

    if (words.length < 25) {
      isValid = false;
      if (firstInvalidPartNumber === null) {
        firstInvalidPartNumber = partNumber;
      }

      textarea.classList.add('is-invalid');
      if (tooltip) {
        tooltip.style.display = 'block';
        tooltip.classList.add('text-center');
      }
    } else {
      textarea.classList.remove('is-invalid');
      if (tooltip) {
        tooltip.style.display = 'none';
      }
    }

    textarea.addEventListener('input', function onInputChange() {
      const currentWords = textarea.value.split(' ').filter(Boolean);
      if (currentWords.length >= 25) {
        if (tooltip) {
          tooltip.style.display = 'none';
        }
        textarea.classList.remove('is-invalid');
        textarea.removeEventListener('input', onInputChange);
      }
    });
  }

  if (firstInvalidPartNumber !== null) {
    progress(firstInvalidPartNumber);
    showPart(firstInvalidPartNumber);
  }

  return isValid;
}



export function submitForm() {
  const tokenId = getTokenId();
  const productSlug = getProductSlug();
  const userData = collectFormData();
  
  console.log("token_id and product_slug before submission: ", tokenId, productSlug);
  
  const dataToSend = {
    story: userData,
    productSlug: productSlug,
    tokenId: tokenId
  };

  return fetch("/report/submit_story", {
    method: "POST",
    body: JSON.stringify(dataToSend),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log(response)
    // Check for a 202 status code for success
    if (response.status === 200) {
      return response.json();  // assuming server responds with json
    }
    // Handle 400 status code for error
    else if (response.status === 400) {
      return response.json().then(data => {
        throw new Error(data.message || 'Error submitting the form.');
      });
    }
    // Handle other unexpected statuses
    else {
      throw new Error('Network response was not ok');
    }
  })
  .then(data => {
    // On success, we redirect
    window.location.href = '/dashboard';
  })
  .catch(error => {
    console.error("There was a problem with the fetch operation:", error.message);
  });
}


