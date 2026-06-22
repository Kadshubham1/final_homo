"""
User models for authentication and profiles
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    """
    Custom User model with additional fields
    Roles: User, Admin
    """
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']
    
    ROLE_CHOICES = (
        ('user', 'Regular User'),
        ('admin', 'Administrator'),
    )
    
    # Basic info
    name = models.CharField(max_length=255, blank=True)
    mobile = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r'^\d{10,15}$', 'Invalid phone number')]
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
    # Profile info
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.name or self.username} ({self.role})"
    
    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def get_full_info(self):
        """Return user details"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'mobile': self.mobile,
            'role': self.role,
            'is_admin': self.is_admin,
            'created_at': self.created_at
        }


class UserActivity(models.Model):
    """
    Track user login activities
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=100)  # 'login', 'logout', etc.
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"


class OTP(models.Model):
    """
    One-Time Password (OTP) for email verification
    Stores OTP codes with expiration time
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)  # Track failed attempts
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp_code}"
    
    @property
    def is_expired(self):
        """Check if OTP has expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if OTP is valid (not expired and not used)"""
        return not self.is_expired and not self.is_used
