// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Form submission
document.getElementById('contact-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const form = this;
    const submitButton = form.querySelector('.btn-submit');
    const originalButtonText = submitButton.textContent;
    
    // Deshabilitar botÃ³n y mostrar estado de carga
    submitButton.disabled = true;
    submitButton.textContent = 'Enviando...';
    
    // Crear FormData
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/api/contact', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Mostrar mensaje de Ã©xito
            const successDiv = document.createElement('div');
            successDiv.style.cssText = 'color: #10b981; background: #d1fae5; padding: 16px; border-radius: 8px; margin-top: 20px; border: 1px solid #10b981;';
            successDiv.textContent = 'âœ“ ' + result.message;
            form.parentNode.insertBefore(successDiv, form);
            
            // Limpiar formulario
            form.reset();
            
            // Remover mensaje despuÃ©s de 5 segundos
            setTimeout(() => {
                successDiv.remove();
            }, 5000);
        } else {
            // Mostrar mensaje de error
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = 'color: #dc2626; background: #fee2e2; padding: 16px; border-radius: 8px; margin-top: 20px; border: 1px solid #dc2626;';
            errorDiv.textContent = 'âœ— ' + result.message;
            form.parentNode.insertBefore(errorDiv, form);
            
            // Remover mensaje despuÃ©s de 5 segundos
            setTimeout(() => {
                errorDiv.remove();
            }, 5000);
        }
    } catch (error) {
        // Mostrar mensaje de error de conexiÃ³n
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = 'color: #dc2626; background: #fee2e2; padding: 16px; border-radius: 8px; margin-top: 20px; border: 1px solid #dc2626;';
        errorDiv.textContent = 'âœ— Error de conexiÃ³n. Por favor, intente nuevamente mÃ¡s tarde.';
        form.parentNode.insertBefore(errorDiv, form);
        
        // Remover mensaje despuÃ©s de 5 segundos
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    } finally {
        // Restaurar botÃ³n
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
    }
});

// Theme toggle functionality
const themeToggle = document.getElementById('theme-toggle');
const htmlElement = document.documentElement;
const logo = document.querySelector('.logo');

// Function to update logo based on theme
function updateLogo(theme) {
    if (logo) {
        if (theme === 'dark') {
            logo.src = 'logo-dark.png';
        } else {
            logo.src = 'logo.png';
        }
    }
}

// Load saved theme or default to light
const currentTheme = localStorage.getItem('theme') || 'light';
if (currentTheme === 'dark') {
    htmlElement.setAttribute('data-theme', 'dark');
    themeToggle.checked = false;
    updateLogo('dark');
} else {
    htmlElement.setAttribute('data-theme', 'light');
    themeToggle.checked = true;
    updateLogo('light');
}

// Toggle theme on switch change
themeToggle.addEventListener('change', function() {
    if (this.checked) {
        htmlElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        updateLogo('light');
    } else {
        htmlElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        updateLogo('dark');
    }
});