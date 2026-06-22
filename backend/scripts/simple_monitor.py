#!/usr/bin/env python
"""
SIMPLE MONITOR - Direct device detection with real-time logging
This version logs EVERY device found, not just changes
"""

import os
import sys
import time
import json
import requests
from datetime import datetime

# Setup paths
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

# Imports
try:
    import wmi
    import pythoncom
except:
    print("ERROR: wmi library missing. Run: pip install wmi")
    sys.exit(1)

try:
    import cv2
except:
    print("ERROR: cv2 library missing. Run: pip install opencv-python")
    sys.exit(1)

# Configuration
API_URL = "http://127.0.0.1:8000/api/security/event/"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_SAVE_DIR = os.path.join(SCRIPT_DIR, "security_captures")

os.makedirs(MEDIA_SAVE_DIR, exist_ok=True)

def get_devices():
    """Get ALL USB and mobile devices currently connected"""
    pythoncom.CoInitialize()
    try:
        wmi_client = wmi.WMI()
        devices = {}
        
        # USB Drives
        for disk in wmi_client.Win32_LogicalDisk():
            if disk.DriveType == 2:  # Removable drives
                devices[disk.DeviceID] = {
                    'type': 'USB_DRIVE',
                    'name': f'USB Drive {disk.DeviceID}',
                    'id': disk.VolumeSerialNumber
                }
        
        # Portable devices (phones, etc)
        for device in wmi_client.Win32_PnPEntity(ConfigManagerErrorCode=0):
            try:
                name = getattr(device, 'Name', '')
                pnp_class = getattr(device, 'PNPClass', '')
                device_id = getattr(device, 'DeviceID', '')
                
                if pnp_class == "WPD" or "Portable" in name or "Phone" in name:
                    devices[device_id] = {
                        'type': 'PORTABLE',
                        'name': name,
                        'id': device_id
                    }
            except:
                pass
        
        return devices
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def capture_photo():
    """Capture one photo"""
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            return None
        
        # Warmup frames
        for _ in range(10):
            cap.read()
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(MEDIA_SAVE_DIR, f"cap_{timestamp}.jpg")
            cv2.imwrite(filename, frame)
            return filename
        
        return None
    except Exception as e:
        print(f"[-] Photo error: {e}")
        return None

def send_event(action, device_name, device_id, photo_path=None):
    """Send event to API"""
    try:
        data = {
            "user_id": 1,
            "action": action,
            "device_name": device_name,
            "device_id": device_id,
            "face_status": "Unknown"
        }
        
        files = {}
        if photo_path and os.path.exists(photo_path):
            files["image"] = open(photo_path, "rb")
        
        response = requests.post(API_URL, data=data, files=files if files else None, timeout=10)
        
        if photo_path and files:
            files["image"].close()
        
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"[-] API error: {e}")
        return False

# Main loop
print("\n" + "="*70)
print("🛡️ SIMPLE MONITOR - REAL-TIME LOGGING")
print("="*70)
print("\nConnecting USB device or mobile phone now...")
print("Watch this console for detection...\n")

seen_devices = {}
error_count = 0

while True:
    try:
        current_devices = get_devices()
        
        # Check for new devices
        for device_id, info in current_devices.items():
            if device_id not in seen_devices:
                print(f"\n{'='*70}")
                print(f"[!] NEW DEVICE DETECTED!")
                print(f"    Type: {info['type']}")
                print(f"    Name: {info['name']}")
                print(f"    ID: {device_id}")
                print(f"    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Try to capture photo
                print(f"[*] Capturing photo...")
                photo = capture_photo()
                if photo:
                    print(f"[+] Photo saved: {photo}")
                else:
                    print(f"[-] Could not capture photo")
                
                # Send to API
                print(f"[*] Sending to API...")
                if send_event(f"{info['type']}_CONNECTED", info['name'], device_id, photo):
                    print(f"[✓] Event logged successfully!")
                else:
                    print(f"[✗] Failed to log event")
                
                print(f"{'='*70}\n")
                seen_devices[device_id] = info
                error_count = 0
        
        # Check for removed devices
        removed = set(seen_devices.keys()) - set(current_devices.keys())
        for device_id in removed:
            info = seen_devices[device_id]
            print(f"[!] Device removed: {info['name']}")
            send_event(f"{info['type']}_REMOVED", info['name'], device_id)
            del seen_devices[device_id]
        
        if not current_devices and seen_devices:
            print(f"[*] No devices connected. Waiting...")
        
        time.sleep(1)
        error_count = 0
        
    except Exception as e:
        error_count += 1
        print(f"[-] Error: {e}")
        if error_count > 5:
            print("[-] Too many errors. Exiting.")
            break
        time.sleep(2)

print("\n[!] Monitor stopped")
