/**
 * SMART-MED Ambulance Telemetry Client (Laptop 1)
 * Group Name: Biomed X (Session 2026-27)
 */

document.addEventListener('DOMContentLoaded', () => {
    // UI Elements - Vitals
    const elId = document.getElementById('p-id');
    const elName = document.getElementById('p-name');
    const elDemographics = document.getElementById('p-demographics');
    const elFrame = document.getElementById('p-frame');
    const elLastUpdate = document.getElementById('p-last-update');
    const elDataSourceTag = document.getElementById('data-source-tag');

    // Status Banner
    const elBanner = document.getElementById('status-banner');
    const elStatusTitle = document.getElementById('status-title');
    const elTriageLevel = document.getElementById('triage-level');
    const elStatusReasons = document.getElementById('status-reasons');

    // Vitals Displays
    const elValHr = document.getElementById('val-hr');
    const elTagHr = document.getElementById('tag-hr');
    const elValSpo2 = document.getElementById('val-spo2');
    const elTagSpo2 = document.getElementById('tag-spo2');
    const elValBp = document.getElementById('val-bp');
    const elTagBp = document.getElementById('tag-bp');
    const elValSys = document.getElementById('val-sys');
    const elValDia = document.getElementById('val-dia');
    const elValTemp = document.getElementById('val-temp');
    const elTagTemp = document.getElementById('tag-temp');
    const elValRr = document.getElementById('val-rr');
    const elTagRr = document.getElementById('tag-rr');

    // Transmission Controls & Diagnostics
    const elCountdownTimer = document.getElementById('countdown-timer');
    const elNextTxTime = document.getElementById('next-tx-time');
    const elProgressCircle = document.getElementById('timer-progress-circle');
    const elBtnSendNow = document.getElementById('btn-send-now');
    const elIntervalSelect = document.getElementById('interval-select');

    const elDiagLastTx = document.getElementById('diag-last-tx');
    const elDiagLastStatus = document.getElementById('diag-last-status');
    const elDiagTotalSent = document.getElementById('diag-total-sent');
    const elCsvFileInput = document.getElementById('csv-file-input');

    // Timer State
    let currentInterval = 180; // Default 3 minutes (180s)
    let timeRemaining = 180;
    let timerId = null;
    let isTransmitting = false;

    // SVG Circle Radius Math
    const circleRadius = 70;
    const circleCircumference = 2 * Math.PI * circleRadius;
    if (elProgressCircle) {
        elProgressCircle.style.strokeDasharray = `${circleCircumference} ${circleCircumference}`;
        elProgressCircle.style.strokeDashoffset = 0;
    }

    // Initialize Chart.js
    const ctx = document.getElementById('ambulanceChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Heart Rate (BPM)',
                    data: [],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.08)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    yAxisID: 'y-hr'
                },
                {
                    label: 'SpO2 (%)',
                    data: [],
                    borderColor: '#0284c7',
                    backgroundColor: 'rgba(2, 132, 199, 0.08)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    yAxisID: 'y-spo2'
                },
                {
                    label: 'Body Temp (°C)',
                    data: [],
                    borderColor: '#f59e0b',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    yAxisID: 'y-temp'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 400 },
            scales: {
                x: { grid: { display: false }, ticks: { font: { size: 10, family: 'JetBrains Mono' } } },
                'y-hr': { type: 'linear', position: 'left', min: 40, max: 180, title: { display: true, text: 'HR (BPM)', font: { size: 10 } } },
                'y-spo2': { type: 'linear', position: 'right', min: 75, max: 100, grid: { display: false }, title: { display: true, text: 'SpO2 (%)', font: { size: 10 } } },
                'y-temp': { type: 'linear', position: 'right', display: false, min: 34, max: 42 }
            },
            plugins: { legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } } }
        }
    });

    function updateProgressRing(secondsLeft, totalInterval) {
        if (!elProgressCircle) return;
        const progress = secondsLeft / totalInterval;
        const offset = circleCircumference - (progress * circleCircumference);
        elProgressCircle.style.strokeDashoffset = offset;
    }

    function formatTime(seconds) {
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    }

    // Fetch Vitals from Backend
    async function fetchVitals() {
        try {
            const res = await fetch('/api/vitals');
            if (!res.ok) throw new Error('Backend offline');
            const data = await res.json();

            // Render Patient Card
            elId.textContent = data.patient_id || 'P-7842';
            elName.textContent = data.patient_name || 'Anonymous Subject';
            elDemographics.textContent = `${data.age} Yrs / ${data.gender}`;
            elFrame.textContent = `Record ${data.record_index + 1} / ${data.total_records}`;
            
            const nowTime = new Date();
            elLastUpdate.textContent = nowTime.toLocaleTimeString();
            elDataSourceTag.innerHTML = `<i class="fa-solid fa-database"></i> ${data.data_source || 'SIMULATED DATA'}`;

            // Render Status Banner
            const status = data.status || 'NORMAL';
            elStatusTitle.textContent = `${status} PATIENT CONDITION`;
            elTriageLevel.textContent = data.emergency_level || 'LEVEL 3 - GREEN';
            elStatusReasons.textContent = (data.reasons && data.reasons.length) ? data.reasons.join(' | ') : 'Normal physiological signs.';

            elBanner.className = 'status-banner';
            if (status === 'CRITICAL') {
                elBanner.classList.add('status-critical');
            } else if (status === 'WARNING') {
                elBanner.classList.add('status-warning');
            } else {
                elBanner.classList.add('status-normal');
            }

            // Render Vitals Display Cards
            elValHr.textContent = data.heart_rate;
            elValSpo2.textContent = data.spo2;
            elValBp.textContent = data.blood_pressure;
            elValSys.textContent = data.systolic_bp;
            elValDia.textContent = data.diastolic_bp;
            elValTemp.textContent = data.temperature;
            elValRr.textContent = data.respiratory_rate;

            updateTag(elTagHr, data.heart_rate, 60, 100, 45, 130);
            updateTag(elTagSpo2, data.spo2, 95, 100, 90, 100);
            updateTag(elTagTemp, data.temperature, 36.5, 37.5, 35.5, 39.0);
            updateTag(elTagRr, data.respiratory_rate, 12, 20, 9, 28);

            // Diagnostics info
            if (data.last_transmission_time) {
                elDiagLastTx.textContent = new Date(data.last_transmission_time).toLocaleTimeString();
            }
            if (data.last_transmission_status) {
                elDiagLastStatus.textContent = data.last_transmission_status;
            }
            elDiagTotalSent.textContent = `${data.total_transmissions_sent} Records`;

            // Update Chart
            const timeLabel = nowTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            chart.data.labels.push(timeLabel);
            chart.data.datasets[0].data.push(data.heart_rate);
            chart.data.datasets[1].data.push(data.spo2);
            chart.data.datasets[2].data.push(data.temperature);

            if (chart.data.labels.length > 15) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
                chart.data.datasets[1].data.shift();
                chart.data.datasets[2].data.shift();
            }
            chart.update();

        } catch (err) {
            console.warn("Failed to fetch vitals frame:", err);
        }
    }

    function updateTag(el, val, normalMin, normalMax, critMin, critMax) {
        if (val < critMin || val > critMax) {
            el.className = "vital-status-tag tag-critical";
            el.textContent = "CRITICAL";
        } else if (val < normalMin || val > normalMax) {
            el.className = "vital-status-tag tag-warning";
            el.textContent = "WARNING";
        } else {
            el.className = "vital-status-tag tag-normal";
            el.textContent = "NORMAL";
        }
    }

    // Auto Transmission Loop
    function startCountdownEngine() {
        if (timerId) clearInterval(timerId);

        timerId = setInterval(() => {
            timeRemaining--;

            if (timeRemaining <= 0) {
                timeRemaining = currentInterval;
                triggerAutoTransmission();
            }

            elCountdownTimer.textContent = formatTime(timeRemaining);
            updateProgressRing(timeRemaining, currentInterval);

            const nextTxDate = new Date(Date.now() + timeRemaining * 1000);
            elNextTxTime.textContent = `Target: ${nextTxDate.toLocaleTimeString()}`;
        }, 1000);
    }

    async function triggerAutoTransmission() {
        if (isTransmitting) return;
        isTransmitting = true;
        elDiagLastStatus.textContent = "TRANSMITTING TELEMETRY...";

        try {
            const res = await fetch('/api/transmit_now', { method: 'POST' });
            const data = await res.json();

            if (data.success) {
                elDiagLastStatus.textContent = "SUCCESSFUL TRANSMISSION";
            } else {
                elDiagLastStatus.textContent = "TRANSMISSION FAILED";
            }
        } catch (e) {
            elDiagLastStatus.textContent = "NETWORK ERROR";
        } finally {
            isTransmitting = false;
            fetchVitals();
        }
    }

    // Manual 'SEND NOW' Button
    elBtnSendNow.addEventListener('click', async () => {
        elBtnSendNow.disabled = true;
        elBtnSendNow.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> TRANSMITTING...`;

        await triggerAutoTransmission();

        timeRemaining = currentInterval;
        elCountdownTimer.textContent = formatTime(timeRemaining);
        updateProgressRing(timeRemaining, currentInterval);

        setTimeout(() => {
            elBtnSendNow.disabled = false;
            elBtnSendNow.innerHTML = `<i class="fa-solid fa-paper-plane"></i> SEND LATEST DATA NOW`;
        }, 1000);
    });

    // Interval Selector (180s, 60s, 30s, 10s)
    elIntervalSelect.addEventListener('change', async (e) => {
        currentInterval = parseInt(e.target.value, 10);
        timeRemaining = currentInterval;
        elCountdownTimer.textContent = formatTime(timeRemaining);
        updateProgressRing(timeRemaining, currentInterval);

        await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transmission_interval: currentInterval })
        });
    });

    // CSV File Upload
    if (elCsvFileInput) {
        elCsvFileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch('/api/upload_csv', { method: 'POST', body: formData });
                const data = await res.json();
                if (res.ok) {
                    alert(`Dataset Loaded: ${data.message}`);
                    fetchVitals();
                } else {
                    alert(`Upload Error: ${data.error}`);
                }
            } catch (err) {
                alert(`File upload failed: ${err.message}`);
            }
        });
    }

    // Initial Startup
    fetchVitals();
    setInterval(fetchVitals, 2000);
    startCountdownEngine();
});
