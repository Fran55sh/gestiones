// Datos de clientes dummy distribuidos en distintas carteras
const clientesDummy = {
    favacard: [
        {
            id: 1,
            nombre: 'Carlos Mendoza',
            dni: '12.345.678',
            numeroId: 'FAV-001',
            telefono: '+54 11 4567-8901',
            email: 'carlos.mendoza@email.com',
            direccion: 'Av. Corrientes 1234, CABA',
            fechaNacimiento: '15/03/1985',
            montoAdeudado: 125000,
            fechaVencimiento: '15/12/2023',
            ultimaGestion: '05/01/2024',
            cuotasPendientes: 12,
            cuotasPagadas: 8,
            entidadFinanciera: 'Banco Nacional S.A.',
            observaciones: 'Cliente con historial de pagos irregular. Última cuota pagada hace 6 meses. Presenta disposición a negociar.',
            estado: 'contactado',
            diasMora: 45,
            clienteId: '#12345'
        },
        {
            id: 2,
            nombre: 'María Rodríguez',
            dni: '23.456.789',
            numeroId: 'FAV-002',
            telefono: '+54 11 5234-5678',
            email: 'maria.rodriguez@email.com',
            direccion: 'Libertador 5678, CABA',
            fechaNacimiento: '22/07/1990',
            montoAdeudado: 85000,
            fechaVencimiento: '10/11/2023',
            ultimaGestion: '02/01/2024',
            cuotasPendientes: 8,
            cuotasPagadas: 10,
            entidadFinanciera: 'Banco Nacional S.A.',
            observaciones: 'Cliente comunicativa. Ha realizado pagos parciales. Negociación en curso.',
            estado: 'con-arreglo',
            diasMora: 60,
            clienteId: '#12346'
        },
        {
            id: 3,
            nombre: 'Luis Fernández',
            dni: '34.567.890',
            numeroId: 'FAV-003',
            telefono: '+54 11 4789-1234',
            email: 'luis.fernandez@email.com',
            direccion: 'Rivadavia 9876, CABA',
            fechaNacimiento: '08/12/1988',
            montoAdeudado: 95000,
            fechaVencimiento: '20/12/2023',
            ultimaGestion: '28/12/2023',
            cuotasPendientes: 15,
            cuotasPagadas: 3,
            entidadFinanciera: 'Banco Nacional S.A.',
            observaciones: 'Primer contacto pendiente. Cliente no responde llamadas.',
            estado: 'sin-gestion',
            diasMora: 50,
            clienteId: '#12347'
        },
        {
            id: 4,
            nombre: 'Ana Martínez',
            dni: '45.678.901',
            numeroId: 'FAV-004',
            telefono: '+54 11 5123-4567',
            email: 'ana.martinez@email.com',
            direccion: 'Córdoba 2345, CABA',
            fechaNacimiento: '03/05/1992',
            montoAdeudado: 67000,
            fechaVencimiento: '05/11/2023',
            ultimaGestion: '01/01/2024',
            cuotasPendientes: 6,
            cuotasPagadas: 12,
            entidadFinanciera: 'Banco Nacional S.A.',
            observaciones: 'Deuda antigua. Cliente con problemas económicos. Evaluar situación.',
            estado: 'contactado',
            diasMora: 70,
            clienteId: '#12348'
        }
    ],
    naldo: [
        {
            id: 5,
            nombre: 'Roberto Silva',
            dni: '56.789.012',
            numeroId: 'NAL-001',
            telefono: '+54 11 4567-8901',
            email: 'roberto.silva@email.com',
            direccion: 'Santa Fe 3456, CABA',
            fechaNacimiento: '19/09/1985',
            montoAdeudado: 145000,
            fechaVencimiento: '18/12/2023',
            ultimaGestion: '04/01/2024',
            cuotasPendientes: 14,
            cuotasPagadas: 6,
            entidadFinanciera: 'Naldo Finanzas',
            observaciones: 'Cliente con trabajo estable. Muestra interés en regularizar situación.',
            estado: 'contactado',
            diasMora: 55,
            clienteId: '#12349'
        },
        {
            id: 6,
            nombre: 'Patricia López',
            dni: '67.890.123',
            numeroId: 'NAL-002',
            telefono: '+54 11 5234-5678',
            email: 'patricia.lopez@email.com',
            direccion: 'Florida 4567, CABA',
            fechaNacimiento: '11/04/1987',
            montoAdeudado: 98000,
            fechaVencimiento: '22/11/2023',
            ultimaGestion: '03/01/2024',
            cuotasPendientes: 10,
            cuotasPagadas: 8,
            entidadFinanciera: 'Naldo Finanzas',
            observaciones: 'Cliente ha cumplido con promesas anteriores. Plan de pago activo.',
            estado: 'con-arreglo',
            diasMora: 65,
            clienteId: '#12350'
        },
        {
            id: 7,
            nombre: 'Jorge García',
            dni: '78.901.234',
            numeroId: 'NAL-003',
            telefono: '+54 11 4789-1234',
            email: 'jorge.garcia@email.com',
            direccion: 'Lavalle 7890, CABA',
            fechaNacimiento: '27/11/1983',
            montoAdeudado: 180000,
            fechaVencimiento: '30/12/2023',
            ultimaGestion: '15/12/2023',
            cuotasPendientes: 18,
            cuotasPagadas: 2,
            entidadFinanciera: 'Naldo Finanzas',
            observaciones: 'Cliente elusivo. No responde comunicación. Considerar incobrable.',
            estado: 'incobrable',
            diasMora: 40,
            clienteId: '#12351'
        },
        {
            id: 8,
            nombre: 'Sofía Herrera',
            dni: '89.012.345',
            numeroId: 'NAL-004',
            telefono: '+54 11 5123-4567',
            email: 'sofia.herrera@email.com',
            direccion: 'Alvear 1234, CABA',
            fechaNacimiento: '14/06/1991',
            montoAdeudado: 72000,
            fechaVencimiento: '12/11/2023',
            ultimaGestion: '29/12/2023',
            cuotasPendientes: 5,
            cuotasPagadas: 13,
            entidadFinanciera: 'Naldo Finanzas',
            observaciones: 'Cliente regulariza deuda. Últimos pagos al día. Seguimiento continuo.',
            estado: 'con-arreglo',
            diasMora: 75,
            clienteId: '#12352'
        }
    ],
    naranjax: [
        {
            id: 9,
            nombre: 'Diego Torres',
            dni: '90.123.456',
            numeroId: 'NAR-001',
            telefono: '+54 11 4456-7890',
            email: 'diego.torres@email.com',
            direccion: 'Cabildo 5678, CABA',
            fechaNacimiento: '09/02/1986',
            montoAdeudado: 110000,
            fechaVencimiento: '25/12/2023',
            ultimaGestion: '06/01/2024',
            cuotasPendientes: 11,
            cuotasPagadas: 7,
            entidadFinanciera: 'NaranjaX S.A.',
            observaciones: 'Cliente negocia activamente. Propuestas de pago en evaluación.',
            estado: 'contactado',
            diasMora: 48,
            clienteId: '#12353'
        },
        {
            id: 10,
            nombre: 'Laura Díaz',
            dni: '01.234.567',
            numeroId: 'NAR-002',
            telefono: '+54 11 5345-6789',
            email: 'laura.diaz@email.com',
            direccion: 'San Martín 9012, CABA',
            fechaNacimiento: '31/08/1989',
            montoAdeudado: 83000,
            fechaVencimiento: '08/11/2023',
            ultimaGestion: '30/12/2023',
            cuotasPendientes: 7,
            cuotasPagadas: 11,
            entidadFinanciera: 'NaranjaX S.A.',
            observaciones: 'Casos cerrados. Cliente de baja del sistema.',
            estado: 'de-baja',
            diasMora: 80,
            clienteId: '#12354'
        }
    ]
};

// Cliente actual
let clienteActual = null;
let carteraActual = 'favacard';
let indiceClienteActual = 0;
let clientesCarteraActual = [];

// Función para obtener lista de clientes de la cartera actual
function getClientesCartera() {
    return clientesDummy[carteraActual] || [];
}

// Función para cambiar de cartera y cargar primer cliente
function changeCartera(cartera) {
    carteraActual = cartera;
    clientesCarteraActual = getClientesCartera();
    if (clientesCarteraActual.length > 0) {
        indiceClienteActual = 0;
        loadCliente(clientesCarteraActual[0], 0);
        updateCarteraSelector(cartera);
        limpiarBusqueda();
    }
}

// Función para navegar entre clientes
function navegarCliente(direccion) {
    clientesCarteraActual = getClientesCartera();
    if (clientesCarteraActual.length === 0) return;

    if (direccion === 'prev') {
        indiceClienteActual = indiceClienteActual > 0 ? indiceClienteActual - 1 : clientesCarteraActual.length - 1;
    } else {
        indiceClienteActual = indiceClienteActual < clientesCarteraActual.length - 1 ? indiceClienteActual + 1 : 0;
    }

    loadCliente(clientesCarteraActual[indiceClienteActual], indiceClienteActual);
}

// Función para ir a un nÁºmero de cliente específico
function irACliente() {
    const input = document.getElementById('go-to-number');
    const numeroCliente = parseInt(input.value);
    
    if (!numeroCliente || numeroCliente < 1) {
        alert('Por favor ingresa un número válido');
        input.focus();
        return;
    }

    clientesCarteraActual = getClientesCartera();
    const totalClientes = clientesCarteraActual.length;

    if (numeroCliente > totalClientes) {
        alert(`No existe el cliente #${numeroCliente}. Total de clientes en esta cartera: ${totalClientes}`);
        input.value = '';
        input.focus();
        return;
    }

    // Limpiar bÁºsqueda si existe
    document.getElementById('search-input').value = '';
    document.getElementById('btn-clear-search').style.display = 'none';

    // Los nÁºmeros de cliente van de 1 a N, pero el índice es 0 a N-1
    indiceClienteActual = numeroCliente - 1;
    loadCliente(clientesCarteraActual[indiceClienteActual], indiceClienteActual);
    
    // Limpiar el input
    input.value = '';
    input.blur();
}

// Función para buscar cliente
function buscarCliente(busqueda) {
    if (!busqueda || busqueda.trim() === '') {
        limpiarBusqueda();
        return;
    }

    const termino = busqueda.trim().toLowerCase();
    clientesCarteraActual = getClientesCartera();
    
    // Buscar en toda la cartera
    const clienteEncontrado = clientesCarteraActual.find(cliente => {
        const nombreMatch = cliente.nombre.toLowerCase().includes(termino);
        const dniMatch = cliente.dni.replace(/\./g, '').toLowerCase().includes(termino.replace(/\./g, ''));
        const numeroIdMatch = cliente.numeroId.toLowerCase().includes(termino);
        
        return nombreMatch || dniMatch || numeroIdMatch;
    });

    if (clienteEncontrado) {
        indiceClienteActual = clientesCarteraActual.indexOf(clienteEncontrado);
        loadCliente(clienteEncontrado, indiceClienteActual);
        // Mostrar botón de limpiar
        document.getElementById('btn-clear-search').style.display = 'block';
    } else {
        // No se encontró, pero mantener el input activo para seguir buscando
        console.log('No se encontró cliente con:', termino);
    }
}

// Función para limpiar bÁºsqueda
function limpiarBusqueda() {
    document.getElementById('search-input').value = '';
    document.getElementById('btn-clear-search').style.display = 'none';
    document.getElementById('go-to-number').value = '';
    clientesCarteraActual = getClientesCartera();
    if (clientesCarteraActual.length > 0) {
        indiceClienteActual = 0;
        loadCliente(clientesCarteraActual[0], 0);
    }
}

// Función para cargar datos de un cliente
function loadCliente(cliente, indice) {
    clienteActual = cliente;
    indiceClienteActual = indice;
    clientesCarteraActual = getClientesCartera();
    
    // Actualizar encabezado
    document.getElementById('client-name-header').textContent = cliente.nombre;
    document.getElementById('client-id-header').textContent = cliente.clienteId;
    document.getElementById('client-dni-header').textContent = cliente.dni;
    document.getElementById('client-numero-id-header').textContent = cliente.numeroId;
    
    // Actualizar datos del cliente
    document.getElementById('client-name').textContent = cliente.nombre;
    document.getElementById('client-dni').textContent = cliente.dni;
    document.getElementById('client-numero-id').textContent = cliente.numeroId;
    document.getElementById('client-phone').innerHTML = `<i data-lucide="phone" class="w-4 h-4 text-gray-400"></i> ${cliente.telefono}`;
    document.getElementById('client-email').innerHTML = `<i data-lucide="mail" class="w-4 h-4 text-gray-400"></i> ${cliente.email}`;
    document.getElementById('client-address').innerHTML = `<i data-lucide="map-pin" class="w-4 h-4 text-gray-400"></i> ${cliente.direccion}`;
    document.getElementById('client-birthdate').textContent = cliente.fechaNacimiento;
    
    // Actualizar cartera
    const carteraNames = {
        'favacard': 'Favacard',
        'naldo': 'Naldo',
        'naranjax': 'NaranjaX'
    };
    document.getElementById('client-cartera').innerHTML = `<i data-lucide="folder" class="w-4 h-4"></i> ${carteraNames[cliente.cartera || carteraActual]}`;
    
    // Actualizar datos de la deuda
    document.getElementById('debt-total-amount').textContent = `$${cliente.montoAdeudado.toLocaleString('es-AR')}`;
    document.getElementById('debt-due-date').textContent = cliente.fechaVencimiento;
    document.getElementById('debt-last-management').textContent = cliente.ultimaGestion;
    document.getElementById('debt-installments').innerHTML = `<span class="text-red-600">${cliente.cuotasPendientes}</span> / <span class="text-green-600">${cliente.cuotasPagadas}</span>`;
    document.getElementById('debt-entity').textContent = cliente.entidadFinanciera;
    document.getElementById('debt-notes').textContent = cliente.observaciones;
    
    // Actualizar resumen
    document.getElementById('summary-amount').textContent = `$${cliente.montoAdeudado.toLocaleString('es-AR')}`;
    document.getElementById('summary-days-overdue').textContent = `${cliente.diasMora} días`;
    
    // Actualizar estado
    const statusMap = {
        'sin-gestion': { text: 'Sin Gestión', class: 'status-sin-gestion' },
        'contactado': { text: 'Contactado', class: 'status-contactado' },
        'con-arreglo': { text: 'Con Arreglo', class: 'status-con-arreglo' },
        'incobrable': { text: 'Incobrable', class: 'status-incobrable' },
        'de-baja': { text: 'De Baja', class: 'status-de-baja' }
    };
    
    const statusInfo = statusMap[cliente.estado];
    document.getElementById('status-selector').value = cliente.estado;
    updateStatusBadge(cliente.estado);
    
    // Actualizar contador de clientes
    const total = clientesCarteraActual.length;
    const actual = indice + 1;
    document.getElementById('cliente-counter').textContent = `Cliente ${actual} de ${total}`;
    
    // Actualizar estado de botones de navegación
    const btnPrev = document.getElementById('btn-prev-cliente');
    const btnNext = document.getElementById('btn-next-cliente');
    btnPrev.disabled = total <= 1;
    btnNext.disabled = total <= 1;
    
    // Recargar iconos
    setTimeout(() => lucide.createIcons(), 100);
}

// Función para actualizar el selector de cartera
function updateCarteraSelector(cartera) {
    const carteraNames = {
        'favacard': '📁 Favacard',
        'naldo': '📁 Naldo',
        'naranjax': '📁 NaranjaX'
    };
    document.getElementById('cartera-selected-text').textContent = carteraNames[cartera];
}

// Función para abrir/cerrar el dropdown de carteras
function toggleCarteraDropdown() {
    const menu = document.getElementById('cartera-dropdown-menu');
    const chevron = document.getElementById('cartera-chevron');
    const isHidden = menu.classList.contains('hidden');
    
    if (isHidden) {
        menu.classList.remove('hidden');
        chevron.style.transform = 'rotate(180deg)';
    } else {
        menu.classList.add('hidden');
        chevron.style.transform = 'rotate(0deg)';
    }
}

// Función para seleccionar una cartera desde el dropdown
function selectCartera(cartera, displayText) {
    changeCartera(cartera);
    toggleCarteraDropdown(); // Cerrar el dropdown
}

// Función para actualizar el badge de estado visualmente
function updateStatusBadge(status) {
    const statusMap = {
        'sin-gestion': { text: 'Sin Gestión', class: 'status-sin-gestion' },
        'contactado': { text: 'Contactado', class: 'status-contactado' },
        'con-arreglo': { text: 'Con Arreglo', class: 'status-con-arreglo' },
        'incobrable': { text: 'Incobrable', class: 'status-incobrable' },
        'de-baja': { text: 'De Baja', class: 'status-de-baja' }
    };
    
    const display = document.getElementById('current-status-display');
    const summaryStatus = document.getElementById('summary-status');
    const statusInfo = statusMap[status];
    
    if (display) {
        display.innerHTML = `<span class="status-badge ${statusInfo.class}">${statusInfo.text}</span>`;
    }
    
    if (summaryStatus) {
        summaryStatus.innerHTML = `<span class="status-badge ${statusInfo.class}">${statusInfo.text}</span>`;
    }
}

// Función para guardar todo (estado + gestión si hay)
function saveAll() {
    // Esta función puede llamar a mÁºltiples endpoints HTMX o hacer un guardado general
    alert('Funcionalidad de guardado general - se implementará con backend');
}

// Manejar el envío del formulario de gestión
document.getElementById('management-form').addEventListener('htmx:afterRequest', function(event) {
    if (event.detail.successful) {
        // Limpiar el textarea después de guardar
        document.getElementById('management-note').value = '';
        // Recargar iconos después de actualizar el DOM
        setTimeout(() => lucide.createIcons(), 100);
    }
});

// Inicializar cuando carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Asignar cartera a cada cliente
    Object.keys(clientesDummy).forEach(cartera => {
        clientesDummy[cartera].forEach(cliente => {
            cliente.cartera = cartera;
        });
    });
    
    // Inicializar cartera actual
    clientesCarteraActual = getClientesCartera();
    
    // Cargar primer cliente de Favacard por defecto
    if (clientesCarteraActual.length > 0) {
        indiceClienteActual = 0;
        loadCliente(clientesCarteraActual[0], 0);
    }
    
    // Inicializar iconos
    lucide.createIcons();
    
    // Cerrar dropdown de carteras al hacer clic fuera
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('cartera-dropdown-menu');
        const button = document.getElementById('cartera-dropdown-btn');
        const chevron = document.getElementById('cartera-chevron');
        
        if (dropdown && !dropdown.contains(event.target) && !button.contains(event.target)) {
            dropdown.classList.add('hidden');
            if (chevron) {
                chevron.style.transform = 'rotate(0deg)';
            }
        }
    });
    
    // Navegación con teclado (flechas izquierda/derecha)
    document.addEventListener('keydown', function(event) {
        // No navegar si el usuario está escribiendo en un input o textarea
        const activeElement = document.activeElement;
        const isInputFocused = activeElement.tagName === 'INPUT' || 
                              activeElement.tagName === 'TEXTAREA' || 
                              activeElement.isContentEditable;
        
        // Si no hay un input enfocado, permitir navegación con flechas
        if (!isInputFocused) {
            if (event.key === 'ArrowLeft') {
                event.preventDefault();
                navegarCliente('prev');
            } else if (event.key === 'ArrowRight') {
                event.preventDefault();
                navegarCliente('next');
            }
        }
    });
});
