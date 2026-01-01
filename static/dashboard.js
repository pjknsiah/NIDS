// Charts
let trafficChart;
let attackChart;

const ctxTraffic = document.getElementById('trafficChart').getContext('2d');
const ctxAttack = document.getElementById('attackChart').getContext('2d');

function initCharts() {
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';

    trafficChart = new Chart(ctxTraffic, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Packets/sec',
                data: [],
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    attackChart = new Chart(ctxAttack, {
        type: 'doughnut',
        data: {
            labels: ['Normal', 'Malicious'],
            datasets: [{
                data: [100, 0],
                backgroundColor: ['#10b981', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%'
        }
    });
}

async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        // Update Text Stats
        document.getElementById('total-packets').textContent = data.total_packets;
        document.getElementById('threats-detected').textContent = data.threats_detected;
        document.getElementById('threat-level').textContent = data.threat_level;

        const levelColor = data.threat_level === 'Critical' ? '#ef4444' : (data.threat_level === 'Elevated' ? '#f59e0b' : '#10b981');
        document.getElementById('threat-level').style.color = levelColor;

        // Update Traffic Chart (mock real-time feel)
        const now = new Date().toLocaleTimeString();
        if (trafficChart.data.labels.length > 20) {
            trafficChart.data.labels.shift();
            trafficChart.data.datasets[0].data.shift();
        }
        trafficChart.data.labels.push(now);
        // Add random variation to total packets for the chart "speed" visualization
        // In a real app we'd get "packets per second" from the API
        const trafficValue = Math.floor(Math.random() * 50) + 10;
        trafficChart.data.datasets[0].data.push(trafficValue);
        trafficChart.update();

        // Update Attack Chart
        const total = data.total_packets || 1;
        const threats = data.threats_detected;
        const normal = total - threats;

        attackChart.data.datasets[0].data = [normal, threats];
        attackChart.update();

    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

async function updateAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const alerts = await response.json();

        const tbody = document.getElementById('alerts-body');
        tbody.innerHTML = '';

        alerts.slice(0, 10).forEach(alert => {
            const row = document.createElement('tr');

            // Badge color
            let badgeClass = 'badge-low';
            if (alert.severity === 'High') badgeClass = 'badge-high';
            else if (alert.severity === 'Medium') badgeClass = 'badge-medium';

            row.innerHTML = `
                <td>#${alert.id}</td>
                <td>${alert.timestamp}</td>
                <td>${alert.type}</td>
                <td><span class="badge ${badgeClass}">${alert.severity}</span></td>
                <td>${alert.score}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching alerts:', error);
    }
}

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    initCharts();

    // Poll APIs
    setInterval(updateStats, 2000);
    setInterval(updateAlerts, 2000); // 2 seconds

    updateStats();
    updateAlerts();
});
