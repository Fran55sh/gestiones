// Prevenir submit normal del formulario - HTMX lo manejará
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Si HTMX no está disponible, prevenir y mostrar error
            if (typeof htmx === 'undefined') {
                e.preventDefault();
                alert('HTMX no está disponible. Por favor, recarga la página.');
                return false;
            }
            // HTMX manejará el submit, no prevenir aquí
        });
    }
});

// Manejo de errores
document.addEventListener('htmx:responseError', function(evt) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = 'Error de conexión. Por favor, inténtalo de nuevo.';
    errorDiv.classList.add('show');
    
    setTimeout(() => {
        errorDiv.classList.remove('show');
    }, 5000);
});

// Manejar redirección después de login exitoso
document.addEventListener('htmx:afterSwap', function(evt) {
    // Si hay un header HX-Redirect, HTMX debería manejarlo automáticamente
    // Pero verificamos por si acaso
    if (evt.detail.xhr.getResponseHeader('HX-Redirect')) {
        window.location.href = evt.detail.xhr.getResponseHeader('HX-Redirect');
    }
});

// Limpiar mensaje de error al enfocar
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('focus', function() {
        const errorDiv = document.getElementById('error-message');
        errorDiv.classList.remove('show');
    });
});
