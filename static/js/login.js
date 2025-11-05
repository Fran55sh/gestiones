// Manejo de errores
document.addEventListener('htmx:responseError', function(evt) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = 'Error de conexión. Por favor, inténtalo de nuevo.';
    errorDiv.classList.add('show');
    
    setTimeout(() => {
        errorDiv.classList.remove('show');
    }, 5000);
});

// Limpiar mensaje de error al enfocar
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('focus', function() {
        const errorDiv = document.getElementById('error-message');
        errorDiv.classList.remove('show');
    });
});
