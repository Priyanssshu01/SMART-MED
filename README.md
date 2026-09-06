# SMART-MED: Smart Medical Emergency Response and Patient Monitoring System

[![Biomedical Engineering Project](https://img.shields.io/badge/Academic%20Project-Semester--5-0d9488.svg)](#)
[![Group](https://img.shields.io/badge/Group-Biomed%20X-0284c7.svg)](#)
[![Session](https://img.shields.io/badge/Session-2026--27-8b5cf6.svg)](#)
[![Cloud Mode](https://img.shields.io/badge/Cloud-Supabase%20HTTPS-3ecf8e.svg)](#)
[![Python](https://img.shields.io/badge/Python-Flask%20%7C%20Pandas-3776ab.svg)](#)

> **SMART-MED** is a Semester-5 Biomedical Engineering academic prototype designed to monitor an emergency patient inside an ambulance and transmit the latest medical vital signs to a hospital receiving computer over REST API or Supabase Cloud Internet every 3 minutes.

---

## 👥 Project Team Details

- **Group Name**: Biomed X
- **Session**: 2026–27
- **Academic Program**: B.Tech Biomedical Engineering (Semester-5)
- **Group Leader**: Sayandeep Chakroborty
- **Group Members**:
  - Uttam Kumar Mahto
  - Prashant Kumar
  - Priyanshu Jaiswal

---

## ⚠️ VERY IMPORTANT MEDICAL DISCLAIMER

> [!CAUTION]
> **"SMART-MED is an academic prototype for patient-data monitoring and communication. It is not a medical device and must not be used for clinical diagnosis or treatment."**
> 
> The vital sign rule classification (NORMAL, WARNING, CRITICAL) is implemented strictly for demonstration purposes.

---

## 🎯 Purpose & Dual Architecture

SMART-MED supports **TWO DUAL OPERATING MODES**:

1. **Local REST API Mode (Single Wi-Fi Network)**: Laptop 1 and Laptop 2 communicate over a shared local Wi-Fi or hotspot.
2. **Supabase Cloud Internet Mode (Worldwide Remote Connectivity)**: Laptop 1 (Ambulance) and Laptop 2 (Hospital) communicate over HTTPS across the Internet using Supabase Cloud Database.

### System Data Flow

```
[ Kaggle Dataset (patient_data.csv) / Future Microcontroller Hardware ]
                                   │
                                   ▼
                         [ BaseSensorInterface ]
                       (common/sensor_interface.py)
                                   │
                                   ▼
                       [ Ambulance App - Laptop 1 ]
                        (Port 5001 / UI Dashboard)
                                   │
                     ┌─────────────┴─────────────┐
                     │                           │
          (Local Wi-Fi Mode)           (Supabase Cloud Mode)
                     │                           │
                     ▼                           ▼
           [ Central REST Server ]     [ SUPABASE CLOUD DATABASE ]
            (server/app.py - 5000)     (https://xyz.supabase.co)
                     │                           │
                     └─────────────┬─────────────┘
                                   │
                                   ▼
                       [ Hospital App - Laptop 2 ]
                        (Port 5002 / UI Dashboard)
```

---

## 🚀 Key Features

### 1. Ambulance Dashboard (Laptop 1 - Port 5001)
- **Simulated Patient Data**: Displays live updating Heart Rate, SpO2, Blood Pressure (Systolic/Diastolic), Body Temperature, and Respiratory Rate.
- **Rule-Based Emergency Status**: Dynamically computes **NORMAL**, **WARNING**, and **CRITICAL** triage levels with clinical reason callouts.
- **Clear Identification Labels**: Labeled as `"AMBULANCE SIDE"` and `"SIMULATED DATA – DEVELOPMENT MODE"`.
- **3-Minute Transmission Engine**:
  - Circular countdown timer ticking down from 180 seconds (`03:00`).
  - Automatically posts the latest vital signs payload every 3 minutes.
  - Manual **"SEND NOW"** button for immediate presentation demonstrations.
  - Speed toggles (10s, 30s, 60s, 180s).
- **Supabase Cloud Internet Toggle**: Configure Supabase URL & Key to send telemetry over the Internet.

### 2. Hospital Receiving Dashboard (Laptop 2 - Port 5002)
- **Receiving Interface**: Labeled as `"HOSPITAL RECEIVING DASHBOARD"`.
- **Patient Telemetry Cards**: Real-time display of inbound vital signs, timestamp of last received packet, and countdown until next expected transmission.
- **Abnormal Value Highlighting**: Visual red pulsing alerts for critical vital values (e.g. SpO2 < 90% or Heart Rate > 130 BPM).
- **Historical Transmissions Table**: Shows timestamped history (`10:00 -> received`, `10:03 -> received`).
- **Telemetry Trend Chart**: Multi-line Chart.js graph tracking vital trends over time.

---

## 📁 Project Directory Structure

```
SMART-MED/
│
├── ambulance/                       # LAPTOP 1: Ambulance Application
│   ├── app.py                       # Ambulance server & transmission scheduler
│   ├── templates/
│   │   └── index.html               # Ambulance Telemetry UI
│   └── static/
│       ├── css/style.css            # Medical UI styling
│       └── js/ambulance.js          # Live dashboard updates & 180s countdown timer
│
├── hospital/                        # LAPTOP 2: Hospital Application
│   ├── app.py                       # Hospital dashboard server
│   ├── templates/
│   │   └── index.html               # Hospital Receiving UI
│   └── static/
│       ├── css/style.css            # Hospital dashboard styling
│       └── js/hospital.js           # Live data polling, alert highlights & charts
│
├── server/                          # CENTRAL REST API SERVER & DATABASE
│   ├── app.py                       # Flask REST API endpoints & SQLite logger
│   └── database/
│       └── smartmed.db              # SQLite database for telemetry logs
│
├── common/                          # MODULAR HARDWARE & CLOUD INTERFACE
│   ├── __init__.py
│   ├── sensor_interface.py          # Abstract base sensor, CSV simulator & hardware stub
│   └── supabase_client.py           # Supabase Cloud REST API Client over HTTPS
│
├── datasets/
│   └── patient_data.csv             # Kaggle-like patient vital signs dataset
│
├── documentation/
│   ├── SUPABASE_SETUP_GUIDE.md      # Supabase Cloud Internet Setup Guide
│   ├── HARDWARE_INTEGRATION_GUIDE.md# Arduino/ESP32 USB/Serial setup instructions
│   └── DUAL_LAPTOP_SETUP.md         # Step-by-step 2-Laptop presentation guide
│
├── requirements.txt                 # Unified Python dependencies
└── README.md                        # Master project documentation
```

---

## 💻 Quickstart Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Single-Laptop Demonstration Mode
Run 3 separate terminal windows:

**Terminal 1 (Central Server)**:
```bash
python server/app.py
```

**Terminal 2 (Ambulance App - Laptop 1)**:
```bash
python ambulance/app.py
```

**Terminal 3 (Hospital App - Laptop 3)**:
```bash
python hospital/app.py
```

#### Access in Browser:
- **Ambulance Dashboard**: [http://localhost:5001](http://localhost:5001)
- **Hospital Dashboard**: [http://localhost:5002](http://localhost:5002)

---

### 🌐 3. Supabase Cloud Internet Setup
To connect Laptop 1 and Laptop 2 over the Internet anywhere in the world:

1. Follow the step-by-step guide in [documentation/SUPABASE_SETUP_GUIDE.md](file:///c:/Users/pryan/OneDrive/Desktop/SMART-MED/documentation/SUPABASE_SETUP_GUIDE.md).
2. Enter your `SUPABASE_URL` and `SUPABASE_KEY` in the Ambulance and Hospital web UI settings.
3. Switch mode to **Supabase Cloud Database (Internet Mode)**!
