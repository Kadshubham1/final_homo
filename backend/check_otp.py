#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import OTP, User

# Get the latest user
user = User.objects.order_by('-created_at').first()
print(f"\n=== Latest User ===")
print(f"Email: {user.email}")
print(f"Username: {user.username}")
print(f"Is Verified: {user.is_verified}")

try:
    otp = OTP.objects.get(user=user)
    print(f"\n=== OTP Details ===")
    print(f"OTP Code: {otp.otp_code}")
    print(f"Is Expired: {otp.is_expired}")
    print(f"Is Valid: {otp.is_valid}")
    print(f"Is Used: {otp.is_used}")
    print(f"Attempts: {otp.attempts}")
    print(f"Created: {otp.created_at}")
    print(f"Expires: {otp.expires_at}")
except OTP.DoesNotExist:
    print("\n❌ No OTP found for this user!")
