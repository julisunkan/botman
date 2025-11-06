function showNotification(message, type = 'info') {
    // Remove any existing inline messages
    const existingMessages = document.querySelectorAll('.inline-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Find the main content container
    const mainContainer = document.querySelector('main.container') || document.querySelector('.container');
    if (!mainContainer) {
        console.error('Main container not found');
        return;
    }
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} inline-message`;
    notification.setAttribute('role', 'alert');
    
    const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle';
    
    notification.innerHTML = `
        <div class="d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-2">
                <i class="fas fa-${icon}"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close btn-close-white" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    notification.style.animation = 'fadeInDown 0.3s ease-out';
    mainContainer.insertBefore(notification, mainContainer.firstChild);
    
    // Scroll to top to show the message
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeOutUp 0.3s ease-out';
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }, 5000);
}

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registered:', registration);
            })
            .catch(error => {
                console.log('ServiceWorker registration failed:', error);
            });
    });
}

document.addEventListener('click', function(event) {
    const userMenu = document.getElementById('user-menu');
    if (!userMenu) return;
    
    const isClickInsideMenu = userMenu.contains(event.target);
    const isClickOnProfileButton = event.target.closest('.footer-nav-item[onclick*="user-menu"]');
    
    if (!isClickInsideMenu && !isClickOnProfileButton && userMenu.classList.contains('show')) {
        userMenu.classList.remove('show');
    }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const userMenu = document.getElementById('user-menu');
        if (userMenu && userMenu.classList.contains('show')) {
            userMenu.classList.remove('show');
        }
    }
});
