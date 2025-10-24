document.addEventListener("DOMContentLoaded", () => {
    const navMenu = document.querySelector('.nav-menu');
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const closeMenu = document.querySelector('.close-menu');

    if (hamburgerMenu && navMenu && closeMenu) {
        // Open navigation menu
        hamburgerMenu.addEventListener('click', () => {
            navMenu.classList.add('active');
        });

        // Close navigation menu
        closeMenu.addEventListener('click', () => {
            navMenu.classList.remove('active');
        });
    }
});