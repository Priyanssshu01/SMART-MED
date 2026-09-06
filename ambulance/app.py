"""
SMART-MED Ambulance Monitoring System (Laptop 1)
Group Name: Biomed X (Session 2026-27)
Runs on Laptop 1 (Default Port: 5001)

Responsibility:
- Simulates live patient vital signs monitoring using DatasetSensorSimulator.
- Displays high-resolution biomedical dashboard with real-time graphs and cards.
- Supports dual transmission mode:
  1. LOCAL SERVER MODE (Local Wi-Fi REST API to Laptop 2)
  2. SUPABASE CLOUD MODE (Direct HTTPS transmission to Supabase Cloud Database over Internet)
- Automatically transmits latest vital data to Central Server / Laptop 2 / Supabase every 3 minutes (180 seconds).
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os
import requests
import datetime

# Add root directory to python path for common modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from common.sensor_interface import DatasetSensorSimulator
from common.supabase_client import SupabaseCloudClient

app = Flask(__name__)
CORS(app)

SERVER_URL = os.environ.get("SMARTMED_SERVER_URL", "http://localhost:5000")
API_TOKEN = "SMARTMED-SECURE-KEY-2026"

DEFAULT_CSV = os.path.join(PROJECT_ROOT, "datasets", "patient_data.csv")
simulator = DatasetSensorSimulator(DEFAULT_CSV)
supabase_client = SupabaseCloudClient()

# System State
state = {
    "mode": os.environ.get("SMARTMED_MODE", "SUPABASE"), # Default SUPABASE Cloud Mode
    "server_url": SERVER_URL,
    "supabase_url": os.environ.get("SUPABASE_URL", "https://xpjsylfngntshglehspe.supabase.co"),
    "supabase_key": os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhwanN5bGZuZ250c2hnbGVoc3BlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg2ODE3NjEsImV4cCI6MjEwNDI1Nzc2MX0.lPXlmI1kMmAKupXOF_smnO-mVSIV7Ms4mTRkkz4J330"),
    "transmission_interval": 180,  # Default 3 minutes (180 seconds)
    "last_transmission_time": None,
    "last_transmission_status": "PENDING INITIAL TRANSMISSION",
    "total_transmissions_sent": 0,
    "column_mapping": simulator.get_column_mapping()
}

def transmit_vitals_payload(vitals_data):
    """
    Worker function to send telemetry payload.
    Supports both Local Server REST API & Direct Supabase Cloud REST API over Internet.
    """
    if state["mode"] == "SUPABASE":
        # Supabase Cloud Internet Transmission
        if not supabase_client.enabled:
            err_msg = "SUPABASE ERROR: Cloud URL or API Key is missing. Please configure Supabase in settings."
            state["last_transmission_status"] = err_msg
            return False, {"error": err_msg}

        success, res = supabase_client.insert_transmission(vitals_data)
        if success:
            rec_id = res.get('record_id', 'N/A')
            state["last_transmission_status"] = f"SUCCESS (Supabase ID: {rec_id})"
            state["total_transmissions_sent"] += 1
            state["last_transmission_time"] = datetime.datetime.now().isoformat()
            return True, res
        else:
            err_msg = f"SUPABASE TRANSMISSION FAILED: {res.get('error')}"
            state["last_transmission_status"] = err_msg
            return False, res
    else:
        # Local Server REST API Transmission
        target_url = f"{state['server_url'].rstrip('/')}/api/v1/transmit"
        headers = {
            "Content-Type": "application/json",
            "X-API-Token": API_TOKEN,
            "Authorization": f"Bearer {API_TOKEN}"
        }

        try:
            response = requests.post(target_url, json=vitals_data, headers=headers, timeout=5)
            if response.status_code in (200, 201):
                res_data = response.json()
                state["last_transmission_status"] = f"SUCCESS (Local ID: {res_data.get('transmission_id', 'N/A')})"
                state["total_transmissions_sent"] += 1
                state["last_transmission_time"] = datetime.datetime.now().isoformat()
                return True, res_data
            else:
                err_msg = f"LOCAL SERVER FAILED (HTTP {response.status_code}): {response.text}"
                state["last_transmission_status"] = err_msg
                return False, {"error": err_msg}
        except Exception as e:
            err_msg = f"LOCAL CONNECTION FAILURE: Could not connect to {target_url}. Details: {str(e)}"
            state["last_transmission_status"] = err_msg
            return False, {"error": err_msg}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vitals', methods=['GET'])
def get_current_vitals():
    """Fetch next sequential vital record from dataset simulator."""
    vitals = simulator.read_vitals()
    vitals["mode_type"] = state["mode"]
    vitals["server_url"] = state["server_url"]
    vitals["supabase_url"] = state["supabase_url"]
    vitals["supabase_key"] = state["supabase_key"]
    vitals["transmission_interval"] = state["transmission_interval"]
    vitals["last_transmission_time"] = state["last_transmission_time"]
    vitals["last_transmission_status"] = state["last_transmission_status"]
    vitals["total_transmissions_sent"] = state["total_transmissions_sent"]
    return jsonify(vitals)

@app.route('/api/transmit_now', methods=['POST'])
def manual_transmit():
    """Manual 'SEND NOW' button endpoint for live presentation demos."""
    vitals = simulator.read_vitals()
    success, res = transmit_vitals_payload(vitals)
    return jsonify({
        "success": success,
        "result": res,
        "vitals_sent": vitals,
        "last_transmission_status": state["last_transmission_status"]
    })

@app.route('/api/config', methods=['GET', 'POST'])
def update_config():
    """Fetch or update server URL, transmission mode, and Supabase credentials."""
    if request.method == 'POST':
        data = request.get_json() or {}
        if 'mode' in data:
            state['mode'] = data['mode'].upper().strip()
        if 'server_url' in data:
            state['server_url'] = data['server_url'].strip()
        if 'supabase_url' in data:
            state['supabase_url'] = data['supabase_url'].strip()
        if 'supabase_key' in data:
            state['supabase_key'] = data['supabase_key'].strip()
        if 'transmission_interval' in data:
            try:
                state['transmission_interval'] = int(data['transmission_interval'])
            except ValueError:
                pass

        supabase_client.set_credentials(state['supabase_url'], state['supabase_key'])
        return jsonify({"status": "SUCCESS", "config": state})
    return jsonify(state)

@app.route('/api/test_supabase', methods=['POST'])
def test_supabase():
    """Endpoint to test Supabase cloud connection."""
    data = request.get_json() or {}
    url = data.get('supabase_url', state['supabase_url'])
    key = data.get('supabase_key', state['supabase_key'])

    test_client = SupabaseCloudClient(url, key)
    res = test_client.test_connection()
    return jsonify(res)

@app.route('/api/upload_csv', methods=['POST'])
def upload_csv():
    """Upload custom Kaggle CSV dataset."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    upload_dir = os.path.join(PROJECT_ROOT, "datasets", "user_uploads")
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, file.filename)
    file.save(save_path)

    try:
        simulator.load_dataset(save_path)
        state['column_mapping'] = simulator.get_column_mapping()
        return jsonify({
            "status": "SUCCESS",
            "message": f"Successfully loaded CSV dataset: {file.filename}",
            "mapping": state['column_mapping']
        })
    except Exception as e:
        return jsonify({"error": f"Failed to load dataset: {str(e)}"}), 500

if __name__ == '__main__':
    print("==================================================")
    print("SMART-MED AMBULANCE DASHBOARD RUNNING (LAPTOP 1)")
    print("Group: Biomed X | Academic Prototype")
    print(f"Transmission Mode: {state['mode']}")
    print("Listening on http://0.0.0.0:5001")
    print("==================================================")
    app.run(host='0.0.0.0', port=5001, debug=True)
