"""
SMART-MED Supabase Cloud Telemetry Integration
Group Name: Biomed X (Session 2026-27)

Provides HTTPS REST API communication with Supabase Cloud Database.
Allows Laptop 1 (Ambulance) and Laptop 2 (Hospital) to operate over the Internet securely.
"""

import requests
import datetime
import os

class SupabaseCloudClient:
    """
    Lightweight REST Client for Supabase Cloud Database.
    Utilizes standard HTTPS REST API endpoints with API Key Authorization.
    """

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.supabase_url = (supabase_url or os.environ.get("SUPABASE_URL", "")).rstrip('/')
        self.supabase_key = supabase_key or os.environ.get("SUPABASE_KEY", "")
        self.enabled = bool(self.supabase_url and self.supabase_key)

    def set_credentials(self, url: str, key: str):
        self.supabase_url = url.rstrip('/') if url else ""
        self.supabase_key = key if key else ""
        self.enabled = bool(self.supabase_url and self.supabase_key)

    def _get_headers(self):
        return {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def test_connection(self) -> dict:
        """Test connectivity to Supabase Cloud REST API."""
        if not self.enabled:
            return {"success": False, "message": "Supabase URL and API Key are missing."}

        endpoint = f"{self.supabase_url}/rest/v1/transmissions?select=id&limit=1"
        try:
            res = requests.get(endpoint, headers=self._get_headers(), timeout=5)
            if res.status_code in (200, 201):
                return {"success": True, "message": "Successfully connected to Supabase Cloud Database over HTTPS!"}
            else:
                return {"success": False, "message": f"Supabase API Error ({res.status_code}): {res.text}"}
        except Exception as e:
            return {"success": False, "message": f"Connection Error: {str(e)}"}

    def insert_transmission(self, payload: dict) -> tuple[bool, dict]:
        """
        Push telemetry JSON payload directly to Supabase Cloud 'transmissions' table over HTTPS.
        """
        if not self.enabled:
            return False, {"error": "Supabase credentials not configured"}

        endpoint = f"{self.supabase_url}/rest/v1/transmissions"
        
        # Prepare Supabase record dictionary
        record = {
            "patient_id": payload.get("patient_id", "P-7842"),
            "patient_name": payload.get("patient_name", "Anonymous Patient"),
            "age": payload.get("age", 58),
            "gender": payload.get("gender", "Male"),
            "heart_rate": payload.get("heart_rate", 75),
            "spo2": payload.get("spo2", 98),
            "systolic_bp": payload.get("systolic_bp", 120),
            "diastolic_bp": payload.get("diastolic_bp", 80),
            "blood_pressure": payload.get("blood_pressure", "120/80"),
            "temperature": payload.get("temperature", 36.8),
            "respiratory_rate": payload.get("respiratory_rate", 16),
            "patient_status": payload.get("status", "NORMAL"),
            "emergency_level": payload.get("emergency_level", "LEVEL 3 - GREEN"),
            "reasons": ", ".join(payload.get("reasons", [])) if isinstance(payload.get("reasons"), list) else str(payload.get("reasons", "")),
            "data_source": payload.get("data_source", "SIMULATED PATIENT DATA (Kaggle CSV)"),
            "transmitted_at": payload.get("timestamp", datetime.datetime.now().isoformat())
        }

        try:
            res = requests.post(endpoint, json=record, headers=self._get_headers(), timeout=7)
            if res.status_code in (200, 201):
                res_data = res.json()
                inserted_record = res_data[0] if isinstance(res_data, list) and len(res_data) > 0 else {}
                return True, {
                    "message": "Telemetry successfully sent to Supabase Cloud over HTTPS!",
                    "record_id": inserted_record.get("id"),
                    "inserted_at": inserted_record.get("created_at") or datetime.datetime.now().isoformat()
                }
            else:
                return False, {"error": f"Supabase HTTP {res.status_code}: {res.text}"}
        except Exception as e:
            return False, {"error": f"Network Error sending to Supabase: {str(e)}"}

    def get_latest_transmission(self) -> tuple[bool, dict]:
        """Fetch newest patient transmission from Supabase Cloud."""
        if not self.enabled:
            return False, {"error": "Supabase not configured"}

        endpoint = f"{self.supabase_url}/rest/v1/transmissions?select=*&order=id.desc&limit=1"
        try:
            res = requests.get(endpoint, headers=self._get_headers(), timeout=5)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    rec = data[0]
                    rec["received_at"] = rec.get("created_at") or rec.get("transmitted_at")
                    return True, rec
                return False, {"message": "No transmissions in Supabase cloud database yet."}
            else:
                return False, {"error": f"Supabase HTTP {res.status_code}: {res.text}"}
        except Exception as e:
            return False, {"error": f"Network error fetching from Supabase: {str(e)}"}

    def get_transmission_history(self, limit: int = 50) -> tuple[bool, list]:
        """Fetch historical transmission log from Supabase Cloud."""
        if not self.enabled:
            return False, []

        endpoint = f"{self.supabase_url}/rest/v1/transmissions?select=*&order=id.desc&limit={limit}"
        try:
            res = requests.get(endpoint, headers=self._get_headers(), timeout=5)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list):
                    for rec in data:
                        rec["received_at"] = rec.get("created_at") or rec.get("transmitted_at")
                    return True, data
            return False, []
        except Exception:
            return False, []
