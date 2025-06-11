/**
 * DTF Charts JavaScript Module
 * Handles all chart-related functionality for the DTF application
 */

// Chart.js default configuration
Chart.defaults.color = '#ffffff';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
Chart.defaults.backgroundColor = 'rgba(255, 255, 255, 0.05)';

/**
 * Initialize DTF Line Chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} data - Chart data object with labels and datasets
 */
function initDTFChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return null;
    }

    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(4)}%`;
                        },
                        title: function(tooltipItems) {
                            return `Fecha: ${tooltipItems[0].label}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Fecha',
                        color: '#ffffff'
                    },
                    ticks: {
                        maxTicksLimit: 10,
                        color: '#ffffff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Tasa DTF (%)',
                        color: '#ffffff'
                    },
                    ticks: {
                        color: '#ffffff',
                        callback: function(value) {
                            return value.toFixed(4) + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            elements: {
                point: {
                    radius: 4,
                    hoverRadius: 6,
                    backgroundColor: '#ffffff',
                    borderWidth: 2
                },
                line: {
                    borderCapStyle: 'round',
                    borderJoinStyle: 'round'
                }
            }
        }
    };

    return new Chart(ctx, config);
}

/**
 * Initialize DTF Bar Chart for comparison data
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} data - Chart data object with labels and datasets
 */
function initDTFBarChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return null;
    }

    const config = {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(4)}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Período',
                        color: '#ffffff'
                    },
                    ticks: {
                        color: '#ffffff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Tasa DTF (%)',
                        color: '#ffffff'
                    },
                    ticks: {
                        color: '#ffffff',
                        callback: function(value) {
                            return value.toFixed(4) + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    };

    return new Chart(ctx, config);
}

/**
 * Create a simple statistics chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} rates - Array of rate objects
 */
function initStatsChart(canvasId, rates) {
    if (!rates || rates.length === 0) {
        console.warn('No rates data provided for stats chart');
        return null;
    }

    const rateValues = rates.map(r => r.tasa);
    const current = rateValues[0];
    const avg = rateValues.reduce((a, b) => a + b, 0) / rateValues.length;
    const max = Math.max(...rateValues);
    const min = Math.min(...rateValues);

    const data = {
        labels: ['Actual', 'Promedio', 'Máxima', 'Mínima'],
        datasets: [{
            label: 'Tasa DTF (%)',
            data: [current, avg, max, min],
            backgroundColor: [
                'rgba(13, 110, 253, 0.7)',   // Primary blue
                'rgba(108, 117, 125, 0.7)',  // Secondary gray
                'rgba(25, 135, 84, 0.7)',    // Success green
                'rgba(220, 53, 69, 0.7)'     // Danger red
            ],
            borderColor: [
                'rgb(13, 110, 253)',
                'rgb(108, 117, 125)',
                'rgb(25, 135, 84)',
                'rgb(220, 53, 69)'
            ],
            borderWidth: 2
        }]
    };

    return initDTFBarChart(canvasId, data);
}

/**
 * Update chart data dynamically
 * @param {Chart} chart - Chart.js instance
 * @param {Object} newData - New data object
 */
function updateChartData(chart, newData) {
    if (!chart || !newData) {
        console.error('Chart instance or new data not provided');
        return;
    }

    chart.data.labels = newData.labels;
    chart.data.datasets = newData.datasets;
    chart.update('active');
}

/**
 * Fetch and update DTF data from API
 * @param {Chart} chart - Chart.js instance to update
 * @param {number} limit - Number of records to fetch
 */
async function fetchAndUpdateDTFData(chart, limit = 30) {
    try {
        const response = await fetch(`/api/dtf/latest/${limit}`);
        const result = await response.json();
        
        if (result.success && result.data.length > 0) {
            const rates = result.data.reverse(); // Reverse to show chronological order
            
            const chartData = {
                labels: rates.map(rate => rate.fecha),
                datasets: [{
                    label: 'Tasa DTF (%)',
                    data: rates.map(rate => rate.tasa),
                    borderColor: 'rgb(13, 110, 253)',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            };
            
            updateChartData(chart, chartData);
            return true;
        } else {
            console.warn('No DTF data received from API');
            return false;
        }
    } catch (error) {
        console.error('Error fetching DTF data:', error);
        return false;
    }
}

/**
 * Format number as percentage with specified decimal places
 * @param {number} value - Number to format
 * @param {number} decimals - Number of decimal places (default: 4)
 * @returns {string} Formatted percentage string
 */
function formatPercentage(value, decimals = 4) {
    return parseFloat(value).toFixed(decimals) + '%';
}

/**
 * Calculate simple moving average
 * @param {Array} data - Array of numbers
 * @param {number} period - Period for moving average
 * @returns {Array} Array of moving averages
 */
function calculateMovingAverage(data, period) {
    if (!data || data.length < period) {
        return [];
    }
    
    const result = [];
    for (let i = period - 1; i < data.length; i++) {
        const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
        result.push(sum / period);
    }
    
    return result;
}

/**
 * Export chart as image
 * @param {Chart} chart - Chart.js instance
 * @param {string} filename - Filename for download
 */
function exportChartAsImage(chart, filename = 'dtf-chart.png') {
    if (!chart) {
        console.error('Chart instance not provided');
        return;
    }
    
    const url = chart.toBase64Image();
    const link = document.createElement('a');
    link.download = filename;
    link.href = url;
    link.click();
}

// Export functions for use in other scripts
window.DTFCharts = {
    initDTFChart,
    initDTFBarChart,
    initStatsChart,
    updateChartData,
    fetchAndUpdateDTFData,
    formatPercentage,
    calculateMovingAverage,
    exportChartAsImage
};
