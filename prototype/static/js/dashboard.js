document.addEventListener('DOMContentLoaded', function () {
    // Main Telemetry Elements
    const speedValue = document.getElementById('speed-value');
    const gpsValue = document.getElementById('gps-value');
    const suspensionStatus = document.getElementById('suspension-status');
    const potholeAlert = document.getElementById('pothole-alert');
    const eventLogBody = document.getElementById('event-log-body');

    // Status Indicator Elements
    const obdStatus = document.getElementById('obd-status');
    const gpsStatus = document.getElementById('gps-status');
    const imuStatus = document.getElementById('imu-status');

    // --- Chart.js G-Force Monitor ---
    const ctx = document.getElementById('g-force-chart').getContext('2d');
    const gForceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array(30).fill(''),
            datasets: [{
                label: 'G-Force',
                data: Array(30).fill(0),
                borderColor: '#ff00ff',
                backgroundColor: 'rgba(255, 0, 255, 0.1)',
                borderWidth: 2,
                pointRadius: 0,
                tension: 0.4,
                fill: true,
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    grid: { color: '#2a2a3a' },
                    ticks: { color: '#e0e0e0' }
                },
                x: {
                    grid: { display: false },
                    ticks: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            },
            animation: {
                duration: 200
            }
        }
    });

    function updateGForceChart(newValue) {
        gForceChart.data.datasets[0].data.push(newValue);
        gForceChart.data.datasets[0].data.shift();
        gForceChart.update();
    }

    function addEventToLog(timestamp, event, details) {
        const row = document.createElement('tr');
        const timeCell = document.createElement('td');
        const eventCell = document.createElement('td');
        const detailsCell = document.createElement('td');

        timeCell.textContent = new Date(timestamp).toLocaleTimeString();
        eventCell.textContent = event;
        detailsCell.textContent = details;

        row.style.animation = 'fadeIn 0.5s';
        eventLogBody.prepend(row);

        if (eventLogBody.children.length > 10) {
            eventLogBody.removeChild(eventLogBody.lastChild);
        }
    }

    function updateStatusIndicator(element, status) {
        if (!element) return;
        element.textContent = status;
        element.style.backgroundColor = 'transparent';
        element.style.color = '#e0e0e0';

        if (status === 'SIMULATED') {
            element.style.color = '#ffd700'; // Gold
        } else if (status === 'DISCONNECTED' || status === 'ERROR') {
            element.style.backgroundColor = '#ff4141'; // Red
            element.style.color = 'white';
        } else if (status === 'LIVE') {
            element.style.backgroundColor = '#00faff'; // Cyan
            element.style.color = '#0a0a0f';
        }
    }

    async function fetchData() {
        try {
            const response = await fetch('/data');
            const data = await response.json();

            // Update telemetry values
            speedValue.textContent = `${data.current_speed.toFixed(1)} km/h`;
            gpsValue.textContent = `${data.latitude.toFixed(4)}, ${data.longitude.toFixed(4)}`;
            suspensionStatus.textContent = data.suspension_status;
            if (data.suspension_status === 'STABILIZING') {
                suspensionStatus.style.color = '#ff4141';
            } else {
                suspensionStatus.style.color = '#00faff';
            }

            // Update status indicators
            updateStatusIndicator(obdStatus, data.obd_status);
            updateStatusIndicator(gpsStatus, data.gps_status);
            updateStatusIndicator(imuStatus, data.imu_status);

            // Update G-Force Chart
            updateGForceChart(data.g_force);

            // Handle pothole alert
            if (data.pothole_detected) {
                potholeAlert.classList.remove('hidden');
            } else {
                potholeAlert.classList.add('hidden');
            }

            // Check for new events
            if (data.latest_event) {
                const firstRow = eventLogBody.firstChild;
                if (!firstRow || firstRow.cells[0].textContent !== new Date(data.latest_event.timestamp).toLocaleTimeString()) {
                    addEventToLog(data.latest_event.timestamp, data.latest_event.type, data.latest_event.details);
                }
            }

        } catch (error) {
            console.error("Error fetching data:", error);
            updateStatusIndicator(obdStatus, 'ERROR');
            updateStatusIndicator(gpsStatus, 'ERROR');
            updateStatusIndicator(imuStatus, 'ERROR');
        }
    }

    setInterval(fetchData, 500);
});
