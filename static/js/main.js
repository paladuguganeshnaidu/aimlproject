document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // 2. Login Error Shake Effect
    // If an alert-danger exists inside a login form context, shake the form
    const loginCard = document.querySelector('.login-card');
    if (loginCard && document.querySelector('.alert-danger')) {
        loginCard.classList.add('shake');
        setTimeout(() => loginCard.classList.remove('shake'), 500);
    }

    // 3. Mark Attendance Interactions (Radio Buttons)
    // Add active styling logic is handled by CSS :checked + label, 
    // but we can add sound or micro-feedback here if requested. 
    // For now, CSS is sufficient for visual feedback.

    // 4. Progress Bar Animation
    // Animate width from 0 to target on load
    const progressBars = document.querySelectorAll('.progress-fill');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0';
        setTimeout(() => {
            bar.style.width = width;
        }, 300);
    });
});

// Toast Notification System
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    // Icon based on type
    const icon = type === 'success' ? '<i class="fas fa-check-circle text-success"></i>' : '<i class="fas fa-exclamation-circle text-danger"></i>';

    toast.innerHTML = `
        ${icon}
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.5s forwards';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}
