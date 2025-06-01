//productNav.js

import {setTextAreaSize} from './_init.js'

export function showPart(targetPartNumber) {
  // Hide all parts
  const allParts = document.querySelectorAll('.form-part');
  allParts.forEach(part => part.classList.add('hidden'));

  // Show the target part
  const targetPart = document.querySelector(`#part${targetPartNumber}`);
  targetPart.classList.remove('hidden');

  // Get all textareas in the current part and adjust their size
  const textareas = targetPart.querySelectorAll('textarea');
  textareas.forEach(textarea => {
    setTextAreaSize(textarea);
  });
}

// Function to get the current part number
export function getCurrentPartNumber() {
  const visiblePart = document.querySelector('.form-part:not(.hidden)');
  if (visiblePart) {
    return parseInt(visiblePart.id.replace('part', ''));
  }
  return 1; // Default to 1 if no visible part found
}

