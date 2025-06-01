export function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

export function displayAuthMessage() {
    const authMessage = getCookie('auth_message');
    if (authMessage) {
        const messageWithoutQuotes = decodeURIComponent(authMessage.replace(/\\054/g, ',')); // Replace octal encoded commas
        // const messageWithoutQuotes = decodedMessage.replace(/^"|"$/g, '');
        if (messageWithoutQuotes) {
            const messageElement = document.getElementById('authMessage');
            if (messageElement) {
                messageElement.innerText = messageWithoutQuotes;
                messageElement.style.display = 'block';
            }
            // Hide the message after 5 seconds (5000 milliseconds)
            setTimeout(() => {
                messageElement.style.display = 'none';
            }, 7000);
    
            // Optionally, clear the cookie after displaying the message
            document.cookie = 'auth_message=; Max-Age=-99999999;';
        }
    }

}
export function clearErrSucMessages() {
const successMessageElement = document.getElementById('successMessage');
      if (successMessageElement) {
        successMessageElement.style.display = 'none';
        successMessageElement.innerText = ''; // Clear text
      }
      
      const errorMessageElement = document.getElementById('errorMessage');
      if (errorMessageElement) {
        errorMessageElement.style.display = 'none';
        errorMessageElement.innerText = ''; // Clear text
      }
    }

export function checkAndRefreshSession() {
      const sessionStart = localStorage.getItem('session_start');
      const now = new Date().getTime();
  
      // Check if session is 30 minutes (1800000 milliseconds) or older
      if (sessionStart && now - parseInt(sessionStart) >= 1800000) {
          fetch('/auth/api/refresh_session', {
              method: 'GET',
              credentials: 'include', // Needed to include cookies for session identification
          })
          .then(response => response.json())
          .then(data => {
              if (data.status === "Session refreshed") {
                  // Update the session start time
                  localStorage.setItem('session_start', now.toString());
              }
          })
          .catch(error => console.error('Error refreshing session:', error));
      }
  }