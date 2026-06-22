"""
Security logging models for USB detection and monitoring
✅ Transparent Mode: Event logging without image capture
"""
from django.db import models
from accounts.models import User
import json


class USBActivityLog(models.Model):
    """
    Transparent USB Activity Logging
    
    ✅ ETHICAL & LEGAL:
    - Event logging only (no image capture)
    - Transparent operation (user informed)
    - GDPR/CCPA compliant
    - Privacy-respecting
    
    Records USB connection/disconnection events for security audit trail.
    """
    
    ACTION_CHOICES = (
        ('USB_INSERTED', 'USB Device Inserted'),
        ('USB_REMOVED', 'USB Device Removed'),
        ('USB_ACCESSED', 'USB Device Accessed'),
    )
    
    DEVICE_TYPE_CHOICES = (
        ('usb_storage', 'USB Storage Device'),
        ('usb_phone', 'USB Mobile Device'),
        ('usb_other', 'Other USB Device'),
        ('unknown', 'Unknown Device'),
    )
    
    # User info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usb_logs')
    
    # Image capture
    image = models.ImageField(upload_to='usb_logs/', null=True, blank=True)
    
    # Action (allow 'USB Inserted' literal string as user requested)
    action = models.CharField(max_length=50)
    
    # Device info
    device_name = models.CharField(max_length=255, blank=True, db_index=True)
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPE_CHOICES, default='unknown')
    device_id = models.CharField(max_length=255, blank=True, db_index=True)
    device_path = models.CharField(max_length=500, blank=True)
    
    # System info
    hostname = models.CharField(max_length=255, blank=True)
    system_type = models.CharField(max_length=50, blank=True)  # Windows, Linux, macOS
    system_info = models.JSONField(default=dict, blank=True)  # CPU, Memory, etc. (optional)
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    connection_duration = models.IntegerField(null=True, blank=True, help_text='Duration in seconds')
    
    # Notes
    notes = models.TextField(blank=True, max_length=1000)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'USB Activity Log'
        verbose_name_plural = 'USB Activity Logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['device_id']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"[{self.action}] {self.device_name} - {self.user.username} ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
    
    @classmethod
    def log_usb_event(cls, user, action, device_name='', device_id='', device_path='', **kwargs):
        """
        Create a new USB activity log entry
        
        Args:
            user: User object
            action: 'USB_INSERTED' or 'USB_REMOVED'
            device_name: Name of USB device
            device_id: Device ID/Serial
            device_path: Mount path
            **kwargs: Additional fields (hostname, system_type, notes, etc.)
        
        Returns:
            USBActivityLog instance
        """
        log = cls.objects.create(
            user=user,
            action=action,
            device_name=device_name,
            device_id=device_id,
            device_path=device_path,
            **kwargs
        )
        return log


class SecurityAlert(models.Model):
    """
    Security alerts generated from unusual activities
    """
    
    ALERT_TYPES = (
        ('usb_multiple', 'Multiple USB Devices'),
        ('unknown_device', 'Unknown Device'),
        ('high_frequency', 'High Frequency Access'),
        ('unauthorized_access', 'Unauthorized Access Attempt'),
        ('file_access_abnormal', 'Abnormal File Access'),
    )
    
    usb_log = models.OneToOneField(USBActivityLog, on_delete=models.CASCADE, null=True, blank=True)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_alerts')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )
    
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert_type} - {self.user.username}"


class SystemLog(models.Model):
    """
    General system activity logs
    """
    
    LOG_TYPES = (
        ('user_action', 'User Action'),
        ('file_operation', 'File Operation'),
        ('security_event', 'Security Event'),
        ('system_event', 'System Event'),
    )
    
    log_type = models.CharField(max_length=50, choices=LOG_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    action = models.CharField(max_length=255)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    is_success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['log_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.log_type} - {self.action} - {self.timestamp}"


class AuthorizedUSB(models.Model):
    """List of authorized USB devices"""
    device_name = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255, unique=True, help_text="Volume Serial Number or Hardware ID")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='authorized_usbs')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.device_name} ({self.device_id})"


class SecurityEvent(models.Model):
    """
    Advanced real-time security events
    Includes video capture and face recognition status
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    video = models.FileField(upload_to='security_videos/', null=True, blank=True)
    image = models.ImageField(upload_to='security_thumbnails/', null=True, blank=True)
    action = models.CharField(max_length=100, default="USB Inserted")
    device_name = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255, blank=True)
    is_authorized = models.BooleanField(default=False)
    face_status = models.CharField(max_length=50, default="Unknown", help_text="Recognized, Unknown, or No Face")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action} - {self.device_name} ({self.face_status}) at {self.timestamp}"
