import os
import time
import ctypes
import requests
from datetime import datetime
import subprocess
import threading
import json

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    print("[-] Warning: watchdog not found. File copy monitoring will be disabled. Run 'pip install watchdog'")

try:
    import wmi
    import pythoncom
    HAS_WMI = True
except ImportError:
    HAS_WMI = False
    print("[-] Warning: WMI not found. Please run 'pip install wmi'")

try:
    import cv2
except ImportError:
    print("[-] Error: OpenCV not found. Please run 'pip install opencv-python'")
    cv2 = None

try:
    import face_recognition
except ImportError:
    print("[-] Warning: face_recognition not found. Face checking will default to 'Unknown'")
    face_recognition = None

# Configuration
API_URL = "http://127.0.0.1:8000/api/security/event/"
USER_ID = 1  

# Get absolute path for media storage (use script's directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_SAVE_DIR = os.path.join(SCRIPT_DIR, "security_captures")
KNOWN_FACES_DIR = os.path.join(SCRIPT_DIR, "known_faces")

# Ensure directories exist
for directory in [MEDIA_SAVE_DIR, KNOWN_FACES_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"[+] Created directory: {directory}")

known_face_encodings = []
known_face_names = []

def load_known_faces():
    """Load authorized faces into memory"""
    if not face_recognition: return
    
    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)
        print(f"[*] Created {KNOWN_FACES_DIR}. Add images here to train face recognition.")
        return

    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            path = os.path.join(KNOWN_FACES_DIR, filename)
            try:
                img = face_recognition.load_image_file(path)
                encodings = face_recognition.face_encodings(img)
                if encodings:
                    known_face_encodings.append(encodings[0])
                    name = os.path.splitext(filename)[0]
                    known_face_names.append(name)
                    print(f"[+] Loaded known face: {name}")
            except Exception as e:
                print(f"[-] Could not load face {filename}: {e}")

def get_wmi_client():
    """Helper to initialize WMI within threads"""
    if not HAS_WMI: return None
    try:
        # CoInitialize is needed for COM in multi-threaded contexts
        pythoncom.CoInitialize()
        client = wmi.WMI()
        return client
    except Exception as e:
        print(f"[-] WMI initialization error: {e}")
        try:
            pythoncom.CoUninitialize()
        except:
            pass
        return None

def get_drives():
    """Gets logical drives using the WMI library"""
    drives = {}
    if not HAS_WMI: return drives
    
    try:
        c = get_wmi_client()
        if not c: return drives
        
        # DriveType 2 = Removable, 3 = Local Disk (fixed)
        # We focus on removable or those with a specific VolumeSerialNumber
        # Note: Some encrypted USBs might appear as Type 3
        for disk in c.Win32_LogicalDisk():
            if (disk.DriveType == 2) or (disk.DriveType == 3 and disk.VolumeSerialNumber):
                serial = getattr(disk, 'VolumeSerialNumber', None)
                if serial:
                    drives[disk.DeviceID] = serial
    except Exception as e:
        print(f"[-] WMI Drive Error: {e}")
        try:
            pythoncom.CoUninitialize()
        except:
            pass
    return drives

def get_camera():
    if cv2 is None:
        return None

    backends = []
    if os.name == 'nt':
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    else:
        backends = [cv2.CAP_V4L2, cv2.CAP_ANY]

    for backend in backends:
        for i in range(0, 8):
            try:
                cap = cv2.VideoCapture(i, backend)
            except Exception:
                continue
            if cap is None:
                continue
            if cap.isOpened():
                print(f"[*] Camera found at index {i} using backend {backend}")
                return cap
            cap.release()

    # Last resort: try default capture without specifying backend
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("[*] Camera found at default index 0")
            return cap
        cap.release()
    except Exception:
        pass

    print("[-] Error: No working camera found.")
    return None

def capture_instant_photo():
    """
    Captures a single photo instantly and tries to perform face recognition on it.
    Returns: image_filename, face_status
    """
    try:
        cap = get_camera()
        if not cap:
            print("[-] Camera not available")
            return None, "No Camera"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = os.path.join(MEDIA_SAVE_DIR, f"cap_{timestamp}.jpg")
        
        # Ensure save directory exists
        if not os.path.exists(MEDIA_SAVE_DIR):
            os.makedirs(MEDIA_SAVE_DIR)
        
        # Warm up the camera for better exposure and focus adjustment
        warmup_success = False
        for _ in range(30):
            ret, _ = cap.read()
            if ret:
                warmup_success = True
                break

        if not warmup_success:
            # Retry a few more times before failing
            retry_count = 0
            while retry_count < 10:
                ret, _ = cap.read()
                if ret:
                    warmup_success = True
                    break
                retry_count += 1

        if not warmup_success:
            print("[-] Warning: Camera warm-up failed")
            cap.release()
            return None, "Camera Error"

        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            print("[-] Error: Failed to capture frame from camera.")
            return None, "Capture Error"
        
        cv2.imwrite(image_filename, frame)
        print(f"[+] Security photo stored locally: {image_filename}")
        
        face_status = "Unknown"
        
        if face_recognition and known_face_encodings:
            try:
                rgb_frame = frame[:, :, ::-1]  # BGR to RGB
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encs = face_recognition.face_encodings(rgb_frame, face_locations)
                
                if not face_locations:
                    print("[*] No faces detected in frame")
                    face_status = "No Face Detected"
                else:
                    for face_encoding in face_encs:
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        if True in matches:
                            first_match_index = matches.index(True)
                            name = known_face_names[first_match_index]
                            face_status = f"Recognized ({name})"
                            print(f"[!] Face Recognized: {name}")
                            break
            except Exception as face_error:
                print(f"[-] Face recognition error: {face_error}")
                face_status = "Recognition Error"
        
        return image_filename, face_status
    except Exception as e:
        print(f"[-] Camera capture exception: {e}")
        return None, "Capture Failed"

def get_mobile_devices():
    """Gets connected Mobile Phones (MTP/WPD/USB Storage) using multiple WMI methods"""
    devices = {}
    if not HAS_WMI: return devices
    
    try:
        c = get_wmi_client()
        if not c: return devices
        
        # Method 1: Detect via Win32_PnPEntity (PNP = Plug and Play)
        # This catches WPD (Portable Devices) like phones
        try:
            for device in c.Win32_PnPEntity(ConfigManagerErrorCode=0):
                try:
                    pnp_class = getattr(device, 'PNPClass', '')
                    name = getattr(device, 'Name', '')
                    device_id = getattr(device, 'PNPDeviceID', '')
                    
                    # Match WPD or Portable Device
                    if pnp_class == "WPD" or "Portable Device" in name or "MTP" in name:
                        print(f"[+] Found mobile device: {name}")
                        devices[name] = device_id
                except:
                    continue
        except Exception as e:
            print(f"[*] PnPEntity method error (non-critical): {e}")
        
        # Method 2: Detect via Win32_USBDevice with description containing phone/mobile
        # This catches MTP devices that might not be classified as WPD
        try:
            for device in c.Win32_USBDevice():
                try:
                    name = getattr(device, 'Name', '')
                    device_id = getattr(device, 'PNPDeviceID', '')
                    description = getattr(device, 'Description', '')
                    
                    # Look for keywords indicating a mobile device
                    keywords = ['phone', 'mtp', 'android', 'iphone', 'samsung', 'mobile', 'portable']
                    if any(keyword in name.lower() + description.lower() for keyword in keywords):
                        print(f"[+] Found mobile USB device: {name} ({description})")
                        devices[name] = device_id
                except:
                    continue
        except Exception as e:
            print(f"[*] USBDevice method error (non-critical): {e}")
        
        # Method 3: Also catch standard USB removable storage that could be phones
        try:
            for device in c.Win32_USBStorageDevice():
                try:
                    name = getattr(device, 'Name', '')
                    device_id = getattr(device, 'PNPDeviceID', '')
                    description = getattr(device, 'Description', '')
                    
                    # Only add if it looks like a mobile device
                    if any(keyword in name.lower() + description.lower() for keyword in ['phone', 'mtp', 'android', 'mobile']):
                        print(f"[+] Found mobile storage: {name}")
                        devices[name] = device_id
                except:
                    continue
        except Exception as e:
            print(f"[*] USBStorageDevice method error (non-critical): {e}")
        
        if devices:
            print(f"[*] Total mobile devices detected: {len(devices)}")
        else:
            print("[*] No mobile devices detected")
            
    except Exception as e:
        print(f"[-] Mobile device detection error: {e}")
        try:
            pythoncom.CoUninitialize()
        except:
            pass
    return devices

# Dynamically resolve active user from the web app
def get_active_user_id():
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.active_user.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('id', 1), data.get('username', 'Unknown')
    except Exception as e:
        print(f"[*] Error reading active user config: {e}")
    return 1, "Default Admin"

def send_security_event(action, device_name, device_id, image_path=None, face_status="N/A"):
    """Send security event to the backend API"""
    # REQUISITE: Use the actual logged-in user for the audit trail
    user_id, username = get_active_user_id()
    
    print(f"[*] Sending Event for User: {username} (ID: {user_id})")
    print(f"[*] Posting to {API_URL}...")
    
    data = {
        "user_id": user_id,
        "action": action,
        "device_name": device_name,
        "device_id": device_id,
        "face_status": face_status
    }
    files = {}
    img_handle = None
    
    try:
        if image_path and os.path.exists(image_path):
            img_handle = open(image_path, "rb")
            files["image"] = img_handle
            print(f"[+] Sending photo with event: {os.path.basename(image_path)}")
            
        print(f"[*] Posting data: action={action}, device={device_name}, face_status={face_status}")
        response = requests.post(API_URL, data=data, files=files if files else None, timeout=15)
        
        if response.status_code in [200, 201]:
            print(f"[+] Event '{action}' logged successfully on server.")
            return True
        else:
            try:
                error_text = response.json()
            except:
                error_text = response.text
            print(f"[-] Upload failed. HTTP {response.status_code}: {error_text}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"[-] ERROR: Cannot connect to API at {API_URL}")
        print(f"[-] Make sure Django backend is running on port 8000")
        return False
    except Exception as e:
        print(f"[-] Unexpected error uploading event: {e}")
        return False
    finally:
        if img_handle:
            try:
                img_handle.close()
            except:
                pass

class USBCopyHandler(FileSystemEventHandler):
    def __init__(self, drive_letter, device_id):
        self.drive_letter = drive_letter
        self.device_id = device_id
        
    def on_created(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            # Filter somewhat to avoid spam
            if not filename.startswith('~') and not filename.startswith('.'):
                msg = f"File Copied: {filename}"
                print(f"[!] {self.drive_letter} -> {msg}")
                # We do not send image for file changes to keep it lightweight
                send_security_event(msg, f"USB Drive ({self.drive_letter})", self.device_id)

    def on_modified(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            if not filename.startswith('~') and not filename.startswith('.'):
                msg = f"File Modified: {filename}"
                print(f"[!] {self.drive_letter} -> {msg}")
                # Optional: Uncomment if you want modified events too
                # send_security_event(msg, self.drive_letter, self.device_id)

active_observers = {}

def start_watching(drive_letter, device_id):
    if not HAS_WATCHDOG: return
    try:
        # drive_letter looks like "E:"
        path = drive_letter + "\\\\"
        if not os.path.exists(path):
            return
            
        event_handler = USBCopyHandler(drive_letter, device_id)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        active_observers[drive_letter] = observer
        print(f"[*] Started monitoring files on {drive_letter}")
    except Exception as e:
        print(f"[-] Could not start watching {drive_letter}: {e}")

def stop_watching(drive_letter):
    if drive_letter in active_observers:
        print(f"[*] Stopping monitoring on {drive_letter}")
        observer = active_observers[drive_letter]
        observer.stop()
        observer.join()
        del active_observers[drive_letter]

def main():
    print("="*50)
    print("🛡️ REAL-TIME SECURITY MONITORING ENGAGED")
    print("   - Using Instant Photo Capture")
    print("   - File Copy Tracking Active" if HAS_WATCHDOG else "   - File Copy Tracking Unavailable")
    print("="*50)
    
    load_known_faces()
    
    print("[*] Monitoring USB Ports & Mobile Phones...")
    print("[*] Starting main monitoring loop (polling every 2 seconds)...")
    current_drives = get_drives()
    current_mobiles = get_mobile_devices()
    
    print(f"[*] Initial state: {len(current_drives)} USB drives, {len(current_mobiles)} mobile devices")
    
    while True:
        try:
            time.sleep(2)
            new_drives = get_drives()
            new_mobiles = get_mobile_devices()
            
            # 1. Check for Mobile Phones Inserted
            for phone_name, device_id in new_mobiles.items():
                if phone_name not in current_mobiles:
                    print(f"\n[!] 📱 ALERT: Mobile Phone Detected: {phone_name}")
                    print(f"[*] Device ID: {device_id}")
                    image_path, face_status = capture_instant_photo()
                    if image_path:
                        print(f"[+] Photo captured: {image_path}")
                    else:
                        print(f"[!] Warning: No photo captured (camera may not be available)")
                    
                    success = send_security_event(
                        action="Mobile Connected",
                        device_name=f"Mobile Device ({phone_name})",
                        device_id=device_id,
                        image_path=image_path,
                        face_status=face_status
                    )
                    print(f"[{'✓' if success else '✗'}] Event {'sent' if success else 'failed'} to server")
            
            # 2. Check for Mobile Phones Removed
            for phone_name, device_id in list(current_mobiles.items()):
                if phone_name not in new_mobiles:
                    print(f"\n[!] ⚪ ALERT: Mobile Phone Removed: {phone_name}")
                    success = send_security_event(
                        action="Mobile Removed",
                        device_name=f"Mobile Device ({phone_name})",
                        device_id=device_id
                    )
                    print(f"[{'✓' if success else '✗'}] Event {'sent' if success else 'failed'} to server")
            
            current_mobiles = new_mobiles
            
            # 3. Check for newly inserted standard drives
            for drive_letter, serial in new_drives.items():
                if drive_letter not in current_drives:
                    print(f"\n[!] 🔴 ALERT: USB Detected: {drive_letter} (ID: {serial})")
                        
                    # Instantly take photo
                    image_path, face_status = capture_instant_photo()
                    if image_path:
                        print(f"[+] Photo captured: {image_path}")
                    else:
                        print(f"[!] Warning: No photo captured (camera may not be available)")
                    
                    success = send_security_event(
                        action="USB Inserted",
                        device_name=f"USB Drive ({drive_letter})", 
                        device_id=serial,
                        image_path=image_path,
                        face_status=face_status
                    )
                    print(f"[{'✓' if success else '✗'}] Event {'sent' if success else 'failed'} to server")
                    
                    # Start monitoring the drive using watchdog
                    start_watching(drive_letter, serial)
                    
            # 4. Check for removed drives
            for drive_letter, serial in list(current_drives.items()):
                if drive_letter not in new_drives:
                    print(f"\n[!] ⚪ ALERT: USB Removed: {drive_letter} (ID: {serial})")
                    stop_watching(drive_letter)
                    
                    success = send_security_event(
                        action="USB Removed",
                        device_name=f"USB Drive ({drive_letter})",
                        device_id=serial
                    )
                    print(f"[{'✓' if success else '✗'}] Event {'sent' if success else 'failed'} to server")
                    
            current_drives = new_drives
            
        except KeyboardInterrupt:
            print("\n[*] Shutting down security monitor.")
            for drv in list(active_observers.keys()):
                stop_watching(drv)
            break
        except Exception as e:
            print(f"\n[-] Unexpected Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
