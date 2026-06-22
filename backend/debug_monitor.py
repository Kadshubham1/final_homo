#!/usr/bin/env python
"""
Debug USB Monitor - Step-by-Step Testing
This script helps identify exactly why logs aren't being created
"""

import os
import sys
import time
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

print("="*70)
print("🔧 USB MONITOR DEBUGGING - STEP BY STEP")
print("="*70)

# TEST 1: Import all required modules
print("\n[TEST 1] Importing Required Modules")
print("-"*70)
try:
    import cv2
    print("✓ cv2 (OpenCV) imported")
except Exception as e:
    print(f"✗ cv2 import failed: {e}")
    sys.exit(1)

try:
    import requests
    print("✓ requests imported")
except Exception as e:
    print(f"✗ requests import failed: {e}")
    sys.exit(1)

try:
    import wmi
    import pythoncom
    print("✓ wmi and pythoncom imported")
except Exception as e:
    print(f"✗ wmi/pythoncom import failed: {e}")
    sys.exit(1)

# TEST 2: Database check
print("\n[TEST 2] Database Check")
print("-"*70)
try:
    from security_logs.models import SecurityEvent
    count = SecurityEvent.objects.count()
    print(f"✓ Database accessible")
    print(f"✓ Current events: {count}")
    
    # Get latest event
    if count > 0:
        latest = SecurityEvent.objects.latest('timestamp')
        print(f"✓ Latest event: {latest.action} - {latest.device_name}")
        print(f"  Timestamp: {latest.timestamp}")
        print(f"  Device ID: {latest.device_id}")
except Exception as e:
    print(f"✗ Database error: {e}")
    sys.exit(1)

# TEST 3: Camera test
print("\n[TEST 3] Camera Test")
print("-"*70)
try:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✓ Camera working")
            print(f"  Frame size: {frame.shape}")
        else:
            print("✗ Camera found but cannot read frames")
        cap.release()
    else:
        print("✗ Camera not found")
except Exception as e:
    print(f"✗ Camera error: {e}")

# TEST 4: API connectivity
print("\n[TEST 4] API Connectivity Test")
print("-"*70)
try:
    response = requests.get('http://127.0.0.1:8000/api/security/event/', timeout=5)
    print(f"✓ API responding")
    print(f"  Status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to API at http://127.0.0.1:8000")
    print("  Django may not be running. Start it with: python manage.py runserver")
    sys.exit(1)
except Exception as e:
    print(f"✗ API error: {e}")

# TEST 5: Manual event creation
print("\n[TEST 5] Manual Event Creation (Testing API POST)")
print("-"*70)
try:
    data = {
        "user_id": 1,
        "action": "TEST_CONNECTION",
        "device_name": "Test Device",
        "device_id": "TEST_ID_123",
        "face_status": "Unknown"
    }
    response = requests.post('http://127.0.0.1:8000/api/security/event/', 
                           data=data, 
                           timeout=5)
    print(f"✓ POST request sent")
    print(f"  Status code: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"✓ Event created successfully!")
        result = response.json()
        print(f"  Response: {result}")
        
        # Verify in database
        count_after = SecurityEvent.objects.count()
        if count_after > count:
            print(f"✓ Event saved to database!")
            print(f"  New total: {count_after}")
        else:
            print(f"✗ Event not saved to database")
    else:
        print(f"✗ API returned error: {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"✗ POST error: {e}")
    import traceback
    traceback.print_exc()

# TEST 6: USB/Mobile device detection
print("\n[TEST 6] USB/Mobile Device Detection")
print("-"*70)
try:
    pythoncom.CoInitialize()
    c = wmi.WMI()
    
    # Check for devices
    devices_found = []
    
    # Method 1: Check removable drives
    for disk in c.Win32_LogicalDisk():
        if disk.DriveType == 2:  # Removable
            devices_found.append(f"USB Drive: {disk.DeviceID}")
    
    # Method 2: Check portable devices
    for device in c.Win32_PnPEntity(ConfigManagerErrorCode=0):
        try:
            pnp_class = getattr(device, 'PNPClass', '')
            name = getattr(device, 'Name', '')
            if pnp_class == "WPD" or "Portable" in name:
                devices_found.append(f"Portable: {name}")
        except:
            pass
    
    if devices_found:
        print(f"✓ Found {len(devices_found)} device(s)")
        for dev in devices_found:
            print(f"  - {dev}")
    else:
        print("✗ No USB/removable devices detected")
        print("  Connect a USB device or mobile phone")
    
    pythoncom.CoUninitialize()
except Exception as e:
    print(f"✗ Device detection error: {e}")

# TEST 7: File system permissions
print("\n[TEST 7] File System Permissions")
print("-"*70)
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    capture_dir = os.path.join(script_dir, 'scripts', 'security_captures')
    
    # Ensure directory exists
    os.makedirs(capture_dir, exist_ok=True)
    
    # Try to write a test file
    test_file = os.path.join(capture_dir, 'test_write.txt')
    with open(test_file, 'w') as f:
        f.write("test")
    
    if os.path.exists(test_file):
        print(f"✓ Can write to directory")
        print(f"  Directory: {capture_dir}")
        os.remove(test_file)
    else:
        print(f"✗ Cannot write to directory")
except Exception as e:
    print(f"✗ Permission error: {e}")

# SUMMARY
print("\n" + "="*70)
print("DEBUGGING SUMMARY")
print("="*70)
print("""
If all tests pass (✓):
  → Monitor should work when you run: python scripts/smart_usb_monitor.py
  → Connect USB/mobile device
  → Watch console for alerts

If any tests failed (✗):
  → Fix the specific issue before running monitor
  → See error messages above

NEXT STEPS:

1. If all tests pass:
   python scripts/smart_usb_monitor.py

2. Connect USB/Mobile device

3. Check console output for:
   [!] 📱 ALERT: Device Detected
   [+] Photo captured
   [✓] Event sent successfully

4. Verify in database:
   python manage.py shell
   >>> from security_logs.models import SecurityEvent
   >>> SecurityEvent.objects.all()[:5]
""")
print("="*70)
