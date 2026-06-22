"""
File sharing models with OTP verification
"""
from django.db import models
from accounts.models import User
from files.models import FileUpload
from django.utils import timezone
from datetime import timedelta
import random
import string


class FileShare(models.Model):
    """
    File sharing between users with OTP verification
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending OTP Verification'),
        ('verified', 'OTP Verified - Transfer Complete'),
        ('expired', 'OTP Expired'),
    )
    
    # Sharing info
    file = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='shares')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_files')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_shares')
    
    # OTP
    otp = models.CharField(max_length=10)
    otp_attempts = models.IntegerField(default=0)
    max_otp_attempts = models.IntegerField(default=3)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Message
    message = models.TextField(blank=True, max_length=500)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['file', 'sender', 'receiver']
        indexes = [
            models.Index(fields=['receiver', 'status']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.file.original_filename} shared from {self.sender.username} to {self.receiver.username}"
    
    def save(self, *args, **kwargs):
        """Generate OTP on creation"""
        if not self.pk:  # Only on creation
            self.generate_otp()
            self.otp_expires_at = timezone.now() + timedelta(minutes=5)  # OTP valid for 5 minutes
        super().save(*args, **kwargs)
    
    def generate_otp(self):
        """Generate random 6-digit OTP"""
        self.otp = ''.join(random.choices(string.digits, k=6))
    
    def is_otp_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.otp_expires_at
    
    def verify_otp(self, entered_otp):
        """Verify OTP and return status"""
        
        # Check if already verified
        if self.is_verified:
            return {'success': False, 'message': 'File already shared and verified.'}
        
        # Check if OTP expired
        if self.is_otp_expired():
            self.status = 'expired'
            self.save()
            return {'success': False, 'message': 'OTP has expired. Please request a new share.'}
        
        # Check attempts
        if self.otp_attempts >= self.max_otp_attempts:
            self.status = 'expired'
            self.save()
            return {'success': False, 'message': 'Maximum OTP attempts exceeded.'}
        
        # Verify OTP
        self.otp_attempts += 1
        self.save()
        
        if str(entered_otp) == str(self.otp):
            self.is_verified = True
            self.status = 'verified'
            self.verified_at = timezone.now()
            self.save()
            return {'success': True, 'message': 'File sharing verified! You can now access it.'}
        else:
            remaining = self.max_otp_attempts - self.otp_attempts
            return {
                'success': False,
                'message': f'Invalid OTP. {remaining} attempts remaining.'
            }
    
    def resend_otp(self):
        """Resend OTP by generating new one"""
        if self.is_otp_expired() and not self.is_verified:
            self.generate_otp()
            self.otp_attempts = 0
            self.otp_expires_at = timezone.now() + timedelta(minutes=5)
            self.save()
            return {'success': True, 'message': 'New OTP sent!', 'otp': self.otp}
        else:
            return {'success': False, 'message': 'Cannot resend OTP at this time.'}


class ShareNotification(models.Model):
    """
    Track share notifications to users
    """
    file_share = models.OneToOneField(FileShare, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='share_notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Share notification for {self.receiver.username}"
