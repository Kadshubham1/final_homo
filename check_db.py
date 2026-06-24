import os
import sys
import django

# Setup Django
sys.path.insert(0, 'c:\\Users\\Admin\\Pictures\\updated-homofinal\\updated-homo\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import OTP, User
from django.utils import timezone

print("\n" + "="*50)
print("DATABASE CHECK - OTP VERIFICATION")    
print("="*50)

# Get all users and their OTP status
users = User.objects.all().order_by('-created_at')[:5]
print(f"\nTotal users in database: {User.objects.count()}")
print("\nRecent users:")

for user in users:
    print(f"\n* Email: {user.email}")
    print(f"  * Username: {user.username}")
    print(f"  * Is Verified: {user.is_verified}")
    print(f"  * Created: {user.created_at}")
    
    try:
        otp = OTP.objects.get(user=user)
        print(f"  * OTP Status:")
        print(f"      * Code: {otp.otp_code}")
        print(f"      * Is Valid: {otp.is_valid}")
        print(f"      * Is Expired: {otp.is_expired}")
        print(f"      * Is Used: {otp.is_used}")
        print(f"      * Attempts: {otp.attempts}")
        print(f"      * Created: {otp.created_at}")
        print(f"      * Expires: {otp.expires_at}")
    except OTP.DoesNotExist:
        print(f"  * NO OTP RECORD FOUND!")

print("\n" + "="*50)
