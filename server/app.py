"""
SMART-MED Central REST API Server & Database Manager
Group Name: Biomed X (Session 2026-27)
Runs on Laptop 2 or Central Server (Default Port: 5000)

Functions:
- Receives HTTP POST transmissions from Laptop 1 (Ambulance).
- Stores telemetry records in SQLite database (smartmed.db).
- Exposes REST API endpoints for Laptop 2 (Hospital Receiving Dashboard).
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
import os

app = Flask(__name__)
CORS(app)

DB_DIR = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'smartmed.db')

API_TOKEN = "SMARTMED-SECURE-KEY-2026"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transmissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            patient_name TEXT,
            age INTEGER,
            gender TEXT,
            heart_rate INTEGER,
            spo2 INTEGER,
            systolic_bp INTEGER,
            diastolic_bp INTEGER,
            blood_pressure TEXT,
            temperature REAL,
            respiratory_rate INTEGER,
            patient_status TEXT,
            emergency_level TEXT,
            reasons TEXT,
            data_source TEXT,
            transmitted_at TEXT NOT NULL,
            received_at TEXT NOT NULL,
            transmission_status TEXT DEFAULT 'SUCCESS'
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM transmissions').fetchone()[0]
    conn.close()
    return jsonify({
        "status": "ONLINE",
        "system": "SMART-MED Central Server API",
        "database": "SQLite",
        "total_transmissions_logged": count,
        "timestamp": datetime.datetime.now().isoformat(),
        "disclaimer": "Academic prototype - Not for clinical use."
    })

@app.route('/api/v1/transmit', methods=['POST'])
def receive_transmission():
    """Endpoint for Laptop 1 (Ambulance) to push 3-minute vital transmissions."""
    # Simple API Key Authorization
    auth_header = request.headers.get('Authorization')
    token = request.headers.get('X-API-Token')
    
    if token != API_TOKEN and auth_header != f"Bearer {API_TOKEN}":
        return jsonify({"error": "Unauthorized API Token", "status": "FAILED"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload", "status": "FAILED"}), 400

    required_fields = ['patient_id', 'heart_rate', 'spo2', 'temperature']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required vital field: {field}", "status": "FAILED"}), 422

    patient_id = data.get('patient_id', 'P-0000')
    patient_name = data.get('patient_name', 'Anonymous Patient')
    age = data.get('age', 0)
    gender = data.get('gender', 'N/A')
    hr = data.get('heart_rate', 0)
    spo2 = data.get('spo2', 0)
    sys_bp = data.get('systolic_bp', 120)
    dia_bp = data.get('diastolic_bp', 80)
    bp = data.get('blood_pressure', f"{sys_bp}/{dia_bp}")
    temp = data.get('temperature', 0.0)
    rr = data.get('respiratory_rate', 0)
    status = data.get('status', 'NORMAL')
    emergency_level = data.get('emergency_level', 'LEVEL 3 - GREEN')
    reasons = ", ".join(data.get('reasons', [])) if isinstance(data.get('reasons'), list) else str(data.get('reasons', ''))
    data_source = data.get('data_source', 'SIMULATED PATIENT DATA')
    transmitted_at = data.get('timestamp', datetime.datetime.now().isoformat())
    received_at = datetime.datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transmissions (
            patient_id, patient_name, age, gender, heart_rate, spo2,
            systolic_bp, diastolic_bp, blood_pressure, temperature,
            respiratory_rate, patient_status, emergency_level, reasons,
            data_source, transmitted_at, received_at, transmission_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        patient_id, patient_name, age, gender, hr, spo2, sys_bp, dia_bp,
        bp, temp, rr, status, emergency_level, reasons, data_source,
        transmitted_at, received_at, 'SUCCESS'
    ))
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "status": "SUCCESS",
        "message": "Patient vitals received and logged into central server.",
        "transmission_id": record_id,
        "received_at": received_at,
        "patient_id": patient_id
    }), 201

@app.route('/api/v1/latest', methods=['GET'])
def get_latest_transmission():
    """Endpoint for Hospital Dashboard to fetch the latest telemetry data."""
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM transmissions ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()

    if not row:
        return jsonify({
            "status": "NO_DATA",
            "message": "No transmissions recorded yet. Waiting for Ambulance telemetry."
        }), 200

    record = dict(row)
    return jsonify({
        "status": "SUCCESS",
        "data": record,
        "fetched_at": datetime.datetime.now().isoformat()
    }), 200

@app.route('/api/v1/history', methods=['GET'])
def get_transmission_history():
    """Endpoint for Hospital Dashboard to fetch telemetry history."""
    limit = request.args.get('limit', 50, type=int)
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM transmissions ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    conn.close()

    history = [dict(row) for row in rows]
    return jsonify({
        "status": "SUCCESS",
        "count": len(history),
        "history": history
    }), 200

@app.route('/api/v1/reset', methods=['POST'])
def reset_database():
    """Clear database logs for fresh presentation demos."""
    conn = get_db_connection()
    conn.execute('DELETE FROM transmissions')
    conn.commit()
    conn.close()
    return jsonify({
        "status": "SUCCESS",
        "message": "Transmission log history reset successfully."
    })

if __name__ == '__main__':
    print("==================================================")
    print("SMART-MED CENTRAL API & DATABASE SERVER RUNNING")
    print("Group: Biomed X | Academic Prototype")
    print("Listening on http://0.0.0.0:5000")
    print("==================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
