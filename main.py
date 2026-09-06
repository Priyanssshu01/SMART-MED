"""
SMART-MED Production Master Application
Group Name: Biomed X (Session 2026-27)
Leader: Sayandeep Chakroborty

Unified Web Application with Dedicated Independent Cloud Endpoints:
- Dedicated Ambulance Portal (/ambulance-login & /ambulance)
- Dedicated Hospital Portal (/hospital-login & /hospital)
- Direct Supabase Cloud Telemetry Integration over HTTPS
- Production WSGI Ready for 1-Click Free Hosting on Render / Vercel
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_cors import CORS
import sys
import os
import requests
import datetime

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from common.sensor_interface import DatasetSensorSimulator
from common.supabase_client import SupabaseCloudClient

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get("SECRET_KEY", "SMARTMED-BIOMEDX-SECRET-KEY-2026")
CORS(app)

# Supabase Credentials (Pre-configured for Biomed X project)
DEFAULT_SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xpjsylfngntshglehspe.supabase.co")
DEFAULT_SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhwanN5bGZuZ250c2hnbGVoc3BlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg2ODE3NjEsImV4cCI6MjEwNDI1Nzc2MX0.lPXlmI1kMmAKupXOF_smnO-mVSIV7Ms4mTRkkz4J330")

DEFAULT_CSV = os.path.join(PROJECT_ROOT, "datasets", "patient_data.csv")
simulator = DatasetSensorSimulator(DEFAULT_CSV)
supabase_client = SupabaseCloudClient(DEFAULT_SUPABASE_URL, DEFAULT_SUPABASE_KEY)

# User Credentials
USERS = {
    "ambulance": {
        "password": "ambulance123",
        "role": "AMBULANCE",
        "name": "Ambulance Emergency Telemetry Officer",
        "redirect": "/ambulance"
    },
    "hospital": {
        "password": "hospital123",
        "role": "HOSPITAL",
        "name": "Dr. Hospital Receiving Officer",
        "redirect": "/hospital"
    }
}

app_state = {
    "mode": "SUPABASE",
    "supabase_url": DEFAULT_SUPABASE_URL,
    "supabase_key": DEFAULT_SUPABASE_KEY,
    "transmission_interval": 180,
    "last_transmission_time": None,
    "last_transmission_status": "READY FOR CLOUD TELEMETRY",
    "total_transmissions_sent": 0
}

# --- WEB ROUTES ---

@app.route('/')
def home():
    # Directly render the primary Ambulance Telemetry Monitor (matching reference UI media_1788689835114.png)
    return render_template('ambulance_index.html', user=USERS['ambulance'])

@app.route('/portal')
def portal_choice():
    return render_template('portal_choice.html')

# --- DEDICATED AMBULANCE PORTAL ---

@app.route('/ambulance-login', methods=['GET', 'POST'])
def ambulance_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()

        if username == 'ambulance' and password == 'ambulance123':
            session['username'] = 'ambulance'
            session['role'] = 'AMBULANCE'
            session['name'] = 'Ambulance Telemetry Officer'
            return redirect('/ambulance')
        else:
            return render_template('ambulance_login.html', error="Invalid Ambulance ID or Password!")

    return render_template('ambulance_login.html')

@app.route('/ambulance')
def ambulance_dashboard():
    return render_template('ambulance_index.html', user=USERS['ambulance'])

# --- DEDICATED HOSPITAL PORTAL ---

@app.route('/hospital-login', methods=['GET', 'POST'])
def hospital_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()

        if username == 'hospital' and password == 'hospital123':
            session['username'] = 'hospital'
            session['role'] = 'HOSPITAL'
            session['name'] = 'Dr. Hospital Specialist'
            return redirect('/hospital')
        else:
            return render_template('hospital_login.html', error="Invalid Hospital Specialist ID or Password!")

    return render_template('hospital_login.html')

@app.route('/hospital')
def hospital_dashboard():
    return render_template('hospital_index.html', user=USERS['hospital'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# --- REST TELEMETRY API ENDPOINTS ---

@app.route('/api/vitals', methods=['GET'])
def get_vitals():
    vitals = simulator.read_vitals()
    vitals["mode_type"] = app_state["mode"]
    vitals["supabase_url"] = app_state["supabase_url"]
    vitals["transmission_interval"] = app_state["transmission_interval"]
    vitals["last_transmission_time"] = app_state["last_transmission_time"]
    vitals["last_transmission_status"] = app_state["last_transmission_status"]
    vitals["total_transmissions_sent"] = app_state["total_transmissions_sent"]
    return jsonify(vitals)

@app.route('/api/transmit_now', methods=['POST'])
def transmit_now():
    vitals = simulator.read_vitals()
    success, res = supabase_client.insert_transmission(vitals)
    if success:
        rec_id = res.get('record_id', 'N/A')
        app_state["last_transmission_status"] = f"SUCCESS (Supabase Cloud ID: {rec_id})"
        app_state["total_transmissions_sent"] += 1
        app_state["last_transmission_time"] = datetime.datetime.now().isoformat()
        return jsonify({"success": True, "result": res, "vitals_sent": vitals})
    else:
        err_msg = f"SUPABASE ERROR: {res.get('error')}"
        app_state["last_transmission_status"] = err_msg
        return jsonify({"success": False, "result": res, "error": err_msg})

@app.route('/api/hospital/latest', methods=['GET'])
def get_hospital_latest():
    success, res = supabase_client.get_latest_transmission()
    if success:
        return jsonify({"status": "SUCCESS", "data": res, "mode": "SUPABASE"}), 200
    else:
        return jsonify({"status": "NO_DATA", "message": res.get("message", "Awaiting telemetry")}), 200

@app.route('/api/hospital/history', methods=['GET'])
def get_hospital_history():
    limit = request.args.get('limit', 50, type=int)
    success, history = supabase_client.get_transmission_history(limit)
    return jsonify({"status": "SUCCESS" if success else "ERROR", "count": len(history), "history": history}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
