"""
File management models
"""
import os
from django.db import models
from accounts.models import User
from django.core.files.base import ContentFile
from cryptography.fernet import Fernet
import base64
import hashlib


class FileUpload(models.Model):
    """
    File Upload model
    Stores file metadata and encrypted file content
    """
    
    SCOPE_CHOICES = (
        ('public', 'Public - Anyone can see'),
        ('private', 'Private - Only owner'),
    )
    
    # File info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    original_filename = models.CharField(max_length=500)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    encrypted_file = models.FileField(upload_to='encrypted/%Y/%m/%d/', blank=True, null=True)
    
    # File metadata
    file_size = models.BigIntegerField()  # In bytes
    mime_type = models.CharField(max_length=100, default='application/octet-stream')
    file_hash = models.CharField(max_length=64, blank=True)  # SHA-256 hash
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='private')
    
    # Encryption info (simulated)
    is_encrypted = models.BooleanField(default=True)
    encryption_key = models.CharField(max_length=500, blank=True)  # Base64 encoded key
    
    # Tracking
    downloads = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'scope']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} - {self.user.username}"
    
    def get_file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.original_filename)[1].lower()
    
    def get_file_size_display(self):
        """Return human-readable file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024:
                return f"{self.file_size:.2f} {unit}"
            self.file_size /= 1024
        return f"{self.file_size:.2f} TB"
    
    def calculate_hash(self):
        """Calculate SHA-256 hash of file"""
        self.file.seek(0)
        file_hash = hashlib.sha256()
        for chunk in self.file.chunks():
            file_hash.update(chunk)
        return file_hash.hexdigest()
    
    def encrypt_file_content(self):
        """
        Simulate homomorphic encryption
        In production, use proper homomorphic encryption libraries
        """
        try:
            # Generate encryption key
            key = Fernet.generate_key()
            cipher_suite = Fernet(key)
            
            # Read file content
            self.file.seek(0)
            file_content = self.file.read()
            
            # Encrypt content
            encrypted_content = cipher_suite.encrypt(file_content)
            
            # Store encryption key FIRST so it's available when file save triggers a model save
            self.encryption_key = base64.b64encode(key).decode('utf-8')
            self.is_encrypted = True
            
            # Save encrypted file (this will trigger a recursive save call)
            # Use a dummy filename to avoid collisions
            encrypted_filename = f"encrypted_{self.original_filename}"
            self.encrypted_file.save(encrypted_filename, ContentFile(encrypted_content), save=False)
            
            return True
        except Exception as e:
            print(f"Encryption error: {e}")
            return False
    
    def decrypt_file_content(self):
        """Decrypt file for download"""
        try:
            if not self.is_encrypted or not self.encryption_key:
                return self.file.read()
            
            key = base64.b64decode(self.encryption_key.encode('utf-8'))
            cipher_suite = Fernet(key)
            
            self.encrypted_file.seek(0)
            encrypted_content = self.encrypted_file.read()
            decrypted_content = cipher_suite.decrypt(encrypted_content)
            
            return decrypted_content
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
    
    def save(self, *args, **kwargs):
        """Override save to add hash and encryption"""
        is_new = not self.pk
        
        if is_new:  # Only on creation
            self.file_hash = self.calculate_hash()
        
        super().save(*args, **kwargs)
        
        # Encrypt after object is saved to database (so it has a pk)
        if is_new and self.is_encrypted:
            # We use a flag to prevent infinite recursion if needed, 
            # though encrypted_file.save(save=False) handles it.
            self.encrypt_file_content()
            super().save(update_fields=['encrypted_file', 'encryption_key', 'is_encrypted'])


class FileDownload(models.Model):
    """
    Track file downloads
    """
    file = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='download_records')
    downloaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    download_size = models.BigIntegerField()  # In bytes
    
    class Meta:
        ordering = ['-downloaded_at']
    
    def __str__(self):
        return f"{self.file.original_filename} - Downloaded by {self.downloaded_by.username}"
