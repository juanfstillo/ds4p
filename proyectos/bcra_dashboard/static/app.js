// Configuración de la API
const API_BASE_URL = window.location.origin + '/api';

// Estado global de la aplicación
let authToken = null;
let dashboardData = null;

// Iconos por variable
const ICONOS_VARIABLES = {
    'tipo_cambio_oficial': '💵',
    'reservas': '💰',
    'inflacion_mensual': '📈',
    'inflacion_anual': '📊',
    'badlar': '🏦',
    'plazo_fijo': '💳',
    'leliq': '📉'
};

// Colores por variable - paleta #632024
const COLORES_VARIABLES = {
    'tipo_cambio_oficial': '#632024',
    'reservas': '#7d2a2e',
    'inflacion_mensual': '#4a181b',
    'inflacion_anual': '#8f2d32',
    'badlar': '#9d363b',
    'plazo_fijo': '#aa4248',
    'leliq': '#b74e54'
};

// ===========================================
// FUNCIONES DE API
// ===========================================

async function fetchAPI(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (authToken) {
        defaultOptions.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

async function login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    });
    
    if (!response.ok) {
        throw new Error('Credenciales inválidas');
    }
    
    const data = await response.json();
    authToken = data.access_token;
    localStorage.setItem('authToken', authToken);
    
    return data;
}

async function obtenerDatosDashboard() {
    return await fetchAPI('/dashboard?dias=30');
}

async function obtenerEstadisticas() {
    return await fetchAPI('/stats');
}

// ===========================================
// FUNCIONES DE UI
// ===========================================

function mostrarLoading(mostrar = true) {
    const overlay = document.getElementById('loadingOverlay');
    if (mostrar) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

function formatearNumero(numero, decimales = 2) {
    return Number(numero).toLocaleString('es-AR', {
        minimumFractionDigits: decimales,
        maximumFractionDigits: decimales
    });
}

function formatearFecha(fechaStr) {
    const fecha = new Date(fechaStr + 'T00:00:00');
    return fecha.toLocaleDateString('es-AR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function crearCardIndicador(dato) {
    const icono = ICONOS_VARIABLES[dato.variable] || '📊';
    const color = COLORES_VARIABLES[dato.variable] || 'primary';
    const claseCard = `card-${dato.variable.replace('_', '-')}`;
    
    return `
        <div class="col-md-6 col-lg-3 fade-in">
            <div class="card indicator-card ${claseCard}">
                <div class="card-body text-center">
                    <div class="indicator-icon">${icono}</div>
                    <div class="indicator-value">${formatearNumero(dato.valor)}</div>
                    <div class="indicator-label">${dato.descripcion}</div>
                    <div class="indicator-date">
                        ${formatearFecha(dato.fecha)}
                        ${dato.unidad ? `<br><small>${dato.unidad}</small>` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderizarUltimosValores(ultimosValores) {
    const container = document.getElementById('ultimosValoresContainer');
    
    if (!ultimosValores || ultimosValores.length === 0) {
        container.innerHTML = '<p class="text-center">No hay datos disponibles</p>';
        return;
    }
    
    const html = ultimosValores.map(dato => crearCardIndicador(dato)).join('');
    container.innerHTML = html;
}

function renderizarTablaDatos(ultimosValores) {
    const tbody = document.getElementById('tablaDatos');
    
    if (!ultimosValores || ultimosValores.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">No hay datos disponibles</td></tr>';
        return;
    }
    
    const html = ultimosValores.map(dato => `
        <tr>
            <td><strong>${ICONOS_VARIABLES[dato.variable] || '📊'} ${dato.descripcion}</strong></td>
            <td>${formatearNumero(dato.valor)}</td>
            <td>${formatearFecha(dato.fecha)}</td>
            <td>${dato.unidad || '-'}</td>
        </tr>
    `).join('');
    
    tbody.innerHTML = html;
}

// ===========================================
// FUNCIONES DE GRÁFICOS (Chart.js)
// ===========================================

let charts = {};

function crearGrafico(canvasId, datos, label, color = '#0d6efd') {
    const ctx = document.getElementById(canvasId);
    
    if (!ctx) {
        console.error(`Canvas con id ${canvasId} no encontrado`);
        return;
    }
    
    // Destruir gráfico anterior si existe
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    
    const labels = datos.map(d => formatearFecha(d.fecha));
    const values = datos.map(d => d.valor);
    
    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                borderColor: color,
                backgroundColor: color + '20',
                tension: 0.4,
                fill: true,
                pointRadius: 3,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return label + ': ' + formatearNumero(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return formatearNumero(value);
                        }
                    }
                }
            }
        }
    });
}

function crearGraficoMultiple(canvasId, seriesData, title) {
    const ctx = document.getElementById(canvasId);
    
    if (!ctx) return;
    
    // Destruir gráfico anterior si existe
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    
    const datasets = Object.entries(seriesData).map(([nombre, data]) => {
        const color = COLORES_VARIABLES[nombre] || '#6c757d';
        return {
            label: data.descripcion,
            data: data.datos.map(d => ({ x: d.fecha, y: d.valor })),
            borderColor: color,
            backgroundColor: color + '20',
            tension: 0.4,
            fill: false
        };
    });
    
    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                },
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

function renderizarGraficos(seriesHistoricas) {
    if (!seriesHistoricas) return;
    
    // Tipo de Cambio
    if (seriesHistoricas['tipo_cambio_oficial']) {
        crearGrafico(
            'chartTipoCambio',
            seriesHistoricas['tipo_cambio_oficial'].datos,
            'Tipo de Cambio USD/ARS',
            COLORES_VARIABLES['tipo_cambio_oficial']
        );
    }
    
    // Reservas
    if (seriesHistoricas['reservas']) {
        crearGrafico(
            'chartReservas',
            seriesHistoricas['reservas'].datos,
            'Reservas Internacionales (Mill. USD)',
            COLORES_VARIABLES['reservas']
        );
    }
    
    // Inflación
    if (seriesHistoricas['inflacion_mensual']) {
        crearGrafico(
            'chartInflacion',
            seriesHistoricas['inflacion_mensual'].datos,
            'Inflación Mensual (%)',
            COLORES_VARIABLES['inflacion_mensual']
        );
    }
    
    // Tasas de Interés (múltiples series)
    const tasas = {};
    ['badlar', 'plazo_fijo', 'leliq'].forEach(tasa => {
        if (seriesHistoricas[tasa]) {
            tasas[tasa] = seriesHistoricas[tasa];
        }
    });
    
    if (Object.keys(tasas).length > 0) {
        crearGraficoMultiple('chartTasas', tasas, 'Tasas de Interés');
    }
}

// ===========================================
// FUNCIONES PRINCIPALES
// ===========================================

function verificarAutenticacion() {
    const token = localStorage.getItem('authToken');
    return token !== null;
}

function mostrarLoginRequerido() {
    // Ocultar loading
    mostrarLoading(false);
    
    // Mostrar modal de login
    const modal = new bootstrap.Modal(document.getElementById('loginModal'));
    modal.show();
    
    // Ocultar contenido del dashboard
    document.getElementById('ultimosValoresContainer').innerHTML = 
        '<div class="col-12 text-center"><p class="text-muted">Inicia sesión para ver los datos</p></div>';
}

async function cargarDashboard() {
    try {
        // Verificar autenticación primero
        if (!verificarAutenticacion()) {
            mostrarLoginRequerido();
            return;
        }
        
        mostrarLoading(true);
        
        // Obtener datos del dashboard
        const data = await obtenerDatosDashboard();
        dashboardData = data;
        
        // Renderizar componentes
        renderizarUltimosValores(data.ultimos_valores);
        renderizarTablaDatos(data.ultimos_valores);
        renderizarGraficos(data.series_historicas);
        
        // Actualizar fecha de última actualización
        const ultimaActualizacion = new Date(data.ultima_actualizacion);
        document.getElementById('ultimaActualizacion').textContent = 
            ultimaActualizacion.toLocaleString('es-AR');
        
        // Obtener estadísticas
        const stats = await obtenerEstadisticas();
        document.getElementById('totalRegistros').textContent = 
            stats.total_datos.toLocaleString('es-AR');
        
        mostrarLoading(false);
        
    } catch (error) {
        console.error('Error al cargar dashboard:', error);
        mostrarLoading(false);
        
        // Si el error es 401 (no autorizado), mostrar login
        if (error.message && error.message.includes('401')) {
            localStorage.removeItem('authToken');
            mostrarLoginRequerido();
        } else {
            alert('Error al cargar los datos. Por favor, intente nuevamente.');
        }
    }
}

// ===========================================
// EVENT LISTENERS
// ===========================================

// Login form
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const alertDiv = document.getElementById('loginAlert');
    
    try {
        await login(email, password);
        
        // Ocultar alerta de error si existía
        alertDiv.classList.add('d-none');
        
        // Cerrar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
        modal.hide();
        
        // Recargar dashboard con los datos
        cargarDashboard();
        
    } catch (error) {
        console.error('Error de login:', error);
        alertDiv.textContent = 'Email o contraseña incorrectos';
        alertDiv.classList.remove('d-none');
    }
});

// ===========================================
// INICIALIZACIÓN
// ===========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Dashboard BCRA iniciado');
    
    // Verificar si hay token guardado
    const savedToken = localStorage.getItem('authToken');
    if (savedToken) {
        authToken = savedToken;
        // Mostrar botón de logout
        document.getElementById('logoutBtn').style.display = 'block';
    }
    
    // Cargar datos iniciales
    cargarDashboard();
    
    // Actualizar cada 5 minutos
    setInterval(cargarDashboard, 5 * 60 * 1000);
});

// Función para cerrar sesión
function cerrarSesion() {
    // Eliminar token
    localStorage.removeItem('authToken');
    authToken = null;
    
    // Ocultar botón de logout
    document.getElementById('logoutBtn').style.display = 'none';
    
    // Mostrar login
    mostrarLoginRequerido();
}

// Manejar errores globales
window.addEventListener('error', (event) => {
    console.error('Error global:', event.error);
});
