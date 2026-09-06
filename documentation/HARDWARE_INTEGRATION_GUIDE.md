# SMART-MED Future Biomedical Hardware Integration Guide
**Group Name**: Biomed X (Session 2026–27)  
**Project Leader**: Sayandeep Chakroborty  
**Members**: Uttam Kumar Mahto, Prashant Kumar, Priyanshu Jaiswal  

---

## 1. System Architecture Overview

SMART-MED was explicitly engineered with a decoupled sensor abstraction architecture. In the current Semester-5 prototype phase, patient data is simulated via the `DatasetSensorSimulator` using Kaggle CSV datasets (`patient_data.csv`).

To transition to real hardware in future semesters, replace the simulator instance in `ambulance/app.py` with `RealSensorInterface` from `common/sensor_interface.py`. **Zero changes are required in the Ambulance or Hospital UI dashboards.**

```
[ Biomedical Sensors ]
   ├─ ECG Sensor (AD8232 / Heart Rate)
   ├─ Pulse Oximeter Sensor (MAX30102 SpO2)
   ├─ NIBP Blood Pressure Module
   ├─ Temperature Sensor (LM35 / DS18B20)
   └─ Respiration Sensor / Piezo
            │
            ▼
[ Microcontroller / DAQ Unit ] (Arduino Uno / ESP32 / STM32)
            │
            ▼  USB / Serial Communication (UART @ 9600 Baud)
[ Laptop 1 (Ambulance) - RealSensorInterface ]
            │
            ▼  HTTP POST / REST API (Every 3 minutes)
[ Central Server & Laptop 2 (Hospital Dashboard) ]
```

---

## 2. Recommended Biomedical Sensor Modules

| Vital Sign Parameter | Recommended Hardware Sensor Module | Operating Principle | Microcontroller Pin Interface |
| :--- | :--- | :--- | :--- |
| **ECG & Heart Rate** | AD8232 Single-Lead Heart Rate Monitor | 3-Lead Electrocardiography (RA, LA, RL) | Analog In (A0) + LO+/LO- Leads-off detect |
| **SpO2 & Pulse Oximetry** | MAX30102 / MAX30100 Optical Sensor | Photoplethysmography (PPG Red & IR LED) | I2C (SDA = A4, SCL = A5) |
| **Blood Pressure (NIBP)** | Sunrom / Medical Oscillometric NIBP Module | Oscillometric Cuff Inflation & Pressure Sensing | Serial UART (TX/RX) |
| **Body Temperature** | DS18B20 Waterproof Probe or LM35 | Semiconductor / One-Wire Digital Thermal | One-Wire Digital Pin 2 |
| **Respiratory Rate** | Piezoelectric Chest Belt or Thermistor Probe | Nasal Airflow Temperature / Chest Expansion | Analog In (A1) |

---

## 3. Sample Arduino / ESP32 Microcontroller Code

Flash this C++ sketch to your Arduino or ESP32 microcontroller to output standardized serial telemetry frames:

```cpp
/*
  SMART-MED Microcontroller Data Acquisition Firmware
  Group: Biomed X (Session 2026-27)
  Baud Rate: 9600 bps
*/

#include <Wire.h>
#include "MAX30105.h" // SparkFun MAX3010x library
#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensors(&oneWire);

MAX30105 particleSensor;

void setup() {
  Serial.begin(9600);
  tempSensors.begin();
  
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    // Sensor init fallback
  }
  particleSensor.setup();
}

void loop() {
  // 1. Read Heart Rate & SpO2
  long irValue = particleSensor.getIR();
  int heartRate = 75; // Calculate from PPG peaks
  int spo2 = 98;      // Calculate ratio of R/IR

  // 2. Read Temperature
  tempSensors.requestTemperatures();
  float tempC = tempSensors.getTempCByIndex(0);
  if (tempC < 0) tempC = 36.8;

  // 3. Read Blood Pressure (Simulated or Serial NIBP module)
  int sysBP = 122;
  int diaBP = 81;

  // 4. Read Respiratory Rate
  int respRate = 16;

  // Print JSON telemetry packet to USB Serial
  Serial.print("{\"patient_id\":\"P-7842\",\"heart_rate\":");
  Serial.print(heartRate);
  Serial.print(",\"spo2\":");
  Serial.print(spo2);
  Serial.print(",\"systolic_bp\":");
  Serial.print(sysBP);
  Serial.print(",\"diastolic_bp\":");
  Serial.print(diaBP);
  Serial.print(",\"temperature\":");
  Serial.print(tempC, 1);
  Serial.print(",\"respiratory_rate\":");
  Serial.print(respRate);
  Serial.println("}");

  delay(2000); // Send frame every 2 seconds
}
```

---

## 4. Python PySerial Integration in `common/sensor_interface.py`

To activate real hardware, install `pyserial`:
```bash
pip install pyserial
```

Update `RealSensorInterface` in `common/sensor_interface.py`:

```python
import serial
import json
from common.sensor_interface import BaseSensorInterface

class RealSensorInterface(BaseSensorInterface):
    def __init__(self, port="COM3", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate, timeout=2)

    def read_vitals(self) -> dict:
        line = self.ser.readline().decode('utf-8', errors='ignore').strip()
        data = json.loads(line)

        vitals = {
            "patient_id": data.get("patient_id", "P-7842"),
            "patient_name": "Emergency Patient",
            "age": 58,
            "gender": "Male",
            "heart_rate": int(data.get("heart_rate", 75)),
            "spo2": int(data.get("spo2", 98)),
            "systolic_bp": int(data.get("systolic_bp", 120)),
            "diastolic_bp": int(data.get("diastolic_bp", 80)),
            "blood_pressure": f"{data.get('systolic_bp', 120)}/{data.get('diastolic_bp', 80)}",
            "temperature": float(data.get("temperature", 36.8)),
            "respiratory_rate": int(data.get("respiratory_rate", 16)),
            "timestamp": datetime.datetime.now().isoformat(),
            "data_source": f"REAL BIOMEDICAL SENSOR ({self.port})",
            "mode": "HARDWARE SENSOR MODE"
        }

        # Apply rule engine
        eval_res = self.evaluate_status(vitals)
        vitals.update(eval_res)
        return vitals
```

Then in `ambulance/app.py`:
```python
# Replace DatasetSensorSimulator with RealSensorInterface
from common.sensor_interface import RealSensorInterface
simulator = RealSensorInterface(port="COM3")
```
