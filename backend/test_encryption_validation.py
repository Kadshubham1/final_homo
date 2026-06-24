import os
import django
import base64
from django.core.files.base import ContentFile
from cryptography.fernet import Fernet

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from files.models import FileUpload
from accounts.models import User

def test_existing_files():
    print("=== Testing Decryption of Existing Files ===")
    files = FileUpload.objects.all()
    if not files.exists():
        print("No files found in the database.")
        return
        
    for f in files:
        print(f"\nChecking File ID: {f.id}")
        print(f"  Name: {f.original_filename}")
        print(f"  Is Encrypted: {f.is_encrypted}")
        print(f"  Encryption Key stored: {bool(f.encryption_key)}")
        
        if f.is_encrypted and f.encryption_key:
            try:
                decrypted = f.decrypt_file_content()
                if decrypted is not None:
                    print(f"  [SUCCESS] Decryption successful. Decrypted content length: {len(decrypted)} bytes.")
                    # Show first 100 bytes if it is text-like
                    try:
                        text_preview = decrypted[:100].decode('utf-8')
                        print(f"  Preview (plain text): {text_preview!r}")
                    except UnicodeDecodeError:
                        print(f"  Preview (binary): {decrypted[:20]!r}")
                else:
                    print("  [FAILED] Decryption returned None.")
            except Exception as e:
                print(f"  [ERROR] Decryption raised an exception: {e}")
        else:
            print("  File is not marked as encrypted or has no encryption key.")

def test_roundtrip_encryption_decryption():
    print("\n=== Running Round-Trip Encryption/Decryption Test on Mock File ===")
    
    # 1. Get or create a test user
    user = User.objects.first()
    if not user:
        # Create a temporary user if none exists
        user = User.objects.create_user(
            username="temp_test_user", 
            email="temp@test.com", 
            password="testpassword123"
        )
        print(f"Created temporary test user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")

    # 2. Define test plaintext
    plaintext_data = b"This is a secret message used to test the homomorphic secure encryption model!"
    filename = "test_secret_document.txt"
    
    # 3. Create and save file object
    print("Creating FileUpload object...")
    f_obj = FileUpload(
        user=user,
        original_filename=filename,
        file=ContentFile(plaintext_data, name=filename),
        file_size=len(plaintext_data),
        mime_type="text/plain",
        scope="private",
        is_encrypted=True
    )
    
    # Save triggers calculation of hash, save, and then encryption
    f_obj.save()
    print(f"Saved FileUpload ID: {f_obj.id}")
    print(f"  Calculated hash: {f_obj.file_hash}")
    print(f"  Is Encrypted: {f_obj.is_encrypted}")
    print(f"  Encryption key generated: {f_obj.encryption_key}")
    
    try:
        # 4. Verify encrypted file exists and has different content
        if not f_obj.encrypted_file:
            print("  [FAILED] Encrypted file was not created or saved.")
            return
            
        f_obj.encrypted_file.seek(0)
        encrypted_data = f_obj.encrypted_file.read()
        print(f"  Encrypted content length: {len(encrypted_data)} bytes")
        print(f"  Encrypted data preview: {encrypted_data[:50]!r}")
        
        if encrypted_data == plaintext_data:
            print("  [FAILED] Encrypted data is identical to plaintext data!")
            return
        else:
            print("  [SUCCESS] File content in storage is encrypted.")

        # 5. Verify decryption works
        decrypted_data = f_obj.decrypt_file_content()
        if decrypted_data == plaintext_data:
            print("  [SUCCESS] Decrypted data matches the original plaintext exactly!")
        else:
            print(f"  [FAILED] Decrypted data does not match! Decrypted: {decrypted_data!r}")
            
    finally:
        # 6. Cleanup
        print("Cleaning up test file and database records...")
        if f_obj.file:
            f_obj.file.delete(save=False)
        if f_obj.encrypted_file:
            f_obj.encrypted_file.delete(save=False)
        f_obj.delete()
        if user.username == "temp_test_user":
            user.delete()
            print("Deleted temporary test user.")
        print("Cleanup completed.")

if __name__ == "__main__":
    test_existing_files()
    test_roundtrip_encryption_decryption()
