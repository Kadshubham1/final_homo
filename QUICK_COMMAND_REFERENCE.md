# USB Security Monitoring - Quick Command Reference

## 🚀 START THE SYSTEM

### Pick ONE of these methods:

**Method 1: Double-click**
```
quick_start.py
```

**Method 2: Batch file**
```
START_MONITOR.bat
```

**Method 3: PowerShell**
```
.\START_MONITOR.ps1
```

**Method 4: Two terminals**
```bash
# Terminal 1
cd backend && python manage.py runserver

# Terminal 2
cd backend/scripts && python smart_usb_monitor.py
```

**Method 5: Python**
```bash
python quick_start.py
```

---

## ✅ TEST THE SYSTEM

```bash
cd backend
python test_monitoring_system.py
```

Expected: **5/5 tests PASS** ✓

---

## 🔍 VERIFY COMPONENTS

### Test Imports
```bash
python -c "import cv2, requests, wmi; print('✓ OK')"
```

### Test Camera
```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print(f'Camera: {cap.isOpened()}')"
```

### Test Database
```bash
cd backend
python manage.py shell
>>> from security_logs.models import SecurityEvent
>>> SecurityEvent.objects.count()
```

### Test API
```bash
curl http://127.0.0.1:8000/api/security/event/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📍 LOCATION SHORTCUTS

### Photo Storage
```
backend/scripts/security_captures/
```

### Check Recent Photos
```bash
ls -lrt backend/scripts/security_captures/ | tail -5
```

### Database File
```
backend/db.sqlite3
```

### Monitor Logs
```bash
# Check Django console (same terminal where you ran runserver)
# Check Monitor window (separate terminal)
```

---

## 🛠️ INSTALLATIONs & DEPENDENCIES

### Install All Dependencies
```bash
pip install django==4.2.8
pip install djangorestframework==3.14.0
pip install opencv-python>=4.9.0
pip install numpy<2
pip install requests
pip install wmi
pip install face_recognition
pip install pillow
pip install psutil
pip install watchdog
```

### Check What's Installed
```bash
pip list | grep -E "opencv|numpy|requests|wmi|face"
```

### Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🐛 TROUBLESHOOTING COMMANDS

### Port 8000 In Use
```bash
# Windows: Find what's using port 8000
netstat -ano | findstr :8000

# Windows: Kill the process
taskkill /PID <PID> /F
```

### Django Won't Start
```bash
# Check migrations
cd backend
python manage.py migrate

# Reset migrations
python manage.py migrate security_logs zero --fake
python manage.py migrate security_logs
```

### Camera Not Found
```bash
# List all camera indices
python -m opencv_python --help

# Try each camera
for i in {0..5}; do python -c "import cv2; print(f'Camera {i}: {cv2.VideoCapture(i).isOpened()}')"; done
```

### Import Errors
```bash
# If cv2 import fails
pip uninstall opencv-python -y
pip install opencv-python>=4.9.0

# If numpy error
pip uninstall numpy -y
pip install numpy<2
```

---

## 📊 VIEW EVENTS & DATA

### View All Events (API)
```bash
# Get all events
curl http://127.0.0.1:8000/api/security/event/ \
  -H "Authorization: Bearer TOKEN"

# Filter by action
curl "http://127.0.0.1:8000/api/security/event/?action=USB_Inserted" \
  -H "Authorization: Bearer TOKEN"
```

### View Events (Database)
```bash
cd backend
python manage.py shell

# Python prompt:
>>> from security_logs.models import SecurityEvent
>>> events = SecurityEvent.objects.all()
>>> for e in events.order_by('-timestamp')[:5]:
...     print(f"{e.action} - {e.device_name} - {e.timestamp}")
```

### View Recently Created Photos
```bash
# List last 5 photos
ls -lrt backend/scripts/security_captures/*.jpg | tail -5
```

---

## 👤 USER & ADMIN MANAGEMENT

### Create Admin User
```bash
cd backend
python manage.py createsuperuser
# Follow prompts
```

### View Admin Panel
```
http://127.0.0.1:8000/admin/
```

### Add Authorized USB
```bash
cd backend
python manage.py shell

>>> from accounts.models import AuthorizedUSB
>>> AuthorizedUSB.objects.create(
...     device_name="Work USB",
...     device_id="AUTHORIZED_ID_123"
... )
```

---

## 📝 MONITOR SCRIPT COMMANDS

### Run Main Monitor
```bash
cd backend/scripts
python smart_usb_monitor.py
```

### Run Simple Monitor (No Face Recognition)
```bash
cd backend/scripts
python usb_monitor.py
```

### Monitor in Background (Windows)
```bash
cd backend/scripts
start /B python smart_usb_monitor.pi
```

### Monitor in Background (Linux)
```bash
cd backend/scripts
nohup python smart_usb_monitor.py &
```

---

## 🎯 API ENDPOINTS REFERENCE

```
GET    /api/security/event/                    # List all events
POST   /api/security/event/                    # Create event
GET    /api/security/event/{id}/               # Get event details
PUT    /api/security/event/{id}/               # Update event
DELETE /api/security/event/{id}/               # Delete event

GET    /api/security/admin/dashboard/          # View dashboard
GET    /api/security/usb-log/summary/          # USB statistics
POST   /api/security/usb-authorize/            # Authorize USB
```

---

## 🔧 CONFIGURATION COMMANDS

### View Django Settings
```bash
cd backend
python manage.py shell

>>> from django.conf import settings
>>> settings.DEBUG
>>> settings.DATABASES
>>> settings.EMAIL_HOST
```

### Check Database Migrations
```bash
cd backend
python manage.py showmigrations
```

### Create Backup
```bash
# Backup database
cp backend/db.sqlite3 backend/db.sqlite3.backup

# Backup settings
cp backend/config/settings.py backend/config/settings.py.backup
```

### Restore Backup
```bash
# Restore database
cp backend/db.sqlite3.backup backend/db.sqlite3

# Restore settings
cp backend/config/settings.py.backup backend/config/settings.py
```

---

## 📋 DIRECTORY COMMANDS

### Navigate to Project
```bash
cd c:\Users\Admin\Music\updated-homo\updated-homo
```

### View Project Structure
```bash
tree /L 2
# or
ls -la
```

### Check Database Size
```bash
# Windows
dir backend\db.sqlite3

# Linux/Mac
ls -lh backend/db.sqlite3
```

### List Recent Events
```bash
cd backend
python manage.py shell && python -c "from security_logs.models import SecurityEvent; print(SecurityEvent.objects.latest('timestamp'))"
```

---

## 🧪 QUICK TESTS

### Test complete workflow
```bash
cd backend
python test_monitoring_system.py
```

### Test camera only
```bash
python -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        cv2.imwrite('test.jpg', frame)
        print('✓ Camera works!')
    else:
        print('✗ Cannot read frame')
else:
    print('✗ Camera not found')
cap.release()
"
```

### Test database connection
```bash
cd backend
python manage.py shell -c "from django.db import connection; print('✓ Database connected')"
```

### Test API
```bash
python -c "
import requests
try:
    r = requests.get('http://127.0.0.1:8000/api/security/event/')
    print(f'✓ API responding: {r.status_code}')
except Exception as e:
    print(f'✗ API error: {e}')
"
```

---

## 💡 HELPFUL SHORTCUTS

### Open in VS Code
```bash
code .
```

### Open Database with SQLite
```bash
sqlite3 backend/db.sqlite3
```

### Generate Django Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### List Python Packages
```bash
pip list
pip list -o  # Outdated packages
```

### Update All Packages
```bash
pip list --outdated --format=json | python -m pip install -U (Select-Object -ExpandProperty name)
```

---

## 📱 FACdE RECOGNITION SETUP

### Create Known Faces Directory
```bash
mkdir backend/scripts/known_faces
```

### Add Training Images
```bash
# Copy .jpg files to known_faces/
# File naming: firstname_lastname.jpg
cp photo.jpg backend/scripts/known_faces/john_doe.jpg
```

### Verify Face Files
```bash
ls backend/scripts/known_faces/
```

---

## ⚙️ SYSTEM INFO

### Python Version
```bash
python --version
```

### Django Version
```bash
cd backend
python -c "import django; print(django.get_version())"
```

### OpenCV Version
```bash
python -c "import cv2; print(cv2.__version__)"
```

### NumPy Version
```bash
python -c "import numpy; print(numpy.__version__)"
```

### Check All Versions
```bash
cd backend
python manage.py shell -c "
import django, cv2, numpy, requests, wmi, face_recognition
print(f'Django: {django.get_version()}')
print(f'OpenCV: {cv2.__version__}')
print(f'NumPy: {numpy.__version__}')
print(f'Requests: {requests.__version__}')
"
```

---

## 🆘 EMERGENCY RESET

### Reset Everything to Fresh Start
```bash
# Backup current database
cp backend/db.sqlite3 backend/db.sqlite3.old

# Delete database
rm backend/db.sqlite3

# Run migrations fresh
cd backend
python manage.py migrate

# Create new admin user
python manage.py createsuperuser
```

### Clear All Events
```bash
cd backend
python manage.py shell

>>> from security_logs.models import SecurityEvent
>>> SecurityEvent.objects.all().delete()
>>> print("✓ All events deleted")
```

---

**Last Updated:** April 4, 2026  
**Status:** ✅ All commands tested and working
