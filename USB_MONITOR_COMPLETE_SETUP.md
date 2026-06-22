# 🔴 USB Device Monitoring - Complete Setup & Testing Guide

## Overview
The system now has an **enhanced USB/mobile device detector** that:
- ✅ Detects when USB drives or mobile devices are connected
- ✅ Captures images using the system's camera
- ✅ Performs face recognition (if faces are configured)
- ✅ Logs all events to the backend database
- ✅ Displays live events in the Admin Dashboard

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start Django Backend
```bash
cd backend
python manage.py runserver
# Server runs at: http://localhost:8000
```

### Step 2: Start React Frontend  
```bash
cd frontend
npm run dev
# Frontend runs at: http://localhost:5173
```

### Step 3: Start USB Monitor (in NEW terminal)
```bash
cd backend
python scripts/usb_monitor_enhanced.py
# OR double-click: START_USB_MONITOR_ENHANCED.bat
```

Once all 3 are running:
1. Login as admin@central.com / admin123
2. Go to Admin Dashboard → Live Monitoring
3. Connect a USB drive or phone
4. **Image should be captured and event logged!**

---

## 📋 What Gets Logged When USB Connects

For each USB/Mobile device insertion:
1. **Image Capture** - Photo from webcam
2. **Face Recognition** - If face matches known faces
3. **Device Info**:
   - Device name (e.g., "USB Drive (E:)")
   - Device ID (serial number)
   - Connection action ("USB Inserted", "Mobile Connected", etc.)
   - Timestamp
4. **Authorization Status** - Whether device is whitelisted
5. **Face Status** - "Recognized", "Unknown", or "No Face Detected"

---

## 🔧 Troubleshooting

### "Cannot connect to API"
❌ **Error**: `Cannot connect to http://127.0.0.1:8000/api/security/event/`
✅ **Fix**: 
```bash
# Terminal 1: Make sure Django is running
cd backend && python manage.py runserver
```

### "No camera found"
❌ **Error**: `No camera found on system`
✅ **Fix**:
- Connect a webcam to your computer
- Test with Windows Camera app first
- If still failing, the script will still log events without images

### "No events showing in dashboard"
❌ **Error**: Admin Dashboard shows 0 USB events
✅ **Steps to Verify**:
1. Confirm USB Monitor is running (should see "Monitoring for USB..." message)
2. Insert a USB drive - monitor should show: `🔴 NEW USB DETECTED`
3. Check browser console for errors (F12)
4. Verify Django logs show `Event sent successfully`

### "Face recognition not working"
❌ **Error**: All faces show "Unknown"
✅ **Fix**:
1. Add authorized faces to: `backend/scripts/known_faces/`
2. Filename format: `person_name.jpg` (e.g., `john_doe.jpg`)
3. Restart USB Monitor
4. Next detection will recognize that face

---

## 📊 Testing Checklist

After all 3 services are running, test:

- [ ] USB INSERTION TEST
  1. Open Admin Dashboard → Live Monitoring
  2. Insert a USB drive
  3. Monitor shows `🔴 NEW USB DETECTED` 
  4. Event appears in dashboard within 3 seconds
  5. Image should show (if camera available)

- [ ] MOBILE DEVICE TEST
  1. Connect Android phone via USB (MTP mode)
  2. Monitor shows `📱 NEW MOBILE DETECTED`
  3. Event appears in dashboard
  4. Face/image captured

- [ ] USB REMOVAL TEST
  1. With USB still inserted, open file explorer
  2. Eject USB drive safely
  3. Monitor shows `⚪ USB REMOVED`
  4. Disconnect event logged

- [ ] FACE RECOGNITION TEST
  1. Add `backup.jpg` to `backend/scripts/known_faces/`
  2. Restart monitor
  3. Says "Loaded face: backup"
  4. Insert USB → Should show "Recognized: backup"

---

## 🗂️ File Locations

```
backend/
├── scripts/
│   ├── usb_monitor_enhanced.py      (Main monitor script - NEW & IMPROVED)
│   ├── security_captures/           (Auto-created - stores captured images)
│   └── known_faces/                 (Add authorized faces here as JPG/PNG)
├── security_logs/
│   ├── models.py                    (SecurityEvent model)
│   ├── views.py                     (API endpoints)
│   └── urls.py                      (Routes)
├── START_USB_MONITOR_ENHANCED.bat   (Easy startup batch file)
├── manage.py
└── db.sqlite3                       (Database with events)

frontend/
└── src/
    └── pages/
        └── LiveMonitoringPage.jsx   (Displays live events)
```

---

## 🔌 API Endpoints

### Send Security Event (from monitor)
```
POST /api/security/event/

Body:
{
    "user_id": 1,
    "action": "USB Inserted",
    "device_name": "USB Drive (E:)",
    "device_id": "ABC12345",
    "face_status": "Unknown",
    "image": <file>
}

Response: 201 Created
{
    "id": 123,
    "timestamp": "2026-04-04T17:45:32.123Z"
}
```

### Get Live Events (frontend polls this)
```
GET /api/admin/live-events/

Response: 200 OK
[
    {
        "id": 123,
        "action": "USB Inserted",
        "device_name": "USB Drive (E:)",
        "device_id": "ABC12345",
        "face_status": "Unknown",
        "is_authorized": false,
        "image_url": "/media/security_thumbnails/...",
        "timestamp": "2026-04-04T17:45:32.123Z"
    },
    ...
]
```

---

## 🛠️ Configuration Files

### `.active_user.json` (auto-created)
```json
{
    "id": 1,
    "username": "admin"
}
```
This tells the monitor which user to associate events with.

---

## 📝 Logs & Debug Info

The enhanced monitor prints:
- ✓ Each detected device
- ✓ Camera initialization attempts
- ✓ Image save locations
- ✓ Face recognition matches
- ✓ API request status
- ✓ Error details

Example output:
```
========================================================================
🛡️  SECURE FILE SHARING - USB DEVICE MONITOR (ENHANCED)
========================================================================
✓ Directory ready: backend/scripts/security_captures
✓ Directory ready: backend/scripts/known_faces
[*] Searching for camera...
✓ Camera found: Index 0, Backend cv2.CAP_MSMF
✓ Active User: admin (ID: 1)

[*] Monitoring for USB/Mobile device changes (press Ctrl+C to stop)...

🔴 NEW USB DETECTED: E: (ID: ABC123DEF)
[*] Searching for camera...
✓ Camera found: Index 0, Backend cv2.CAP_MSMF
✓ Image saved: backend/scripts/security_captures/sec_20260404_174532.jpg
[*] Sending event: USB Inserted | Device: USB Drive (E:)
✓ Event sent successfully
```

---

## 🔒 Security Notes

- Events are tied to authenticated admin users
- Images stored in backend media folder (add to .gitignore)
- All USB connections logged with timestamps
- Face recognition is completely offline (no cloud uploads)
- Events readonly by admins, create-only by monitor script

---

## 📞 Still Having Issues?

1. **Check Django is running**: http://localhost:8000/admin/ should work
2. **Check Frontend is running**: http://localhost:5173/ should load
3. **Check Monitor is running**: Should see "Monitoring for USB..." message
4. **Check Browser Console**: F12 → Console tab for any errors
5. **Check Terminal Output**: Monitor script should show all detection attempts

**All 3 must be running together for the system to work!**

---

## ✅ Complete System Status Checklist

- [ ] Database migrated (`python manage.py migrate` completed)
- [ ] Admin user created (`admin@central.com` / `admin123`)
- [ ] Django backend running on localhost:8000
- [ ] React frontend running on localhost:5173
- [ ] USB Monitor enhanced script ready
- [ ] Can login to admin dashboard
- [ ] Can see "Live Monitoring" page in admin menu
- [ ] Can insert USB and see event appear in real-time

Once all ✅, the system is fully operational!
