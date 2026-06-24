import os
import sys
import django

sys.path.insert(0, 'c:\\Users\Admin\\Pictures\\updated-homofinal\\updated-homo\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from sharing.models import FileShare
from files.models import FileUpload
from accounts.models import User

print("=== FILE SHARES ===")
shares = FileShare.objects.all()
print(f"Total shares: {shares.count()}")
for s in shares:
    print(f"Share ID: {s.id}")
    print(f"  File ID: {s.file.id} ({s.file.original_filename})")
    print(f"  File Scope: {s.file.scope}")
    print(f"  Sender: {s.sender.email} / {s.sender.username}")
    print(f"  Receiver: {s.receiver.email} / {s.receiver.username}")
    print(f"  Is Verified: {s.is_verified}")
    print(f"  Status: {s.status}")
    print(f"  OTP: {s.otp}")
    print("-" * 30)

print("\n=== FILES ===")
files = FileUpload.objects.all()
print(f"Total files: {files.count()}")
for f in files:
    print(f"File ID: {f.id} ({f.original_filename}) - Scope: {f.scope} - Owner: {f.user.username}")
