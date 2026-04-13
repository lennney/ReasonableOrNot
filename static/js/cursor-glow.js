/**
 * Cursor Glow Effect
 * Creates a subtle blue glow that follows the mouse cursor
 */

(function() {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    // Create glow element
    const glow = document.createElement('div');
    glow.className = 'cursor-glow';
    document.body.appendChild(glow);

    let mouseX = 0, mouseY = 0;
    let glowX = 0, glowY = 0;
    const smoothing = 0.15; // Lower = smoother/slower

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    // Hide glow when leaving window
    document.addEventListener('mouseleave', () => {
        glow.style.opacity = '0';
    });

    document.addEventListener('mouseenter', () => {
        glow.style.opacity = '1';
    });

    // Smooth animation loop
    function animate() {
        // Smooth interpolation for trailing effect
        glowX += (mouseX - glowX) * smoothing;
        glowY += (mouseY - glowY) * smoothing;

        glow.style.left = glowX + 'px';
        glow.style.top = glowY + 'px';

        requestAnimationFrame(animate);
    }

    animate();
})();
