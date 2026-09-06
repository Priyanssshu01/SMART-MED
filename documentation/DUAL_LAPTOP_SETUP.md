# SMART-MED Dual-Laptop Network Setup Guide
**Group Name**: Biomed X (Session 2026–27)  
**Project Leader**: Sayandeep Chakroborty  
**Members**: Uttam Kumar Mahto, Prashant Kumar, Priyanshu Jaiswal  

---

## 1. Objective

This guide explains how to connect **TWO LAPTOPS** over a shared Wi-Fi network or mobile hotspot for your Semester-5 project presentation.

- **LAPTOP 1**: AMBULANCE SIDE (Runs Ambulance Simulator & UI)
- **LAPTOP 2**: HOSPITAL SIDE (Runs Central REST API Server & Hospital Receiving Dashboard)

---

## 2. Network Prerequisites

1. Connect both Laptop 1 and Laptop 2 to the **same Wi-Fi network** or **mobile hotspot**.
2. Find the Local IP Address of **LAPTOP 2**:
   - On Laptop 2, open Command Prompt (`cmd`) or PowerShell.
   - Run: `ipconfig`
   - Note the **IPv4 Address** (e.g. `192.168.1.50` or `192.168.43.120`).

---

## 3. Step-by-Step Launch Procedure

### STEP A: Setup LAPTOP 2 (Hospital Side)

1. Open terminal on Laptop 2 and navigate to project folder:
   ```bash
   cd SMART-MED
   ```
2. Start the **Central Server API & Database**:
   ```bash
   python server/app.py
   ```
   *Server will listen on `http://0.0.0.0:5000`.*

3. Open a second terminal window on Laptop 2 and start the **Hospital Receiving Dashboard**:
   ```bash
   python hospital/app.py
   ```
   *Hospital UI will listen on `http://0.0.0.0:5002`.*

4. Open Web Browser on Laptop 2:
   ```
   http://localhost:5002
   ```
   *You will see the "HOSPITAL RECEIVING DASHBOARD" listening for incoming ambulance telemetry.*

---

### STEP B: Setup LAPTOP 1 (Ambulance Side)

1. Open terminal on Laptop 1 and navigate to project folder:
   ```bash
   cd SMART-MED
   ```
2. Start the **Ambulance Application**:
   ```bash
   python ambulance/app.py
   ```
   *Ambulance UI will listen on `http://0.0.0.0:5001`.*

3. Open Web Browser on Laptop 1:
   ```
   http://localhost:5001
   ```
   *You will see the "AMBULANCE TELEMETRY MONITOR".*

4. **Connect Ambulance to Hospital Laptop 2**:
   - On the right sidebar under **Kaggle Dataset & Hardware Interface**, locate **Hospital Laptop IP Address**.
   - Change `http://localhost:5000` to Laptop 2's IP address:
     `http://192.168.1.50:5000` (replace with Laptop 2's actual IP).
   - Click **Save**.

---

## 4. Live Presentation Demonstration Sequence

1. **Demonstrate Ambulance Monitoring (Laptop 1)**:
   - Point out live vital signs updating sequentially from `datasets/patient_data.csv`.
   - Point out Emergency Status Banner transitioning between **NORMAL**, **WARNING**, and **CRITICAL** with clinical reason callouts.
   - Point out clear labels: `AMBULANCE SIDE` and `SIMULATED DATA – DEVELOPMENT MODE`.

2. **Demonstrate 3-Minute Transmission Countdown**:
   - Point out the circular countdown timer counting down from **03:00** (180 seconds).
   - Explain that data updates continuously in the ambulance, but only the **latest vital payload** transmits every 3 minutes to save bandwidth.

3. **Trigger Immediate Transmission**:
   - For fast presentation testing, click the **"SEND LATEST DATA NOW"** button on Laptop 1 or switch interval to **10 Seconds**.

4. **Demonstrate Hospital Reception (Laptop 2)**:
   - Switch to Laptop 2 screen.
   - Show the new entry automatically appearing in **Historical Patient Telemetry Transmissions** table (e.g., `10:00 -> Received`, `10:03 -> Received`).
   - Show abnormal vital values highlighted with pulsing alerts (e.g. SpO2 < 90%).
   - Show live line graphs updating on Laptop 2.

---

## 5. Troubleshooting Network Connection

If Laptop 1 cannot reach Laptop 2:
- **Windows Firewall Check**: Ensure Windows Defender Firewall allows Python through Port `5000`.
  - On Laptop 2: Temporarily allow Python or turn off Domain/Private Firewall during demo.
- **Ping Test**: On Laptop 1, run `ping 192.168.1.50`. If request times out, verify both laptops are on the same Wi-Fi subnet.
