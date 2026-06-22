#!/usr/bin/env python
"""
Complete Test Suite for USB Security Monitoring System
Tests:
1. Database connectivity
2. API endpoints
3. Camera access
4. Event logging
5. Image capture and storage
"""

import os
import sys
import django

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import cv2
import requests
import json
from datetime import datetime
from security_logs.models import SecurityEvent, AuthorizedUSB
from accounts.models import User

def test_database():
    """Test database connectivity"""
    print("\n" + "="*60)
    print("TEST 1: Database Connectivity")
    print("="*60)
    
    try:
        user_count = User.objects.count()
        event_count = SecurityEvent.objects.count()
        print(f"[+] Database connected successfully")
        print(f"    - Users in DB: {user_count}")
        print(f"    - Security events: {event_count}")
        
        if user_count == 0:
            print("[-] WARNING: No users found in database!")
        
        return True
    except Exception as e:
        print(f"[-] Database error: {e}")
        return False

def test_camera():
    """Test camera access"""
    print("\n" + "="*60)
    print("TEST 2: Camera Access")
    print("="*60)
    
    try:
        for i in range(6):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                print(f"[+] Camera found at index {i}")
                
                # Warm up
                for _ in range(5):
                    cap.read()
                
                ret, frame = cap.read()
                cap.release()
                
                if ret and frame is not None:
                    print(f"[+] Successfully captured frame from camera {i}")
                    
                    # Save test image
                    os.makedirs('security_captures', exist_ok=True)
                    test_image = f'security_captures/test_frame_{i}.jpg'
                    cv2.imwrite(test_image, frame)
                    print(f"[+] Test image saved: {test_image}")
                    return True
                else:
                    print(f"[-] Failed to read frame from camera {i}")
            cap.release()
        
        print("[-] No working camera found")
        return False
        
    except Exception as e:
        print(f"[-] Camera error: {e}")
        return False

def test_api_connectivity():
    """Test API endpoint connectivity"""
    print("\n" + "="*60)
    print("TEST 3: API Connectivity")
    print("="*60)
    
    api_url = "http://127.0.0.1:8000/api/security/event/"
    
    try:
        response = requests.get(api_url, timeout=5)
        print(f"[+] API is accessible at {api_url}")
        print(f"    - Status code: {response.status_code}")
        
        if response.status_code == 200:
            events = response.json()
            print(f"    - Events in API: {events.get('count', len(events.get('results', [])))}")
            return True
        elif response.status_code == 401:
            print(f"[*] API requires authentication (expected for GET)")
            return True
        else:
            print(f"[-] Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[-] ERROR: Cannot connect to API at {api_url}")
        print(f"    Make sure Django backend is running:")
        print(f"    cd backend && python manage.py runserver")
        return False
    except Exception as e:
        print(f"[-] API error: {e}")
        return False

def test_event_creation():
    """Test creating a security event"""
    print("\n" + "="*60)
    print("TEST 4: Event Creation")
    print("="*60)
    
    try:
        # Get or create admin user
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            print("[-] No admin user found!")
            return False
        
        print(f"[+] Using admin user: {admin.username}")
        
        # Create test event
        event = SecurityEvent.objects.create(
            user=admin,
            action="Test USB Connection",
            device_name="Test USB Device",
            device_id="TEST_123456",
            is_authorized=False,
            face_status="Test"
        )
        
        print(f"[+] Security event created successfully")
        print(f"    - Event ID: {event.id}")
        print(f"    - Device: {event.device_name}")
        print(f"    - Timestamp: {event.timestamp}")
        
        return True
        
    except Exception as e:
        print(f"[-] Event creation error: {e}")
        return False

def test_api_post():
    """Test posting data to API"""
    print("\n" + "="*60)
    print("TEST 5: API POST (Event Logging)")
    print("="*60)
    
    api_url = "http://127.0.0.1:8000/api/security/event/"
    
    # Prepare test data
    data = {
        "action": "USB Inserted (TEST)",
        "device_name": "Test USB Drive (E:)",
        "device_id": "TEST_DEVICE_001",
        "user_id": 1,
        "face_status": "Test Face"
    }
    
    try:
        # First try with test image
        os.makedirs('security_captures', exist_ok=True)
        test_image_path = 'security_captures/test_frame_0.jpg'
        
        if os.path.exists(test_image_path):
            with open(test_image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(api_url, data=data, files=files, timeout=15)
        else:
            response = requests.post(api_url, data=data, timeout=15)
        
        print(f"[+] API POST request sent")
        print(f"    - URL: {api_url}")
        print(f"    - Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"[+] Event logged successfully!")
            print(f"    - Response: {result}")
            return True
        else:
            print(f"[-] POST failed with status {response.status_code}")
            print(f"    - Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[-] ERROR: Cannot connect to API")
        print(f"    Make sure Django is running on port 8000")
        return False
    except Exception as e:
        print(f"[-] API POST error: {e}")
        return False

def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║  USB SECURITY MONITORING - COMPLETE TEST SUITE           ║")
    print("║  Testing all components of the monitoring system         ║")
    print("╚" + "="*58 + "╝")
    
    results = {
        "Database": test_database(),
        "Camera": test_camera(),
        "API_Connectivity": test_api_connectivity(),
        "Event_Creation": test_event_creation(),
        "API_POST": test_api_post(),
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! System is ready to monitor USB devices.")
        print("\nNext steps:")
        print("1. Start the monitor: python backend/scripts/smart_usb_monitor.py")
        print("2. Insert a USB device")
        print("3. Check the API: http://127.0.0.1:8000/api/security/event/")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
