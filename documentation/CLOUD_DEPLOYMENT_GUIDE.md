# SMART-MED Free Cloud Hosting & Live Link Setup Guide
**Group Name**: Biomed X (Session 2026–27)  
**Project Leader**: Sayandeep Chakroborty  
**Members**: Uttam Kumar Mahto, Prashant Kumar, Priyanshu Jaiswal  

---

## 🌐 1. Overview

This guide explains how to host SMART-MED **FREE on Render.com** so you get a permanent online HTTPS link:

`https://smart-med-biomedx.onrender.com/login`

With this online link:
- **LAPTOP 1 (Ambulance)**: Opens link -> Enters Ambulance User ID & Password -> Telemetry Dashboard opens on Internet!
- **LAPTOP 2 (Hospital)**: Opens link -> Enters Hospital User ID & Password -> Receiving Dashboard opens on Internet!

---

## 🔑 2. Login User IDs & Passwords

SMART-MED includes built-in role-based authentication:

| Role | Username (User ID) | Password | Redirect Target |
| :--- | :--- | :--- | :--- |
| **Ambulance Staff** | `ambulance` | `ambulance123` | `/ambulance` (Ambulance Telemetry Dashboard) |
| **Hospital Specialist** | `hospital` | `hospital123` | `/hospital` (Hospital Receiving Dashboard) |
| **System Admin** | `admin` | `admin123` | `/hospital` |

---

## 🚀 3. How to Deploy to Render.com in 2 Minutes (Free)

### STEP A: Upload Code to GitHub
1. Create a free GitHub repository (e.g. `SMART-MED`).
2. Upload/push your `SMART-MED` project folder to GitHub.

### STEP B: Connect GitHub to Render.com
1. Go to [https://render.com](https://render.com) and create a free account (Sign in with GitHub).
2. Click **New +** and select **Web Service**.
3. Select your `SMART-MED` GitHub repository.
4. Fill in these settings:
   - **Name**: `smart-med-biomedx` (or any name you like)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app`
   - **Instance Type**: `Free`
5. Click **Create Web Service**.

Render will deploy your site in ~1 minute and give you a permanent live URL!

---

## 📱 4. Using the Online Links

Once deployed, your project URL will look like:
`https://smart-med-biomedx.onrender.com`

### On Laptop 1 (Ambulance):
1. Open Browser -> Go to `https://smart-med-biomedx.onrender.com/login`
2. Enter User ID: `ambulance` | Password: `ambulance123`
3. Click **Sign In**. Laptop 1 is now broadcasting live telemetry over the Internet!

### On Laptop 2 (Hospital):
1. Open Browser -> Go to `https://smart-med-biomedx.onrender.com/login`
2. Enter User ID: `hospital` | Password: `hospital123`
3. Click **Sign In**. Laptop 2 is now receiving live patient condition & historical logs over the Internet!
