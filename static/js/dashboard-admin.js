// Update last update time
document.getElementById('lastUpdate').textContent = new Date().toLocaleString('es-ES');

// Initialize Charts
const ctx1 = document.getElementById('performanceChart').getContext('2d');
const performanceChart = new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
        datasets: [{
            label: 'Cartera A',
            data: [45000, 52000, 48000, 61000],
            backgroundColor: '#667eea',
        }, {
            label: 'Cartera B',
            data: [35000, 41000, 39000, 48000],
            backgroundColor: '#764ba2',
        }, {
            label: 'Cartera C',
            data: [28000, 32000, 29000, 35000],
            backgroundColor: '#f093fb',
        }]
    },
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
                        return `Total: $${total.toLocaleString()}`;
                    }
                }
            }
        }
    }
});

const ctx2 = document.getElementById('carteraChart').getContext('2d');
const carteraChart = new Chart(ctx2, {
    type: 'doughnut',
    data: {
        labels: ['Cartera A', 'Cartera B', 'Cartera C'],
        datasets: [{
            data: [86000, 68000, 52000],
            backgroundColor: ['#667eea', '#764ba2', '#f093fb'],
            borderWidth: 0
        }]
    },
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
                        return `${item.label}: $${item.parsed.toLocaleString()} (${percentage}%)`;
                    }
                }
            }
        }
    }
});

const ctx3 = document.getElementById('comparisonChart').getContext('2d');
const comparisonChart = new Chart(ctx3, {
    type: 'line',
    data: {
        labels: ['Monto Recuperado', 'Promesas Cumplidas', 'Contactos Efectivos'],
        datasets: [{
            label: 'Mes Actual',
            data: [245890, 82.1, 1247],
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            fill: true,
        }, {
            label: 'Mes Anterior',
            data: [218560, 75.6, 1082],
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
                        if (index === 0) return '$' + value.toLocaleString();
                        if (index === 1) return value + '%';
                        return value;
                    }
                }
            }
        }
    }
});

// Functions
function updatePeriod(value) {
    console.log('Period updated:', value);
    // HTMX call here
}

function filterBy(type, value) {
    console.log('Filter:', type, value);
    // HTMX call here
}

function toggleFilter(element) {
    element.classList.toggle('active');
}

function toggleNotifications() {
    alert('Notificaciones: 3 alertas activas\n1. Gestor A superÃ³ su meta\n2. Nuevo caso urgente\n3. Reporte semanal listo');
}

function openGestorDetail(gestor) {
    alert(`Abriendo panel del ${gestor}\n(Para implementar con HTMX)`);
}

function exportReport(format) {
    alert(`Generando reporte en formato ${format.toUpperCase()}...`);
}