# Security Monitoring Fix - Complete Solution

## Problem Summary
When USB devices connected, the security monitoring system was not:
1. Capturing photos from camera
2. Creating logs in the database
3. Properly handling errors

## Root Causes Fixed

### 1. **String Escaping Bug in smart_usb_monitor.py**
- **Issue**: Print statements used `\\n` instead of `\n`
- **Impact**: Newlines were being printed as literal text instead of actual newlines
- **Fix**: Changed all `\\n` to `\n` in the main() function

### 2. **Camera Initialization Issues**
- **Issue**: Camera detection didn't handle multiple failures gracefully
- **Impact**: Camera would fail silently, no logs created
- **Fix**: 
  - Added proper error handling in `get_camera()` function
  - Improved camera warmup with frame-by-frame error checking
  - Added exception handling in `capture_instant_photo()`

### 3. **WMI Threading Issues** 
- **Issue**: COM initialization (`pythoncom.CoInitialize()`) not properly managed in threads
- **Impact**: Drive detection would fail in multi-threaded contexts
- **Fix**:
  - Added `pythoncom.CoUninitialize()` in error handlers
  - Added error logging for WMI initialization failures
  - Added try-except blocks around COM operations

### 4. **API Connection Error Handling**
- **Issue**: Connection failures were silently ignored
- **Impact**: No indication when backend was unreachable
- **Fix**:
  - Separated `requests.ConnectionError` from generic exceptions
  - Added helpful error messages pointing to port 8000
  - Added response return values for tracking

### 5. **Database Model Mismatch**
- **Issue**: Views tried to filter by non-existent fields (`is_suspicious`, `risk_level`)
- **Impact**: Dashboard queries would crash
- **Fix**: Updated AdminSecurityDashboard to use actual database fields

### 6. **Missing Event Logging**
- **Issue**: Security events not saved to database on errors
- **Impact**: No audit trail of USB detection attempts
- **Fix**: Added detailed console logging and database save verification

## Files Modified

### 1. `backend/scripts/smart_usb_monitor.py`
- Fixed string escaping in main() function
- Improved `get_wmi_client()` error handling
- Enhanced `capture_instant_photo()` with proper exception handling
- Improved `get_mobile_devices()` robustness
- Enhanced `send_security_event()` with detailed logging

### 2. `backend/scripts/usb_monitor.py`
- Improved `get_camera()` error handling
- Enhanced `capture_instant_photo()` error handling
- Improved `send_to_server()` with connection error detection

### 3. `backend/security_logs/views.py`
- Fixed AdminSecurityDashboard model field references
- Enhanced SecurityEventViewSet.create() with detailed logging
- Added timestamp to response

## How to Test

### Step 1: Start Django Backend
```bash
cd backend
python manage.py runserver
```
Should see: `Starting development server at http://127.0.0.1:8000/`

### Step 2: Verify Database Tables Exist
```bash
cd backend
python manage.py migrate
```

### Step 3: Run the Monitor Script
```bash
cd backend/scripts
python smart_usb_monitor.py
```

You should see:
```
==================================================
🛡️ REAL-TIME SECURITY MONITORING ENGAGED
   - Using Instant Photo Capture
   - File Copy Tracking Active
==================================================
[*] Monitoring USB Ports & Mobile Phones...
```

### Step 4: Insert USB Device
When you insert a USB:
1. Monitor logs should show: `[!] 🔴 ALERT: USB Detected: E: (ID: xxxxx)`
2. Camera should attempt capture: `[+] Security photo stored locally: security_captures/cap_YYYYMMDD_HHMMSS.jpg`
3. API call should log: `[+] Event 'USB Inserted' logged successfully on server.`
4. In Django, check: `http://127.0.0.1:8000/api/security/event/`

## Debugging Guide

### Issue: "Cannot connect to API at http://127.0.0.1:8000"
**Solution**:
- Make sure Django is running: `python manage.py runserver`
- Check port 8000 is not in use: `netstat -ano | findstr :8000`

### Issue: "No working camera found"
**Solution**:
- Install OpenCV: `pip install opencv-python`
- Check camera in Device Manager (should be under Imaging devices)
- Try lower indices first (0-2 are usually integrated cameras)

### Issue: "WMI Drive Error"
**Solution**:
- Ensure you have WMI installed: `pip install wmi`
- Run as Administrator (some WMI queries need elevated privileges)
- Check Windows Event Viewer for COM errors

### Issue: Photos not being saved
**Solution**:
- Check directory exists: `security_captures/` folder in backend/scripts
- Check file permissions - script needs write access
- Check `capture_instant_photo()` returns a valid path

### Issue: Logs not appearing in database
**Solution**:
- Verify SecurityEvent table exists: `python manage.py migrate`
- Check API response status code (should be 201)
- Look for error messages in Django console

## Verification Checklist

- [ ] Django backend running on http://127.0.0.1:8000
- [ ] Database migrated: `python manage.py migrate`
- [ ] Monitor script runs without immediate errors
- [ ] Camera is detected or "No Camera" message shown
- [ ] Insert USB detects and logs event
- [ ] Photo saved to `security_captures/` folder
- [ ] Event appears in `/api/security/event/` endpoint
- [ ] Check dashboard: `http://127.0.0.1:8000/api/security/admin/dashboard/`

## Active User Tracking

The monitor scripts now read from `.active_user.json` to track which user is logged in:

```json
{
  "id": 1,
  "username": "admin"
}
```

This file should be updated by the login system when users log in. Currently defaults to user ID 1 (admin).

## API Endpoints

### View Live Events
```
GET /api/security/event/
```

### View Summary
```
GET /api/security/usb-log/summary/
```

### Admin Dashboard
```
GET /api/security/admin/dashboard/
```

### Manual Event Creation (for testing)
```bash
curl -X POST http://127.0.0.1:8000/api/security/event/ \
  -F "action=USB Inserted" \
  -F "device_name=Test USB" \
  -F "device_id=TEST123" \
  -F "user_id=1" \
  -F "face_status=Unknown" \
  -F "image=@test_photo.jpg"
```

## Important Configuration

### `.env` Variables (if used)
```
API_URL=http://127.0.0.1:8000/api/security/event/
USER_ID=1
```

### Camera Setup
- For face recognition: Add jpeg images to `known_faces/` folder
- File naming: `{person_name}.jpg` (e.g., `john_doe.jpg`)
- Images should show clear frontal face

## Performance Tips

1. **Reduce CPU usage**: Increase polling interval in main loop from 2 seconds
2. **Improve camera capture speed**: Reduce warmup frames if quality acceptable
3. **Batch events**: Implement event queuing if lots of USB devices detected
4. **Database optimization**: Add indexes on frequently queried fields

## Security Notes

⚠️ **Important**: This system logs USB connections and captures photos when USB devices are detected. Ensure:
- Users are informed (transparent mode)
- Appropriate privacy policies are in place
- Data is protected (use HTTPS in production)
- Access to logs is restricted to authorized personnel
- Keep Django DEBUG=False in production
- Store database securely with proper backups

## Next Steps

1. Test with real USB devices
2. Configure face recognition with known_faces/ dataset
3. Set up email alerts in Django settings
4. Deploy monitor script as system service/scheduled task
5. Implement log rotation for security_captures/
6. Monitor database growth and plan archival strategy
