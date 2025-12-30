// Dashboard Admin - Integrado con APIs reales

// Variables globales
let performanceChart, carteraChart, comparisonChart;
let currentFilters = {
    start_date: null,
    end_date: null,
    cartera: null,
    gestor_id: null
};

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

async function initializeDashboard() {
    try {
        // Actualizar última actualización
        document.getElementById('lastUpdate').textContent = new Date().toLocaleString('es-ES');
        
        // Cargar todos los datos
        await Promise.all([
            loadKPIs(),
            loadPerformanceChart(),
            loadCarteraChart(),
            loadComparisonChart(),
            loadGestoresRanking()
        ]);
    } catch (error) {
        console.error('Error inicializando dashboard:', error);
        showError('Error al cargar datos del dashboard');
    }
}

// Cargar KPIs
async function loadKPIs() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.start_date) params.append('start_date', currentFilters.start_date);
        if (currentFilters.end_date) params.append('end_date', currentFilters.end_date);
        if (currentFilters.cartera) params.append('cartera', currentFilters.cartera);
        if (currentFilters.gestor_id) params.append('gestor_id', currentFilters.gestor_id);
        
        const response = await fetch(`/api/dashboard/kpis?${params}`);
        const result = await response.json();
        
        if (result.success) {
            const kpis = result.data;
            
            // Actualizar KPI cards
            updateKPICard('Monto Total Recuperado', `$${kpis.monto_recuperado.toLocaleString('es-ES')}`, kpis.monto_recuperado);
            updateKPICard('Tasa de Recupero', `${kpis.tasa_recupero.toFixed(1)}%`, kpis.tasa_recupero);
            updateKPICard('Promesas Cumplidas', `${kpis.promesas_cumplidas.toFixed(1)}%`, kpis.promesas_cumplidas);
            updateKPICard('Gestiones Realizadas', kpis.gestiones_realizadas.toLocaleString('es-ES'), kpis.gestiones_realizadas);
        }
    } catch (error) {
        console.error('Error cargando KPIs:', error);
    }
}

function updateKPICard(label, value, rawValue) {
    // Buscar el card por el label
    const cards = document.querySelectorAll('.kpi-card');
    cards.forEach(card => {
        const labelEl = card.querySelector('.kpi-label');
        if (labelEl && labelEl.textContent.includes(label)) {
            const valueEl = card.querySelector('.kpi-value');
            if (valueEl) {
                valueEl.textContent = value;
            }
        }
    });
}

// Cargar gráfico de rendimiento
async function loadPerformanceChart() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.start_date) params.append('start_date', currentFilters.start_date);
        if (currentFilters.end_date) params.append('end_date', currentFilters.end_date);
        if (currentFilters.cartera) params.append('cartera', currentFilters.cartera);
        
        const response = await fetch(`/api/dashboard/charts/performance?${params}`);
        const result = await response.json();
        
        if (result.success) {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            
            if (performanceChart) {
                performanceChart.destroy();
            }
            
            performanceChart = new Chart(ctx, {
                type: 'bar',
                data: result.data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {
                                footer: (items) => {
                                    let total = items.reduce((sum, item) => sum + item.parsed.y, 0);
                                    return `Total: $${total.toLocaleString('es-ES')}`;
                                }
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error cargando gráfico de rendimiento:', error);
    }
}

// Cargar gráfico de cartera
async function loadCarteraChart() {
    try {
        const response = await fetch('/api/dashboard/charts/cartera');
        const result = await response.json();
        
        if (result.success) {
            const ctx = document.getElementById('carteraChart').getContext('2d');
            
            if (carteraChart) {
                carteraChart.destroy();
            }
            
            carteraChart = new Chart(ctx, {
                type: 'doughnut',
                data: result.data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {
                                label: (item) => {
                                    const total = item.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((item.parsed / total) * 100).toFixed(1);
                                    return `${item.label}: $${item.parsed.toLocaleString('es-ES')} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error cargando gráfico de cartera:', error);
    }
}

// Cargar gráfico de comparación
async function loadComparisonChart() {
    try {
        const response = await fetch('/api/dashboard/stats/comparison');
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            const ctx = document.getElementById('comparisonChart').getContext('2d');
            
            if (comparisonChart) {
                comparisonChart.destroy();
            }
            
            comparisonChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Monto Recuperado', 'Promesas Cumplidas', 'Gestiones Realizadas'],
                    datasets: [{
                        label: 'Mes Actual',
                        data: [
                            data.current.monto_recuperado,
                            data.current.promesas_cumplidas,
                            data.current.gestiones_realizadas
                        ],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        fill: true,
                    }, {
                        label: 'Mes Anterior',
                        data: [
                            data.previous.monto_recuperado,
                            data.previous.promesas_cumplidas,
                            data.previous.gestiones_realizadas
                        ],
                        borderColor: '#94a3b8',
                        backgroundColor: 'rgba(148, 163, 184, 0.1)',
                        fill: true,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value, index) {
                                    if (index === 0) return '$' + value.toLocaleString('es-ES');
                                    if (index === 1) return value + '%';
                                    return value;
                                }
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error cargando gráfico de comparación:', error);
    }
}

// Cargar ranking de gestores
async function loadGestoresRanking() {
    try {
        const response = await fetch('/api/dashboard/gestores/ranking?limit=10');
        const result = await response.json();
        
        if (result.success) {
            const rankingTable = document.querySelector('.ranking-table tbody');
            if (rankingTable) {
                rankingTable.innerHTML = '';
                result.data.forEach((gestor, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${gestor.gestor_name}</td>
                        <td>$${gestor.monto_recuperado.toLocaleString('es-ES')}</td>
                        <td>${gestor.casos_pagados}/${gestor.total_casos}</td>
                        <td>${gestor.promesas_cumplidas.toFixed(1)}%</td>
                        <td><button onclick="openGestorDetail('${gestor.gestor_name}')">Ver</button></td>
                    `;
                    rankingTable.appendChild(row);
                });
            }
        }
    } catch (error) {
        console.error('Error cargando ranking:', error);
    }
}

// Funciones de filtrado
function updatePeriod(value) {
    const now = new Date();
    let startDate, endDate;
    
    switch(value) {
        case 'week':
            startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            break;
        case 'month':
            startDate = new Date(now.getFullYear(), now.getMonth(), 1);
            break;
        case 'quarter':
            const quarter = Math.floor(now.getMonth() / 3);
            startDate = new Date(now.getFullYear(), quarter * 3, 1);
            break;
        case 'custom':
            // TODO: Implementar selector de fechas personalizado
            return;
        default:
            startDate = new Date(now.getFullYear(), now.getMonth(), 1);
    }
    
    endDate = now;
    
    currentFilters.start_date = startDate.toISOString();
    currentFilters.end_date = endDate.toISOString();
    
    // Recargar datos
    initializeDashboard();
}

function filterBy(type, value) {
    if (value === '' || value === 'all') {
        if (type === 'cartera') {
            currentFilters.cartera = null;
        } else if (type === 'gestor') {
            currentFilters.gestor_id = null;
        }
    } else {
        if (type === 'cartera') {
            currentFilters.cartera = value;
        } else if (type === 'gestor') {
            currentFilters.gestor_id = parseInt(value);
        }
    }
    
    // Recargar datos
    initializeDashboard();
}

function toggleFilter(element) {
    element.classList.toggle('active');
    // TODO: Implementar lógica de filtrado por chips
}

function toggleNotifications() {
    alert('Notificaciones: 3 alertas activas\n1. Gestor A superó su meta\n2. Nuevo caso urgente\n3. Reporte semanal listo');
}

function openGestorDetail(gestor) {
    alert(`Abriendo panel del ${gestor}\n(Para implementar con HTMX)`);
}

function exportReport(format) {
    alert(`Generando reporte en formato ${format.toUpperCase()}...`);
}

function showError(message) {
    // Crear o actualizar mensaje de error
    let errorDiv = document.getElementById('error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = 'error-message';
        errorDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #ef4444; color: white; padding: 15px; border-radius: 8px; z-index: 1000;';
        document.body.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}
