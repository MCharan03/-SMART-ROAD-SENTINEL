document.addEventListener('DOMContentLoaded', function () {
    const startBtn = document.getElementById('start-scan-btn');
    const stopBtn = document.getElementById('stop-scan-btn');
    const eventLogBody = document.getElementById('event-log-body');
    
    // Keep track of logged event IDs to prevent duplicates
    const loggedEventIds = new Set();

    // --- Control Button Logic ---
    startBtn.addEventListener('click', async () => {
        try {
            await fetch('/api/control/start', { method: 'POST' });
            console.log("Scan started");
            startBtn.style.backgroundColor = '#00faff'; // Cyan for active
            stopBtn.style.backgroundColor = '';
        } catch (error) {
            console.error("Error starting scan:", error);
        }
    });

    stopBtn.addEventListener('click', async () => {
        try {
            await fetch('/api/control/stop', { method: 'POST' });
            console.log("Scan stopped");
            stopBtn.style.backgroundColor = '#ff4141'; // Red for stopped
            startBtn.style.backgroundColor = '';
        } catch (error)
        {
            console.error("Error stopping scan:", error);
        }
    });

    // --- Data Fetching and UI Update Logic ---
    function addEventToLog(defect) {
        // Create table row and cells
        const row = document.createElement('tr');
        const timeCell = document.createElement('td');
        const eventCell = document.createElement('td');
        const detailsCell = document.createElement('td');

        // Format and populate cells
        timeCell.textContent = new Date(defect.timestamp * 1000).toLocaleTimeString();
        eventCell.textContent = defect.type;
        
        // Create a link for the image
        const imageLink = document.createElement('a');
        imageLink.href = defect.image_url;
        imageLink.textContent = `Image (Conf: ${defect.confidence.toFixed(2)})`;
        imageLink.target = '_blank'; // Open in new tab
        detailsCell.appendChild(imageLink);

        row.style.animation = 'fadeIn 0.5s';
        eventLogBody.prepend(row); // Add to the top of the log

        // Limit the log to the last 20 entries
        if (eventLogBody.children.length > 20) {
            eventLogBody.removeChild(eventLogBody.lastChild);
        }
    }

    async function fetchStatus() {
        try {
            const response = await fetch('/api/status');
            if (!response.ok) {
                console.error("Failed to fetch status");
                return;
            }
            const data = await response.json();

            // Update telemetry (example for scanning status)
            const telemetryGpu = document.querySelector('#telemetry-container .telemetry-widget h2');
            if(telemetryGpu) {
                telemetryGpu.style.color = data.telemetry.is_scanning ? '#00faff' : '#e0e0e0';
            }

            // Update defect log
            if (data.defects) {
                data.defects.forEach(defect => {
                    if (!loggedEventIds.has(defect.id)) {
                        addEventToLog(defect);
                        loggedEventIds.add(defect.id);
                    }
                });
            }

        } catch (error) {
            console.error("Error fetching status:", error);
        }
    }

    // Fetch status every 2 seconds
    setInterval(fetchStatus, 2000);
});