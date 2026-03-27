# Finsight App Start Guide (Windows + iPhone)

This guide explains how to start both:
1. Django backend server
2. Expo mobile app

It is written for your current project structure and iPhone testing with Expo Go.

## Prerequisites

1. Use project virtual environment:
- Path: `.venv`

2. Install dependencies (if not already done):
- Backend: `pip install -r requirements.txt`
- Mobile: `cd mobile_app && npm install`

3. iPhone and laptop should be on the same Wi-Fi.

---

## Terminal 1: Start Django Backend

From project root:

```powershell
cd "D:\OneDrive - The University of Hong Kong - Connect\FITE4801\Finsight"
& ".\.venv\Scripts\Activate.ps1"
```

If you want local SQLite testing (recommended for quick startup):

```powershell
$env:DATABASE_URL = "sqlite:///D:/OneDrive - The University of Hong Kong - Connect/FITE4801/Finsight/db.sqlite3"
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Expected result:
- Django server running on port 8000.

---

## Find Your Computer LAN IP

In another terminal:

```powershell
ipconfig
```

Use your IPv4 address, for example:
- `192.168.1.100`

Backend URL for mobile becomes:
- `http://192.168.1.100:8000/api`

---

## Terminal 2: Start Expo App

From project root:

```powershell
cd "D:\OneDrive - The University of Hong Kong - Connect\FITE4801\Finsight\mobile_app"
$env:EXPO_PUBLIC_API_BASE_URL = "http://<YOUR_LAN_IP>:8000/api"
npm start
```

Replace `<YOUR_LAN_IP>` with your real IP.

Example:

```powershell
$env:EXPO_PUBLIC_API_BASE_URL = "http://192.168.1.100:8000/api"
```

Expected result:
- Expo Metro starts and shows a QR code.

---

## iPhone Testing Steps

1. Install Expo Go from App Store.
2. Open Expo Go on iPhone.
3. Scan QR code shown by `npm start` terminal.
4. App opens on iPhone.
5. Test login, home, scan/upload, and past uploads.

---

## Quick Health Checks

Backend check:

```powershell
python manage.py check
```

Mobile lint check:

```powershell
cd mobile_app
npm run lint
```

---

## Common Issues and Fixes

1. Error: `No module named 'rest_framework_simplejwt'`
- Fix:

```powershell
& ".\.venv\Scripts\python.exe" -m pip install djangorestframework-simplejwt==5.5.1
```

2. Error: PostgreSQL connection refused (`127.0.0.1:5432`)
- Fix: use SQLite for testing:

```powershell
$env:DATABASE_URL = "sqlite:///D:/OneDrive - The University of Hong Kong - Connect/FITE4801/Finsight/db.sqlite3"
```

3. Expo cannot find `package.json`
- Fix: run Expo from `mobile_app` folder, not project root.

4. iPhone cannot reach backend
- Check:
1. Same Wi-Fi network
2. Correct LAN IP in `EXPO_PUBLIC_API_BASE_URL`
3. Backend running with `0.0.0.0:8000`

5. QR scan works but API calls fail
- Check backend URL includes `/api` suffix.

---

## One-Session Quick Start (Copy/Paste)

Terminal A (backend):

```powershell
cd "D:\OneDrive - The University of Hong Kong - Connect\FITE4801\Finsight"
& ".\.venv\Scripts\Activate.ps1"
$env:DATABASE_URL = "sqlite:///D:/OneDrive - The University of Hong Kong - Connect/FITE4801/Finsight/db.sqlite3"
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Terminal B (mobile):

```powershell
cd "D:\OneDrive - The University of Hong Kong - Connect\FITE4801\Finsight\mobile_app"
$env:EXPO_PUBLIC_API_BASE_URL = "http://<YOUR_LAN_IP>:8000/api"
npm start
```
