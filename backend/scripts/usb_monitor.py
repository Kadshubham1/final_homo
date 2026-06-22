import os
import time
import ctypes
import requests
from datetime import datetime
import subprocess

try:
    import cv2
except ImportError:
    print("[-] Error: OpenCV not found. Please run 'pip install opencv-python'")
    cv2 = None

# Configuration
API_URL = "http://127.0.0.1:8000/api/security/event/"
USER_ID = 1  # Replace with actual user ID
MEDIA_SAVE_DIR = "usb_captures"

if not os.path.exists(MEDIA_SAVE_DIR):
    os.makedirs(MEDIA_SAVE_DIR)

def get_drives():
    drives = {}
    try:
        result = subprocess.run(['wmic', 'logicaldisk', 'get', 'deviceid,volumeserialnumber'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                device_id_letter = parts[0]
                serial = parts[1]
                if serial:  
                    drives[device_id_letter] = serial
    except Exception as e:
        print(f"[-] Error fetching drives: {e}")
    return drives

def get_camera():
    if cv2 is None:
        print("[-] OpenCV not available for camera capture")
        return None
    for i in range(6):
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                print(f"[+] Camera found at index {i}")
                return cap
            cap.release()
        except Exception as e:
            print(f"[-] Error checking camera index {i}: {e}")
    print("[-] No working camera found on indices 0-5.")
    return None

def capture_instant_photo():
    try:
        cap = get_camera()
        if not cap:
            print("[-] Camera unavailable, cannot capture photo")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = os.path.join(MEDIA_SAVE_DIR, f"capture_{timestamp}.jpg")
        
        # Ensure directory exists
        if not os.path.exists(MEDIA_SAVE_DIR):
            os.makedirs(MEDIA_SAVE_DIR)
        
        # Warm up camera briefly
        for _ in range(5):
            cap.read()
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            print("[-] Failed to capture frame from camera")
            return None
            
        cv2.imwrite(image_filename, frame)
        print(f"[+] Photo saved: {image_filename}")
        return image_filename
    except Exception as e:
        print(f"[-] Photo capture error: {e}")
        return None

def send_to_server(action, drive_letter, device_id, image_path=None):
    print(f"[*] Sending to server ({API_URL})...")
    
    data = {
        "action": action,
        "user_id": USER_ID,
        "device_name": f"USB Drive ({drive_letter})",
        "device_id": device_id,
        "is_authorized": "false",
        "face_status": "Unknown"
    }
    
    files = {}
    file_handle = None
    
    try:
        if image_path and os.path.exists(image_path):
            file_handle = open(image_path, "rb")
            files = {"image": file_handle}
            print(f"[+] Sending photo: {os.path.basename(image_path)}")
            
        response = requests.post(API_URL, data=data, files=files if files else None, timeout=15)
        
        if response.status_code in [200, 201]:
            print(f"[+] '{action}' logged successfully")
            return True
        else:
            try:
                error_detail = response.json()
            except:
                error_detail = response.text
            print(f"[-] Upload failed. HTTP {response.status_code}: {error_detail}")
            return False
    except requests.exceptions.ConnectionError:
        print("[-] ERROR: Could not connect to the server.")
        print(f"[-] Make sure Django backend is running at {API_URL}")
        return False
    except Exception as e:
        print(f"[-] Error sending event: {e}")
        return False
    finally:
        if file_handle:
            try:
                file_handle.close()
            except:
                pass

def main():
    print("="*50)
    print("🛡️ REAL-TIME SECURITY MONITORING ENGAGED")
    print("="*50)
    print("[*] Monitoring USB Ports...")
    current_drives = get_drives()
    
    while True:
        try:
            time.sleep(1)
            new_drives = get_drives()
            
            for drive_letter, serial in new_drives.items():
                if drive_letter not in current_drives:
                    print(f"\n[!] 🔴 ALERT: USB Detected: {drive_letter} (ID: {serial})")
                    image_path = capture_instant_photo()
                    send_to_server("USB Inserted", drive_letter, serial, image_path)
                    
            for drive_letter, serial in list(current_drives.items()):
                if drive_letter not in new_drives:
                    print(f"\n[!] ⚪ ALERT: USB Removed: {drive_letter} (ID: {serial})")
                    send_to_server("USB Removed", drive_letter, serial)
                
            current_drives = new_drives
            
        except KeyboardInterrupt:
            print("\n[*] Script stopped.")
            break
        except Exception as e:
            print(f"\n[-] Critical script error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
