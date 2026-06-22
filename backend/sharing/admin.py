"""
Django admin configuration for File Sharing models
"""
from django.contrib import admin
from .models import FileShare, ShareNotification


@admin.register(FileShare)
class FileShareAdmin(admin.ModelAdmin):
    """Admin interface for FileShare model"""
    
    list_display = ['file', 'sender', 'receiver', 'status', 'is_verified', 'otp_attempts', 'created_at']
    list_filter = ['status', 'is_verified', 'created_at']
    search_fields = ['file__original_filename', 'sender__username', 'receiver__username']
    readonly_fields = ['otp', 'otp_created_at', 'otp_expires_at', 'verified_at', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Share Info', {'fields': ('file', 'sender', 'receiver')}),
        ('OTP', {'fields': ('otp', 'otp_attempts', 'max_otp_attempts', 'otp_created_at', 'otp_expires_at')}),
        ('Status', {'fields': ('status', 'is_verified', 'verified_at', 'message')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ShareNotification)
class ShareNotificationAdmin(admin.ModelAdmin):
    """Admin interface for ShareNotification model"""
    
    list_display = ['file_share', 'receiver', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['receiver__username', 'file_share__file__original_filename']
    readonly_fields = ['file_share', 'receiver', 'created_at']
