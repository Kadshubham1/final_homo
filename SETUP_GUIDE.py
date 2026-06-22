#!/usr/bin/env python
"""
STEP-BY-STEP USB MONITORING SETUP GUIDE

This file provides a checklist for setting up and testing USB monitoring
"""

print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   USB & MOBILE DEVICE MONITORING - SETUP & VERIFICATION GUIDE    ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

CURRENT STATUS:
✓ Database: Connected (38 events)
✓ Camera: Working (index 0)
✓ API: Responding (port 8000)
✓ Mobile Device: Detected (realme X7 5G)
✓ Monitor Script: Fixed (path handling)
✓ Photo Directory: Ready (backend/scripts/security_captures/)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRE-FLIGHT CHECKLIST:

Before starting, verify:

1. [ ] Django Backend Running
   Command: cd backend && python manage.py runserver
   Check: http://127.0.0.1:8000/admin/
   
2. [ ] USB/Mobile Device Connected & Ready
   - Plug in via USB cable
   - Phone setting: "File Transfer" or "MTP" mode (NOT charging)
   - Unlock device if required
   - Accept any permission prompts on device

3. [ ] Camera Available
   - Not being used by other apps (Zoom, Teams, etc.)
   - Permissions granted for Python access
   - Test: Run quick_diagnostic.py

4. [ ] Proper Path Setup
   - Monitor located at: backend/scripts/smart_usb_monitor.py
   - Photo dir ready: backend/scripts/security_captures/
   - Test: Run quick_diagnostic.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUICK START (Choose one method):

METHOD 1: Batch File (Windows - EASIEST)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1. Double-click: START_USB_MONITOR.bat
   2. Wait for "STARTING MONITOR" message
   3. Connect mobile device or USB
   4. Watch for alerts in console

METHOD 2: Python Startup Script
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1. Open terminal
   2. Run: python start_usb_monitor.py
   3. Connect mobile device or USB
   4. Watch for alerts in console

METHOD 3: Manual Two-Terminal Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Terminal 1 (Django):
   $ cd backend
   $ python manage.py runserver
   
   Terminal 2 (Monitor):
   $ cd backend/scripts
   $ python smart_usb_monitor.py
   
   Then connect mobile device or USB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXPECTED OUTPUT (When Device Connected):

[!] 📱 ALERT: Mobile Phone Detected: realme X7 5G
[*] Device ID: \\\\?\\usb#vid_0e8d&pid_0006...
[*] Camera found at index 0
[+] Security photo stored locally: backend/scripts/security_captures/cap_20260404_151523.jpg
[+] Photo captured: backend/scripts/security_captures/cap_20260404_151523.jpg
[*] Posting to http://127.0.0.1:8000/api/security/event/...
[+] Event 'Mobile Connected' logged successfully on server.
[✓] Event sent successfully to server

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERIFICATION AFTER RUNNING:

1. Check Photo Captured:
   $ ls backend\\scripts\\security_captures\\
   → Should see: cap_20260404_151523.jpg (or similar)

2. Check Database Event:
   $ cd backend
   $ python manage.py shell
   >>> from security_logs.models import SecurityEvent
   >>> e = SecurityEvent.objects.latest('id')
   >>> print(e.action, e.device_name, e.timestamp)
   Output: Mobile Connected Mobile Device (realme X7 5G) 2026-04-04 15:15:23...

3. Check API:
   http://127.0.0.1:8000/api/security/event/
   (May need authentication token)

4. Check Admin Dashboard:
   http://127.0.0.1:8000/admin/logs/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TROUBLESHOOTING:

If Monitor Doesn't Start:
┌─────────────────────────────────────────────────────────────────┐
│ 1. Run diagnostic: python backend\\quick_diagnostic.py          │
│ 2. Check Django: http://127.0.0.1:8000/admin/ (in browser)     │
│ 3. Check camera: python backend\\test_monitoring_system.py     │
│ 4. Check path: ls -R backend\\scripts\\                         │
```ψ 5. Try manual: cd backend\\scripts && python smart_usb_monitor.py│
└─────────────────────────────────────────────────────────────────┘

If Mobile Not Detected:
┌─────────────────────────────────────────────────────────────────┐
│ 1. Check Device Manager (Windows key + X)                       │
│ 2. Mobile setting: Settings → USB → File Transfer / MTP        │
│ 3. Different USB port (try USB 2.0 if available)               │
│ 4. Install phone drivers from manufacturer                      │
│ 5. Unplug, restart monitor, replug device                       │
└─────────────────────────────────────────────────────────────────┘

If Photos Not Saving:
┌─────────────────────────────────────────────────────────────────┐
│ 1. Directory exists: backend\\scripts\\security_captures\\     │
│ 2. Run diagnostic: python backend\\quick_diagnostic.py          │
│ 3. Check permissions: Can you create files in that folder?      │
│ 4. Restart monitor: Quit and restart                            │
└─────────────────────────────────────────────────────────────────┘

If Events Not in Database:
┌─────────────────────────────────────────────────────────────────┐
│ 1. Check Django console for errors                              │
│ 2. Verify API: curl -X POST http://127.0.0.1:8000/api/...      │
│ 3. Check migrations: python manage.py migrate                   │
│ 4. Check user: python manage.py shell                           │
│    >>> from django.contrib.auth.models import User             │
│    >>> User.objects.count()  # Should be > 0                    │
└─────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUICK DIAGNOSTIC TEST:

Run this to verify everything is working:

  $ cd backend
  $ python quick_diagnostic.py

Expected results:
  ✓ Database connected
  ✓ Camera found at index 0
  ✓ API responding with HTTP 401
  ✓ Portable device: realme X7 5G
  ✓ Monitor script exists
  ✓ Photo directory created

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEY FACTS:

• USB/Mobile Detection: Uses WMI (Windows Management Instrumentation)
  → Scans for Portable Devices, USB Storage, Removable Drives
  → Polls every 2 seconds for changes

• Camera Capture: Uses OpenCV (cv2)
  → Automatically captures photo when device connected
  → Performs face recognition if trained images available

• Event Logging: Uses Django REST API
  → Posts event data to http://127.0.0.1:8000/api/security/event/
  → Stores in database with timestamp and metadata

• Photo Storage: Absolute path from script location
  → backend/scripts/security_captures/cap_YYYYMMDD_HHMMSS.jpg
  → Creates automatically on first run

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SYSTEM ARCHITECTURE:

  USB Connected
      ↓
  WMI Detection (2s polling)
      ↓
  Device Found? → YES → Capture Photo (cv2)
                         ↓
                    Face Recognition
                         ↓
                    POST to API
                         ↓
                    Save to Database
                         ↓
                    HTTP 201 Response

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FILES UPDATED:

✓ backend/scripts/smart_usb_monitor.py
  - Path handling fixed (absolute paths)
  - Mobile detection enhanced (3 methods)
  - Better logging and error messages

✓ start_usb_monitor.py (NEW)
  - Proper directory setup
  - Django status check
  - Clean startup process

✓ START_USB_MONITOR.bat (NEW)
  - One-click Windows launcher
  - Django compatibility check
  - Error reporting

✓ quick_diagnostic.py
  - Comprehensive system check
  - Component status verification
  - Issue identification

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

READY TO START?

1. Make sure Django is running
2. Run: START_USB_MONITOR.bat (or python start_usb_monitor.py)
3. Connect mobile device or USB
4. Check console for alerts
5. Verify photo saved to backend/scripts/security_captures/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("\n✅ Setup guide complete! Ready to monitor USB devices.")
print("\nNext step: Run START_USB_MONITOR.bat or python start_usb_monitor.py")
