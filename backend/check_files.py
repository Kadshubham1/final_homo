import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from files.models import FileUpload
for f in FileUpload.objects.all():
    print(f'ID: {f.id}, Name: {f.original_filename}')
    try:
        if f.file and os.path.exists(f.file.path):
            print(f'  Original exists: {f.file.path}')
        else:
            print(f'  Original MISSING: {f.file.path if f.file else "N/A"}')
        
        if f.encrypted_file and os.path.exists(f.encrypted_file.path):
            print(f'  Encrypted exists: {f.encrypted_file.path}')
        else:
            print(f'  Encrypted MISSING: {f.encrypted_file.path if f.encrypted_file else "N/A"}')
    except Exception as e:
        print(f'  Error checking paths: {e}')
