//_utils.js
export function updateWordCount(textAreaId) {
    const textArea = document.getElementById(textAreaId);
    let wordCountDisplay = document.getElementById('wordCount-' + textAreaId);
    const minWordCount = 25;
    const words = textArea.value.match(/\b[-?(\w+)?]+\b/gi);
    const wordCount = words ? words.length : 0;
    if (wordCount < minWordCount) {
        wordCountDisplay.innerHTML = `Minimum: ${wordCount}/${minWordCount} words`;
    } else {
        wordCountDisplay.innerHTML = `${wordCount} words`;
    }
}


