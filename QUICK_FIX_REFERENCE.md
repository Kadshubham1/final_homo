# Quick Reference - USB Security Monitoring Fix

## 🔧 Problems Fixed

| Problem | Cause | Solution |
|---------|-------|----------|
| Camera not opening | String escaping bug (`\\n` → `\n`) | Fixed print statements |
| Logs not created | Silent API failures | Added connection error handling |
| WMI errors in threads | COM not properly initialized | Added CoUninitialize in handlers |
| Dashboard crashes | Non-existent database fields | Updated queries to actual fields |

---

## 📁 Files Changed

### `backend/scripts/smart_usb_monitor.py`
- ✅ Fixed `get_wmi_client()` → added error handling
- ✅ Fixed `get_drives()` → added null checks
- ✅ Fixed `capture_instant_photo()` → comprehensive exception handling
- ✅ Fixed `get_mobile_devices()` → added try-except per device
- ✅ Fixed `send_security_event()` → detailed logging
- ✅ Fixed `main()` → corrected all escape sequences

### `backend/scripts/usb_monitor.py`
- ✅ Fixed `get_camera()` → error handling
- ✅ Fixed `capture_instant_photo()` → exception handling
- ✅ Fixed `send_to_server()` → connection error detection

### `backend/security_logs/views.py`
- ✅ Fixed `AdminSecurityDashboard.get()` → use actual DB fields
- ✅ Fixed `SecurityEventViewSet.create()` → enhanced logging

---

## 🚀 Quick Start

### 1. Start Backend
```bash
cd backend
python manage.py runserver
# Should show: "Starting development server at http://127.0.0.1:8000/"
```

### 2. Run Monitor
```bash
cd backend/scripts
python smart_usb_monitor.py
# Should show: "🛡️ REAL-TIME SECURITY MONITORING ENGAGED"
```

### 3. Insert USB & Check Logs
- **Photo**: Check `backend/scripts/security_captures/cap_YYYYMMDD_HHMMSS.jpg`
- **Event**: Visit `http://127.0.0.1:8000/api/security/event/`
- **Dashboard**: Visit `http://127.0.0.1:8000/api/security/admin/dashboard/`

---

## ⚙️ Key Improvements

### Camera Capture Flow
```
USB Inserted
    ↓
Attempt get_camera()
    ├─ Try indices 0-5
    ├─ Add error handling per index
    └─ Graceful fallback if not found
    ↓
Warmup frames (30 iterations)
    ├─ Check each frame
    ├─ Exit early if camera fails
    └─ Better error messages
    ↓
cv2.imwrite() → save to security_captures/
    ↓
Face recognition (if available)
    ├─ Load known faces
    ├─ Detect faces in image
    └─ Identify or mark as Unknown
    ↓
send_security_event() to API
    ├─ Include user info
    ├─ Include device info
    ├─ Include face status
    └─ Include photo file
```

### API Logging Flow
```
POST /api/security/event/
    ↓
SecurityEventViewSet.create()
    ├─ Validate serializer
    ├─ Resolve user (or use admin)
    ├─ Check authorization status
    ├─ Save to SecurityEvent table
    ├─ Log all details to console
    └─ Trigger alerts if needed
    ↓
Response with event ID & timestamp
```

---

## 🔍 Troubleshooting

### ❌ "Cannot connect to API"
- Check Django is running: `python manage.py runserver`
- Port 8000: `netstat -ano | findstr :8000`

### ❌ "No Camera Found"
- Install OpenCV: `pip install opencv-python`
- Check camera in Device Manager
- Try indices 0-2 (integrated cameras)

### ❌ "No logs appearing"
- Database migrated: `python manage.py migrate`
- Check Django console for error message
- Verify `/api/security/event/` endpoint accessible

### ❌ "WMI errors"
- Run as Administrator
- Install WMI: `pip install wmi`
- Check Windows Event Viewer

---

## 📊 Expected Output

### Console (Monitor Script)
```
==================================================
🛡️ REAL-TIME SECURITY MONITORING ENGAGED
   - Using Instant Photo Capture
   - File Copy Tracking Active
==================================================
[*] Monitoring USB Ports & Mobile Phones...
[*] Posting to http://127.0.0.1:8000/api/security/event/...
[+] Sending photo with event: cap_20260404_143022.jpg
[*] Posting data: action=USB Inserted, device=USB Drive (E:), face_status=Unknown
[+] Event 'USB Inserted' logged successfully on server.
```

### Database (API Response)
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "user": 1,
      "action": "USB Inserted",
      "device_name": "USB Drive (E:)",
      "device_id": "ABC123",
      "is_authorized": false,
      "face_status": "Unknown",
      "image": "/media/security_thumbnails/cap_20260404_143022.jpg",
      "timestamp": "2026-04-04T14:30:22.123456Z"
    }
  ]
}
```

---

## ✅ Verification Checklist

- [ ] Django running on :8000
- [ ] No errors during `runserver`
- [ ] Monitor starts without crashes
- [ ] Camera detected or "No Camera" message shown
- [ ] Insert USB triggers detection
- [ ] Photo saved to `security_captures/`
- [ ] Event appears in API response
- [ ] Dashboard shows stats

---

## 📚 Reference

- **Monitor Script**: `backend/scripts/smart_usb_monitor.py`
- **API Endpoint**: `POST /api/security/event/`
- **Dashboard**: `/api/security/admin/dashboard/`
- **Database**: `SecurityEvent`, `SecurityAlert`, `USBActivityLog` models
- **Full Guide**: `SECURITY_MONITORING_FIX.md`
