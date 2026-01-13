// Dashboard Gestor - Integrado con APIs reales

// Variables globales
let clienteActual = null;  // Cliente actual (datos del cliente)
let deudaActual = null;  // Deuda actual (caso específico)
let grupoClienteActual = null;  // Grupo actual (cliente + todas sus deudas)
let carteraActual = null;  // Ahora será un objeto con id y nombre
let carteraActualId = null;  // ID de la cartera actual
let indiceGrupoActual = 0;  // Índice del grupo actual (cliente)
let indiceDeudaActual = 0;  // Índice de la deuda actual dentro del grupo
let gruposCarteraActual = [];  // Grupos de clientes (agrupados por DNI) de la cartera actual
let todosLosGrupos = [];  // Todos los grupos cargados desde la API
let isLoading = false;
let carterasDisponibles = [];  // Lista de carteras cargadas desde la API

// Función para calcular meses de mora desde fecha_ultimo_pago
function calcularMesesMora(fechaUltimoPago) {
    if (!fechaUltimoPago) {
        console.log('[DEBUG] calcularMesesMora: No hay fecha_ultimo_pago');
        return 0;
    }
    
    try {
        // Parsear fecha manualmente para evitar problemas de zona horaria
        let fechaPago;
        if (typeof fechaUltimoPago === 'string' && fechaUltimoPago.match(/^\d{4}-\d{2}-\d{2}/)) {
            // Formato ISO: YYYY-MM-DD
            const partes = fechaUltimoPago.split('T')[0].split('-');
            const año = parseInt(partes[0], 10);
            const mes = parseInt(partes[1], 10) - 1; // Mes es 0-indexed en JS
            const dia = parseInt(partes[2], 10);
            // Crear fecha en hora local (no UTC) para evitar problemas de zona horaria
            fechaPago = new Date(año, mes, dia);
        } else {
            fechaPago = new Date(fechaUltimoPago);
        }
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
    // IMPORTANTE: Parsear la fecha manualmente para evitar problemas de zona horaria
    // La BD tiene formato YYYY-MM-DD y debe mostrarse como DD-MM-YYYY
    let fechaUltimoPagoFormateada = 'N/A';
    if (caseData.fecha_ultimo_pago) {
        try {
            const fechaStr = String(caseData.fecha_ultimo_pago).trim();
            
            // Detectar formato YYYY-MM-DD (puede tener 1 o 2 dígitos en mes/día)
            // Ejemplos: "2024-10-05", "2024-10-5", "2024-1-5"
            const isoMatch = fechaStr.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
            if (isoMatch) {
                // Formato ISO: YYYY-MM-DD
                const año = parseInt(isoMatch[1], 10);
                const mes = parseInt(isoMatch[2], 10); // Mes (1-12)
                const dia = parseInt(isoMatch[3], 10);
                
                // Validar que los valores sean correctos
                if (año > 0 && mes >= 1 && mes <= 12 && dia >= 1 && dia <= 31) {
                    // Formatear manualmente como DD-MM-YYYY
                    fechaUltimoPagoFormateada = `${dia.toString().padStart(2, '0')}-${mes.toString().padStart(2, '0')}-${año}`;
                    console.log(`[DEBUG] Fecha formateada: ${fechaStr} -> ${fechaUltimoPagoFormateada}`);
                } else {
                    console.warn(`[WARN] Fecha inválida: ${fechaStr} (año=${año}, mes=${mes}, dia=${dia})`);
                    fechaUltimoPagoFormateada = fechaStr;
                }
            } else {
                // Si no es formato ISO, intentar parsear con Date
                const fecha = new Date(fechaStr);
                if (!isNaN(fecha.getTime())) {
                    // Formatear manualmente como DD-MM-YYYY
                    const dia = fecha.getDate();
                    const mes = fecha.getMonth() + 1; // getMonth() retorna 0-11
                    const año = fecha.getFullYear();
                    fechaUltimoPagoFormateada = `${dia.toString().padStart(2, '0')}-${mes.toString().padStart(2, '0')}-${año}`;
                } else {
                    console.warn(`[WARN] No se pudo parsear fecha: ${fechaStr}`);
                    fechaUltimoPagoFormateada = fechaStr;
                }
            }
        } catch (e) {
            console.error('[ERROR] Error formateando fecha_ultimo_pago:', e, caseData.fecha_ultimo_pago);
            fechaUltimoPagoFormateada = caseData.fecha_ultimo_pago;
        }
    }
    
    // Calcular meses de mora
    const mesesMora = calcularMesesMora(caseData.fecha_ultimo_pago);
    
    // Calcular monto total con interés simple del 5% mensual
    // Fórmula: monto * (1 + 0.05 * meses_mora) = monto + (monto * 0.05 * meses_mora)
    const montoBase = parseFloat(caseData.total) || 0;
    const interesMensual = 0.05; // 5%
    const montoConInteres = montoBase * (1 + interesMensual * mesesMora);
    
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

// Función para cargar casos agrupados desde la API
async function loadCasosFromAPI() {
    if (isLoading) return;
    
    isLoading = true;
    try {
        // Usar el nuevo endpoint que retorna datos agrupados por DNI
        const url = carteraActualId 
            ? `/api/cases/gestor/agrupados?cartera_id=${carteraActualId}`
            : '/api/cases/gestor/agrupados';
        const response = await fetch(url);
        
        // Verificar si la respuesta es OK
        if (!response.ok) {
            const errorText = await response.text();
            console.error('[ERROR] Respuesta del servidor no OK:', response.status, errorText);
            throw new Error(`Error del servidor: ${response.status} - ${errorText}`);
        }
        
        const result = await response.json();
        console.log('[DEBUG] Respuesta de la API:', result);
        
        if (result.success) {
            // Limpiar datos antiguos primero
            todosLosGrupos = [];
            gruposCarteraActual = [];
            grupoClienteActual = null;
            clienteActual = null;
            deudaActual = null;
            indiceGrupoActual = 0;
            indiceDeudaActual = 0;
            
            // Cargar nuevos datos (ya vienen agrupados por DNI)
            todosLosGrupos = result.data || [];
            console.log(`[OK] Cargados ${todosLosGrupos.length} grupos (clientes) desde la API, ${result.total_deudas} deudas totales`);
            
            // DEBUG: Verificar grupos con múltiples deudas
            todosLosGrupos.forEach(grupo => {
                console.log(`[DEBUG] Grupo DNI ${grupo.dni}: total_deudas=${grupo.total_deudas}, deudas.length=${grupo.deudas?.length || 0}`);
                if (grupo.total_deudas > 1 || (grupo.deudas && grupo.deudas.length > 1)) {
                    console.log(`[DEBUG] Grupo DNI ${grupo.dni}: ${grupo.total_deudas} deudas (array length: ${grupo.deudas?.length})`, grupo.deudas.map(d => ({id: d.id, nro_cliente: d.nro_cliente, cartera_id: d.cartera_id, total: d.total})));
                }
                // Verificar si hay discrepancia
                if (grupo.total_deudas !== (grupo.deudas?.length || 0)) {
                    console.error(`[ERROR] Discrepancia en grupo DNI ${grupo.dni}: total_deudas=${grupo.total_deudas} pero deudas.length=${grupo.deudas?.length || 0}`);
                }
                // Log especial para DNI 20737173
                if (grupo.dni === '20737173') {
                    console.log(`[DEBUG ESPECIAL] DNI 20737173 encontrado:`, {
                        total_deudas: grupo.total_deudas,
                        deudas_length: grupo.deudas?.length || 0,
                        deudas: grupo.deudas,
                        grupo_completo: grupo
                    });
                }
            });
            
            // Si no hay grupos, mostrar mensaje y salir
            if (todosLosGrupos.length === 0) {
                showNoCasesMessage();
                updateTotalCounter();
                return;
            }
            
            // Filtrar grupos por cartera actual si hay cartera seleccionada
            // IMPORTANTE: Mantener todas las deudas del grupo, solo filtrar grupos que tengan al menos una deuda en la cartera
            if (carteraActualId) {
                gruposCarteraActual = todosLosGrupos.filter(grupo => {
                    // Verificar si alguna deuda del grupo pertenece a la cartera actual
                    const tieneDeudaEnCartera = grupo.deudas.some(deuda => deuda.cartera_id === carteraActualId);
                    if (tieneDeudaEnCartera && grupo.total_deudas > 1) {
                        console.log(`[DEBUG] Grupo DNI ${grupo.dni} tiene ${grupo.total_deudas} deudas, al menos una en cartera ${carteraActualId}`);
                    }
                    return tieneDeudaEnCartera;
                });
            } else {
                gruposCarteraActual = todosLosGrupos;
            }
            
            // Si no hay cartera seleccionada y hay grupos, seleccionar la primera cartera con casos
            if (!carteraActualId && todosLosGrupos.length > 0) {
                // Obtener la primera cartera que tenga casos
                const primeraCarteraConCasos = carterasDisponibles.find(c => 
                    todosLosGrupos.some(grupo => 
                        grupo.deudas.some(deuda => deuda.cartera_id === c.id)
                    )
                );
                if (primeraCarteraConCasos) {
                    selectCartera(primeraCarteraConCasos.id, primeraCarteraConCasos.nombre);
                    return; // selectCartera ya actualiza todo
                }
            }
            
            // Cargar primer grupo si hay
            if (gruposCarteraActual.length > 0) {
                indiceGrupoActual = 0;
                indiceDeudaActual = 0;
                cargarGrupoCliente(gruposCarteraActual[0], 0, 0);
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
            todosLosGrupos = [];
            gruposCarteraActual = [];
            grupoClienteActual = null;
            clienteActual = null;
            deudaActual = null;
            showNoCasesMessage();
        }
    } catch (error) {
        console.error('[ERROR] Error en fetch:', error);
        console.error('[ERROR] Detalles del error:', error.message, error.stack);
        
        // Intentar obtener más información del error
        let errorMessage = 'Error de conexión al cargar casos';
        if (error.message) {
            errorMessage += ': ' + error.message;
        }
        
        showErrorMessage(errorMessage);
        // Limpiar datos en caso de error
        todosLosGrupos = [];
        gruposCarteraActual = [];
        grupoClienteActual = null;
        clienteActual = null;
        deudaActual = null;
        showNoCasesMessage();
    } finally {
        isLoading = false;
    }
}

// Función para obtener grupos de clientes de la cartera actual
function getGruposCartera() {
    if (!todosLosGrupos || todosLosGrupos.length === 0) {
        return [];
    }
    
    // Filtrar grupos que tengan al menos una deuda en la cartera actual
    if (carteraActualId) {
        return todosLosGrupos.filter(grupo => {
            return grupo.deudas.some(deuda => deuda.cartera_id === carteraActualId);
        });
    }
    
    return todosLosGrupos;
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

// Función para cambiar de cartera y cargar primer grupo
function changeCartera(carteraId) {
    carteraActualId = carteraId;
    const cartera = carterasDisponibles.find(c => c.id === carteraId);
    carteraActual = cartera ? cartera.nombre : null;
    
    gruposCarteraActual = getGruposCartera();
    
    if (gruposCarteraActual.length > 0) {
        indiceGrupoActual = 0;
        indiceDeudaActual = 0;
        cargarGrupoCliente(gruposCarteraActual[0], 0, 0);
        updateCarteraSelector(carteraId, cartera ? cartera.nombre : null);
        limpiarBusqueda();
    } else {
        showNoCasesMessage();
    }
}

// Función para navegar entre clientes (GLOBAL - usada por onclick en HTML)
window.navegarCliente = function(direccion) {
    gruposCarteraActual = getGruposCartera();
    if (gruposCarteraActual.length === 0) return;

    if (direccion === 'prev') {
        indiceGrupoActual = indiceGrupoActual > 0 ? indiceGrupoActual - 1 : gruposCarteraActual.length - 1;
    } else {
        indiceGrupoActual = indiceGrupoActual < gruposCarteraActual.length - 1 ? indiceGrupoActual + 1 : 0;
    }
    
    // Al cambiar de cliente, volver a la primera deuda
    indiceDeudaActual = 0;
    cargarGrupoCliente(gruposCarteraActual[indiceGrupoActual], indiceGrupoActual, 0);
    actualizarContadores();
}

// Función para navegar entre deudas del mismo cliente (GLOBAL - usada por onclick en HTML)
window.navegarDeuda = function(direccion) {
    if (!grupoClienteActual || grupoClienteActual.deudas.length <= 1) return;
    
    const totalDeudas = grupoClienteActual.deudas.length;
    
    if (direccion === 'prev') {
        indiceDeudaActual = indiceDeudaActual > 0 ? indiceDeudaActual - 1 : totalDeudas - 1;
    } else {
        indiceDeudaActual = indiceDeudaActual < totalDeudas - 1 ? indiceDeudaActual + 1 : 0;
    }
    
    // Cargar la nueva deuda
    const deudaData = grupoClienteActual.deudas[indiceDeudaActual];
    deudaActual = mapCaseToCliente(deudaData);
    loadCliente(deudaActual, indiceGrupoActual);
    actualizarContadores();
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

    gruposCarteraActual = getGruposCartera();
    const totalClientes = gruposCarteraActual.length;

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
    indiceGrupoActual = numeroCliente - 1;
    indiceDeudaActual = 0;
    cargarGrupoCliente(gruposCarteraActual[indiceGrupoActual], indiceGrupoActual, 0);
    actualizarContadores();
    
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
    gruposCarteraActual = getGruposCartera();
    
    // Buscar en toda la cartera (buscar en grupos por DNI, nombre, o nro_cliente de deudas)
    const grupoEncontrado = gruposCarteraActual.find(grupo => {
        const cliente = grupo.cliente;
        const nombreMatch = `${cliente.name} ${cliente.lastname}`.toLowerCase().includes(termino);
        const dniMatch = (cliente.dni || '').replace(/\./g, '').toLowerCase().includes(termino.replace(/\./g, ''));
        
        // También buscar en nro_cliente de las deudas
        const nroClienteMatch = grupo.deudas.some(deuda => 
            (deuda.nro_cliente || '').toLowerCase().includes(termino)
        );
        
        return nombreMatch || dniMatch || nroClienteMatch;
    });

    if (grupoEncontrado) {
        indiceGrupoActual = gruposCarteraActual.indexOf(grupoEncontrado);
        indiceDeudaActual = 0;
        cargarGrupoCliente(grupoEncontrado, indiceGrupoActual, 0);
        actualizarContadores();
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
    gruposCarteraActual = getGruposCartera();
    if (gruposCarteraActual.length > 0) {
        indiceGrupoActual = 0;
        indiceDeudaActual = 0;
        cargarGrupoCliente(gruposCarteraActual[0], 0, 0);
        actualizarContadores();
    }
}

// Función para cargar un grupo de cliente (cliente + deudas)
function cargarGrupoCliente(grupo, indiceGrupo, indiceDeuda) {
    console.log(`[DEBUG] cargarGrupoCliente - DNI: ${grupo.dni}`);
    console.log(`[DEBUG]   - total_deudas: ${grupo.total_deudas}`);
    console.log(`[DEBUG]   - deudas.length: ${grupo.deudas?.length || 0}`);
    console.log(`[DEBUG]   - deudas:`, grupo.deudas?.map(d => ({id: d.id, nro_cliente: d.nro_cliente, cartera_id: d.cartera_id})) || []);
    
    // Verificar discrepancia
    if (grupo.total_deudas !== (grupo.deudas?.length || 0)) {
        console.error(`[ERROR] Discrepancia al cargar grupo: total_deudas=${grupo.total_deudas} pero deudas.length=${grupo.deudas?.length || 0}`);
    }
    
    grupoClienteActual = grupo;
    indiceGrupoActual = indiceGrupo;
    indiceDeudaActual = indiceDeuda || 0;
    
    // Validar índice de deuda
    if (indiceDeudaActual < 0 || indiceDeudaActual >= grupo.deudas.length) {
        indiceDeudaActual = 0;
    }
    
    console.log(`[DEBUG] Cargando deuda ${indiceDeudaActual + 1} de ${grupo.deudas.length} para DNI ${grupo.dni}`);
    
    // Obtener datos del cliente (del grupo)
    clienteActual = grupo.cliente;
    
    // Obtener deuda actual
    const deudaData = grupo.deudas[indiceDeudaActual];
    if (!deudaData) {
        console.error(`[ERROR] No hay deuda en índice ${indiceDeudaActual} para grupo DNI ${grupo.dni}`);
        return;
    }
    
    console.log(`[DEBUG] Deuda actual: ID ${deudaData.id}, Nro Cliente ${deudaData.nro_cliente}, Total ${deudaData.total}`);
    
    deudaActual = mapCaseToCliente(deudaData);
    
    // Cargar datos del cliente y deuda actual
    loadCliente(deudaActual, indiceGrupo);
    
    // Actualizar selector de deudas si hay múltiples
    actualizarSelectorDeudas(grupo);
    
    // Verificación adicional después de un pequeño delay
    if (grupo.deudas.length > 1) {
        setTimeout(() => {
            const selectorEl = document.getElementById('deuda-selector');
            if (selectorEl && selectorEl.classList.contains('hidden')) {
                console.warn('[WARN] Selector aún tiene clase hidden, forzando visibilidad...');
                selectorEl.classList.remove('hidden');
                selectorEl.style.display = '';
            }
        }, 200);
    } else {
        // Si solo hay 1 deuda, asegurar que el selector esté oculto
        setTimeout(() => {
            const selectorEl = document.getElementById('deuda-selector');
            if (selectorEl && !selectorEl.classList.contains('hidden')) {
                console.log('[DEBUG] Forzando ocultación del selector (solo 1 deuda)');
                selectorEl.classList.add('hidden');
                selectorEl.style.display = '';
            }
        }, 200);
    }
}

// Función para cargar datos de un cliente (mantener compatibilidad)
function loadCliente(cliente, indice) {
    // Nota: clienteActual y deudaActual ya están establecidos en cargarGrupoCliente()
    // Esta función solo actualiza el DOM con los datos del cliente/deuda actual
    // 'cliente' aquí es en realidad la deuda actual (deudaActual)
    // 'clienteActual' contiene los datos compartidos del cliente
    
    if (!deudaActual) {
        console.error('[ERROR] deudaActual no está definido');
        return;
    }
    
    // Usar deudaActual para datos específicos de la deuda
    // Usar clienteActual para datos compartidos del cliente
    
    // Actualizar encabezado
    const nameHeader = document.getElementById('client-name-header');
    const idHeader = document.getElementById('client-id-header');
    const dniHeader = document.getElementById('client-dni-header');
    const numeroIdHeader = document.getElementById('client-numero-id-header');
    
    if (nameHeader && clienteActual) {
        nameHeader.textContent = `${clienteActual.name || ''} ${clienteActual.lastname || ''}`.trim() || 'N/A';
    }
    if (idHeader) idHeader.textContent = `#${deudaActual.caseId || deudaActual.id}`;
    if (dniHeader && clienteActual) dniHeader.textContent = clienteActual.dni || 'N/A';
    if (numeroIdHeader) numeroIdHeader.textContent = deudaActual.numeroId || 'N/A';
    
    // Actualizar datos del cliente (usar clienteActual para datos compartidos)
    const nameEl = document.getElementById('client-name');
    const dniEl = document.getElementById('client-dni');
    const numeroIdEl = document.getElementById('client-numero-id');
    const phoneEl = document.getElementById('client-phone');
    const emailEl = document.getElementById('client-email');
    const addressEl = document.getElementById('client-address');
    const birthdateEl = document.getElementById('client-birthdate');
    
    if (nameEl && clienteActual) {
        nameEl.textContent = `${clienteActual.name || ''} ${clienteActual.lastname || ''}`.trim() || 'N/A';
    }
    if (dniEl && clienteActual) dniEl.textContent = clienteActual.dni || 'N/A';
    if (numeroIdEl) numeroIdEl.textContent = deudaActual.numeroId || 'N/A';
    if (phoneEl && clienteActual) {
        phoneEl.innerHTML = `<i data-lucide="phone" class="w-4 h-4 text-gray-400"></i> ${clienteActual.telefono || 'N/A'}`;
    }
    if (emailEl) emailEl.innerHTML = `<i data-lucide="mail" class="w-4 h-4 text-gray-400"></i> ${deudaActual.email || 'N/A'}`;
    
    // Actualizar dirección (solo calle_nombre + calle_nro) - usar clienteActual
    const addressTextEl = document.getElementById('client-address-text');
    let direccionCompleta = 'N/A';
    if (clienteActual) {
        const partes = [];
        if (clienteActual.calle_nombre) partes.push(clienteActual.calle_nombre);
        if (clienteActual.calle_nro) partes.push(clienteActual.calle_nro);
        direccionCompleta = partes.join(' ') || 'N/A';
    }
    if (addressTextEl) {
        addressTextEl.textContent = direccionCompleta;
    } else if (addressEl) {
        addressEl.innerHTML = `<i data-lucide="map-pin" class="w-4 h-4 text-gray-400"></i> ${direccionCompleta}`;
    }
    
    // Actualizar localidad, provincia y CP - usar clienteActual
    const localidadEl = document.getElementById('client-localidad');
    const provinciaEl = document.getElementById('client-provincia');
    const cpEl = document.getElementById('client-cp');
    if (localidadEl && clienteActual) localidadEl.textContent = clienteActual.localidad || 'N/A';
    if (provinciaEl && clienteActual) provinciaEl.textContent = clienteActual.provincia || 'N/A';
    if (cpEl && clienteActual) cpEl.textContent = clienteActual.cp || 'N/A';
    
    if (birthdateEl) birthdateEl.textContent = 'N/A'; // No está en el modelo
    
    // Actualizar cartera - usar deudaActual (cada deuda puede tener diferente cartera)
    const carteraEl = document.getElementById('client-cartera');
    if (carteraEl) {
        carteraEl.innerHTML = `<i data-lucide="folder" class="w-4 h-4"></i> ${deudaActual.cartera || 'Sin cartera'}`;
    }
    
    // Actualizar datos de la deuda - usar deudaActual (datos específicos de esta deuda)
    const debtNroClienteEl = document.getElementById('debt-nro-cliente');
    const debtCarteraEl = document.getElementById('debt-cartera');
    const debtAmountEl = document.getElementById('debt-total-amount');
    const debtDueDateEl = document.getElementById('debt-due-date');
    const debtLastMgmtEl = document.getElementById('debt-last-management');
    const debtInstallmentsEl = document.getElementById('debt-installments');
    const debtEntityEl = document.getElementById('debt-entity');
    const debtNotesEl = document.getElementById('debt-notes');
    
    // Mostrar número de cliente y cartera de esta deuda específica
    if (debtNroClienteEl) debtNroClienteEl.textContent = deudaActual.numeroId || 'N/A';
    if (debtCarteraEl) debtCarteraEl.textContent = deudaActual.cartera || 'N/A';
    
    // Monto con interés aplicado (5% mensual según meses de mora) - usar deudaActual (de esta deuda específica)
    if (debtAmountEl) debtAmountEl.textContent = `$${deudaActual.montoAdeudado.toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    if (debtDueDateEl) debtDueDateEl.textContent = deudaActual.fechaVencimiento;
    if (debtLastMgmtEl) debtLastMgmtEl.textContent = deudaActual.ultimaGestion;
    if (debtInstallmentsEl) debtInstallmentsEl.innerHTML = `<span class="text-red-600">${deudaActual.cuotasPendientes}</span> / <span class="text-green-600">${deudaActual.cuotasPagadas}</span>`;
    if (debtEntityEl) debtEntityEl.textContent = deudaActual.cartera || 'N/A';
    if (debtNotesEl) debtNotesEl.textContent = deudaActual.observaciones;
    
    // Actualizar resumen - usar deudaActual
    const summaryMontoInicialEl = document.getElementById('summary-monto-inicial');
    const summaryMontoAdeudadoEl = document.getElementById('summary-monto-adeudado');
    const summaryMontoInteresesEl = document.getElementById('summary-monto-intereses');
    const summaryDaysEl = document.getElementById('summary-days-overdue');
    
    if (summaryMontoInicialEl) {
        summaryMontoInicialEl.textContent = `$${(deudaActual.montoInicial || 0).toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    }
    if (summaryMontoAdeudadoEl) {
        summaryMontoAdeudadoEl.textContent = `$${(deudaActual.montoBase || 0).toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    }
    if (summaryMontoInteresesEl) {
        // Monto con intereses (montoAdeudado ya incluye los intereses calculados)
        summaryMontoInteresesEl.textContent = `$${(deudaActual.montoAdeudado || 0).toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    }
    
    // Actualizar calculadora de intereses - usar deudaActual
    const calcMontoTotalEl = document.getElementById('calc-monto-total');
    if (calcMontoTotalEl) {
        // Formatear a 2 decimales
        const montoFormateado = (deudaActual.montoAdeudado || 0).toFixed(2);
        calcMontoTotalEl.value = montoFormateado;
        calcularIntereses();
    }
    if (summaryDaysEl) {
        const meses = deudaActual.mesesMora || 0;
        summaryDaysEl.textContent = `${meses} ${meses === 1 ? 'mes' : 'meses'}`;
    }
    
    // Actualizar case_id en formularios - CRÍTICO: debe actualizarse siempre - usar deudaActual
    const currentCaseIdEl = document.getElementById('current-case-id');
    const managementCaseIdEl = document.getElementById('management-case-id');
    const caseIdValue = String(deudaActual.caseId || deudaActual.id || '');
    
    console.log(`[DEBUG] loadCliente - Cliente: ${clienteActual ? `${clienteActual.name} ${clienteActual.lastname}` : 'N/A'}, caseId: ${deudaActual.caseId}, id: ${deudaActual.id}, estado: ${deudaActual.estado}`);
    
    if (currentCaseIdEl) {
        currentCaseIdEl.value = caseIdValue;
        const nombreCliente = clienteActual ? `${clienteActual.name} ${clienteActual.lastname}` : 'N/A';
        console.log(`[DEBUG] ✓ Actualizado current-case-id: "${caseIdValue}" para cliente: ${nombreCliente}`);
    } else {
        console.error('[ERROR] ✗ No se encontró elemento current-case-id en el DOM');
    }
    
    if (managementCaseIdEl) {
        managementCaseIdEl.value = caseIdValue;
        console.log(`[DEBUG] ✓ Actualizado management-case-id: "${caseIdValue}"`);
    } else {
        console.warn('[WARN] No se encontró elemento management-case-id (puede ser normal)');
    }
    
    // Actualizar estado del selector - debe reflejar el estado real del caso - usar deudaActual
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
    
    const statusInfo = statusMap[deudaActual.estado] || statusMap['sin-gestion'];
    const statusSelectorEl = document.getElementById('status-selector');
    if (statusSelectorEl) {
        // Asegurar que el selector muestre el estado correcto
        statusSelectorEl.value = deudaActual.estado;
        console.log(`[DEBUG] Estado del selector actualizado a: ${deudaActual.estado} para caso ${deudaActual.caseId || deudaActual.id}`);
        
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
                e.target.value = deudaActual.estado; // Restaurar
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
                    
                    // Actualizar deudaActual inmediatamente
                    if (deudaActual) {
                        deudaActual.estado = newStatus;
                        console.log(`[DEBUG] deudaActual.estado actualizado a: ${newStatus}`);
                    }
                    
                    // Actualizar en el grupo actual
                    if (grupoClienteActual) {
                        const deudaIndex = grupoClienteActual.deudas.findIndex(d => d.id == caseId);
                        if (deudaIndex !== -1) {
                            grupoClienteActual.deudas[deudaIndex].status_nombre = newStatus;
                            console.log(`[DEBUG] grupoClienteActual.deudas[${deudaIndex}] actualizado con nuevo estado`);
                        }
                    }
                    
                    // Recargar casos desde la API para obtener datos actualizados
                    setTimeout(async () => {
                        await loadCasosFromAPI();
                    }, 500);
                } else {
                    console.error('[ERROR] Error actualizando estado:', await response.text());
                    alert('Error al guardar el estado');
                    e.target.value = deudaActual.estado; // Restaurar
                }
            } catch (error) {
                console.error('[ERROR] Error en petición:', error);
                alert('Error al guardar el estado');
                e.target.value = deudaActual.estado; // Restaurar
            } finally {
                // Ocultar loading
                if (loadingEl) loadingEl.style.display = 'none';
            }
        });
    }
    updateStatusBadge(cliente.estado);
    
    // Cargar historial de gestiones
    if (deudaActual && (deudaActual.caseId || deudaActual.id)) {
        const caseIdToLoad = deudaActual.caseId || deudaActual.id;
        console.log(`[DEBUG] Cargando actividades para caso ${caseIdToLoad}`);
        loadActivities(caseIdToLoad);
    } else {
        console.warn('[WARN] No hay caseId para cargar actividades');
        // Mostrar mensaje de que no hay gestiones
        const historyContainer = document.getElementById('management-history');
        if (historyContainer) {
            historyContainer.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i data-lucide="inbox" class="w-12 h-12 mx-auto mb-2 opacity-50"></i>
                    <p>No hay gestiones registradas para este cliente</p>
                </div>
            `;
        }
        const summaryLastManagementEl = document.getElementById('summary-last-management');
        if (summaryLastManagementEl) {
            summaryLastManagementEl.textContent = 'N/A';
        }
    }
    
    // Los contadores se actualizan en actualizarContadores()
    // Usar setTimeout para asegurar que el DOM esté actualizado
    setTimeout(() => {
        actualizarContadores();
    }, 50);
    
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
    if (!deudaActual || !deudaActual.caseId) {
        console.log('[WARN] No hay deuda seleccionada para recargar');
        return;
    }
    
    try {
        const response = await fetch(`/api/cases/${deudaActual.caseId}`);
        const result = await response.json();
        
        if (result.success) {
            // Actualizar la deuda en el grupo actual
            if (grupoClienteActual) {
                const deudaIndex = grupoClienteActual.deudas.findIndex(d => d.id === result.data.id);
                if (deudaIndex !== -1) {
                    grupoClienteActual.deudas[deudaIndex] = result.data;
                    console.log(`[DEBUG] Actualizado deuda en grupoClienteActual.deudas[${deudaIndex}]`);
                    
                    // Actualizar deudaActual con datos frescos
                    deudaActual = mapCaseToCliente(result.data);
                    
                    // Recargar la vista
                    loadCliente(deudaActual, indiceGrupoActual);
                }
            }
            
            // Actualizar el selector de estado
            const statusSelector = document.getElementById('status-selector');
            if (statusSelector && deudaActual) {
                statusSelector.value = deudaActual.estado;
            }
            if (deudaActual) {
                updateStatusBadge(deudaActual.estado);
            }
            
            // Actualizar case_id en formularios
            const currentCaseIdEl = document.getElementById('current-case-id');
            const managementCaseIdEl = document.getElementById('management-case-id');
            if (currentCaseIdEl && deudaActual) currentCaseIdEl.value = deudaActual.caseId || '';
            if (managementCaseIdEl && deudaActual) managementCaseIdEl.value = deudaActual.caseId || '';
            
            if (deudaActual) {
                console.log(`[OK] Deuda ${deudaActual.caseId} recargada y actualizada en memoria, estado: ${deudaActual.estado}`);
            }
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
            if (activities.length > 0) {
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
                    console.log(`[DEBUG] Última gestión actualizada: ${ultimaGestionTexto}`);
                }
            } else {
                // No hay gestiones, mostrar "N/A"
                const summaryLastManagementEl = document.getElementById('summary-last-management');
                if (summaryLastManagementEl) {
                    summaryLastManagementEl.textContent = 'N/A';
                }
            }
        } else {
            console.error('[ERROR] Error cargando gestiones:', result.error);
            const historyContainer = document.getElementById('management-history');
            if (historyContainer) {
                historyContainer.innerHTML = `
                    <div class="text-center py-8 text-red-500">
                        <i data-lucide="alert-circle" class="w-12 h-12 mx-auto mb-2 opacity-50"></i>
                        <p>Error al cargar gestiones: ${result.error || 'Error desconocido'}</p>
                    </div>
                `;
                if (typeof lucide !== 'undefined' && lucide.createIcons) {
                    lucide.createIcons();
                }
            }
            // Si hay error, mostrar "N/A"
            const summaryLastManagementEl = document.getElementById('summary-last-management');
            if (summaryLastManagementEl) {
                summaryLastManagementEl.textContent = 'N/A';
            }
        }
    } catch (error) {
        console.error('[ERROR] Error en loadActivities:', error);
        const historyContainer = document.getElementById('management-history');
        if (historyContainer) {
            historyContainer.innerHTML = `
                <div class="text-center py-8 text-red-500">
                    <i data-lucide="alert-circle" class="w-12 h-12 mx-auto mb-2 opacity-50"></i>
                    <p>Error al cargar gestiones: ${error.message || 'Error desconocido'}</p>
                </div>
            `;
            if (typeof lucide !== 'undefined' && lucide.createIcons) {
                lucide.createIcons();
            }
        }
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
// Función para actualizar contadores de cliente y deuda
function actualizarContadores() {
    if (!grupoClienteActual) {
        console.log('[DEBUG] actualizarContadores: grupoClienteActual es null');
        return;
    }
    
    console.log(`[DEBUG] actualizarContadores: grupoClienteActual tiene ${grupoClienteActual.deudas?.length || 0} deudas`);
    
    // Contador de clientes
    const totalClientes = gruposCarteraActual.length;
    const clienteNum = indiceGrupoActual + 1;
    const clienteCounterEl = document.getElementById('cliente-counter');
    if (clienteCounterEl) {
        clienteCounterEl.textContent = `Cliente ${clienteNum} de ${totalClientes}`;
    }
    
    // Contador de deudas (solo si hay múltiples)
    const totalDeudas = grupoClienteActual.deudas?.length || 0;
    const deudaNum = indiceDeudaActual + 1;
    const deudaCounterEl = document.getElementById('deuda-counter');
    const deudaSelectorEl = document.getElementById('deuda-selector');
    const btnPrevDeuda = document.getElementById('btn-prev-deuda');
    const btnNextDeuda = document.getElementById('btn-next-deuda');
    
    console.log(`[DEBUG] actualizarContadores: totalDeudas = ${totalDeudas}, deudaNum = ${deudaNum}, indiceDeudaActual = ${indiceDeudaActual}`);
    
    // Verificación explícita: si totalDeudas === 1, ocultar el selector inmediatamente
    if (totalDeudas === 1) {
        console.log('[DEBUG] totalDeudas === 1, ocultando selector de deudas');
        if (deudaSelectorEl) {
            deudaSelectorEl.classList.add('hidden');
            deudaSelectorEl.style.display = 'none'; // Forzar ocultación
            console.log('[DEBUG] Selector ocultado: clase hidden + display none');
        } else {
            console.error('[ERROR] No se encontró deuda-selector para ocultar');
        }
        if (btnPrevDeuda) {
            btnPrevDeuda.disabled = true;
        }
        if (btnNextDeuda) {
            btnNextDeuda.disabled = true;
        }
        // Ocultar otros elementos relacionados
        const multiDeudaBadge = document.getElementById('multi-deuda-badge');
        if (multiDeudaBadge) multiDeudaBadge.classList.add('hidden');
        
        // Ocultar resumen consolidado si totalDeudas === 1
        const resumenConsolidado = document.getElementById('resumen-consolidado');
        if (resumenConsolidado) {
            resumenConsolidado.classList.add('hidden');
            resumenConsolidado.style.display = 'none'; // Forzar ocultación
            console.log('[DEBUG] Resumen consolidado ocultado (totalDeudas === 1)');
        } else {
            console.warn('[WARN] No se encontró resumen-consolidado para ocultar');
        }
        
        const deudaCurrentBadge = document.getElementById('deuda-current-badge');
        if (deudaCurrentBadge) deudaCurrentBadge.classList.add('hidden');
        return; // Salir temprano si solo hay 1 deuda
    }
    
    // Si totalDeudas > 1, mostrar el selector
    if (totalDeudas > 1) {
        console.log('[DEBUG] Mostrando selector de deudas');
        // Mostrar selector de deuda
        if (deudaCounterEl) {
            deudaCounterEl.textContent = `${deudaNum} de ${totalDeudas}`;
            console.log(`[DEBUG] Contador actualizado: ${deudaNum} de ${totalDeudas}`);
        } else {
            console.error('[ERROR] No se encontró el elemento deuda-counter en el DOM');
        }
        
        if (deudaSelectorEl) {
            // Remover clase hidden
            deudaSelectorEl.classList.remove('hidden');
            // Remover cualquier estilo inline que pueda estar interfiriendo
            deudaSelectorEl.style.display = '';
            console.log('[DEBUG] Clase "hidden" removida del selector de deudas');
            console.log('[DEBUG] Estilos aplicados:', {
                display: deudaSelectorEl.style.display || 'flex (por clase Tailwind)',
                classList: Array.from(deudaSelectorEl.classList),
                computedDisplay: window.getComputedStyle(deudaSelectorEl).display
            });
        } else {
            console.error('[ERROR] No se encontró el elemento deuda-selector en el DOM');
            console.error('[ERROR] Intentando buscar de nuevo...');
            // Intentar buscar de nuevo después de un pequeño delay
            setTimeout(() => {
                const retryEl = document.getElementById('deuda-selector');
                if (retryEl) {
                    console.log('[DEBUG] Elemento encontrado en segundo intento');
                    retryEl.classList.remove('hidden');
                    retryEl.style.display = '';
                } else {
                    console.error('[ERROR] Elemento aún no encontrado después del delay');
                }
            }, 100);
        }
        // Habilitar/deshabilitar botones según posición
        if (btnPrevDeuda) {
            btnPrevDeuda.disabled = (indiceDeudaActual === 0);
            console.log(`[DEBUG] btn-prev-deuda disabled: ${btnPrevDeuda.disabled}`);
        }
        if (btnNextDeuda) {
            btnNextDeuda.disabled = (indiceDeudaActual >= totalDeudas - 1);
            console.log(`[DEBUG] btn-next-deuda disabled: ${btnNextDeuda.disabled}`);
        }
        
        // Actualizar badge de múltiples deudas
        const multiDeudaBadge = document.getElementById('multi-deuda-badge');
        const deudaCountBadge = document.getElementById('deuda-count-badge');
        if (multiDeudaBadge) multiDeudaBadge.classList.remove('hidden');
        if (deudaCountBadge) deudaCountBadge.textContent = `${totalDeudas} deudas`;
        
        // Mostrar indicador en la tarjeta de deuda
        const deudaIndicator = document.getElementById('deuda-indicator');
        const deudaIndicatorText = document.getElementById('deuda-indicator-text');
        if (deudaIndicator) deudaIndicator.classList.remove('hidden');
        if (deudaIndicatorText) deudaIndicatorText.textContent = `Deuda ${deudaNum} de ${totalDeudas}`;
        
        // Mostrar badge en el resumen
        const deudaActualBadge = document.getElementById('deuda-actual-badge');
        const deudaActualNum = document.getElementById('deuda-actual-num');
        const deudaActualTotal = document.getElementById('deuda-actual-total');
        if (deudaActualBadge) deudaActualBadge.classList.remove('hidden');
        if (deudaActualNum) deudaActualNum.textContent = deudaNum;
        if (deudaActualTotal) deudaActualTotal.textContent = totalDeudas;
        
        // Mostrar resumen consolidado
        const resumenConsolidado = document.getElementById('resumen-consolidado');
        const consolidadoTotalDeudas = document.getElementById('consolidado-total-deudas');
        const consolidadoMontoInicial = document.getElementById('consolidado-monto-inicial');
        const consolidadoMontoAdeudado = document.getElementById('consolidado-monto-adeudado');
        
        if (resumenConsolidado) {
            resumenConsolidado.classList.remove('hidden');
            resumenConsolidado.style.display = ''; // Remover cualquier display: none
            console.log('[DEBUG] Resumen consolidado mostrado (totalDeudas > 1)');
        }
        if (consolidadoTotalDeudas) consolidadoTotalDeudas.textContent = totalDeudas;
        if (consolidadoMontoInicial) {
            consolidadoMontoInicial.textContent = `$${(grupoClienteActual.monto_inicial_total || 0).toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }
        if (consolidadoMontoAdeudado) {
            consolidadoMontoAdeudado.textContent = `$${(grupoClienteActual.deuda_consolidada || 0).toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }
    } else {
        console.log('[DEBUG] Ocultando selector de deudas (solo 1 deuda o ninguna)');
        // Ocultar selector si solo hay una deuda
        if (deudaSelectorEl) {
            deudaSelectorEl.classList.add('hidden');
            // Remover cualquier estilo inline que pueda estar interfiriendo
            deudaSelectorEl.style.display = '';
            console.log('[DEBUG] Selector de deudas ocultado (clase hidden agregada)');
            console.log('[DEBUG] Estado del selector:', {
                classList: Array.from(deudaSelectorEl.classList),
                computedDisplay: window.getComputedStyle(deudaSelectorEl).display
            });
        } else {
            console.warn('[WARN] No se encontró el elemento deuda-selector para ocultar');
        }
        if (btnPrevDeuda) {
            btnPrevDeuda.disabled = true;
        }
        if (btnNextDeuda) {
            btnNextDeuda.disabled = true;
        }
        
        // Ocultar badge
        const multiDeudaBadge = document.getElementById('multi-deuda-badge');
        if (multiDeudaBadge) multiDeudaBadge.classList.add('hidden');
        
        // Ocultar indicador en la tarjeta de deuda
        const deudaIndicator = document.getElementById('deuda-indicator');
        if (deudaIndicator) deudaIndicator.classList.add('hidden');
        
        // Ocultar badge en el resumen
        const deudaActualBadge = document.getElementById('deuda-actual-badge');
        if (deudaActualBadge) deudaActualBadge.classList.add('hidden');
        
        // Ocultar resumen consolidado
        const resumenConsolidado = document.getElementById('resumen-consolidado');
        if (resumenConsolidado) resumenConsolidado.classList.add('hidden');
    }
}

// Función para actualizar selector de deudas
function actualizarSelectorDeudas(grupo) {
    // Esta función se llama desde cargarGrupoCliente
    // Asegurar que grupoClienteActual esté establecido
    if (!grupoClienteActual && grupo) {
        grupoClienteActual = grupo;
        console.log('[DEBUG] actualizarSelectorDeudas: grupoClienteActual establecido desde parámetro');
    }
    // Los contadores se actualizan en actualizarContadores()
    // Usar setTimeout para asegurar que el DOM esté listo
    setTimeout(() => {
        actualizarContadores();
    }, 50);
}

function updateTotalCounter() {
    const totalGrupos = todosLosGrupos.length;
    const totalDeudas = todosLosGrupos.reduce((sum, grupo) => sum + grupo.total_deudas, 0);
    // Actualizar algún elemento del DOM si existe
    console.log(`Total de grupos (clientes): ${totalGrupos}, Total de deudas: ${totalDeudas}`);
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
                if (managementCaseIdEl && deudaActual && deudaActual.caseId) {
                    managementCaseIdEl.value = deudaActual.caseId;
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
    
    // Calcular total a abonar con interés simple: monto * (1 + interés/100 * cantidad_cuotas)
    // NOTA: Esta calculadora usa interés simple por cuota
    const interesDecimal = interesMensual / 100;
    const totalAbonar = montoTotal * (1 + interesDecimal * cantidadCuotas);
    
    // Calcular monto por cuota
    const montoCuota = totalAbonar / cantidadCuotas;
    
    // Formatear y mostrar resultados
    totalAbonarEl.textContent = `$${totalAbonar.toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    montoCuotaEl.textContent = `$${montoCuota.toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
};
