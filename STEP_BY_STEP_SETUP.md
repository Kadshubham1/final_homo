# 📧 STEP-BY-STEP EMAIL SETUP (FOLLOW THIS EXACTLY)

## What We're Doing
Setting up Gmail SMTP so OTP codes are sent to real email addresses

---

## 📋 CHECKLIST (Follow steps in order)

### ✅ STEP 1: Get Gmail App Password (2 minutes)

1. Open browser → Go to: **https://myaccount.google.com/apppasswords**

2. Login with your Gmail account

3. If you see "2-Step Verification Not Set Up":
   - Go to: https://myaccount.google.com/security
   - Click: **2-Step Verification**
   - Follow prompts to enable it
   - Return to apppasswords page

4. You should see two dropdowns:

   **First dropdown**: Select **Mail**
   
   **Second dropdown**: Select **Windows Computer**

5. Click: **GENERATE**

6. You'll see a 16-character password like: `abcd efgh ijkl mnop`
   
   **COPY THIS** (or write it down)

7. **REMOVE ANY SPACES** from the password
   - Before: `abcd efgh ijkl mnop`
   - After: `abcdefghijklmnop`

---

### ✅ STEP 2: Set Environment Variables (Choose ONE option)

#### **OPTION A: Use PowerShell Script (EASIEST)**

PowerShell > (in project root folder):

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
.\setup_email.ps1
```

Then follow the prompts:
- Enter Gmail email
- Enter 16-char password
- Django starts automatically

**SKIP TO STEP 3** if you use this option.

---

#### **OPTION B: Manual PowerShell Commands**

Open PowerShell in project root folder (`c:\Users\Admin\Music\updated-homo\updated-homo`)

Run these commands one by one:

```powershell
$env:EMAIL_HOST_USER = "YOUR-EMAIL@gmail.com"
```

Replace `YOUR-EMAIL@gmail.com` with your actual Gmail address

```powershell
$env:EMAIL_HOST_PASSWORD = "16-character-password"
```

Replace `16-character-password` with your app password (NO SPACES)

```powershell
$env:EMAIL_HOST = "smtp.gmail.com"
$env:EMAIL_PORT = "587"
$env:EMAIL_USE_TLS = "True"
```

Verify they're set:

```powershell
Write-Host "Email: $env:EMAIL_HOST_USER"
Write-Host "Host: $env:EMAIL_HOST"
```

**You should see your email and smtp.gmail.com**

---

### ✅ STEP 3: Start Django Backend

In PowerShell terminal (same folder):

```powershell
cd backend
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

**Leave this terminal running** ✓

---

### ✅ STEP 4: Start Frontend (New Terminal)

Open a **NEW** PowerShell window in project root:

```powershell
cd frontend
npm run dev
```

You should see:
```
VITE v5.4.21  ready in XXX ms
➜  Local:   http://localhost:5173/
```

**Leave this terminal running** ✓

---

### ✅ STEP 5: Test Email Configuration

Open **THIRD** PowerShell window in project root:

```powershell
python test_email_config.py
```

Follow the prompts:
1. Enter a test email address (must be one you can check)
2. Script sends test email
3. Wait 5-10 seconds

Check your email inbox for test message with OTP code

**If email arrives** ✓ → Continue to STEP 6

**If email doesn't arrive** → Check spam folder or see TROUBLESHOOTING

---

### ✅ STEP 6: Test Full Signup Flow

1. Open browser → Go to: **http://localhost:5173/signup**

2. Fill in form:
   - **Email**: Use the SAME email you tested (must be real)
   - **Password**: Anything (min 8 chars)
   - **Confirm Password**: Same as above
   - **Name**: Optional

3. Click: **Create Account**

4. You'll see on screen:
   ```
   Account created successfully!
   Your OTP Code: 123456
   ```

5. Check email inbox (wait 5-10 seconds) for OTP email

6. Copy OTP from email

7. Page should auto-redirect to verification

8. Paste OTP if not auto-filled

9. Click: **Verify OTP**

10. ✅ **SUCCESS!** Account verified

---

## 🧪 EXPECTED RESULTS

✅ Test email arrives in email inbox within 5-10 seconds

✅ Email shows: "OTP System Test - Email Working!"

✅ Shows test OTP code: 123456

✅ When you sign up, OTP arrives in email

✅ You can verify and complete signup

---

## 🆘 TROUBLESHOOTING

### Email not sent - "SMTPAuthenticationError"
**Fix:**
1. Go to: https://myaccount.google.com/apppasswords
2. Generate a NEW app password
3. Make sure to REMOVE SPACES from password
4. Set environment variables again
5. Restart Django

### Email is in SPAM folder
**Fix:**
1. Mark email as "Not Spam"
2. This trains Gmail
3. Future emails arrive in inbox

### 2-Step Verification not working
**Fix:**
1. Go to: https://myaccount.google.com/account
2. Select: Security (left menu)
3. Scroll: "Your devices"
4. Click: "2-Step Verification"
5. Enable it
6. Return to apppasswords

### Environment variables not persisting
**Note:** They only last for current PowerShell session
- If you close PowerShell, run the commands again
- Or use `.env` file (see advanced section)

---

## 📊 CONFIGURATION SUMMARY

| Setting | Value |
|---------|-------|
| EMAIL_BACKEND | Gmail SMTP |
| EMAIL_HOST | smtp.gmail.com |
| EMAIL_PORT | 587 |
| EMAIL_USE_TLS | True |
| EMAIL_HOST_USER | your-email@gmail.com |
| EMAIL_HOST_PASSWORD | 16-char app password |

---

## ✅ COMPLETE FLOW

```
User visits: http://localhost:5173/signup
         ↓
Fills form + Click "Create Account"
         ↓
Backend generates OTP: 123456
         ↓
Email sent via Gmail SMTP ← EMAIL WORKS NOW!
         ↓ (5-10 seconds)
User receives email with OTP
         ↓
User enters OTP on verification page
         ↓
Account verified ✅
         ↓
User logged in ✅
```

---

## 🎯 QUICK REFERENCE

**Three Terminals You Need:**

Terminal 1 (Django):
```
cd backend
python manage.py runserver
```

Terminal 2 (Frontend):
```
cd frontend
npm run dev
```

Terminal 3 (Testing):
```
python test_email_config.py
```

**Browser Tests:**
- Signup: http://localhost:5173/signup
- Debug: http://localhost:5173/otp-debug

---

## ⏱️ TIME NEEDED

- Get app password: 2 min
- Set variables: 1 min
- Start servers: 1 min
- Test email: 2 min
- **Total: 6 minutes to full working system!**

---

**Ready?** Start with **STEP 1** above! 🚀

Any issues? Check TROUBLESHOOTING section or EMAIL_SETUP_GUIDE.md for detailed help.
