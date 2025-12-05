/**
 * ACCL - Main JavaScript
 * Client-side interactivity using vanilla JS
 * Handles form validation, password strength, and UI interactions
 */

// Form Validation (Bootstrap 5)
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Password strength indicator
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            checkPasswordStrength(this.value);
        });
    }

    // Password matching validation
    const confirmPasswordInput = document.getElementById('confirm_password');
    if (confirmPasswordInput && passwordInput) {
        confirmPasswordInput.addEventListener('input', function() {
            checkPasswordMatch();
        });
    }

    // Alert auto-dismiss
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (alert.classList.contains('alert-dismissible')) {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    alert.style.display = 'none';
                });
            }
        }
        // Auto-dismiss success alerts after 5 seconds
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => { alert.style.display = 'none'; }, 300);
            }, 5000);
        }
    });
});

// Simple AJAX helper for form submissions
function submitFormViaAjax(formId, successCallback) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const url = form.getAttribute('action');
        
        fetch(url, {
            method: form.getAttribute('method') || 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (successCallback) successCallback(data);
            } else {
                console.error('Form submission failed:', data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });
}

// Check password strength
function checkPasswordStrength(password) {
    const strengthIndicator = document.getElementById('passwordStrength');
    if (!strengthIndicator) return;

    let strength = 0;
    const checks = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        numbers: /[0-9]/.test(password),
        special: /[!@#$%^&*]/.test(password)
    };

    Object.values(checks).forEach(check => {
        if (check) strength += 20;
    });

    strengthIndicator.style.display = 'block';
    const progressBar = strengthIndicator.querySelector('.progress-bar');
    progressBar.style.width = strength + '%';

    if (strength < 40) {
        progressBar.className = 'progress-bar bg-danger';
    } else if (strength < 60) {
        progressBar.className = 'progress-bar bg-warning';
    } else if (strength < 80) {
        progressBar.className = 'progress-bar bg-info';
    } else {
        progressBar.className = 'progress-bar bg-success';
    }

    checkPasswordMatch();
}

// Check if passwords match
function checkPasswordMatch() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    const matchWarning = document.getElementById('passwordMatch');

    if (!password || !confirmPassword || !matchWarning) return;

    if (confirmPassword.value && password.value !== confirmPassword.value) {
        matchWarning.style.display = 'block';
        confirmPassword.classList.add('is-invalid');
    } else {
        matchWarning.style.display = 'none';
        confirmPassword.classList.remove('is-invalid');
    }
}

// Highlight navigation active link
function highlightActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Call on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', highlightActiveNavLink);
} else {
    highlightActiveNavLink();
}
