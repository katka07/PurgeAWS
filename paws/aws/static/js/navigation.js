document.addEventListener('DOMContentLoaded', function() {
    if (cameFromHome === true) {
        sessionStorage.removeItem('cameFromHome');
    } else {
        window.location.href = '/'; // Change this URL to your home page URL
    }
});
