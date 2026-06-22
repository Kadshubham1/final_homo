# Email OTP Verification System - Documentation

## Overview

A complete user signup and email OTP verification system built with:
- **Backend**: Django + Django REST Framework
- **Frontend**: React with Hooks, Functional Components, and Axios
- **Email**: Django Email Backend (Console for development, SMTP for production)

---

## Backend Implementation

### 1. Models

#### User Model (Extended)
Located in `backend/accounts/models.py`

The existing `User` model was extended with the `is_verified` field:
```python
is_verified = models.BooleanField(default=False)
```

#### OTP Model
New model created to store OTP codes with expiration:
```python
class OTP(models.Model):
    user = models.OneToOneField(User, ...)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_expired and not self.is_used
```

### 2. API Endpoints

#### POST `/api/auth/signup-otp/`
**Create user account and send OTP verification email**

Request:
```json
{
    "email": "user@example.com",
    "password": "secure_password_123",
    "password2": "secure_password_123",
    "name": "John Doe"
}
```

Response:
```json
{
    "message": "Signup successful! Check your email for OTP verification code.",
    "email": "user@example.com",
    "user": {
        "id": 1,
        "username": "user@example.com",
        "email": "user@example.com",
        "name": "John Doe",
        "is_verified": false
    }
}
```

Features:
- Creates user with `is_verified=False`
- Generates 6-digit OTP
- Saves OTP with 5-minute expiry
- Sends OTP via email
- Password hashing using Django's default hasher
- Email uniqueness validation

#### POST `/api/auth/verify-otp/`
**Verify OTP and activate user account**

Request:
```json
{
    "email": "user@example.com",
    "otp": "123456"
}
```

Response:
```json
{
    "message": "Email verified successfully! Your account is now active.",
    "user": { ... },
    "refresh": "eyJ...",
    "access": "eyJ..."
}
```

Features:
- Validates OTP code against stored value
- Checks OTP expiration (5 minutes)
- Prevents OTP reuse
- Tracks failed attempts (max 3 attempts)
- Marks user as verified
- Deletes OTP after success
- Sends verification success email
- Returns JWT tokens for immediate login

#### POST `/api/auth/resend-otp/`
**Resend OTP with rate limiting**

Request:
```json
{
    "email": "user@example.com"
}
```

Response:
```json
{
    "message": "New OTP sent to your email. It will expire in 5 minutes.",
    "expires_in": 300,
    "email": "user@example.com"
}
```

Features:
- 30-second cooldown between resend requests
- Generates new OTP
- Resets attempt counter
- Uses Django Cache for rate limiting
- Sends new OTP via email

### 3. Email Configuration

Located in `backend/config/settings.py`

**Development Mode** (Console backend):
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@secure-file-sharing.com'
```

**Production Mode** (SMTP backend):
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

### 4. Security Features

- **Password Hashing**: Uses Django's `make_password()` algorithm
- **Email Validation**: Validates email format and uniqueness
- **OTP Expiration**: 5-minute expiry time
- **Rate Limiting**: 30-second cooldown for resend
- **Attempt Tracking**: Maximum 3 failed OTP attempts
- **Environment Variables**: Email credentials via .env
- **OTP Randomization**: Cryptographically secure 6-digit generation

### 5. Serializers

All serializers include comprehensive validation:

**SignupWithOTPSerializer**:
- Email uniqueness check
- Password matching validation
- Email format validation

**VerifyOTPSerializer**:
- OTP existence validation
- OTP expiration check
- Attempt tracking
- OTP match validation

**ResendOTPSerializer**:
- Email existence validation
- Rate limit checking via Django Cache

---

## Frontend Implementation

### 1. Auth Service (Axios API Client)

Located in `frontend/src/services/authService.js`

Provides:
- `signupWithOTP(userData)` - Register new user
- `verifyOTP(email, otp)` - Verify OTP and login
- `resendOTP(email)` - Resend OTP
- `login(username, password)` - Regular login
- `logout()` - Logout user
- `getCurrentUser()` - Get logged-in user
- Automatic token management in localStorage
- Request/response interceptors
- Error handling

### 2. Signup Page (`SignupPage.jsx`)

Features:
- **Email input** with format validation
- **Password field** with 8-character minimum requirement
- **Confirm password** field with match validation
- **Name field** (optional)
- **Real-time error messages** per field
- **Loading state** with spinner
- **Success redirect** to OTP verification page
- **Error handling** with user-friendly messages

Validation:
- Email format check
- Password strength (min 8 characters)
- Password confirmation match
- Email uniqueness check (via backend)

### 3. OTP Verification Page (`VerifyOTPPage.jsx`)

Features:
- **6-digit OTP input** with numeric-only restriction
- **Auto-submit** when all 6 digits are entered
- **Visual OTP display** boxes
- **Loading state** during verification
- **Resend button** with 30-second cooldown timer
- **Attempt counter** (shows remaining attempts)
- **Back button** to signup
- **Success redirect** to dashboard
- **Comprehensive error messages**

Auto-verify Logic:
```javascript
useEffect(() => {
  if (otp.length === 6 && /^\d{6}$/.test(otp)) {
    handleVerifyOTP();
  }
}, [otp]);
```

Cooldown Timer:
```javascript
useEffect(() => {
  if (resendCooldown > 0) {
    const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
    return () => clearTimeout(timer);
  }
}, [resendCooldown]);
```

### 4. Styling

Professional, responsive CSS with:
- Gradient backgrounds
- Smooth animations
- Mobile-responsive design
- Accessible form inputs
- Clear error states
- Loading animations
- Professional color scheme

---

## Complete Signup Flow

### Step 1: User Navigates to Signup
```
User visits /signup
```

### Step 2: User Enters Details
```
Email: user@example.com
Password: secure_password_123
Name: John Doe
```

### Step 3: Frontend Validates
```
- Email format check
- Password strength check
- Password confirmation match
```

### Step 4: API Call - Signup
```
POST /api/auth/signup-otp/
  ↓
Backend creates user (is_verified=false)
Backend generates 6-digit OTP
Backend stores OTP with 5-min expiry
Backend sends OTP email
Returns user data
  ↓
Frontend stores email in localStorage
Frontend redirects to /verify-otp
```

### Step 5: Email Received
```
User receives HTML email with OTP code:
┌─────────────────────────────────┐
│   Your Email Verification OTP   │
│         Secure File Share        │
│                                 │
│            123456               │
│                                 │
│   This OTP is valid for         │
│   5 minutes                     │
└─────────────────────────────────┘
```

### Step 6: User Enters OTP
```
User visits /verify-otp
User enters 6-digit OTP
Frontend auto-submits on 6th digit
```

### Step 7: API Call - Verify OTP
```
POST /api/auth/verify-otp/
  ↓
Backend validates OTP:
  - Check OTP exists
  - Check not expired
  - Check not previously used
  - Check OTP matches
  ↓
If valid:
  - Mark user as_verified=true
  - Mark OTP as is_used=true
  - Generate JWT tokens
  - Send success email
  - Return tokens and user data
  ↓
Frontend stores tokens
Frontend clears localStorage
Frontend redirects to /dashboard
```

### Step 8: User Logged In
```
User is now fully registered and logged in
Can access all features
Account is activated
```

---

## Environment Setup

### Backend Setup

1. **Create OTP Model** ✓
   ```bash
   python manage.py makemigrations accounts
   python manage.py migrate accounts
   ```

2. **Configure Email** (in `settings.py`) ✓
   - Development: Console backend (prints to console)
   - Production: SMTP backend (configure in .env)

3. **URL Routes** ✓
   Added to `backend/accounts/urls.py`:
   - `/api/auth/signup-otp/`
   - `/api/auth/verify-otp/`
   - `/api/auth/resend-otp/`

### Frontend Setup

1. **Create Components** ✓
   - `SignupPage.jsx` + `SignupPage.css`
   - `VerifyOTPPage.jsx` + `VerifyOTPPage.css`

2. **Create Auth Service** ✓
   - `services/authService.js`

3. **Update Routing** ✓
   - Added routes in `App.jsx`

4. **Environment Variables** (optional)
   Create `.env` in frontend folder:
   ```
   VITE_API_URL=http://localhost:8000/api
   ```

---

## Testing the System

### Manual Testing

1. **Start Backend**:
   ```bash
   python manage.py runserver
   ```

2. **Start Frontend**:
   ```bash
   npm run dev
   ```

3. **Test Signup Flow**:
   - Visit http://localhost:5173/signup
   - Enter test email: test@example.com
   - Enter password: TestPassword123
   - Click "Create Account"
   - Check backend console for OTP email (if using console backend)

4. **Test OTP Verification**:
   - Copy OTP from console
   - Enter OTP in verification page
   - Should see success message and redirect

5. **Test Resend OTP**:
   - Click "Resend OTP"
   - Verify cooldown timer shows 30 seconds
   - After 30 seconds, can resend again

---

## Error Handling

### Frontend Error Messages

```
"Email is required"
"Please enter a valid email address"
"This email is already registered"
"Password must be at least 8 characters"
"Passwords do not match"
"OTP must be 6 digits"
"Invalid OTP. Please try again."
"OTP has expired. Please request a new one."
"Too many failed attempts. Please request a new OTP."
```

### Backend Error Responses

```json
{
    "email": ["This email is already registered."]
}

{
    "password": ["Passwords do not match."]
}

{
    "otp": ["Invalid OTP. Please try again."]
}

{
    "email": ["No account found with this email."]
}
```

---

## Production Deployment

### Email Configuration

1. **Gmail SMTP**:
   ```python
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_HOST_USER = 'your-email@gmail.com'
   EMAIL_HOST_PASSWORD = 'your-app-password'
   ```

2. **SendGrid**:
   ```python
   EMAIL_HOST = 'smtp.sendgrid.net'
   EMAIL_PORT = 587
   EMAIL_HOST_USER = 'apikey'
   EMAIL_HOST_PASSWORD = 'SG.xxx...'
   ```

3. **AWS SES**:
   ```python
   EMAIL_BACKEND = 'django_ses.SESBackend'
   AWS_ACCESS_KEY_ID = '...'
   AWS_SECRET_ACCESS_KEY = '...'
   ```

### Security Checklist

- [ ] DEBUG = False
- [ ] SECRET_KEY changed from default
- [ ] ALLOWED_HOSTS configured
- [ ] Email credentials in .env file
- [ ] CORS restricted to allowed origins
- [ ] HTTPS enabled
- [ ] OTP expiry configured (recommended 5 minutes)
- [ ] Rate limiting configured (recommended 30 seconds)
- [ ] Database backups enabled

---

## API Response Examples

### Success Responses

**Signup Success** (201):
```json
{
    "message": "Signup successful! Check your email for OTP verification code.",
    "email": "user@example.com",
    "user": {
        "id": 1,
        "username": "user@example.com",
        "email": "user@example.com",
        "name": "John Doe",
        "created_at": "2026-04-04T13:30:00Z"
    }
}
```

**Verify OTP Success** (200):
```json
{
    "message": "Email verified successfully! Your account is now active.",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "is_verified": true,
        ...
    },
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Error Responses

**Invalid Email** (400):
```json
{
    "email": ["This email is already registered."]
}
```

**Invalid OTP** (400):
```json
{
    "otp": ["Invalid OTP. Please try again."]
}
```

**Expired OTP** (400):
```json
{
    "otp": ["OTP has expired. Please request a new one."]
}
```

---

## Features Summary

✅ Email-based signup
✅ 6-digit OTP verification
✅ Password hashing and validation
✅ Email format validation
✅ Duplicate email prevention
✅ OTP expiration (5 minutes)
✅ Rate limiting (30 seconds)
✅ Attempt tracking (max 3 attempts)
✅ HTML email templates
✅ JWT token generation
✅ Automatic email verification
✅ Professional UI/UX
✅ Responsive design
✅ Error handling
✅ Loading states
✅ Auto-submit on OTP input
✅ Resend with cooldown
✅ Success redirects

---

## Troubleshooting

### Emails not sending?
1. Check EMAIL_BACKEND in settings
2. For console backend: Check terminal output
3. For SMTP: Verify credentials in .env
4. Check firewall/port 587 (SMTP)

### OTP not working?
1. Check OTP length is 6 digits
2. Verify OTP hasn't expired (5 minutes)
3. Verify OTP hasn't been used
4. Check attempt count (max 3 attempts)

### Database migration failed?
```bash
python manage.py migrate accounts --fake-initial
python manage.py makemigrations accounts
python manage.py migrate accounts
```

### Frontend not connecting to backend?
1. Check CORS is enabled in Django settings
2. Verify API_BASE_URL in authService.js
3. Check backend is running on port 8000
4. Check frontend is running on port 5173

---

## Next Steps

- Integrate with existing login system ✓
- Add SMS OTP option
- Add two-factor authentication
- Add password reset with OTP
- Add email change verification
- Add optional email notifications

---

Generated: April 4, 2026
Version: 1.0
