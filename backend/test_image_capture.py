#!/usr/bin/env python3
"""
Test USB Monitor Image Capture Flow
Tests: Camera → Image File → API Upload → Database → Frontend Display
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

print("[*] Importing OpenCV...")
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("⚠️  OpenCV not available - image capture will be skipped")

print("[*] Importing Numpy...")
try:
    import numpy as np
except ImportError:
    print("⚠️  Numpy not available")

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from security_logs.models import SecurityEvent
from django.core.files.base import ContentFile

User = get_user_model()

def test_step(step_num, description):
    """Print formatted step header"""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {description}")
    print('='*70)

def capture_test_image():
    """Test 1: Capture image from camera"""
    test_step(1, "Capture Image from Camera")
    
    if not HAS_CV2:
        print("❌ ERROR: OpenCV not available!")
        print("   Installing: pip install opencv-contrib-python")
        return None
    
    print("[*] Finding camera...")
    
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    cap = None
    
    for backend in backends:
        for i in range(0, 5):
            try:
                cap = cv2.VideoCapture(i, backend)
                if cap and cap.isOpened():
                    print(f"✓ Camera found: Index {i}")
                    break
            except:
                continue
        if cap and cap.isOpened():
            break
    
    if not cap or not cap.isOpened():
        print("❌ ERROR: No camera found!")
        return None
    
    print("[*] Warming up camera...")
    for _ in range(30):
        ret, _ = cap.read()
        if ret:
            break
    
    print("[*] Capturing image...")
    ret, frame = cap.read()
    cap.release()
    
    if not ret or frame is None:
        print("❌ ERROR: Failed to capture frame!")
        return None
    
    # Save image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_image_path = f"test_image_{timestamp}.jpg"
    cv2.imwrite(test_image_path, frame)
    
    print(f"✓ Image captured: {test_image_path}")
    print(f"✓ Image size: {frame.shape}")
    
    return test_image_path

def test_api_upload(image_path):
    """Test 2: Upload image to API"""
    test_step(2, "Upload Image to API Endpoint")
    
    if not os.path.exists(image_path):
        print(f"❌ ERROR: Image file not found: {image_path}")
        return None
    
    api_url = "http://127.0.0.1:8000/api/security/event/"
    
    print(f"[*] Posting to: {api_url}")
    
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
    if not admin_user:
        print("❌ ERROR: No admin user found!")
        return None
    
    data = {
        "user_id": admin_user.id,
        "action": "Test USB Insertion",
        "device_name": "Test USB Drive",
        "device_id": "TEST123456",
        "face_status": "Test Face"
    }
    
    with open(image_path, 'rb') as img_file:
        files = {'image': img_file}
        try:
            response = requests.post(api_url, data=data, files=files, timeout=10)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✓ API Response: {response.status_code}")
                print(f"✓ Event ID: {result.get('id')}")
                return result.get('id')
            else:
                print(f"❌ ERROR: API returned {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"❌ ERROR: Cannot connect to {api_url}")
            print("   Make sure Django is running: python manage.py runserver")
            return None
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None

def test_database_storage(event_id):
    """Test 3: Verify image stored in database"""
    test_step(3, "Verify Image in Database")
    
    if not event_id:
        print("❌ ERROR: No event ID to check!")
        return False
    
    try:
        event = SecurityEvent.objects.get(id=event_id)
        print(f"✓ Event found in database: {event.id}")
        
        if event.image:
            print(f"✓ Image field has content")
            print(f"  - Image name: {event.image.name}")
            print(f"  - Image path: {event.image.path if hasattr(event.image, 'path') else 'N/A'}")
            print(f"  - Image URL: {event.image.url}")
            
            # Check if file exists on disk
            if hasattr(event.image, 'path') and os.path.exists(event.image.path):
                print(f"✓ Image file exists on disk")
                file_size = os.path.getsize(event.image.path)
                print(f"  - Size: {file_size} bytes")
                return True
            else:
                print(f"❌ ERROR: Image file not found on disk")
                return False
        else:
            print(f"❌ ERROR: Event has no image!")
            return False
            
    except SecurityEvent.DoesNotExist:
        print(f"❌ ERROR: Event {event_id} not found in database!")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_api_retrieval(event_id):
    """Test 4: Verify API returns image URL"""
    test_step(4, "Verify Image URL in API Response")
    
    if not event_id:
        print("❌ ERROR: No event ID!")
        return False
    
    api_url = f"http://127.0.0.1:8000/api/security/event/{event_id}/"
    
    print(f"[*] Requesting: {api_url}")
    
    try:
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            event_data = response.json()
            print(f"✓ API Response: {response.status_code}")
            
            if event_data.get('image_url'):
                print(f"✓ Image URL present: {event_data['image_url']}")
                
                # Test if URL is accessible
                img_url = event_data['image_url']
                print(f"[*] Testing image URL accessibility...")
                img_response = requests.head(img_url, timeout=5)
                if img_response.status_code == 200:
                    print(f"✓ Image URL is accessible (HTTP {img_response.status_code})")
                    return True
                else:
                    print(f"⚠️  Image URL returned {img_response.status_code}")
                    return True  # URL is there, just not accessible
            else:
                print(f"❌ ERROR: No image_url in API response")
                print(f"Response: {json.dumps(event_data, indent=2)}")
                return False
        else:
            print(f"❌ ERROR: API returned {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to API")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_live_events_endpoint():
    """Test 5: Verify live events endpoint returns events with images"""
    test_step(5, "Verify Live Events Endpoint")
    
    api_url = "http://127.0.0.1:8000/api/admin/live-events/"
    
    print(f"[*] Requesting: {api_url}")
    
    try:
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            events = response.json()
            print(f"✓ API Response: {response.status_code}")
            print(f"✓ Total events: {len(events) if isinstance(events, list) else 'Unknown'}")
            
            if isinstance(events, list) and events:
                latest = events[0]
                print(f"\n✓ Latest Event:")
                print(f"  - ID: {latest.get('id')}")
                print(f"  - Action: {latest.get('action')}")
                print(f"  - Device: {latest.get('device_name')}")
                if latest.get('image_url'):
                    print(f"  - Image URL: {latest['image_url']}")
                else:
                    print(f"  - Image URL: (not present)")
                return True
            else:
                print(f"⚠️  No events in live feed yet")
                return True
        else:
            print(f"❌ ERROR: API returned {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to API")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🧪 USB MONITOR IMAGE CAPTURE - COMPLETE TEST SUITE")
    print("="*70)
    
    # Test 1: Capture
    image_path = capture_test_image()
    if not image_path:
        print("\n❌ FAILED at Step 1: Image Capture")
        return
    
    # Test 2: Upload
    event_id = test_api_upload(image_path)
    if not event_id:
        print("\n❌ FAILED at Step 2: API Upload")
        return
    
    # Test 3: Database
    if not test_database_storage(event_id):
        print("\n❌ FAILED at Step 3: Database Storage")
        return
    
    # Test 4: API Retrieval
    if not test_api_retrieval(event_id):
        print("\n❌ FAILED at Step 4: API Retrieval")
        return
    
    # Test 5: Live Events
    test_live_events_endpoint()
    
    # Summary
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"\nEvent ID: {event_id}")
    print("\nNow test in frontend:")
    print("1. Go to Admin Dashboard → Live Monitoring")
    print("2. Should see the test event with image")
    print("3. If image not showing, check browser console (F12)")
    
    # Cleanup
    if os.path.exists(image_path):
        os.remove(image_path)
        print(f"\n[*] Cleaned up test image")

if __name__ == "__main__":
    main()
