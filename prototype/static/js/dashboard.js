document.addEventListener('DOMContentLoaded', function () {
    const startBtn = document.getElementById('start-camera-btn');
    const stopBtn = document.getElementById('stop-camera-btn');

    startBtn.addEventListener('click', () => {
        fetch('/start_camera', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.status);
                startBtn.style.backgroundColor = '#00faff';
                stopBtn.style.backgroundColor = '';
            })
            .catch(error => console.error('Error:', error));
    });

    stopBtn.addEventListener('click', () => {
        fetch('/stop_camera', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.status);
                stopBtn.style.backgroundColor = '#ff4141';
                startBtn.style.backgroundColor = '';
            })
            .catch(error => console.error('Error:', error));
    });

    // Main Telemetry Elements
    const gaugeNeedle = document.querySelector('.gauge-needle');
    const gaugeValue = document.querySelector('.gauge-value');
    const gpsValue = document.getElementById('gps-value');
    const suspensionStatus = document.getElementById('suspension-status');
    const potholeAlert = document.getElementById('pothole-alert');
    const eventLogBody = document.getElementById('event-log-body');
    const potholeAudio = document.getElementById('pothole-audio-alert'); // Get audio element

    // Status Indicator Elements
    const obdStatus = document.getElementById('obd-status');
    const gpsStatus = document.getElementById('gps-status');
    const imuStatus = document.getElementById('imu-status');

    // Global flag to prevent repeated audio alerts for the same continuous detection
    let lastPotholeDetected = false;


    // --- Chart.js G-Force Monitor ---
    const gForceChartElement = document.getElementById('g-force-chart');
    let gForceChart; // Declare gForceChart here
    if (gForceChartElement) {
        const ctx = gForceChartElement.getContext('2d');
        gForceChart = new Chart(ctx, { // Assign to gForceChart
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
                responsive: true,
                maintainAspectRatio: false,
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
    }


    function updateGForceChart(gForceHistory, impactEventsHistory) {
        if (gForceChart) {
            // Update G-Force data
            gForceChart.data.labels = Array(gForceHistory.length).fill(''); // Clear labels or use timestamps if needed
            gForceChart.data.datasets[0].data = gForceHistory;

            // Clear previous impact markers
            if (gForceChart.data.datasets.length > 1) {
                gForceChart.data.datasets.pop();
            }

            // Add impact markers if there are events
            if (impactEventsHistory && impactEventsHistory.length > 0) {
                // Map impact events to data points, assuming impactEventsHistory contains indices or can be aligned
                const impactData = impactEventsHistory.map((event, index) => ({
                    x: gForceHistory.length - impactEventsHistory.length + index, // Approximate index for plotting
                    y: event.g_force
                }));
                gForceChart.data.datasets.push({
                    type: 'scatter', // Use scatter for individual points
                    label: 'Impact',
                    data: impactData,
                    backgroundColor: '#ff4141', // Red for impacts
                    borderColor: '#ff4141',
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    showLine: false,
                    fill: false,
                });
            }

            gForceChart.update();
        }
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

            // Update speed gauge
            const maxSpeed = 100; // Max speed for gauge (km/h)
            const speed = data.current_speed;
            const rotation = -90 + (speed / maxSpeed) * 180;
            if (gaugeNeedle) {
                gaugeNeedle.style.transform = `translateX(-50%) rotate(${rotation}deg)`;
            }
            if (gaugeValue) {
                gaugeValue.textContent = speed.toFixed(0);
            }
            
            // Update other telemetry values
            gpsValue.textContent = `${data.latitude.toFixed(4)}, ${data.longitude.toFixed(4)}`;
            // Update suspension status with visual classes
            suspensionStatus.textContent = data.suspension_status; // Keep text for accessibility
            suspensionStatus.classList.remove('status-active', 'status-stabilizing', 'status-default'); // Clean previous classes
            if (data.suspension_status === 'ACTIVE') {
                suspensionStatus.classList.add('status-active');
            } else if (data.suspension_status === 'STABILIZING') {
                suspensionStatus.classList.add('status-stabilizing');
            } else {
                suspensionStatus.classList.add('status-default'); // Fallback or for other states
            }

            // Update status indicators
            updateStatusIndicator(obdStatus, data.obd_status);
            updateStatusIndicator(gpsStatus, data.gps_status);
            updateStatusIndicator(imuStatus, data.imu_status);

            // Update G-Force Chart
            // The g_force_history from the backend is a Python deque, which becomes an array in JS.
            // Ensure to convert it to a regular array if not already.
            const gForceHistoryArray = Array.from(data.g_force_history);
            updateGForceChart(gForceHistoryArray, data.impact_events_history);

            // Handle pothole alert
            if (data.pothole_detected) {
                potholeAlert.classList.remove('hidden');
                // Remove existing severity classes
                potholeAlert.classList.remove('severity-low', 'severity-medium', 'severity-high');

                // Apply new severity class based on confidence
                const confidence = data.pothole_confidence;
                if (confidence < 0.6) {
                    potholeAlert.classList.add('severity-low');
                } else if (confidence < 0.8) {
                    potholeAlert.classList.add('severity-medium');
                } else {
                    potholeAlert.classList.add('severity-high');
                }

                if (!lastPotholeDetected && potholeAudio) {
                    potholeAudio.play();
                }
                lastPotholeDetected = true;
            } else {
                potholeAlert.classList.add('hidden');
                potholeAlert.classList.remove('severity-low', 'severity-medium', 'severity-high'); // Clean up
                lastPotholeDetected = false;
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

    // --- Historical Data View Logic ---
    const dateFilter = document.getElementById('date-filter');
    const applyFilterBtn = document.getElementById('apply-filter');
    const resetFilterBtn = document.getElementById('reset-filter');
    const historicalDataBody = document.getElementById('historical-data-body');

    // --- Defect Details Modal Elements ---
    const defectModal = document.getElementById('defect-modal');
    const closeButton = defectModal ? defectModal.querySelector('.close-button') : null;
    const modalDefectImage = document.getElementById('modal-defect-image');
    const modalDefectId = document.getElementById('modal-defect-id');
    const modalDefectType = document.getElementById('modal-defect-type');
    const modalDefectConfidence = document.getElementById('modal-defect-confidence');
    const modalDefectTimestamp = document.getElementById('modal-defect-timestamp');
    const modalDefectLocation = document.getElementById('modal-defect-location');


    // Function to fetch historical data and populate the table
    async function fetchHistoricalData(date = null) {
        try {
            let url = '/api/historical_potholes';
            if (date) {
                url += `?date_filter=${date}`;
            }
            const response = await fetch(url);
            const potholes = await response.json();

            historicalDataBody.innerHTML = ''; // Clear existing data

            if (potholes.length === 0) {
                historicalDataBody.innerHTML = '<tr><td colspan="5">No historical data available.</td></tr>';
            } else {
                potholes.forEach(pothole => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${new Date(pothole.timestamp).toLocaleString()}</td>
                        <td>${pothole.latitude.toFixed(4)}</td>
                        <td>${pothole.longitude.toFixed(4)}</td>
                        <td>${pothole.confidence ? pothole.confidence.toFixed(2) : 'N/A'}</td>
                        <td><button class="view-details-btn" data-defect-id="${pothole.id}">View Details</button></td>
                    `;
                    historicalDataBody.appendChild(row);
                });
            }
        } catch (error) {
            console.error("Error fetching historical data:", error);
            historicalDataBody.innerHTML = '<tr><td colspan="5">Error loading historical data.</td></tr>';
        }
    }

    async function showDefectDetails(defectId) {
        if (!defectModal) return;

        try {
            const response = await fetch(`/api/defect_details/${defectId}`);
            const data = await response.json();

            if (data.error) {
                console.error("Error fetching defect details:", data.error);
                return;
            }

            modalDefectId.textContent = data.id;
            modalDefectType.textContent = 'Pothole'; // Assuming only Pothole for now
            modalDefectConfidence.textContent = data.confidence ? data.confidence.toFixed(2) : 'N/A';
            modalDefectTimestamp.textContent = new Date(data.timestamp).toLocaleString();
            modalDefectLocation.textContent = `${data.latitude.toFixed(4)}, ${data.longitude.toFixed(4)}`;
            
            if (modalDefectImage && data.image_url) {
                modalDefectImage.src = data.image_url;
                modalDefectImage.alt = `Pothole at ${data.latitude.toFixed(4)}, ${data.longitude.toFixed(4)}`;
            } else if (modalDefectImage) {
                modalDefectImage.src = '';
                modalDefectImage.alt = 'No image available';
            }

            defectModal.classList.remove('hidden'); // Show the modal

        } catch (error) {
            console.error("Failed to fetch defect details:", error);
        }
    }

    function hideDefectDetails() {
        if (defectModal) {
            defectModal.classList.add('hidden'); // Hide the modal
        }
    }

    // Event listener for close button
    if (closeButton) {
        closeButton.addEventListener('click', hideDefectDetails);
    }

    // Event listener for clicking outside the modal content
    if (defectModal) {
        defectModal.addEventListener('click', (event) => {
            if (event.target === defectModal) {
                hideDefectDetails();
            }
        });
    }

    // Initial load of historical data
    fetchHistoricalData();

    applyFilterBtn.addEventListener('click', () => {
        fetchHistoricalData(dateFilter.value);
    });

    resetFilterBtn.addEventListener('click', () => {
        dateFilter.value = ''; // Clear date input
        fetchHistoricalData();
    });

    // Attach event listeners to dynamically added buttons in the event log (real-time)
    eventLogBody.addEventListener('click', (event) => {
        if (event.target.classList.contains('view-details-btn')) {
            showDefectDetails(event.target.dataset.defectId);
        }
    });

    // Event listener for historical data table to show details
    historicalDataBody.addEventListener('click', (event) => {
        if (event.target.classList.contains('view-details-btn')) {
            showDefectDetails(event.target.dataset.defectId);
        }
    });

});
