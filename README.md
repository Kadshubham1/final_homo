# 🔐 Homomorphic Secure File Sharing System

An advanced college-level secure file sharing platform with Django backend, React frontend, and USB detection security monitoring.

## 📋 Project Overview

A complete file sharing system with:
- JWT-based authentication (User & Admin roles)
- Encrypted file uploads
- Secure file sharing with OTP verification
- USB connection detection with webcam capture
- Comprehensive admin panel
- Modern responsive UI with Tailwind CSS

## 🏗️ Project Structure

```
homomorphic-secure-file-sharing/
├── backend/                      # Django REST API
│   ├── accounts/                # User authentication & profiles
│   ├── files/                   # File upload & management
│   ├── sharing/                 # File sharing logic
│   ├── security_logs/           # USB activity & security logs
│   ├── config/                  # Django settings
│   ├── manage.py
│   ├── requirements.txt
│   └── db.sqlite3
│
├── frontend/                     # React + Vite app
│   ├── src/
│   │   ├── components/          # Reusable React components
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom hooks
│   │   ├── services/            # API integration
│   │   ├── context/             # React context
│   │   ├── styles/              # Global styles
│   │   └── App.jsx
│   ├── vite.config.js
│   ├── package.json
│   └── tailwind.config.js
│
├── scripts/                      # Python utilities
│   ├── usb_monitor.py           # USB detection service
│   ├── camera_capture.py        # Webcam capture
│   └── requirements.txt
│
└── README.md

```

## 🔑 Key Features

### 1. Authentication System
- User Registration & Login with JWT
- Admin panel access
- Role-based access control

### 2. File Management
- Upload files with Public/Private scope
- Simulated homomorphic encryption
- Download encrypted files

### 3. File Sharing
- Share files with specific users
- OTP-based verification (5-min expiry)
- Activity tracking

### 4. Security Monitoring
- USB connection detection
- Automatic webcam capture on USB insert
- Security logs with images and timestamps
- Admin access to all logs

### 5. Admin Panel
- User management
- File monitoring
- USB security logs
- Analytics dashboard

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Create admin
python manage.py runserver
```

**Admin Credentials:**
- Email: admin@central.com
- Password: admin123

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### USB Monitoring (Background Service)

```bash
cd scripts
pip install -r requirements.txt
python usb_monitor.py
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/refresh/` - Refresh JWT

### Files
- `POST /api/files/upload/` - Upload file
- `GET /api/files/` - List user's files
- `GET /api/files/{id}/download/` - Download file
- `DELETE /api/files/{id}/` - Delete file

### Sharing
- `POST /api/sharing/share/` - Share file with user
- `POST /api/sharing/verify-otp/` - Verify OTP

### Security
- `POST /api/security/log-usb-event/` - Log USB activity
- `GET /api/security/logs/` - Get USB activity logs

### Admin
- `GET /api/admin/users/` - List all users
- `GET /api/admin/files/` - List all files
- `GET /api/admin/logs/` - List all security logs
- `GET /api/admin/stats/` - Dashboard statistics

## 🛠️ Technology Stack

**Backend:**
- Django 4.2+
- Django REST Framework
- Django Corsheaders
- PyJWT
- Pillow (Image processing)
- OpenCV (Camera)
- psutil (System monitoring)

**Frontend:**
- React 18+
- Vite
- Tailwind CSS
- Axios
- React Router
- zustand (State management)

**Database:**
- SQLite (default)

**Security:**
- JWT Authentication
- Password hashing (bcrypt)
- CORS protection
- File encryption (AES simulation)

## 📱 Default Login Credentials

### Admin
- Email: `admin@central.com`
- Password: `admin123`

### Test User
- Email: `user@test.com`
- Password: `Test@123`

## 🔒 Security Features

✅ JWT-based authentication
✅ Password encryption
✅ File encryption (simulated homomorphic)
✅ USB detection monitoring
✅ Webcam capture on USB insert
✅ OTP verification for file sharing
✅ Role-based access control
✅ CORS protection

## 📝 Database Models

### User
- id, name, email, mobile, password, role, is_active, created_at

### File
- id, user, filename, file (encrypted), mimetype, scope, created_at

### Share
- id, file, sender, receiver, otp, is_verified, otp_expires_at, created_at

### USBActivityLog
- id, user, image, timestamp, device_name, system_info

## 🎨 UI Features

- Gradient header (Orange → Pink)
- Responsive sidebar navigation
- Clean card-based layout
- Toast notifications
- Loading spinners
- Modal dialogs
- Data tables with sorting/filtering
- File preview capabilities
- Image compression

## 👨‍💻 Developer Notes

- All code is well-commented for learning
- Follows Django & React best practices
- Production-like folder structure
- Easy to extend and modify
- Suitable for final year project demonstration

## 📞 Support

For issues or questions, refer to the code comments and API documentation in each app's `urls.py` file.

---

**Built for College Final Year Project** 🎓
**Last Updated:** March 2026
