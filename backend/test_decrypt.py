import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from files.models import FileUpload
from cryptography.fernet import Fernet
import base64

f = FileUpload.objects.get(id=3)
print(f'Attempting to decrypt file ID {f.id}...')
try:
    if not f.is_encrypted or not f.encryption_key:
        print('File is not encrypted.')
        content = f.file.read()
    else:
        key = base64.b64decode(f.encryption_key.encode('utf-8'))
        cipher_suite = Fernet(key)
        f.encrypted_file.seek(0)
        encrypted_content = f.encrypted_file.read()
        print(f'Encrypted content length: {len(encrypted_content)}')
        decrypted_content = cipher_suite.decrypt(encrypted_content)
        print(f'Decrypted content length: {len(decrypted_content)}')
except Exception as e:
    print(f'Decryption failed: {e}')
    import traceback
    traceback.print_exc()
