// Small helpers for HTMX + Django CSRF.
//
// The UI works without HTMX (normal form POST + redirects), but when HTMX
// is available this makes requests smoother and ensures CSRF headers are
// set correctly.

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Add CSRF header for all HTMX requests
document.addEventListener('htmx:configRequest', function (event) {
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
        event.detail.headers['X-CSRFToken'] = csrfToken;
    }
});

// Reset forms after a successful HTMX request
document.addEventListener('htmx:afterRequest', function (event) {
    if (event.detail.successful) {
        const form = event.target.closest('form');
        if (form) form.reset();
    }
});

// Show a simple alert for HTMX errors (useful during development)
document.addEventListener('htmx:responseError', function () {
    alert('Something went wrong. Please try again.');
});
