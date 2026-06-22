# ⚡ QUICK EMAIL SETUP - 5 MINUTES

## What Changed?
✅ OTP emails will now be actually sent to user's email inbox (not console)

---

## 🎯 STEP 1: Get Gmail App Password (2 minutes)

1. Go to: **https://myaccount.google.com/apppasswords**

2. Login with your Gmail account

3. If you see "2-Step verification":
   - Go to: https://myaccount.google.com/security
   - Turn ON: "2-Step Verification"
   - Return to apppasswords

4. Select:
   - **App**: Mail
   - **Device**: Windows Computer

5. Click: **GENERATE**

6. **COPY** the 16-character password (remove spaces)
   - Example: `abcd efgh ijkl mnop` → `abcdefghijklmnop`

---

## 🎯 STEP 2: Run Setup Script (1 minute)

**Option A: Quick Setup (EASIEST)**
```
Double-click: setup_email.bat
Enter your Gmail email
Enter your 16-char password
Wait for Django to start
Done!
```

**Option B: Manual Setup (PowerShell)**

Open PowerShell in project folder and run:
```powershell
$env:EMAIL_HOST_USER = "your-email@gmail.com"
$env:EMAIL_HOST_PASSWORD = "16-char-password"
cd backend
python manage.py runserver
```

---

## 🎯 STEP 3: Test It (2 minutes)

1. Django is running on: http://localhost:8000

2. Frontend running on: http://localhost:5173 (if not started, run `cd frontend && npm run dev` in another terminal)

3. Go to: **http://localhost:5173/signup**

4. Sign up:
   - Email: **Use an email you can check** ✓ (important!)
   - Password: anything
   - Name: optional
   - Click: "Create Account"

5. **CHECK YOUR EMAIL INBOX** (or spam folder)

6. Look for **OTP code** from: noreply@secure-file-sharing.com

7. Copy the OTP code → Paste in verification page

8. ✅ **Success!** Account verified & logged in

---

## ✅ EXPECTED FLOW NOW

```
User fills signup form
        ↓
   Clicks "Create Account"
        ↓
Backend generates OTP (6 digits)
        ↓
GMAIL SENDS EMAIL ← NEW!
        ↓
OTP arrives in user's inbox
        ↓
User enters OTP on verification page
        ↓
Account verified + Logged in ✓
```

---

## 🆘 TROUBLESHOOTING

### "SMTPAuthenticationError"
- Use Gmail App Password (not your regular Gmail password)
- Make sure 2-Step Verification is ON
- No spaces in the password

### "Email not arriving"
- Check SPAM folder
- Verify you entered the correct recipient email
- Try signup with a different email address
- Check Django terminal for error messages

### "Connection timeout"
- Check internet connection
- Try again in 30 seconds
- Check firewall isn't blocking SMTP

---

## 📝 WHAT YOU'LL NEED

- ✓ Gmail account
- ✓ 2-Step Verification enabled
- ✓ Gmail App Password (16 chars)
- ✓ Email you can access to receive OTP

---

## 🚀 TL;DR (SUPER QUICK)

```
1. Go to: https://myaccount.google.com/apppasswords
2. Get 16-char password
3. Run: setup_email.bat (double-click)
4. Enter email + password
5. Test signup at: http://localhost:5173/signup
6. Check email for OTP
7. Done!
```

---

**That's it!** OTP emails will now be sent to real email inboxes! 🎉
