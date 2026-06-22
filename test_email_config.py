"""
Test Email Configuration
Run this to verify Gmail SMTP is working
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent / 'backend'
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("\n" + "="*60)
print("EMAIL CONFIGURATION TEST")
print("="*60 + "\n")

# Display current configuration
print("📧 Current Email Configuration:")
print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print()

# Check if credentials are set
if settings.EMAIL_HOST_USER in ['', 'your-email@gmail.com']:
    print("❌ ERROR: Gmail credentials not configured!")
    print("\nSet environment variables FIRST:")
    print('   Windows PowerShell:')
    print('   $env:EMAIL_HOST_USER = "your-email@gmail.com"')
    print('   $env:EMAIL_HOST_PASSWORD = "your-16-char-password"')
    print()
    print('   Or double-click: setup_email.bat')
    print()
    sys.exit(1)

# Get recipient email
recipient = input("📬 Enter test email to receive OTP (e.g., your-personal-email@gmail.com): ").strip()

if not recipient or '@' not in recipient:
    print("❌ Invalid email address")
    sys.exit(1)

print(f"\n⏳ Sending test email to: {recipient}")
print("   This may take 5-10 seconds...")

try:
    send_mail(
        subject='🎉 OTP System Test - Email Working!',
        message='''
Hello!

If you received this email, your OTP email system is working perfectly! ✅

Test OTP Code: 123456

This is a test from the Secure File Sharing System.

---
Setup Complete!

Now you can:
1. Go to http://localhost:5173/signup
2. Sign up with your actual email
3. OTP will be sent to your email
4. Complete the verification process

---
Best regards,
Secure File Sharing System
''',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient],
        fail_silently=False,
    )
    print("\n✅ SUCCESS! Email sent!")
    print(f"   Check: {recipient}")
    print("   (May take 5-10 seconds to arrive)")
    print("\n🎉 Email system is working! Ready to use in signup flow.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("   1. Check Gmail credentials are correct")
    print("   2. Verify 2-Step Verification is enabled")
    print("   3. Use Gmail App Password (not regular password)")
    print("   4. Check internet connection")
    print("\nFor help: See EMAIL_SETUP_GUIDE.md")
    sys.exit(1)
