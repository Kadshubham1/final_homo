# OTP Signup System - Quick Start Guide

## 🚀 Feature Overview

This system implements a complete email-based OTP (One-Time Password) verification for user signup. Users create an account, receive a 6-digit OTP code via email, and verify their email to activate their account.

---

## 🎯 How to Use

### For Users (Frontend)

#### 1. **Sign Up with Email**
```
1. Visit http://localhost:5173/signup
2. Enter email, password, and name
3. Click "Create Account"
4. Check your email for OTP code
```

#### 2. **Verify Email with OTP**
```
1. Automatically redirected to /verify-otp
2. Enter the 6-digit OTP from email
3. Auto-submits when all 6 digits entered
4. Success → Redirected to dashboard
```

#### 3. **Resend OTP (if needed)**
```
1. Click "Resend OTP" button on verification page
2. New OTP sent to email (30 second cooldown)
3. Enter new OTP
4. Verify
```

---

## 🔧 Technical Architecture

### Backend Flow

```
User Signup Request
    ↓
[1] Create User (is_verified=false)
[2] Generate 6-digit OTP
[3] Store OTP with 5-min expiry
[4] Send OTP Email
[5] Return user data
    ↓
User Verification Request
    ↓
[1] Validate OTP (exists, not expired, not used)
[2] Mark user as_verified=true
[3] Generate JWT tokens
[4] Send success email
[5] Return tokens
```

### Frontend Flow

```
Load Signup Page
    ↓
User enters details & clicks submit
    ↓
Validate form locally
    ↓
Call /api/auth/signup-otp/
    ↓
Store email in localStorage
    ↓
Redirect to /verify-otp
    ↓
Load OTP input
    ↓
User enters OTP
    ↓
Auto-submit when 6 digits
    ↓
Call /api/auth/verify-otp/
    ↓
Store tokens in localStorage
    ↓
Redirect to /dashboard
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup-otp/` | Create account & send OTP |
| POST | `/api/auth/verify-otp/` | Verify OTP & activate |
| POST | `/api/auth/resend-otp/` | Resend OTP (rate limited) |

---

## 📁 File Structure

```
backend/
├── accounts/
│   ├── models.py          # OTP model added
│   ├── views.py           # SignupWithOTPView, VerifyOTPView, ResendOTPView
│   ├── serializers.py     # OTP serializers
│   ├── utils.py           # Email & OTP utility functions
│   └── urls.py            # New OTP routes
└── config/
    └── settings.py        # Email configuration

frontend/
├── src/
│   ├── pages/
│   │   ├── SignupPage.jsx         # Signup form component
│   │   ├── SignupPage.css         # Signup styles
│   │   ├── VerifyOTPPage.jsx      # OTP verification component
│   │   └── VerifyOTPPage.css      # OTP verification styles
│   ├── services/
│   │   └── authService.js         # Axios API client
│   └── App.jsx                     # Updated with new routes
```

---

## 🔑 Key Features

### Backend
✅ Custom User model with `is_verified` field
✅ OTP model with expiration tracking
✅ 6-digit random OTP generation
✅ 5-minute OTP expiry
✅ 3-attempt limit before blocking
✅ 30-second resend cooldown
✅ Password hashing with Django default
✅ Email format validation
✅ Duplicate email prevention
✅ HTML email templates
✅ JWT token generation
✅ Django Cache for rate limiting

### Frontend
✅ Email validation with regex
✅ Password strength validation (min 8 chars)
✅ Real-time error messages
✅ Loading states with spinners
✅ Auto-submit on 6-digit OTP
✅ 30-second cooldown timer for resend
✅ Visual OTP digit boxes
✅ Comprehensive error handling
✅ Success redirects
✅ Responsive mobile design
✅ Professional UI with gradients
✅ Accessibility features

---

## 📧 Email Delivery

### Console Output (Development)
```
In terminal where Django is running:
------------- start of email -----------
From: noreply@secure-file-sharing.com
To: user@example.com
Subject: Your Email Verification OTP - Secure File Sharing

Your OTP code is: 123456

This code is valid for 5 minutes.
------------ end of email ------------
```

### HTML Email Template
The system sends professional HTML emails with:
- Branded header
- Clear OTP display
- Expiry information
- Call-to-action
- Footer with copyright

---

## 🧪 Testing

### Test Signup Flow
```bash
# 1. Start backend
cd backend
python manage.py runserver

# 2. In another terminal, start frontend
cd frontend
npm run dev

# 3. Open browser
Visit http://localhost:5173/signup

# 4. Enter test data
Email: test@example.com
Password: TestPassword123
Name: Test User

# 5. Check Django console for OTP
Find the 6-digit code in terminal output

# 6. Enter OTP on verification page
Should verify successfully and redirect to dashboard
```

### API Testing (cURL)

**Signup:**
```bash
curl -X POST http://localhost:8000/api/auth/signup-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "password2": "TestPassword123",
    "name": "Test User"
  }'
```

**Verify OTP:**
```bash
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "otp": "123456"
  }'
```

**Resend OTP:**
```bash
curl -X POST http://localhost:8000/api/auth/resend-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'
```

---

## 🔒 Security Features

| Feature | Implementation |
|---------|-----------------|
| Password Hashing | Django's `make_password()` |
| Email Validation | Regex pattern + database uniqueness |
| OTP Expiry | 5-minute auto-expiration |
| Rate Limiting | Django Cache (30-sec cooldown) |
| Attempt Limit | 3 failed attempts, then block |
| Email Credentials | Environment variables (.env) |
| CORS | Configured for allowed origins |
| HTTPS | Recommended for production |
| JWT Tokens | RS256 algorithm for auth |

---

## ⚙️ Configuration

### Backend Configuration (`settings.py`)
```python
# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Dev
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'   # Prod

# OTP Settings
OTP_LENGTH = 6          # 6-digit OTP
OTP_EXPIRY_MINUTES = 5  # 5 minute expiry

# Cache for rate limiting
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### Frontend Environment (`.env`)
```
VITE_API_URL=http://localhost:8000/api
```

---

## 🐛 Troubleshooting

### Issue: "Email backend not sending"
**Solution**: Check `EMAIL_BACKEND` in settings. For development, use console backend (emails print to terminal).

### Issue: "OTP verification fails"
**Solution**: 
- Verify OTP hasn't expired (5 minutes)
- Check OTP matches exactly (case-sensitive)
- Ensure less than 3 failed attempts

### Issue: "Resend button is disabled"
**Solution**: Wait 30 seconds for cooldown timer to expire.

### Issue: "Frontend not connecting to backend"
**Solution**:
- Verify `VITE_API_URL` in `.env`
- Check CORS is enabled in Django
- Ensure backend is running on port 8000
- Check no firewall blocking port 8000

---

## 📚 Additional Resources

### Documentation Files
- `OTP_SYSTEM_DOCUMENTATION.md` - Complete technical documentation
- This file - Quick start guide

### Backend Code
- `backend/accounts/models.py` - Data models
- `backend/accounts/serializers.py` - API serializers
- `backend/accounts/views.py` - API endpoints
- `backend/accounts/utils.py` - Helper functions

### Frontend Code
- `frontend/src/pages/SignupPage.jsx` - Signup component
- `frontend/src/pages/VerifyOTPPage.jsx` - OTP verification component
- `frontend/src/services/authService.js` - Axios client

---

## 🚢 Production Deployment

### Email Configuration
Configure SMTP in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

### Environment Variables
```
DEBUG=False
SECRET_KEY=your-secret-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Security Checklist
- [ ] Change SECRET_KEY
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS
- [ ] Set CORS_ALLOWED_ORIGINS
- [ ] Configure email service (Gmail, SendGrid, AWS SES)
- [ ] Set OTP expiry and cooldown rates

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `OTP_SYSTEM_DOCUMENTATION.md` for technical details
3. Check Django and React console for error messages

---

**System Status**: ✅ Complete and Ready to Use

Generated: April 4, 2026
Last Updated: April 4, 2026
