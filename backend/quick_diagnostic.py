#!/usr/bin/env python
"""
USB Monitoring System - Quick Diagnostic Test
Focus on USB detection, camera, database, and API
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

print("="*70)
print("🔧 USB MONITORING SYSTEM - DIAGNOSTIC TEST")
print("="*70)

# Test 1: Database Connection
print("\n[TEST 1] Database Connection")
print("-" * 70)
try:
    from security_logs.models import SecurityEvent
    count = SecurityEvent.objects.count()
    print(f"✓ Database connected")
    print(f"✓ Total events in database: {count}")
    
    # Show recent events
    recent = SecurityEvent.objects.all().order_by('-id')[:5]
    if recent:
        print(f"\nRecent events:")
        for event in recent:
            print(f"  - {event.action}: {event.device_name} ({event.timestamp})")
except Exception as e:
    print(f"✗ Database error: {e}")

# Test 2: Camera Detection
print("\n[TEST 2] Camera Detection")
print("-" * 70)
try:
    import cv2
    print("✓ OpenCV imported successfully")
    
    found_cameras = []
    for i in range(6):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"✓ Camera found at index {i}")
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"  ✓ Can capture frames")
                found_cameras.append(i)
            cap.release()
        else:
            cap.release()
    
    if not found_cameras:
        print("✗ No working camera found")
    else:
        print(f"✓ Total working cameras: {len(found_cameras)}")
except Exception as e:
    print(f"✗ Camera error: {e}")

# Test 3: API Connectivity
print("\n[TEST 3] API Connectivity")
print("-" * 70)
try:
    import requests
    response = requests.get('http://127.0.0.1:8000/api/security/event/', timeout=5)
    print(f"✓ API is responding")
    print(f"✓ Status code: {response.status_code}")
    if response.status_code == 401:
        print("  (401 is expected - authentication required)")
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to API at http://127.0.0.1:8000")
    print("  Make sure Django is running: python manage.py runserver")
except Exception as e:
    print(f"✗ API error: {e}")

# Test 4: USB Device Detection
print("\n[TEST 4] USB Device Detection (WMI)")
print("-" * 70)
try:
    import wmi
    import pythoncom
    
    # Initialize COM
    pythoncom.CoInitialize()
    
    c = wmi.WMI()
    print("✓ WMI initialized")
    
    # Check drives
    drives_found = []
    for disk in c.Win32_LogicalDisk():
        if disk.DriveType == 2:  # Removable
            drives_found.append(disk.DeviceID)
            print(f"✓ Found removable drive: {disk.DeviceID}")
    
    if not drives_found:
        print("  (No removable drives currently detected)")
    
    # Check portable devices
    portable_found = []
    for device in c.Win32_PnPEntity(ConfigManagerErrorCode=0):
        try:
            pnp_class = getattr(device, 'PNPClass', '')
            name = getattr(device, 'Name', '')
            if pnp_class == "WPD" or "Portable" in name:
                portable_found.append(name)
                print(f"✓ Found portable device: {name}")
        except:
            pass
    
    if not portable_found:
        print("  (No portable devices currently detected)")
    
    # Check USB devices
    usb_devices = []
    for device in c.Win32_USBDevice():
        try:
            name = getattr(device, 'Name', '')
            if name and len(usb_devices) < 5:  # Show first 5
                usb_devices.append(name)
                print(f"  USB: {name}")
        except:
            pass
    
    print(f"✓ WMI scan complete")
    
    pythoncom.CoUninitialize()
    
except Exception as e:
    print(f"✗ USB detection error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Monitor Script Check
print("\n[TEST 5] Monitor Script Availability")
print("-" * 70)
script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'smart_usb_monitor.py')
if os.path.exists(script_path):
    print(f"✓ Monitor script found: {script_path}")
    print(f"  File size: {os.path.getsize(script_path)} bytes")
else:
    print(f"✗ Monitor script not found: {script_path}")

# Test 6: Photo Directory
print("\n[TEST 6] Photo Storage Directory")
print("-" * 70)
photo_dir = os.path.join(os.path.dirname(__file__), 'scripts', 'security_captures')
if os.path.exists(photo_dir):
    photos = [f for f in os.listdir(photo_dir) if f.endswith('.jpg')]
    print(f"✓ Photo directory exists: {photo_dir}")
    print(f"✓ Photos stored: {len(photos)}")
    if photos:
        print(f"  Recent photos:")
        for photo in sorted(photos)[-3:]:
            path = os.path.join(photo_dir, photo)
            size = os.path.getsize(path)
            print(f"    - {photo} ({size} bytes)")
else:
    print(f"✗ Photo directory not found: {photo_dir}")
    print(f"  Creating directory...")
    os.makedirs(photo_dir, exist_ok=True)
    print(f"  ✓ Directory created")

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print("""
Next steps:
1. Make sure Django is running: python manage.py runserver
2. Connect a USB device or mobile phone (set to MTP mode)
3. Run the monitor: python scripts/smart_usb_monitor.py
4. Check the console for detection alerts
5. Verify photos appear in security_captures/
6. Check database for new events: python manage.py shell

If USB not detected:
- Check Device Manager for the device
- Try different USB port
- For mobile phones, set to "File Transfer" / MTP mode
- Install phone-specific USB drivers
- Restart the monitoring system
""")

print("="*70)
