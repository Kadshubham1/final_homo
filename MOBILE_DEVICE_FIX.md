# 📱 Mobile Device Monitoring - Fix & Troubleshooting Guide

## 🔴 ISSUE REPORTED

When connecting a mobile device:
- ✗ Logs not being created
- ✗ Camera not capturing
- ✗ No events in database

---

## ✅ WHAT WAS FIXED

### 1. **Enhanced Mobile Device Detection**
- **Before**: Only checked WPD (Windows Portable Devices) class
- **After**: Now uses 3 different detection methods:
  - Win32_PnPEntity (WPD/Portable devices)
  - Win32_USBDevice (Direct USB enumeration)
  - Win32_USBStorageDevice (USB storage detection)

### 2. **Better Error Logging**
- Added detailed console output for each detection step
- Shows which detection methods succeed/fail
- Displays device names and IDs as they're found

### 3. **Camera Capture on Mobile Connection**
- Camera now triggers when mobile device detected
- Better feedback if camera unavailable
- Photos saved with timestamp

### 4. **Event Logging Feedback**
- Shows if event was successfully sent to server
- Logs connection errors
- Reports HTTP response codes

---

## 🧪 DIAGNOSTIC TEST

### What to Do

1. **Connect your mobile device via USB**
2. **Open PowerShell and run:**

```bash
cd c:\Users\Admin\Music\updated-homo\updated-homo
python test_mobile_detection.py
```

3. **Follow the prompts:**
   - The test will scan for all connected devices
   - Results show all detection methods
   - You'll see which method(s) found your device

### Expected Output Example

```
TEST 1: Win32_PnPEntity (Plug and Play Devices)
  Device: Samsung Galaxy S22
  PNP Class: WPD
  ✓ MOBILE DEVICE DETECTED!

TEST SUMMARY
✓ PASS: PnPEntity (WPD)
✓ PASS: USBDevice
✓ PASS: LogicalDisk

✓ Device detection working!
```

---

## 🚀 IMPROVED MONITOR SCRIPT

### What Changed

**File:** `backend/scripts/smart_usb_monitor.py`

**Changes:**
1. **get_mobile_devices()** - Now uses 3 detection methods
2. **Main loop** - Added detailed logging for each event
3. **Camera capture** - Now logs if photo captured successfully
4. **Event posting** - Reports success/failure to console

### Starting the Monitor

```bash
cd backend
python manage.py runserver      # Terminal 1

cd backend/scripts
python smart_usb_monitor.py     # Terminal 2
```

### Expected Console Output

**When mobile device connects:**
```
[*] Monitoring USB Ports & Mobile Phones...
[*] Starting main monitoring loop (polling every 2 seconds)...
[*] Initial state: 0 USB drives, 0 mobile devices

... wait for device ...

[!] 📱 ALERT: Mobile Phone Detected: Samsung Galaxy S22
[*] Device ID: \\?\usb#vid_04e8&pid_...
[*] Camera found at index 0
[+] Security photo stored locally: security_captures/cap_20260404_143022.jpg
[+] Photo captured: security_captures/cap_20260404_143022.jpg
[*] Posting to http://127.0.0.1:8000/api/security/event/...
[+] Event 'Mobile Connected' logged successfully on server.
[✓] Event sent successfully to server
```

---

## 🔧 TROUBLESHOOTING STEPS

### Problem 1: Mobile device not detected by test

**Solution A: Check USB Mode**
1. On your phone, go to Settings
2. Search for "USB" or "Connection"
3. Change from "Charging" to **"File Transfer"** or **"MTP"**
4. Re-run test

**Solution B: Install Phone Drivers**
1. Visit manufacturer website (Samsung, Google, Apple, etc.)
2. Download USB drivers for your phone model
3. Install drivers
4. Reconnect phone
5. Re-run test

**Solution C: Try Different USB Port**
1. Try the other USB port on your computer
2. Some ports may have better device compatibility

**Solution D: Check Device Manager**
1. Open Device Manager (Windows key + X, then Device Manager)
2. Look for "Unknown devices" or devices with warning (!)
3. Right-click → Update driver
4. Choose "Browse my computer for drivers"

### Problem 2: Test shows device but monitor still doesn't work

**Check 1: Django Backend Running**
```bash
# Another terminal
curl http://127.0.0.1:8000/api/security/event/
# Should return JSON (may need auth token)
```

**Check 2: Camera Working**
```bash
python -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print('✓ Camera works')
        cv2.imwrite('test.jpg', frame)
    else:
        print('✗ Cannot read frame')
else:
    print('✗ Camera not found')
cap.release()
"
```

**Check 3: API Connectivity**
```bash
python -c "
import requests
try:
    r = requests.post('http://127.0.0.1:8000/api/security/event/', 
                      data={'action': 'test', 'device_name': 'test'})
    print(f'✓ API responding: {r.status_code}')
except Exception as e:
    print(f'✗ API error: {e}')
"
```

### Problem 3: Events not saving to database

**Cause:** Usually API authentication issue

**Solution:**
1. Check Django has admin user created:
```bash
cd backend
python manage.py shell
>>> from accounts.models import User
>>> User.objects.count()
```

2. If 0 users, create admin:
```bash
python manage.py createsuperuser
```

3. Check API endpoint accepts POST:
```bash
curl -X POST http://127.0.0.1:8000/api/security/event/ \
  -H "Content-Type: application/json" \
  -d '{"action":"Test","device_name":"test"}'
```

### Problem 4: Camera not capturing when mobile connected

**Check 1: Camera available**
```bash
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
# Should print: True
```

**Check 2: Camera in use**
- Close any other apps using camera (zoom, Teams, etc.)
- Close browser camera access
- Try camera test again

**Check 3: Different camera index**
```bash
python -c "
import cv2
for i in range(6):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f'Camera found at index {i}')
    cap.release()
"
```

If different camera found, edit `smart_usb_monitor.py`:
```python
# Line ~115 - change 0 to found index
cap = cv2.VideoCapture(CAMERA_INDEX)  # Default: 0
```

---

## 📊 VERIFICATION CHECKLIST

Before running, verify:

- [ ] Mobile device plugged in via USB
- [ ] Mobile set to "File Transfer" / "MTP" mode
- [ ] Mobile device drivers installed
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Django backend running on port 8000
- [ ] Camera working on computer
- [ ] No other apps using camera
- [ ] test_mobile_detection.py runs and finds device

---

## 🎯 QUICK START AFTER FIX

1. **Test detection:**
```bash
python test_mobile_detection.py
```

2. **Start monitoring:**
```bash
START_MONITOR.bat
# OR
python quick_start.py
```

3. **Connect mobile device**

4. **Check results:**
   - Monitor window shows alert
   - Photo appears in `backend/scripts/security_captures/`
   - Event appears in database

---

## 📱 DEVICE SPECIFIC SETUP

### Samsung Phones
1. Settings → Connections → USB
2. Select "File Transfer"
3. Computer will recognize as portable device

### iPhone (With Windows)
1. Install iTunes from Microsoft Store
2. Plugin iPhone
3. Trust this computer on iPhone
4. USB driver installed automatically

### Google Pixel
1. Settings → Developer Options → USB Configuration
2. Select "File Transfer"

### OnePlus
1. Settings → Connected devices → USB
2. Select "File Transfer" or "MIDI"

### Generic Android
1. Settings → About Phone → Tap 7x to enable Developer Options
2. Settings → Developer Options → USB Configuration
3. Select "File Transfer" or "MTP"

---

## 📋 FILES MODIFIED/CREATED

| File | Change |
|------|--------|
| `backend/scripts/smart_usb_monitor.py` | Enhanced get_mobile_devices(), better logging |
| `test_mobile_detection.py` | NEW - Diagnostic test for mobile detection |
| `backend/test_monitoring_system.py` | Already includes mobile device test |

---

## 🎯 NEXT STEPS

1. **Immediate:**
   - Run `python test_mobile_detection.py`
   - Verify device is detected
   - Report results

2. **If test passes:**
   - Start monitor with `START_MONITOR.bat`
   - Connect mobile device
   - Check for photo and log entry

3. **If test fails:**
   - Follow troubleshooting for your device
   - Try different USB port
   - Install vendor drivers
   - Re-test

---

## 💡 ADVANCED DEBUGGING

### Enable Verbose Output

Edit `backend/scripts/smart_usb_monitor.py` and add after line 40:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check WMI Directly (PowerShell)

```powershell
Get-WmiObject Win32_PnPEntity | Where {$_.Name -match "phone|mtp|portable"}
```

### View All Connected USB Devices

```powershell
Get-PnpDevice | Where {$_.Class -match "USB|WPD"}
```

---

**Status: Enhanced mobile device detection implemented**  
**Test: Run `test_mobile_detection.py` to verify**  
**Support: Follow troubleshooting steps above**

Let me know if mobile devices are now being detected! ✅
