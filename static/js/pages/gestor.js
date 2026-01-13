// Dashboard Gestor - Integrado con APIs reales

// Variables globales
let clienteActual = null;
let carteraActual = null;  // Ahora será un objeto con id y nombre
let carteraActualId = null;  // ID de la cartera actual
let indiceClienteActual = 0;
let clientesCarteraActual = [];
let todosLosCasos = [];  // Todos los casos cargados desde la API
let isLoading = false;
let carterasDisponibles = [];  // Lista de carteras cargadas desde la API

// Función para calcular meses de mora desde fecha_ultimo_pago
function calcularMesesMora(fechaUltimoPago) {
    if (!fechaUltimoPago) {
        console.log('[DEBUG] calcularMesesMora: No hay fecha_ultimo_pago');
        return 0;
    }
    
    try {
        // La fecha viene en formato ISO string (ej: "2024-10-05")
        const fechaPago = new Date(fechaUltimoPago);
        const hoy = new Date();
        
        // Validar que la fecha sea válida
        if (isNaN(fechaPago.getTime())) {
            console.warn('[DEBUG] calcularMesesMora: Fecha inválida:', fechaUltimoPago);
            return 0;
        }
        
        // Calcular diferencia en meses
        const años = hoy.getFullYear() - fechaPago.getFullYear();
        const meses = hoy.getMonth() - fechaPago.getMonth();
        const dias = hoy.getDate() - fechaPago.getDate();
        
        let totalMeses = años * 12 + meses;
        
        // Si el día del mes actual es menor al día del último pago, restar un mes
        if (dias < 0) {
            totalMeses -= 1;
        }
        
        // Si la fecha de pago es en el futuro, retornar 0
        const resultado = totalMeses < 0 ? 0 : totalMeses;
        console.log(`[DEBUG] calcularMesesMora: ${fechaUltimoPago} -> ${resultado} meses`);
        return resultado;
    } catch (e) {
        console.error('[ERROR] calcularMesesMora:', e, 'Fecha:', fechaUltimoPago);
        return 0;
    }
}

// Función para convertir Case de la API a formato cliente del frontend
function mapCaseToCliente(caseData) {
    // Extraer información de contacto de las notas si está disponible (fallback)
    const notes = caseData.notes || '';
    const emailMatch = notes.match(/Email: ([^\n]+)/);
    
    // Obtener última actividad (se calculará dinámicamente desde el historial)
    let ultimaGestion = 'N/A';
    // Nota: La última gestión se calculará desde loadActivities cuando se cargue el historial
    
    // Mapear status_id a nombre de estado para el frontend
    let estadoNombre = 'Sin Arreglo';
    if (caseData.status_nombre) {
        estadoNombre = caseData.status_nombre;
    }
    
    // Mapear nombre de estado a código de estado del frontend
    // Este mapeo debe coincidir exactamente con el mapeo en loadCaseStatuses y en el backend
    const estadoMap = {
        'Sin Arreglo': 'sin-gestion',
        'En gestión': 'en-gestion',
        'Contactado': 'contactado',
        'Con Arreglo': 'con-arreglo',
        'Incobrable': 'incobrable',
        'A Juicio': 'a-juicio',
        'De baja': 'de-baja'
    };
    estado = estadoMap[estadoNombre] || 'sin-gestion';
    
    // Construir dirección (solo calle_nombre + calle_nro)
    let direccionCompleta = 'N/A';
    if (caseData.calle_nombre || caseData.calle_nro) {
        const partes = [];
        if (caseData.calle_nombre) {
            partes.push(caseData.calle_nombre);
        }
        if (caseData.calle_nro) {
            partes.push(caseData.calle_nro);
        }
        direccionCompleta = partes.join(' ');
    }
    
    // Formatear fecha último pago
    let fechaUltimoPagoFormateada = 'N/A';
    if (caseData.fecha_ultimo_pago) {
        try {
            const fecha = new Date(caseData.fecha_ultimo_pago);
            fechaUltimoPagoFormateada = fecha.toLocaleDateString('es-AR');
        } catch (e) {
            fechaUltimoPagoFormateada = caseData.fecha_ultimo_pago;
        }
    }
    
    // Calcular meses de mora
    const mesesMora = calcularMesesMora(caseData.fecha_ultimo_pago);
    
    // Calcular monto total con interés del 5% mensual
    const montoBase = parseFloat(caseData.total) || 0;
    const interesMensual = 0.05; // 5%
    const montoConInteres = montoBase * Math.pow(1 + interesMensual, mesesMora);
    
    return {
        id: caseData.id,
        nombre: `${caseData.name || ''} ${caseData.lastname || ''}`.trim() || 'N/A',
        dni: caseData.dni || 'N/A',
        numeroId: caseData.nro_cliente || `CASE-${caseData.id}`,  // Usar nro_cliente directamente
        telefono: caseData.telefono || 'N/A',  // Usar campo directo
        email: emailMatch ? emailMatch[1] : 'N/A',
        direccion: direccionCompleta,  // Solo calle_nombre + calle_nro
        localidad: caseData.localidad || 'N/A',
        provincia: caseData.provincia || 'N/A',
        cp: caseData.cp || 'N/A',
        fechaNacimiento: 'N/A',  // No está en el modelo Case
        montoBase: montoBase,  // Monto original sin interés (campo "total")
        montoInicial: parseFloat(caseData.monto_inicial) || 0,  // Monto inicial
        montoAdeudado: montoConInteres,  // Monto con interés aplicado
        fechaVencimiento: fechaUltimoPagoFormateada,  // Mostrar fecha último pago
        ultimaGestion: ultimaGestion,  // Se actualizará desde loadActivities
        cuotasPendientes: 0,  // No está en el modelo Case
        cuotasPagadas: 0,  // No está en el modelo Case
        observaciones: notes || 'Sin observaciones',
        estado: estado,
        estadoId: caseData.status_id || 1,
        estadoNombre: estadoNombre,
        mesesMora: mesesMora,  // Cambiar de diasMora a mesesMora
        clienteId: `#${caseData.id}`,
        cartera: caseData.cartera_nombre || caseData.cartera,
        carteraId: caseData.cartera_id,
        caseId: caseData.id  // Guardar ID del caso para actualizaciones
    };
}

// Función para cargar casos desde la API
async function loadCasosFromAPI() {
    if (isLoading) return;
    
    isLoading = true;
    try {
        const response = await fetch('/api/cases/gestor');
        const result = await response.json();
        
        if (result.success) {
            // Limpiar datos antiguos primero
            todosLosCasos = [];
            clientesCarteraActual = [];
            clienteActual = null;
            indiceClienteActual = 0;
            
            // Cargar nuevos datos
            todosLosCasos = result.data || [];
            console.log(`[OK] Cargados ${todosLosCasos.length} casos desde la API`);
            
            // Si no hay casos, mostrar mensaje y salir
            if (todosLosCasos.length === 0) {
                showNoCasesMessage();
                updateTotalCounter();
                return;
            }
            
            // Convertir a formato cliente
            const clientes = todosLosCasos.map(mapCaseToCliente);
            
            // Si no hay cartera seleccionada y hay casos, seleccionar la primera cartera con casos
            if (!carteraActualId && clientes.length > 0) {
                // Obtener la primera cartera que tenga casos
                const primeraCarteraConCasos = carterasDisponibles.find(c => 
                    clientes.some(cl => cl.cartera_id === c.id)
                );
                if (primeraCarteraConCasos) {
                    selectCartera(primeraCarteraConCasos.id, primeraCarteraConCasos.nombre);
                    return; // selectCartera ya actualiza todo
                }
            }
            
            // Actualizar lista de clientes según la cartera actual
            clientesCarteraActual = getClientesCartera();
            
            // Cargar primer cliente si hay
            if (clientesCarteraActual.length > 0) {
                indiceClienteActual = 0;
                loadCliente(clientesCarteraActual[0], 0);
            } else {
                // Mostrar mensaje de que no hay casos
                showNoCasesMessage();
            }
            
            // Actualizar contador total
            updateTotalCounter();
        } else {
            console.error('[ERROR] Error cargando casos:', result.error);
            showErrorMessage('Error al cargar casos: ' + result.error);
            // Limpiar datos en caso de error
            todosLosCasos = [];
            clientesCarteraActual = [];
            clienteActual = null;
            showNoCasesMessage();
        }
    } catch (error) {
        console.error('[ERROR] Error en fetch:', error);
        showErrorMessage('Error de conexión al cargar casos');
        // Limpiar datos en caso de error
        todosLosCasos = [];
        clientesCarteraActual = [];
        clienteActual = null;
        showNoCasesMessage();
    } finally {
        isLoading = false;
    }
}

// Función para obtener lista de clientes de la cartera actual
function getClientesCartera() {
    if (!todosLosCasos || todosLosCasos.length === 0) {
        return [];
    }
    
    // Filtrar por cartera actual usando cartera_id
    return todosLosCasos
        .filter(c => c.cartera_id === carteraActualId)
        .map(mapCaseToCliente);
}

// Función para cargar estados de casos desde la API
async function loadCaseStatuses() {
    try {
        const response = await fetch('/api/case-statuses');
        if (!response.ok) {
            throw new Error('Error al cargar estados');
        }
        const statuses = await response.json();
        
        const statusSelector = document.getElementById('status-selector');
        if (!statusSelector) return;
        
        // Limpiar opciones existentes
        statusSelector.innerHTML = '<option value="">Seleccionar estado...</option>';
        
        // Mapeo de nombres de estados de BD a valores del selector
        const statusValueMap = {
            'Sin Arreglo': 'sin-gestion',
            'En gestión': 'en-gestion',
            'Incobrable': 'incobrable',
            'Contactado': 'contactado',
            'Con Arreglo': 'con-arreglo',
            'A Juicio': 'a-juicio',
            'De baja': 'de-baja'
        };
        
        // Agregar opciones
        statuses.forEach(status => {
            const option = document.createElement('option');
            const value = statusValueMap[status.nombre] || status.nombre.toLowerCase().replace(/\s+/g, '-');
            option.value = value;
            option.textContent = status.nombre;
            statusSelector.appendChild(option);
        });
        
        console.log(`[OK] Cargados ${statuses.length} estados desde la API`);
    } catch (error) {
        console.error('Error cargando estados:', error);
        const statusSelector = document.getElementById('status-selector');
        if (statusSelector) {
            statusSelector.innerHTML = '<option value="">Error al cargar estados</option>';
        }
    }
}

// Función para cargar carteras desde la API
async function loadCarteras() {
    try {
        const response = await fetch('/api/carteras');
        if (!response.ok) {
            throw new Error('Error al cargar carteras');
        }
        carterasDisponibles = await response.json();
        
        // Renderizar dropdown
        renderCarteraDropdown(carterasDisponibles);
        
        // Si no hay cartera seleccionada, seleccionar la primera
        if (!carteraActualId && carterasDisponibles.length > 0) {
            const primeraCartera = carterasDisponibles[0];
            selectCartera(primeraCartera.id, primeraCartera.nombre);
        }
    } catch (error) {
        console.error('Error cargando carteras:', error);
        // Fallback: mostrar mensaje de error
        const content = document.getElementById('cartera-dropdown-content');
        if (content) {
            content.innerHTML = '<div class="px-4 py-2 text-sm text-red-500">Error al cargar carteras</div>';
        }
    }
}

// Función para renderizar el dropdown de carteras
function renderCarteraDropdown(carteras) {
    const content = document.getElementById('cartera-dropdown-content');
    if (!content) return;
    
    if (carteras.length === 0) {
        content.innerHTML = '<div class="px-4 py-2 text-sm text-gray-500">No hay carteras disponibles</div>';
        return;
    }
    
    content.innerHTML = carteras.map(cartera => `
        <button 
            onclick="selectCartera(${cartera.id}, '📁 ${cartera.nombre}')"
            class="w-full text-left px-4 py-2 text-sm font-semibold text-purple-600 hover:bg-purple-50 transition-colors"
        >
            📁 ${cartera.nombre}
        </button>
    `).join('');
}

// Función para cambiar de cartera y cargar primer cliente
function changeCartera(carteraId) {
    carteraActualId = carteraId;
    const cartera = carterasDisponibles.find(c => c.id === carteraId);
    carteraActual = cartera ? cartera.nombre : null;
    
    clientesCarteraActual = getClientesCartera();
    
    if (clientesCarteraActual.length > 0) {
        indiceClienteActual = 0;
        loadCliente(clientesCarteraActual[0], 0);
        updateCarteraSelector(carteraId, cartera ? cartera.nombre : null);
        limpiarBusqueda();
    } else {
        showNoCasesMessage();
    }
}

// Función para navegar entre clientes (GLOBAL - usada por onclick en HTML)
window.navegarCliente = function(direccion) {
    clientesCarteraActual = getClientesCartera();
    if (clientesCarteraActual.length === 0) return;

    if (direccion === 'prev') {
        indiceClienteActual = indiceClienteActual > 0 ? indiceClienteActual - 1 : clientesCarteraActual.length - 1;
    } else {
        indiceClienteActual = indiceClienteActual < clientesCarteraActual.length - 1 ? indiceClienteActual + 1 : 0;
    }

    loadCliente(clientesCarteraActual[indiceClienteActual], indiceClienteActual);
}

// Función para ir a un número de cliente específico (GLOBAL - usada por onclick en HTML)
window.irACliente = function() {
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

    // Limpiar búsqueda si existe
    document.getElementById('search-input').value = '';
    document.getElementById('btn-clear-search').style.display = 'none';

    // Los números de cliente van de 1 a N, pero el índice es 0 a N-1
    indiceClienteActual = numeroCliente - 1;
    loadCliente(clientesCarteraActual[indiceClienteActual], indiceClienteActual);
    
    // Limpiar el input
    input.value = '';
    input.blur();
}

// Función para buscar cliente (GLOBAL - usada por onkeyup en HTML)
window.buscarCliente = function(busqueda) {
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

// Función para limpiar búsqueda (GLOBAL - usada por onclick en HTML)
window.limpiarBusqueda = function() {
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
    const nameHeader = document.getElementById('client-name-header');
    const idHeader = document.getElementById('client-id-header');
    const dniHeader = document.getElementById('client-dni-header');
    const numeroIdHeader = document.getElementById('client-numero-id-header');
    
    if (nameHeader) nameHeader.textContent = cliente.nombre;
    if (idHeader) idHeader.textContent = cliente.clienteId;
    if (dniHeader) dniHeader.textContent = cliente.dni;
    if (numeroIdHeader) numeroIdHeader.textContent = cliente.numeroId;
    
    // Actualizar datos del cliente
    const nameEl = document.getElementById('client-name');
    const dniEl = document.getElementById('client-dni');
    const numeroIdEl = document.getElementById('client-numero-id');
    const phoneEl = document.getElementById('client-phone');
    const emailEl = document.getElementById('client-email');
    const addressEl = document.getElementById('client-address');
    const birthdateEl = document.getElementById('client-birthdate');
    
    if (nameEl) nameEl.textContent = cliente.nombre;
    if (dniEl) dniEl.textContent = cliente.dni;
    if (numeroIdEl) numeroIdEl.textContent = cliente.numeroId;
    if (phoneEl) phoneEl.innerHTML = `<i data-lucide="phone" class="w-4 h-4 text-gray-400"></i> ${cliente.telefono || 'N/A'}`;
    if (emailEl) emailEl.innerHTML = `<i data-lucide="mail" class="w-4 h-4 text-gray-400"></i> ${cliente.email || 'N/A'}`;
    
    // Actualizar dirección (solo calle_nombre + calle_nro)
    const addressTextEl = document.getElementById('client-address-text');
    if (addressTextEl) {
        addressTextEl.textContent = cliente.direccion || 'N/A';
    } else if (addressEl) {
        addressEl.innerHTML = `<i data-lucide="map-pin" class="w-4 h-4 text-gray-400"></i> ${cliente.direccion || 'N/A'}`;
    }
    
    // Actualizar localidad, provincia y CP
    const localidadEl = document.getElementById('client-localidad');
    const provinciaEl = document.getElementById('client-provincia');
    const cpEl = document.getElementById('client-cp');
    if (localidadEl) localidadEl.textContent = cliente.localidad || 'N/A';
    if (provinciaEl) provinciaEl.textContent = cliente.provincia || 'N/A';
    if (cpEl) cpEl.textContent = cliente.cp || 'N/A';
    
    if (birthdateEl) birthdateEl.textContent = cliente.fechaNacimiento;
    
    // Actualizar cartera
    const carteraEl = document.getElementById('client-cartera');
    if (carteraEl) {
        carteraEl.innerHTML = `<i data-lucide="folder" class="w-4 h-4"></i> ${cliente.cartera || 'Sin cartera'}`;
    }
    
    // Actualizar datos de la deuda
    const debtAmountEl = document.getElementById('debt-total-amount');
    const debtDueDateEl = document.getElementById('debt-due-date');
    const debtLastMgmtEl = document.getElementById('debt-last-management');
    const debtInstallmentsEl = document.getElementById('debt-installments');
    const debtEntityEl = document.getElementById('debt-entity');
    const debtNotesEl = document.getElementById('debt-notes');
    
    // Monto con interés aplicado (5% mensual según meses de mora)
    if (debtAmountEl) debtAmountEl.textContent = `$${cliente.montoAdeudado.toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    if (debtDueDateEl) debtDueDateEl.textContent = cliente.fechaVencimiento;
    if (debtLastMgmtEl) debtLastMgmtEl.textContent = cliente.ultimaGestion;
    if (debtInstallmentsEl) debtInstallmentsEl.innerHTML = `<span class="text-red-600">${cliente.cuotasPendientes}</span> / <span class="text-green-600">${cliente.cuotasPagadas}</span>`;
    if (debtEntityEl) debtEntityEl.textContent = cliente.entidadFinanciera;
    if (debtNotesEl) debtNotesEl.textContent = cliente.observaciones;
    
    // Actualizar resumen
    const summaryMontoInicialEl = document.getElementById('summary-monto-inicial');
    const summaryMontoAdeudadoEl = document.getElementById('summary-monto-adeudado');
    const summaryDaysEl = document.getElementById('summary-days-overdue');
    
    if (summaryMontoInicialEl) {
        summaryMontoInicialEl.textContent = `$${(cliente.montoInicial || 0).toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    }
    if (summaryMontoAdeudadoEl) {
        summaryMontoAdeudadoEl.textContent = `$${(cliente.montoBase || 0).toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    }
    
    // Actualizar calculadora de intereses
    const calcMontoTotalEl = document.getElementById('calc-monto-total');
    if (calcMontoTotalEl) {
        // Formatear a 2 decimales
        const montoFormateado = (cliente.montoAdeudado || 0).toFixed(2);
        calcMontoTotalEl.value = montoFormateado;
        calcularIntereses();
    }
    if (summaryDaysEl) {
        const meses = cliente.mesesMora || 0;
        summaryDaysEl.textContent = `${meses} ${meses === 1 ? 'mes' : 'meses'}`;
    }
    
    // Actualizar case_id en formularios - CRÍTICO: debe actualizarse siempre
    const currentCaseIdEl = document.getElementById('current-case-id');
    const managementCaseIdEl = document.getElementById('management-case-id');
    const caseIdValue = String(cliente.caseId || cliente.id || '');
    
    console.log(`[DEBUG] loadCliente - Cliente: ${cliente.nombre}, caseId: ${cliente.caseId}, id: ${cliente.id}, estado: ${cliente.estado}`);
    
    if (currentCaseIdEl) {
        currentCaseIdEl.value = caseIdValue;
        console.log(`[DEBUG] ✓ Actualizado current-case-id: "${caseIdValue}" para cliente: ${cliente.nombre}`);
    } else {
        console.error('[ERROR] ✗ No se encontró elemento current-case-id en el DOM');
    }
    
    if (managementCaseIdEl) {
        managementCaseIdEl.value = caseIdValue;
        console.log(`[DEBUG] ✓ Actualizado management-case-id: "${caseIdValue}"`);
    } else {
        console.warn('[WARN] No se encontró elemento management-case-id (puede ser normal)');
    }
    
    // Actualizar estado del selector - debe reflejar el estado real del caso
    const statusMap = {
        'sin-gestion': { text: 'Sin Arreglo', class: 'status-sin-gestion' },
        'en-gestion': { text: 'En gestión', class: 'status-en-gestion' },
        'contactado': { text: 'Contactado', class: 'status-contactado' },
        'con-arreglo': { text: 'Con Arreglo', class: 'status-con-arreglo' },
        'incobrable': { text: 'Incobrable', class: 'status-incobrable' },
        'a-juicio': { text: 'A Juicio', class: 'status-a-juicio' },
        'de-baja': { text: 'De baja', class: 'status-de-baja' },
        'pagada': { text: 'Pagada', class: 'status-pagada' }
    };
    
    const statusInfo = statusMap[cliente.estado] || statusMap['sin-gestion'];
    const statusSelectorEl = document.getElementById('status-selector');
    if (statusSelectorEl) {
        // Asegurar que el selector muestre el estado correcto
        statusSelectorEl.value = cliente.estado;
        console.log(`[DEBUG] Estado del selector actualizado a: ${cliente.estado} para caso ${cliente.caseId || cliente.id}`);
        
        // Remover event listener anterior si existe
        const newSelector = statusSelectorEl.cloneNode(true);
        statusSelectorEl.parentNode.replaceChild(newSelector, statusSelectorEl);
        
        // Agregar event listener para guardar cambios
        newSelector.addEventListener('change', async function(e) {
            const newStatus = e.target.value;
            const caseId = document.getElementById('current-case-id')?.value;
            
            console.log(`[DEBUG] Cambiando estado de caso ${caseId} a: ${newStatus}`);
            
            if (!caseId) {
                console.error('[ERROR] No hay case_id');
                alert('Error: No se puede cambiar el estado sin un cliente seleccionado.');
                e.target.value = cliente.estado; // Restaurar
                return;
            }
            
            // Mostrar loading
            const loadingEl = document.getElementById('status-loading');
            if (loadingEl) loadingEl.style.display = 'flex';
            
            try {
                const formData = new FormData();
                formData.append('case_id', caseId);
                formData.append('status-selector', newStatus);
                
                const response = await fetch('/api/update-status', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    console.log('[OK] Estado actualizado en BD');
                    updateStatusBadge(newStatus);
                    
                    // Actualizar el clienteActual inmediatamente
                    if (clienteActual) {
                        clienteActual.estado = newStatus;
                        console.log(`[DEBUG] clienteActual.estado actualizado a: ${newStatus}`);
                    }
                    
                    // Actualizar en todosLosCasos inmediatamente
                    const caseIndex = todosLosCasos.findIndex(c => c.id === caseId);
                    if (caseIndex !== -1) {
                        // Actualizar status_id basado en el nuevo estado
                        // Esto se actualizará cuando se guarde en el servidor
                        console.log(`[DEBUG] todosLosCasos[${caseIndex}] actualizado con nuevo estado`);
                    }
                    
                    // Actualizar en clientesCarteraActual inmediatamente
                    const clienteIndex = clientesCarteraActual.findIndex(c => c.caseId == caseId);
                    if (clienteIndex !== -1) {
                        clientesCarteraActual[clienteIndex].estado = newStatus;
                        console.log(`[DEBUG] clientesCarteraActual[${clienteIndex}].estado actualizado`);
                    }
                    
                    // Recargar el caso para confirmar (esto actualizará los arrays de nuevo con datos frescos de la BD)
                    setTimeout(() => reloadCurrentCase(), 500);
                } else {
                    console.error('[ERROR] Error actualizando estado:', await response.text());
                    alert('Error al guardar el estado');
                    e.target.value = cliente.estado; // Restaurar
                }
            } catch (error) {
                console.error('[ERROR] Error en petición:', error);
                alert('Error al guardar el estado');
                e.target.value = cliente.estado; // Restaurar
            } finally {
                // Ocultar loading
                if (loadingEl) loadingEl.style.display = 'none';
            }
        });
    }
    updateStatusBadge(cliente.estado);
    
    // Cargar gestiones del cliente
    if (cliente.caseId) {
        loadActivities(cliente.caseId);
    }
    
    // Actualizar contador de clientes
    const total = clientesCarteraActual.length;
    const actual = indice + 1;
    const counterEl = document.getElementById('cliente-counter');
    if (counterEl) {
        counterEl.textContent = `Cliente ${actual} de ${total}`;
    }
    
    // Actualizar estado de botones de navegación
    const btnPrev = document.getElementById('btn-prev-cliente');
    const btnNext = document.getElementById('btn-next-cliente');
    if (btnPrev) btnPrev.disabled = total <= 1;
    if (btnNext) btnNext.disabled = total <= 1;
    
    // Recargar iconos
    setTimeout(() => {
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
            lucide.createIcons();
        }
    }, 100);
}

// Función para actualizar el selector de cartera
function updateCarteraSelector(carteraId, carteraNombre) {
    const selectedTextEl = document.getElementById('cartera-selected-text');
    if (selectedTextEl && carteraNombre) {
        selectedTextEl.textContent = `📁 ${carteraNombre}`;
    }
}

// Función para abrir/cerrar el dropdown de carteras
// Función para toggle del dropdown de cartera (GLOBAL - usada por onclick en HTML)
window.toggleCarteraDropdown = function() {
    const menu = document.getElementById('cartera-dropdown-menu');
    const chevron = document.getElementById('cartera-chevron');
    if (!menu || !chevron) return;
    
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
// Función para seleccionar cartera (GLOBAL - usada por onclick en HTML)
window.selectCartera = function(carteraId, displayText) {
    changeCartera(carteraId);
    toggleCarteraDropdown(); // Cerrar el dropdown
}

// Función para actualizar el badge de estado visualmente
// Función para actualizar el badge de estado (GLOBAL - usada por onchange en HTML)
window.updateStatusBadge = function(status) {
    const statusMap = {
        'sin-gestion': { text: 'Sin Arreglo', class: 'status-sin-gestion' },
        'en-gestion': { text: 'En gestión', class: 'status-en-gestion' },
        'contactado': { text: 'Contactado', class: 'status-contactado' },
        'con-arreglo': { text: 'Con Arreglo', class: 'status-con-arreglo' },
        'incobrable': { text: 'Incobrable', class: 'status-incobrable' },
        'a-juicio': { text: 'A Juicio', class: 'status-a-juicio' },
        'de-baja': { text: 'De baja', class: 'status-de-baja' }
    };
    
    const display = document.getElementById('current-status-display');
    const statusInfo = statusMap[status] || statusMap['sin-gestion'];
    
    if (display) {
        display.innerHTML = `<span class="status-badge ${statusInfo.class}">${statusInfo.text}</span>`;
    }
}

// Función para recargar el caso actual desde la API (definida globalmente)
async function reloadCurrentCase() {
    if (!clienteActual || !clienteActual.caseId) {
        console.log('[WARN] No hay caso seleccionado para recargar');
        return;
    }
    
    try {
        const response = await fetch(`/api/cases/${clienteActual.caseId}`);
        const result = await response.json();
        
        if (result.success) {
            // Actualizar el caso en todosLosCasos (array en memoria)
            const caseIndex = todosLosCasos.findIndex(c => c.id === result.data.id);
            if (caseIndex !== -1) {
                todosLosCasos[caseIndex] = result.data;
                console.log(`[DEBUG] Actualizado caso en todosLosCasos[${caseIndex}]`);
            }
            
            // Actualizar el cliente actual con datos frescos
            const updatedCliente = mapCaseToCliente(result.data);
            clienteActual = updatedCliente;
            
            // Actualizar también en clientesCarteraActual
            const clienteIndex = clientesCarteraActual.findIndex(c => c.caseId === updatedCliente.caseId);
            if (clienteIndex !== -1) {
                clientesCarteraActual[clienteIndex] = updatedCliente;
                console.log(`[DEBUG] Actualizado cliente en clientesCarteraActual[${clienteIndex}]`);
            }
            
            // Actualizar el selector de estado
            const statusSelector = document.getElementById('status-selector');
            if (statusSelector) {
                statusSelector.value = updatedCliente.estado;
            }
            updateStatusBadge(updatedCliente.estado);
            
            // Actualizar case_id en formularios
            const currentCaseIdEl = document.getElementById('current-case-id');
            const managementCaseIdEl = document.getElementById('management-case-id');
            if (currentCaseIdEl) currentCaseIdEl.value = updatedCliente.caseId || '';
            if (managementCaseIdEl) managementCaseIdEl.value = updatedCliente.caseId || '';
            
            console.log(`[OK] Caso ${updatedCliente.caseId} recargado y actualizado en memoria, estado: ${updatedCliente.estado}`);
        }
    } catch (error) {
        console.error('[ERROR] Error recargando caso:', error);
    }
}

// Función para actualizar estado y guardar en BD (ya no se usa directamente, HTMX lo maneja)
async function updateStatusAndSave(status) {
    // Esta función ya no es necesaria porque HTMX maneja el POST
    // Pero la mantenemos por compatibilidad
    console.log('[INFO] Estado actualizado por HTMX, recargando caso...');
    setTimeout(() => {
        reloadCurrentCase();
    }, 500);
}

// Función para cargar gestiones de un caso
async function loadActivities(caseId) {
    if (!caseId) {
        console.warn('[WARN] No hay case_id para cargar gestiones');
        return;
    }
    
    try {
        const response = await fetch(`/api/activities/case/${caseId}`);
        const result = await response.json();
        
        if (result.success) {
            const activities = result.data;
            console.log(`[OK] Cargadas ${activities.length} gestiones para caso ${caseId}`);
            
            const historyContainer = document.getElementById('management-history');
            if (!historyContainer) return;
            
            if (activities.length === 0) {
                historyContainer.innerHTML = `
                    <div class="text-center py-8 text-gray-500">
                        <i data-lucide="inbox" class="w-12 h-12 mx-auto mb-2 opacity-50"></i>
                        <p>No hay gestiones registradas para este cliente</p>
                    </div>
                `;
                if (typeof lucide !== 'undefined' && lucide.createIcons) {
                    lucide.createIcons();
                }
                // Actualizar "Última Gestión" a "N/A" si no hay gestiones
                const summaryLastManagementEl = document.getElementById('summary-last-management');
                if (summaryLastManagementEl) {
                    summaryLastManagementEl.textContent = 'N/A';
                }
                return;
            }
            
            // Renderizar gestiones
            historyContainer.innerHTML = activities.map(activity => {
                const date = new Date(activity.created_at);
                const formattedDate = date.toLocaleDateString('es-AR') + ' - ' + date.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
                const borderColor = getBorderColorForActivity(activity.type);
                
                return `
                    <div class="border-l-4 ${borderColor} pl-4 pb-4" id="activity-${activity.id}">
                        <div class="flex items-start justify-between mb-2">
                            <div class="flex items-center gap-2">
                                <i data-lucide="user" class="w-4 h-4 text-gray-400"></i>
                                <span class="text-sm font-semibold text-gray-900">${activity.created_by || 'Usuario'}</span>
                            </div>
                            <div class="flex items-center gap-2">
                                <span class="text-xs text-gray-500">${formattedDate}</span>
                                <button 
                                    onclick="deleteActivity(${activity.id})"
                                    class="text-red-500 hover:text-red-700 transition-colors"
                                    title="Eliminar gestión">
                                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                                </button>
                            </div>
                        </div>
                        <p class="text-sm text-gray-700 leading-relaxed">${activity.notes || 'Sin notas'}</p>
                    </div>
                `;
            }).join('');
            
            // Reinicializar iconos de Lucide
            if (typeof lucide !== 'undefined' && lucide.createIcons) {
                lucide.createIcons();
            }
            
            // Actualizar "Última Gestión" en el resumen con la gestión más reciente
            const lastActivity = activities[0]; // Ya están ordenadas por fecha descendente
            const lastDate = new Date(lastActivity.created_at);
            const now = new Date();
            const diffTime = Math.abs(now - lastDate);
            const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
            
            let ultimaGestionTexto = 'N/A';
            if (diffDays === 0) {
                ultimaGestionTexto = 'Hoy';
            } else if (diffDays === 1) {
                ultimaGestionTexto = 'Hace 1 día';
            } else {
                ultimaGestionTexto = `Hace ${diffDays} días`;
            }
            
            const summaryLastManagementEl = document.getElementById('summary-last-management');
            if (summaryLastManagementEl) {
                summaryLastManagementEl.textContent = ultimaGestionTexto;
            }
        } else {
            console.error('[ERROR] Error cargando gestiones:', result.error);
            // Si hay error, mostrar "N/A"
            const summaryLastManagementEl = document.getElementById('summary-last-management');
            if (summaryLastManagementEl) {
                summaryLastManagementEl.textContent = 'N/A';
            }
        }
    } catch (error) {
        console.error('[ERROR] Error en loadActivities:', error);
        // Si hay error, mostrar "N/A"
        const summaryLastManagementEl = document.getElementById('summary-last-management');
        if (summaryLastManagementEl) {
            summaryLastManagementEl.textContent = 'N/A';
        }
    }
}

// Función auxiliar para obtener color de borde según tipo de actividad
function getBorderColorForActivity(type) {
    const colors = {
        'call': 'border-blue-500',
        'email': 'border-purple-500',
        'visit': 'border-green-500',
        'note': 'border-gray-500',
        'payment': 'border-emerald-500',
        'promise': 'border-yellow-500'
    };
    return colors[type] || 'border-gray-500';
}

// Función para eliminar una gestión (GLOBAL - usada por onclick en HTML)
window.deleteActivity = async function(activityId) {
    if (!confirm('¿Estás seguro de que deseas eliminar esta gestión?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/activities/${activityId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`[OK] Gestión ${activityId} eliminada`);
            
            // Remover del DOM
            const activityElement = document.getElementById(`activity-${activityId}`);
            if (activityElement) {
                activityElement.remove();
            }
            
            // Verificar si no quedan gestiones
            const historyContainer = document.getElementById('management-history');
            if (historyContainer && historyContainer.children.length === 0) {
                historyContainer.innerHTML = `
                    <div class="text-center py-8 text-gray-500">
                        <i data-lucide="inbox" class="w-12 h-12 mx-auto mb-2 opacity-50"></i>
                        <p>No hay gestiones registradas para este cliente</p>
                    </div>
                `;
                if (typeof lucide !== 'undefined' && lucide.createIcons) {
                    lucide.createIcons();
                }
            }
        } else {
            alert('Error al eliminar la gestión: ' + result.error);
        }
    } catch (error) {
        console.error('[ERROR] Error eliminando gestión:', error);
        alert('Error al eliminar la gestión');
    }
};

// Función para mostrar mensaje cuando no hay casos
function showNoCasesMessage() {
    // Limpiar cualquier cliente mostrado
    clienteActual = null;
    
    // Remover mensaje anterior si existe
    const existingMessage = document.getElementById('no-cases-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Limpiar el contenido del cliente
    const nameHeader = document.getElementById('client-name-header');
    const idHeader = document.getElementById('client-id-header');
    if (nameHeader) nameHeader.textContent = 'Sin casos';
    if (idHeader) idHeader.textContent = '';
    
    const mainContent = document.querySelector('.main-content') || document.body;
    const message = document.createElement('div');
    message.id = 'no-cases-message';
    message.className = 'p-8 text-center';
    message.innerHTML = `
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <p class="text-yellow-800 font-semibold">No hay casos asignados en esta cartera</p>
            <p class="text-yellow-600 text-sm mt-2">Los casos aparecerán aquí cuando te sean asignados</p>
        </div>
    `;
    mainContent.appendChild(message);
}

// Función para mostrar mensaje de error
function showErrorMessage(message) {
    console.error(message);
    // Puedes implementar un toast o alert aquí
}

// Función para actualizar contador total
function updateTotalCounter() {
    const total = todosLosCasos.length;
    // Actualizar algún elemento del DOM si existe
    console.log(`Total de casos: ${total}`);
}

// Ya no necesitamos este listener porque lo manejamos en el DOMContentLoaded
// con htmx:afterSwap que es más específico y no recarga todos los casos

// Inicializar cuando carga la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('[INFO] Inicializando dashboard de gestor...');
    
    // Listener para limpiar formulario después de guardar gestión
    document.body.addEventListener('htmx:afterSwap', function(event) {
        if (event.detail.target.id === 'management-history') {
            console.log('[DEBUG] Gestión guardada, limpiando formulario...');
            const form = document.getElementById('management-form');
            if (form) {
                form.reset();
                // Mantener el case_id en el formulario
                const managementCaseIdEl = document.getElementById('management-case-id');
                if (managementCaseIdEl && clienteActual && clienteActual.caseId) {
                    managementCaseIdEl.value = clienteActual.caseId;
                }
            }
            
            // NO recargar gestiones porque HTMX ya las agregó
            // Solo reinicializar los iconos de Lucide
            setTimeout(() => {
                if (typeof lucide !== 'undefined' && lucide.createIcons) {
                    lucide.createIcons();
                }
            }, 100);
        }
    });
    
    // Cargar estados, carteras y casos
    loadCaseStatuses().then(() => {
        return loadCarteras();
    }).then(() => {
        // Cargar casos desde la API después de que las carteras estén disponibles
        loadCasosFromAPI();
    });
    
    // Inicializar iconos
    setTimeout(() => {
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
            lucide.createIcons();
        }
    }, 500);
    
    // Cerrar dropdown de carteras al hacer clic fuera
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('cartera-dropdown-menu');
        const button = document.getElementById('cartera-dropdown-btn');
        const chevron = document.getElementById('cartera-chevron');
        
        if (dropdown && button && !dropdown.contains(event.target) && !button.contains(event.target)) {
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
    
    // Ya no necesitamos reconnectStatusSelector porque ahora el listener se agrega en loadCliente
    
    // Ya no usamos HTMX para actualizar el estado, lo hacemos con fetch directamente
});

// Función para calcular intereses (GLOBAL - usada por oninput en HTML)
window.calcularIntereses = function() {
    const montoTotalEl = document.getElementById('calc-monto-total');
    const interesMensualEl = document.getElementById('calc-interes-mensual');
    const cantidadCuotasEl = document.getElementById('calc-cantidad-cuotas');
    const totalAbonarEl = document.getElementById('calc-total-abonar');
    const montoCuotaEl = document.getElementById('calc-monto-cuota');
    
    if (!montoTotalEl || !interesMensualEl || !cantidadCuotasEl || !totalAbonarEl || !montoCuotaEl) {
        return;
    }
    
    const montoTotal = parseFloat(montoTotalEl.value) || 0;
    const interesMensual = parseFloat(interesMensualEl.value) || 0;
    const cantidadCuotas = parseInt(cantidadCuotasEl.value) || 1;
    
    if (montoTotal <= 0) {
        totalAbonarEl.textContent = '$0.00';
        montoCuotaEl.textContent = '$0.00';
        return;
    }
    
    // Calcular total a abonar: monto * (1 + interés/100) ^ cantidad_cuotas
    const interesDecimal = interesMensual / 100;
    const totalAbonar = montoTotal * Math.pow(1 + interesDecimal, cantidadCuotas);
    
    // Calcular monto por cuota
    const montoCuota = totalAbonar / cantidadCuotas;
    
    // Formatear y mostrar resultados
    totalAbonarEl.textContent = `$${totalAbonar.toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    montoCuotaEl.textContent = `$${montoCuota.toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
};
