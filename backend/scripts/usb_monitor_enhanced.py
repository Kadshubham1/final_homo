#!/usr/bin/env python3
"""
Enhanced Real-Time USB/Mobile Device Monitor with Image Capture
✅ Automatic admin user detection
✅ Robust camera initialization
✅ Comprehensive logging
✅ Cross-platform support (Windows, Linux, macOS)
"""

import os
import sys
import time
import json
import requests
import threading
from datetime import datetime
from pathlib import Path

print("=" * 70)
print("[SECURE]  SECURE FILE SHARING - USB DEVICE MONITOR (ENHANCED)")
print("=" * 70)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    print("[WARNING] watchdog not installed. Install with: pip install watchdog")

try:
    import wmi
    import pythoncom
    HAS_WMI = True
except ImportError:
    HAS_WMI = False
    print("[WARNING] WMI not available (Windows only library). USB detection may be limited.")

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    print("[ERROR] OpenCV not installed. Install with: pip install opencv-contrib-python")

try:
    import face_recognition
    HAS_FACE_RECOGNITION = True
except ImportError:
    HAS_FACE_RECOGNITION = False
    print("[WARNING] face_recognition not installed. Face detection disabled.")

# Configuration
API_URL = "http://127.0.0.1:8000/api/security/event/"
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_SAVE_DIR = os.path.join(SCRIPT_DIR, "security_captures")
KNOWN_FACES_DIR = os.path.join(SCRIPT_DIR, "known_faces")
ACTIVE_USER_CONFIG = os.path.join(BACKEND_DIR, '.active_user.json')

# Ensure directories exist
for directory in [MEDIA_SAVE_DIR, KNOWN_FACES_DIR]:
    Path(directory).mkdir(parents=True, exist_ok=True)
    print(f"[OK] Directory ready: {directory}")

known_face_encodings = []
known_face_names = []

def get_active_user_id():
    """Get the active admin user ID"""
    try:
        # Check if config file exists
        if os.path.exists(ACTIVE_USER_CONFIG):
            with open(ACTIVE_USER_CONFIG, 'r') as f:
                data = json.load(f)
                return data.get('id', 1), data.get('username', 'Default Admin')
    except Exception as e:
        print(f"[WARNING] Could not read active user config: {e}")
    
    # Query Django ORM to get first admin user
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        import django
        django.setup()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            return admin_user.id, admin_user.username
    except Exception as e:
        print(f"[WARNING] Could not query database for admin user: {e}")
    
    # Create config file with default user
    try:
        default_config = {'id': 1, 'username': 'Default Admin'}
        with open(ACTIVE_USER_CONFIG, 'w') as f:
            json.dump(default_config, f)
        return 1, 'Default Admin'
    except Exception as e:
        print(f"[ERROR] Could not create config file: {e}")
        return 1, 'Default Admin'

def load_known_faces():
    """Load authorized faces for recognition"""
    if not HAS_FACE_RECOGNITION or not os.path.exists(KNOWN_FACES_DIR):
        return
    
    face_files = list(Path(KNOWN_FACES_DIR).glob("*.jpg")) + list(Path(KNOWN_FACES_DIR).glob("*.png"))
    
    if not face_files:
        print(f"[*] No known faces found in {KNOWN_FACES_DIR}")
        return
    
    for face_file in face_files:
        try:
            img = face_recognition.load_image_file(str(face_file))
            encodings = face_recognition.face_encodings(img)
            if encodings:
                known_face_encodings.append(encodings[0])
                name = face_file.stem
                known_face_names.append(name)
                print(f"[OK] Loaded face: {name}")
        except Exception as e:
            print(f"[ERROR] Failed to load face {face_file.name}: {e}")

def get_camera():
    """Find and initialize camera with multiple backends"""
    if not HAS_OPENCV:
        print("[ERROR] OpenCV not available")
        return None

    print("[*] Searching for camera...")
    
    backends = []
    if os.name == 'nt':  # Windows
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    elif sys.platform == 'darwin':  # macOS
        backends = [cv2.CAP_AVFOUNDATION, cv2.CAP_ANY]
    else:  # Linux
        backends = [cv2.CAP_V4L2, cv2.CAP_ANY]

    for backend in backends:
        for i in range(0, 10):
            try:
                cap = cv2.VideoCapture(i, backend)
                if cap and cap.isOpened():
                    print(f"[OK] Camera found: Index {i}, Backend {backend}")
                    return cap
                if cap:
                    cap.release()
            except Exception as e:
                continue

    print("[ERROR] No camera found on system")
    return None

def capture_instant_photo():
    """Capture photo from camera with face recognition"""
    try:
        cap = get_camera()
        if not cap:
            return None, "No Camera Available"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = os.path.join(MEDIA_SAVE_DIR, f"sec_{timestamp}.jpg")
        
        # Warm up camera
        for attempt in range(50):
            ret, _ = cap.read()
            if ret:
                break
        
        # Capture frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            return None, "Camera Read Error"
        
        # Save image
        cv2.imwrite(image_filename, frame)
        print(f"[OK] Image saved: {image_filename}")
        
        # Face recognition
        face_status = "Unknown"
        if HAS_FACE_RECOGNITION and known_face_encodings:
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encs = face_recognition.face_encodings(rgb_frame, face_locations)
                
                if face_locations:
                    for face_encoding in face_encs:
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
                        if True in matches:
                            match_idx = matches.index(True)
                            face_status = f"Recognized: {known_face_names[match_idx]}"
                            print(f"[OK] Face recognized: {known_face_names[match_idx]}")
                            break
                else:
                    face_status = "No Face Detected"
            except Exception as e:
                face_status = f"Recognition Error: {str(e)[:30]}"
        
        return image_filename, face_status
        
    except Exception as e:
        print(f"[ERROR] Camera error: {e}")
        return None, f"Error: {str(e)[:50]}"

def get_drives():
    """Get list of USB drives with comprehensive hardware info"""
    drives = {}
    
    if not HAS_WMI:
        return drives
    
    try:
        pythoncom.CoInitialize()
        c = wmi.WMI()
        
        for logical_disk in c.Win32_LogicalDisk(DriveType=2):
            drive_letter = logical_disk.DeviceID
            serial = getattr(logical_disk, 'VolumeSerialNumber', '')
            disk_info = {
                "serial": serial,
                "drive_letter": drive_letter,
                "manufacturer": "Unknown",
                "model": "USB Drive",
                "vid": "",
                "pid": ""
            }
            
            try:
                partitions = c.query(f"ASSOCIATORS OF {{Win32_LogicalDisk.DeviceID='{drive_letter}'}} WHERE AssocClass=Win32_LogicalDiskToPartition")
                for p in partitions:
                    disk_drives = c.query(f"ASSOCIATORS OF {{Win32_DiskPartition.DeviceID='{p.DeviceID}'}} WHERE AssocClass=Win32_DiskDriveToDiskPartition")
                    for dd in disk_drives:
                        pnp_id = dd.PNPDeviceID or ""
                        vid, pid = "", ""
                        if "VID_" in pnp_id and "PID_" in pnp_id:
                            try:
                                parts = pnp_id.split("\\")[1].split("&")
                                vid = next((x.replace("VID_", "") for x in parts if x.startswith("VID_")), "")
                                pid = next((x.replace("PID_", "") for x in parts if x.startswith("PID_")), "")
                            except:
                                pass
                        disk_info["manufacturer"] = dd.Manufacturer or "Unknown"
                        disk_info["model"] = dd.Model or "Unknown"
                        disk_info["vid"] = vid
                        disk_info["pid"] = pid
                        if dd.SerialNumber:
                            disk_info["serial"] = dd.SerialNumber.strip()
            except Exception as e:
                pass
            
            drives[drive_letter] = disk_info
            print(f"[*] Detected USB: {drive_letter} (Model: {disk_info['model']}, VID: {disk_info['vid']}, PID: {disk_info['pid']})")
        
        pythoncom.CoUninitialize()
    except Exception as e:
        print(f"[WARNING] WMI Error: {e}")
    
    return drives

def get_mobile_devices():
    """Get list of connected mobile devices via WMI (MTP/WPD)"""
    devices = {}
    
    if not HAS_WMI:
        return devices
    
    try:
        pythoncom.CoInitialize()
        c = wmi.WMI()
        
        # Method: Find WPD (Windows Portable Devices) which includes Android phones
        try:
            for device in c.Win32_PnPEntity():
                pnp_class = getattr(device, 'PNPClass', '')
                if not pnp_class:
                    continue
                    
                if pnp_class.upper() in ['WPD', 'IMAGE']:
                    name = getattr(device, 'Name', '') or getattr(device, 'Description', '')
                    device_id = getattr(device, 'PNPDeviceID', '')
                    
                    if name and device_id:
                        devices[name] = device_id
                        print(f"[*] Detected Mobile/MTP Device: {name}")
        except Exception as e:
            print(f"[WARNING] WMI Mobile Enum Error: {e}")
        
        pythoncom.CoUninitialize()
    except Exception as e:
        print(f"[WARNING] Mobile detection error: {e}")
    
    return devices

def send_security_event(action, device_name, device_id, image_path=None, face_status="Unknown", system_info=None):
    """Send security event to backend API"""
    user_id, username = get_active_user_id()
    
    print(f"[*] Sending event: {action} | Device: {device_name}")
    
    data = {
        "user_id": user_id,
        "action": action,
        "device_name": device_name,
        "device_id": device_id,
        "face_status": face_status
    }
    
    import platform
    if system_info:
        system_info["os"] = platform.system()
        data["system_info"] = json.dumps(system_info)
    data["hostname"] = platform.node()
    
    files = {}
    img_handle = None
    
    try:
        if image_path and os.path.exists(image_path):
            img_handle = open(image_path, "rb")
            files["image"] = img_handle
        
        response = requests.post(API_URL, data=data, files=files if files else None, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"[OK] Event sent successfully")
            return True
        else:
            print(f"[ERROR] API Error {response.status_code}: {response.text[:100]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to {API_URL}")
        print(f"   Make sure Django is running: python manage.py runserver")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False
    finally:
        if img_handle:
            img_handle.close()

def main():
    print("\n" + "=" * 70)
    print("Starting USB Device Monitor...")
    print("=" * 70)
    
    print("[*] Verifying backend connection...")
    try:
        r = requests.get(API_URL.rsplit('/', 1)[0], timeout=2)
        print(f"[OK] Backend API reachable")
    except:
        print(f"[ERROR] Cannot reach {API_URL}")
        print(f"   Please start Django: cd backend && python manage.py runserver")
        return
    
    print("[*] Loading face recognition database...")
    load_known_faces()
    
    user_id, username = get_active_user_id()
    print(f"[OK] Active User: {username} (ID: {user_id})\n")
    
    current_drives = get_drives()
    current_mobiles = get_mobile_devices()
    
    print(f"[OK] Initial state: {len(current_drives)} USB drives, {len(current_mobiles)} mobile devices")
    print("\n[*] Monitoring for USB/Mobile device changes (press Ctrl+C to stop)...\n")
    
    while True:
        try:
            time.sleep(3)  # Check every 3 seconds
            
            new_drives = get_drives()
            new_mobiles = get_mobile_devices()
            
            # Check for new USB drives
            for drive_letter, info in new_drives.items():
                if drive_letter not in current_drives:
                    print(f"\n[NEW] USB DETECTED: {drive_letter} (ID: {info['serial']})")
                    print("   [+] Started Database Logging...")
                    image_path, face_status = capture_instant_photo()
                    if send_security_event("USB Inserted", f"USB Drive ({drive_letter}) - {info['model']}", info['serial'], image_path, face_status, system_info=info):
                        print("   [+] Database Save Successful. Broadcasting Event.")
                    else:
                        print("   [-] Database Insert Failed.")
            
            # Check for removed USB drives
            for drive_letter, info in current_drives.items():
                if drive_letter not in new_drives:
                    print(f"\n[REMOVED] USB REMOVED: {drive_letter}")
                    print("   [-] Updating Security Logs...")
                    send_security_event("USB Removed", f"USB Drive ({drive_letter}) - {info['model']}", info['serial'], system_info=info)
            
            # Check for new mobile devices
            for phone_name, device_id in new_mobiles.items():
                if phone_name not in current_mobiles:
                    print(f"\n[NEW] MOBILE DETECTED: {phone_name}")
                    print("   [+] Started Database Logging...")
                    image_path, face_status = capture_instant_photo()
                    if send_security_event("Mobile Connected", f"Mobile Device ({phone_name})", device_id, image_path, face_status, system_info={"model": phone_name, "type": "mobile"}):
                        print("   [+] Database Save Successful. Broadcasting Event.")
                    else:
                        print("   [-] Database Insert Failed.")
            
            # Check for removed mobile devices
            for phone_name, device_id in current_mobiles.items():
                if phone_name not in new_mobiles:
                    print(f"\n[REMOVED] MOBILE REMOVED: {phone_name}")
                    print("   [-] Updating Security Logs...")
                    send_security_event("Mobile Removed", f"Mobile Device ({phone_name})", device_id, system_info={"model": phone_name, "type": "mobile"})
            
            current_drives = new_drives
            current_mobiles = new_mobiles
            
        except KeyboardInterrupt:
            print("\n\n[*] Monitor shutdown requested")
            print("=" * 70)
            break
        except Exception as e:
            print(f"[ERROR] Error in monitor loop: {e}")
            time.sleep(5)
            print("[*] Restarting monitor loop...")

if __name__ == "__main__":
    main()
