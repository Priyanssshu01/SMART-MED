"""
SMART-MED Hospital Receiving Application (Laptop 2)
Group Name: Biomed X (Session 2026-27)
Runs on Laptop 2 (Default Port: 5002)

Responsibility:
- Serves the Hospital Receiving Dashboard UI.
- Supports dual receiver modes:
  1. LOCAL SERVER MODE (Queries Local Central Server on Wi-Fi)
  2. SUPABASE CLOUD MODE (Queries Supabase Cloud Database over the Internet)
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os
import requests

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from common.supabase_client import SupabaseCloudClient

app = Flask(__name__)
CORS(app)

SERVER_URL = os.environ.get("SMARTMED_SERVER_URL", "http://localhost:5000")
supabase_client = SupabaseCloudClient()

hosp_state = {
    "mode": os.environ.get("SMARTMED_MODE", "SUPABASE"), # Default SUPABASE Cloud Mode
    "server_url": SERVER_URL,
    "supabase_url": os.environ.get("SUPABASE_URL", "https://xpjsylfngntshglehspe.supabase.co"),
    "supabase_key": os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhwanN5bGZuZ250c2hnbGVoc3BlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg2ODE3NjEsImV4cCI6MjEwNDI1Nzc2MX0.lPXlmI1kMmAKupXOF_smnO-mVSIV7Ms4mTRkkz4J330")
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/hospital/config', methods=['GET', 'POST'])
def handle_config():
    """Get or update Hospital Receiver configuration."""
    if request.method == 'POST':
        data = request.get_json() or {}
        if 'mode' in data:
            hosp_state['mode'] = data['mode'].upper().strip()
        if 'server_url' in data:
            hosp_state['server_url'] = data['server_url'].strip()
        if 'supabase_url' in data:
            hosp_state['supabase_url'] = data['supabase_url'].strip()
        if 'supabase_key' in data:
            hosp_state['supabase_key'] = data['supabase_key'].strip()

        supabase_client.set_credentials(hosp_state['supabase_url'], hosp_state['supabase_key'])
        return jsonify({"status": "SUCCESS", "config": hosp_state})
    return jsonify(hosp_state)

@app.route('/api/hospital/latest', methods=['GET'])
def get_latest():
    """Fetch latest patient telemetry from Supabase Cloud or Local Central Server."""
    if hosp_state["mode"] == "SUPABASE":
        if not supabase_client.enabled:
            return jsonify({
                "status": "ERROR",
                "message": "Supabase credentials not configured on Hospital Laptop 2."
            }), 400

        success, res = supabase_client.get_latest_transmission()
        if success:
            return jsonify({"status": "SUCCESS", "data": res, "mode": "SUPABASE"}), 200
        else:
            return jsonify({"status": "NO_DATA", "message": res.get("message", "No cloud data")}), 200
    else:
        try:
            url = f"{hosp_state['server_url'].rstrip('/')}/api/v1/latest"
            res = requests.get(url, timeout=3)
            return jsonify(res.json()), res.status_code
        except Exception as e:
            return jsonify({
                "status": "ERROR",
                "message": f"Cannot connect to Local Central Server at {hosp_state['server_url']}. Details: {str(e)}"
            }), 503

@app.route('/api/hospital/history', methods=['GET'])
def get_history():
    """Fetch full transmission history from Supabase Cloud or Local Server."""
    limit = request.args.get('limit', 50, type=int)

    if hosp_state["mode"] == "SUPABASE":
        if not supabase_client.enabled:
            return jsonify({"status": "ERROR", "history": [], "count": 0}), 400

        success, history = supabase_client.get_transmission_history(limit)
        return jsonify({
            "status": "SUCCESS" if success else "ERROR",
            "count": len(history),
            "history": history,
            "mode": "SUPABASE"
        }), 200
    else:
        try:
            url = f"{hosp_state['server_url'].rstrip('/')}/api/v1/history?limit={limit}"
            res = requests.get(url, timeout=3)
            return jsonify(res.json()), res.status_code
        except Exception as e:
            return jsonify({
                "status": "ERROR",
                "message": f"Cannot connect to Central Server at {hosp_state['server_url']}. Details: {str(e)}"
            }), 503

@app.route('/api/hospital/reset', methods=['POST'])
def reset_history():
    """Reset history endpoint for presentation demos."""
    if hosp_state["mode"] == "SUPABASE":
        return jsonify({"status": "WARNING", "message": "Cloud reset must be performed via Supabase Dashboard SQL."})
    else:
        try:
            url = f"{hosp_state['server_url'].rstrip('/')}/api/v1/reset"
            res = requests.post(url, timeout=3)
            return jsonify(res.json()), res.status_code
        except Exception as e:
            return jsonify({"status": "ERROR", "message": str(e)}), 503

if __name__ == '__main__':
    print("==================================================")
    print("SMART-MED HOSPITAL DASHBOARD RUNNING (LAPTOP 2)")
    print("Group: Biomed X | Academic Prototype")
    print(f"Receiver Mode: {hosp_state['mode']}")
    print("Listening on http://0.0.0.0:5002")
    print("==================================================")
    app.run(host='0.0.0.0', port=5002, debug=True)
