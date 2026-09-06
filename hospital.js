/**
 * SMART-MED Hospital Receiving Dashboard Client (Laptop 2)
 * Group Name: Biomed X (Session 2026-27)
 */

document.addEventListener('DOMContentLoaded', () => {
    // UI Elements - Patient Info
    const elHospId = document.getElementById('hosp-p-id');
    const elHospName = document.getElementById('hosp-p-name');
    const elHospDemographics = document.getElementById('hosp-p-demographics');
    const elHospReceivedTime = document.getElementById('hosp-p-received-time');
    const elHospSource = document.getElementById('hosp-p-source');
    const elConnectionPill = document.getElementById('connection-pill');

    // Status Banner
    const elBanner = document.getElementById('hosp-status-banner');
    const elStatusTitle = document.getElementById('hosp-status-title');
    const elTriageLevel = document.getElementById('hosp-triage-level');
    const elStatusReasons = document.getElementById('hosp-status-reasons');

    // Vitals Cards
    const elValHr = document.getElementById('hosp-val-hr');
    const elTagHr = document.getElementById('hosp-tag-hr');
    const elAlertHr = document.getElementById('alert-hr');
    const elVcardHr = document.getElementById('vcard-hr');

    const elValSpo2 = document.getElementById('hosp-val-spo2');
    const elTagSpo2 = document.getElementById('hosp-tag-spo2');
    const elAlertSpo2 = document.getElementById('alert-spo2');
    const elVcardSpo2 = document.getElementById('vcard-spo2');

    const elValBp = document.getElementById('hosp-val-bp');
    const elTagBp = document.getElementById('hosp-tag-bp');
    const elAlertBp = document.getElementById('alert-bp');

    const elValTemp = document.getElementById('hosp-val-temp');
    const elTagTemp = document.getElementById('hosp-tag-temp');
    const elAlertTemp = document.getElementById('alert-temp');

    const elValRr = document.getElementById('hosp-val-rr');
    const elTagRr = document.getElementById('hosp-tag-rr');
    const elAlertRr = document.getElementById('alert-rr');

    // History Table & Actions
    const elHistoryTbody = document.getElementById('history-tbody');
    const elBtnRefreshHistory = document.getElementById('btn-refresh-history');

    // Timer & Diagnostics
    const elHospCountdown = document.getElementById('hosp-countdown');
    const elHospLastReceivedLabel = document.getElementById('hosp-last-received-label');
    const elProgressCircle = document.getElementById('hosp-progress-circle');
    const elTotalPackets = document.getElementById('hosp-total-packets');
    const elApiStatus = document.getElementById('hosp-api-status');

    let lastTransmissionId = null;
    let expectedInterval = 180; // Default 3 minutes
    let timeRemaining = 180;
    let countdownTimerId = null;

    // Circle Math
    const circleRadius = 70;
    const circleCircumference = 2 * Math.PI * circleRadius;
    if (elProgressCircle) {
        elProgressCircle.style.strokeDasharray = `${circleCircumference} ${circleCircumference}`;
        elProgressCircle.style.strokeDashoffset = 0;
    }

    // Chart.js Setup
    const ctx = document.getElementById('hospitalChart').getContext('2d');
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
                    label: 'SpO2 Saturation (%)',
                    data: [],
                    borderColor: '#0284c7',
                    backgroundColor: 'rgba(2, 132, 199, 0.08)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    yAxisID: 'y-spo2'
                },
                {
                    label: 'Temperature (°C)',
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
                'y-hr': { type: 'linear', position: 'left', min: 40, max: 180, title: { display: true, text: 'BPM', font: { size: 10 } } },
                'y-spo2': { type: 'linear', position: 'right', min: 75, max: 100, grid: { display: false }, title: { display: true, text: 'SpO2 %', font: { size: 10 } } },
                'y-temp': { type: 'linear', position: 'right', display: false, min: 34, max: 42 }
            },
            plugins: { legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } } }
        }
    });

    function formatTime(seconds) {
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    }

    function updateProgressRing(secondsLeft, totalInterval) {
        if (!elProgressCircle) return;
        const progress = secondsLeft / totalInterval;
        const offset = circleCircumference - (progress * circleCircumference);
        elProgressCircle.style.strokeDashoffset = offset;
    }

    // Fetch Latest Telemetry Payload
    async function fetchLatestTelemetry() {
        try {
            const res = await fetch('/api/hospital/latest');
            if (!res.ok) throw new Error('API offline');
            const result = await res.json();

            if (result.status === 'NO_DATA') {
                elHospId.textContent = 'Awaiting Telemetry...';
                elHospName.textContent = 'No ambulance payload yet';
                elHospReceivedTime.textContent = '--:--:--';
                elConnectionPill.className = 'status-pill-online';
                elConnectionPill.innerHTML = `<i class="fa-solid fa-circle"></i> LISTENING FOR TELEMETRY`;
                return;
            }

            const data = result.data;
            if (!data) return;

            elConnectionPill.className = 'status-pill-online';
            elConnectionPill.innerHTML = `<i class="fa-solid fa-circle"></i> ACTIVE TELEMETRY`;
            elApiStatus.className = 'diag-val online';
            elApiStatus.innerHTML = `<i class="fa-solid fa-check-circle"></i> ONLINE`;

            // If a new transmission packet arrived!
            if (data.id !== lastTransmissionId) {
                lastTransmissionId = data.id;
                timeRemaining = expectedInterval;
                elHospLastReceivedLabel.textContent = `Last: ${new Date(data.received_at).toLocaleTimeString()}`;
            }

            // Populate Metadata
            elHospId.textContent = data.patient_id || 'P-7842';
            elHospName.textContent = data.patient_name || 'Anonymous Subject';
            elHospDemographics.textContent = `${data.age} Yrs / ${data.gender}`;
            elHospReceivedTime.textContent = new Date(data.received_at).toLocaleTimeString();
            elHospSource.textContent = data.data_source || 'Ambulance Telemetry';

            // Populate Banner
            const status = data.patient_status || 'NORMAL';
            elStatusTitle.textContent = `${status} PATIENT CONDITION`;
            elTriageLevel.textContent = data.emergency_level || 'LEVEL 3 - GREEN';
            elStatusReasons.textContent = data.reasons || 'All vital signs normal.';

            elBanner.className = 'status-banner';
            if (status === 'CRITICAL') {
                elBanner.classList.add('status-critical');
            } else if (status === 'WARNING') {
                elBanner.classList.add('status-warning');
            } else {
                elBanner.classList.add('status-normal');
            }

            // Populate Vitals Values & Abnormal Highlighting
            elValHr.textContent = data.heart_rate;
            elValSpo2.textContent = data.spo2;
            elValBp.textContent = data.blood_pressure || `${data.systolic_bp}/${data.diastolic_bp}`;
            elValTemp.textContent = data.temperature;
            elValRr.textContent = data.respiratory_rate;

            updateHospTag(elTagHr, elAlertHr, elVcardHr, data.heart_rate, 60, 100, 45, 130, "BPM Abnormal");
            updateHospTag(elTagSpo2, elAlertSpo2, elVcardSpo2, data.spo2, 95, 100, 90, 100, "SpO2 Low");
            updateHospTag(elTagTemp, elAlertTemp, null, data.temperature, 36.5, 37.5, 35.5, 39.0, "Temp Fever");
            updateHospTag(elTagRr, elAlertRr, null, data.respiratory_rate, 12, 20, 9, 28, "RR Distress");

        } catch (err) {
            console.warn("Error querying receiver API:", err);
            elConnectionPill.className = "status-pill-online text-danger";
            elConnectionPill.innerHTML = `<i class="fa-solid fa-circle"></i> DISCONNECTED`;
            elApiStatus.className = "diag-val text-danger";
            elApiStatus.textContent = "OFFLINE";
        }
    }

    function updateHospTag(tagEl, alertEl, cardEl, val, nMin, nMax, cMin, cMax, alertText) {
        if (cardEl) cardEl.classList.remove('card-alert-pulse');

        if (val < cMin || val > cMax) {
            tagEl.className = "vital-status-tag tag-critical";
            tagEl.textContent = "CRITICAL";
            alertEl.textContent = alertText;
            if (cardEl) cardEl.classList.add('card-alert-pulse');
        } else if (val < nMin || val > nMax) {
            tagEl.className = "vital-status-tag tag-warning";
            tagEl.textContent = "WARNING";
            alertEl.textContent = "Borderline";
        } else {
            tagEl.className = "vital-status-tag tag-normal";
            tagEl.textContent = "NORMAL";
            alertEl.textContent = "--";
        }
    }

    // Fetch Full Transmission History Log Table
    async function fetchTransmissionHistory() {
        try {
            const res = await fetch('/api/hospital/history?limit=50');
            if (!res.ok) return;
            const result = await res.json();
            const history = result.history || [];

            elTotalPackets.textContent = `${result.count || history.length} Transmissions`;

            if (history.length === 0) {
                elHistoryTbody.innerHTML = `
                    <tr>
                        <td colspan="10" class="text-center text-muted" style="padding: 2rem;">
                            <i class="fa-solid fa-satellite-dish fa-spin text-teal" style="font-size: 1.5rem;"></i><br>
                            Awaiting initial 3-minute telemetry payload from Ambulance...
                        </td>
                    </tr>`;
                return;
            }

            // Build Table Rows
            let html = '';
            chart.data.labels = [];
            chart.data.datasets[0].data = [];
            chart.data.datasets[1].data = [];
            chart.data.datasets[2].data = [];

            const chronHistory = [...history].reverse();
            chronHistory.forEach(row => {
                const timeStr = new Date(row.received_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                chart.data.labels.push(timeStr);
                chart.data.datasets[0].data.push(row.heart_rate);
                chart.data.datasets[1].data.push(row.spo2);
                chart.data.datasets[2].data.push(row.temperature);
            });
            chart.update();

            history.forEach((row) => {
                const status = row.patient_status || 'NORMAL';
                let rowClass = '';
                let statusBadge = `<span class="vital-status-tag tag-normal">NORMAL</span>`;

                if (status === 'CRITICAL') {
                    rowClass = 'row-critical';
                    statusBadge = `<span class="vital-status-tag tag-critical"><i class="fa-solid fa-triangle-exclamation"></i> CRITICAL</span>`;
                } else if (status === 'WARNING') {
                    rowClass = 'row-warning';
                    statusBadge = `<span class="vital-status-tag tag-warning">WARNING</span>`;
                }

                const receivedTime = new Date(row.received_at).toLocaleTimeString();

                html += `
                    <tr class="${rowClass}">
                        <td>#${row.id}</td>
                        <td><strong>${receivedTime}</strong></td>
                        <td>${row.patient_id}</td>
                        <td class="${row.heart_rate > 100 ? 'text-danger font-bold' : ''}">${row.heart_rate} BPM</td>
                        <td class="${row.spo2 < 92 ? 'text-danger font-bold' : ''}">${row.spo2}%</td>
                        <td>${row.blood_pressure || `${row.systolic_bp}/${row.diastolic_bp}`}</td>
                        <td>${row.temperature}°C</td>
                        <td>${row.respiratory_rate} bpm</td>
                        <td>${statusBadge}</td>
                        <td><span class="text-teal font-bold"><i class="fa-solid fa-circle-check"></i> RECEIVED</span></td>
                    </tr>
                `;
            });

            elHistoryTbody.innerHTML = html;

        } catch (err) {
            console.warn("Failed to fetch transmission history log:", err);
        }
    }

    // Countdown Timer Loop
    function startTimerLoop() {
        if (countdownTimerId) clearInterval(countdownTimerId);

        countdownTimerId = setInterval(() => {
            timeRemaining--;
            if (timeRemaining < 0) {
                timeRemaining = expectedInterval;
            }
            elHospCountdown.textContent = formatTime(timeRemaining);
            updateProgressRing(timeRemaining, expectedInterval);
        }, 1000);
    }

    // Refresh History Button
    if (elBtnRefreshHistory) {
        elBtnRefreshHistory.addEventListener('click', () => {
            fetchLatestTelemetry();
            fetchTransmissionHistory();
        });
    }

    // Initial Startup
    fetchLatestTelemetry();
    fetchTransmissionHistory();

    setInterval(fetchLatestTelemetry, 3000);
    setInterval(fetchTransmissionHistory, 5000);
    startTimerLoop();
});
