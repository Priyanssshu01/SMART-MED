"""
SMART-MED Sensor Interface Module
Group Name: Biomed X (Session 2026-27)
Project Leader: Sayandeep Chakroborty
Members: Uttam Kumar Mahto, Prashant Kumar, Priyanshu Jaiswal

Architecture Purpose:
Provides an abstract base interface for data acquisition. Currently uses
DatasetSensorSimulator to stream patient records from CSV files (Kaggle dataset).
In future versions, this can be seamlessly replaced by RealSensorInterface 
(USB / Serial microcontroller interface with ECG, SpO2, BP, Temp, RR sensors).
"""

from abc import ABC, abstractmethod
import pandas as pd
import datetime
import random
import time
import os

class BaseSensorInterface(ABC):
    """
    Abstract Base Class for SMART-MED Patient Data Acquisition Interfaces.
    Ensures decoupling of data acquisition (CSV vs Hardware) from display/transmission logic.
    """

    @abstractmethod
    def read_vitals(self) -> dict:
        """
        Fetch the current frame of patient vitals.
        Returns a standardized dictionary.
        """
        pass

    @staticmethod
    def evaluate_status(vitals: dict) -> dict:
        """
        Academic Rule-based Emergency Evaluation System.
        DISCLAIMER: For academic demonstration only. NOT a clinical diagnostic system.
        """
        hr = vitals.get('heart_rate', 75)
        spo2 = vitals.get('spo2', 98)
        sys_bp = vitals.get('systolic_bp', 120)
        dia_bp = vitals.get('diastolic_bp', 80)
        temp = vitals.get('temperature', 37.0)
        rr = vitals.get('respiratory_rate', 16)

        reasons = []

        # Heart Rate Rules (Normal: 60 - 100 BPM)
        if hr > 130 or hr < 45:
            reasons.append(f"Severe Heart Rate abnormality: {hr} BPM")
        elif hr > 100 or hr < 50:
            reasons.append(f"Elevated/Low Heart Rate: {hr} BPM")

        # SpO2 Rules (Normal: 95% - 100%)
        if spo2 < 90:
            reasons.append(f"Critical Hypoxia (SpO2: {spo2}%)")
        elif spo2 < 95:
            reasons.append(f"Mild Desaturation (SpO2: {spo2}%)")

        # Blood Pressure Rules (Normal: 90/60 - 130/85)
        if sys_bp >= 160 or sys_bp <= 80 or dia_bp >= 100 or dia_bp <= 50:
            reasons.append(f"Severe BP: {sys_bp}/{dia_bp} mmHg")
        elif sys_bp >= 135 or sys_bp <= 85 or dia_bp >= 90 or dia_bp <= 55:
            reasons.append(f"Borderline BP: {sys_bp}/{dia_bp} mmHg")

        # Temperature Rules (Normal: 36.5 - 37.5 °C)
        if temp >= 39.0 or temp <= 35.0:
            reasons.append(f"Severe Fever/Hypothermia: {temp}°C")
        elif temp >= 37.8 or temp <= 36.0:
            reasons.append(f"Fever/Low Temp: {temp}°C")

        # Respiratory Rate Rules (Normal: 12 - 20 bpm)
        if rr >= 30 or rr <= 8:
            reasons.append(f"Severe Respiratory Distress: {rr} bpm")
        elif rr >= 22 or rr <= 10:
            reasons.append(f"Tachypnea/Bradypnea: {rr} bpm")

        # Categorize overall status
        if any("Critical" in r or "Severe" in r for r in reasons):
            status = "CRITICAL"
            emergency_level = "LEVEL 1 - RED (EMERGENCY RESUSCITATION REQUIRED)"
        elif len(reasons) > 0:
            status = "WARNING"
            emergency_level = "LEVEL 2 - YELLOW (URGENT MEDICAL ATTENTION)"
        else:
            status = "NORMAL"
            emergency_level = "LEVEL 3 - GREEN (STABLE PATIENT CONDITION)"
            reasons.append("All vital signs within normal range.")

        return {
            "status": status,
            "emergency_level": emergency_level,
            "reasons": reasons,
            "disclaimer": "Academic demonstration rule engine. Not clinically validated."
        }


class DatasetSensorSimulator(BaseSensorInterface):
    """
    Simulates patient vital monitoring by streaming sequential records from a CSV file.
    Supports auto-column detection and custom column mapping.
    """

    DEFAULT_MAPPING = {
        'patient_id': ['patient_id', 'id', 'pid', 'subject_id'],
        'patient_name': ['patient_name', 'name', 'subject_name'],
        'age': ['age'],
        'gender': ['gender', 'sex'],
        'heart_rate': ['heart_rate', 'hr', 'pulse', 'bpm'],
        'spo2': ['spo2', 'oximetry', 'oxygen_saturation', 'sat'],
        'systolic_bp': ['systolic_bp', 'sys_bp', 'systolic', 'bp_sys'],
        'diastolic_bp': ['diastolic_bp', 'dia_bp', 'diastolic', 'bp_dia'],
        'temperature': ['temperature', 'temp', 'body_temp'],
        'respiratory_rate': ['respiratory_rate', 'rr', 'resp_rate', 'respiration']
    }

    def __init__(self, csv_filepath: str, custom_mapping: dict = None):
        self.csv_filepath = csv_filepath
        self.custom_mapping = custom_mapping or {}
        self.df = None
        self.current_index = 0
        self.column_map = {}
        self.is_running = False
        self.load_dataset(csv_filepath)

    def load_dataset(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset CSV not found at: {filepath}")

        self.df = pd.read_csv(filepath)
        self.csv_filepath = filepath
        self.current_index = 0
        self._auto_detect_columns()

    def _auto_detect_columns(self):
        """Auto-detect columns based on standard names or custom user mappings."""
        csv_cols = [c.lower().strip() for c in self.df.columns]
        raw_cols = list(self.df.columns)

        mapped = {}
        for target_key, candidate_names in self.DEFAULT_MAPPING.items():
            # Check user custom override first
            if target_key in self.custom_mapping and self.custom_mapping[target_key] in raw_cols:
                mapped[target_key] = self.custom_mapping[target_key]
                continue

            # Check candidates
            found = False
            for candidate in candidate_names:
                if candidate in csv_cols:
                    idx = csv_cols.index(candidate)
                    mapped[target_key] = raw_cols[idx]
                    found = True
                    break
            if not found:
                mapped[target_key] = None

        self.column_map = mapped

    def set_column_mapping(self, mapping: dict):
        """Set explicit user column mapping."""
        self.custom_mapping = mapping
        self._auto_detect_columns()

    def get_column_mapping(self):
        return {
            'detected': self.column_map,
            'available_columns': list(self.df.columns) if self.df is not None else []
        }

    def read_vitals(self) -> dict:
        if self.df is None or len(self.df) == 0:
            return self._fallback_vitals()

        row = self.df.iloc[self.current_index]

        # Helper to extract value safely
        def val(key, default):
            col = self.column_map.get(key)
            if col and col in row:
                v = row[col]
                try:
                    if isinstance(default, float):
                        return float(v)
                    elif isinstance(default, int):
                        return int(float(v))
                    return str(v)
                except (ValueError, TypeError):
                    return default
            return default

        pid = val('patient_id', 'P-7842')
        pname = val('patient_name', 'Anonymous Patient')
        age = val('age', 58)
        gender = val('gender', 'Male')
        hr = val('heart_rate', 75)
        spo2 = val('spo2', 98)
        sys_bp = val('systolic_bp', 120)
        dia_bp = val('diastolic_bp', 80)
        temp = val('temperature', 36.8)
        rr = val('respiratory_rate', 16)

        # Advance pointer sequentially for live simulation
        self.current_index = (self.current_index + 1) % len(self.df)

        vitals = {
            "patient_id": str(pid),
            "patient_name": str(pname),
            "age": int(age),
            "gender": str(gender),
            "heart_rate": int(hr),
            "spo2": int(spo2),
            "systolic_bp": int(sys_bp),
            "diastolic_bp": int(dia_bp),
            "blood_pressure": f"{int(sys_bp)}/{int(dia_bp)}",
            "temperature": round(float(temp), 1),
            "respiratory_rate": int(rr),
            "timestamp": datetime.datetime.now().isoformat(),
            "record_index": self.current_index,
            "total_records": len(self.df),
            "data_source": "SIMULATED PATIENT DATA (Kaggle CSV Dataset)",
            "mode": "SIMULATED DATA – DEVELOPMENT MODE"
        }

        # Evaluate rules
        eval_result = self.evaluate_status(vitals)
        vitals.update(eval_result)

        return vitals

    def _fallback_vitals(self):
        return {
            "patient_id": "P-0000",
            "patient_name": "Fallback Subject",
            "age": 45,
            "gender": "Unknown",
            "heart_rate": 72,
            "spo2": 98,
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "blood_pressure": "120/80",
            "temperature": 37.0,
            "respiratory_rate": 16,
            "timestamp": datetime.datetime.now().isoformat(),
            "record_index": 0,
            "total_records": 0,
            "data_source": "FALLBACK CONSTANT DATA",
            "mode": "SIMULATED DATA – DEVELOPMENT MODE",
            "status": "NORMAL",
            "emergency_level": "LEVEL 3 - GREEN (STABLE PATIENT CONDITION)",
            "reasons": ["Fallback data active."],
            "disclaimer": "Academic demonstration rule engine."
        }


class RealSensorInterface(BaseSensorInterface):
    """
    Future Hardware Integration Stub.
    Demonstrates how biomedical sensors connected via Microcontroller (Arduino/ESP32)
    over USB/Serial (e.g. PySerial) will feed directly into SMART-MED without changing
    the rest of the application codebase.
    """

    def __init__(self, port="COM3", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.connected = False
        # In real deployment: self.serial_conn = serial.Serial(port, baudrate, timeout=1)

    def connect(self):
        """Mock connection logic for microcontroller interface."""
        print(f"[FUTURE HARDWARE] Attempting serial connection to Microcontroller on {self.port} at {self.baudrate} baud...")
        # Self-check or ping Arduino
        self.connected = False # Default false until real hardware is attached
        return self.connected

    def read_vitals(self) -> dict:
        """
        Future Serial Data Reader implementation.
        Expected incoming Arduino Serial JSON structure:
        {"hr": 82, "spo2": 97, "sys": 124, "dia": 82, "temp": 37.1, "rr": 18}
        """
        if not self.connected:
            raise NotImplementedError(
                "Hardware sensors are not connected in current Semester-5 development build. "
                "Use DatasetSensorSimulator for current Kaggle CSV dataset simulation."
            )

        # Pseudocode for future hardware reading:
        # line = self.serial_conn.readline().decode('utf-8').strip()
        # raw_data = json.loads(line)
        # return standardized dictionary...
        pass
