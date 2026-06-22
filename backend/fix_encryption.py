import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from files.models import FileUpload
from cryptography.fernet import Fernet
import base64
from django.core.files.base import ContentFile

for f in FileUpload.objects.all():
    print(f'Processing ID {f.id}: {f.original_filename}...')
    try:
        # Check if decryption works
        if f.is_encrypted and f.encryption_key:
            try:
                key = base64.b64decode(f.encryption_key.encode('utf-8'))
                cipher_suite = Fernet(key)
                f.encrypted_file.seek(0)
                encrypted_content = f.encrypted_file.read()
                cipher_suite.decrypt(encrypted_content)
                print(f'  ID {f.id} is already healthy.')
                continue
            except Exception:
                print(f'  ID {f.id} is BROKEN. Re-encrypting...')
        
        # If broken or not encrypted, re-encrypt from original if possible
        if f.file and os.path.exists(f.file.path):
            f.file.seek(0)
            original_content = f.file.read()
            
            # Generate new key
            key = Fernet.generate_key()
            cipher_suite = Fernet(key)
            encrypted_content = cipher_suite.encrypt(original_content)
            
            # Update record
            f.encryption_key = base64.b64encode(key).decode('utf-8')
            f.is_encrypted = True
            
            # Save new encrypted file
            encrypted_filename = f"encrypted_{f.original_filename}"
            f.encrypted_file.save(encrypted_filename, ContentFile(encrypted_content), save=False)
            f.save(update_fields=['encrypted_file', 'encryption_key', 'is_encrypted'])
            print(f'  ID {f.id} RE-ENCRYPTED SUCCESSFULLY.')
        else:
            print(f'  ID {f.id} CANNOT BE FIXED (Original file missing).')
            
    except Exception as e:
        print(f'  Error processing ID {f.id}: {e}')
