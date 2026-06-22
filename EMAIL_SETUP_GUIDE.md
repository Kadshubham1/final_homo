# 📧 EMAIL CONFIGURATION SETUP - GMAIL SMTP

## Status: Email sending now configured ✅

The system is now set up to send real emails via **Gmail SMTP**

---

## 🚀 QUICK SETUP (5 minutes)

### Step 1: Get Gmail App Password

1. Go to: **https://myaccount.google.com/apppasswords**
2. If you see a message saying "2-Step verification required":
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification"
   - Then return to apppasswords
3. Select:
   - App: **Mail**
   - Device: **Windows Computer** (or your device)
4. Click **Generate**
5. Copy the **16-character password** it shows
   - Example: `abcd efgh ijkl mnop` (spaces will be removed)

### Step 2: Set Environment Variables

**For Development (quick test):**

Open PowerShell and run these commands (one at a time):

```powershell
$env:EMAIL_HOST_USER="your-email@gmail.com"
$env:EMAIL_HOST_PASSWORD="abcdefghijklmnop"
```

Then start Django:
```powershell
cd backend
python manage.py runserver
```

**Alternative: Create a `.env` file in `backend/` folder:**

Create file: `backend/.env`
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

Then in Python, install and use python-dotenv:
```bash
pip install python-dotenv
```

And add to `backend/config/settings.py` at the very top:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Step 3: Test Email

**Using Python:**
```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test OTP email from the system',
    'your-email@gmail.com',
    ['recipient@example.com'],
    fail_silently=False,
)
print('✓ Email sent successfully!')
```

**Via Signup:**
1. Go to: http://localhost:5173/signup
2. Sign up with an email you can check
3. OTP should arrive in that email inbox

---

## 🔧 ALTERNATIVE EMAIL SERVICES

### Option A: Gmail (RECOMMENDED)
- Free
- 500 emails/day limit
- No setup costs
- Best for development

Setup: Follow Quick Setup above

### Option B: Mailgun (UP TO 100/MONTH FREE)
- Free tier: 100 emails/month
- Good for production
- Domain verification required

Setup:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@mg.yourdomain.com'
EMAIL_HOST_PASSWORD = 'your-mailgun-password'
```

### Option C: SendGrid (100/DAY FREE)
- Free tier: 100 emails/day
- Best for scale
- API key based

Setup:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'SG.your-sendgrid-api-key'
```

---

## 📋 COMPLETE SETUP CHECKLIST

- [ ] Gmail account created (or existing)
- [ ] 2-Step Verification enabled on Gmail
- [ ] App Password generated (16 characters)
- [ ] `EMAIL_HOST_USER` environment variable set
- [ ] `EMAIL_HOST_PASSWORD` environment variable set
- [ ] Django restarted
- [ ] Test email sent successfully
- [ ] OTP arrives in email inbox

---

## 🧪 TROUBLESHOOTING

### "SMTPAuthenticationError" or "535 5.7.8 Username and password not accepted"
**Fix:**
- Use Gmail App Password (not your regular password)
- Make sure NO spaces in the password
- Check 2-Step Verification is enabled
- Go to: https://myaccount.google.com/less-secure-apps (scroll down)
   - If you see "Allow less secure app access": Turn it ON

### "SMTPNotSupportedError: SMTP AUTH extension not supported by server"
**Fix:**
- Make sure `EMAIL_USE_TLS = True`
- Make sure `EMAIL_PORT = 587`

### "Connection refused" or "Connection timeout"
**Fix:**
- Check internet connection
- Try port 465 with `EMAIL_USE_TLS = False`
- Check firewall isn't blocking SMTP

### Email not arriving
**Fix:**
- Check spam/junk folder
- Verify recipient email address is correct
- Check Django logs for errors
- Test with: `python manage.py shell` then send test email

---

## 🧑‍💻 TEST IT NOW

### Python Test Script

Create file: `backend/test_email.py`

```python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail

try:
    send_mail(
        subject='🎉 OTP Test Email',
        message='If you see this, email is working!\n\nYour OTP: 123456',
        from_email=os.getenv('EMAIL_HOST_USER', 'system@example.com'),
        recipient_list=['your-email@example.com'],  # Change this!
        fail_silently=False,
    )
    print('✅ Email sent successfully!')
except Exception as e:
    print(f'❌ Error: {e}')
```

Run:
```bash
cd backend
python test_email.py
```

---

## 🔐 SECURITY NOTES

- Never commit API keys/passwords to git
- Always use environment variables
- App passwords are safer than main Gmail password
- Delete app passwords you no longer use
- For production, use proper secrets management

---

## 📧 FLOW NOW

User Signs Up
    ↓
OTP Generated
    ↓
Email sent via Gmail SMTP ← ✅ THIS NOW WORKS
    ↓
OTP arrives in user's inbox
    ↓
User enters OTP on verification page
    ↓
Account verified + Logged in

---

## 🎯 NEXT STEPS

1. **Set environment variables** with your Gmail credentials
2. **Restart Django** (`python manage.py runserver`)
3. **Test signup** at http://localhost:5173/signup
4. **Check email** inbox for OTP
5. **Done!** 🎉

---

**Questions?** All OTP emailsshould arrive within seconds!

**Pro Tip**: Check spam folder first if email doesn't appear.
