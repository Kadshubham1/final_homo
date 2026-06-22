"""
Django admin configuration for File models
"""
from django.contrib import admin
from .models import FileUpload, FileDownload


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    """Admin interface for FileUpload model"""
    
    list_display = ['original_filename', 'user', 'scope', 'file_size', 'downloads', 'is_encrypted', 'created_at']
    list_filter = ['scope', 'is_encrypted', 'created_at']
    search_fields = ['original_filename', 'user__username', 'user__email']
    readonly_fields = ['file_hash', 'is_encrypted', 'downloads', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('File Info', {'fields': ('user', 'original_filename', 'file', 'encrypted_file')}),
        ('Metadata', {'fields': ('file_size', 'mime_type', 'file_hash')}),
        ('Security', {'fields': ('scope', 'is_encrypted', 'encryption_key')}),
        ('Tracking', {'fields': ('downloads', 'created_at', 'updated_at')}),
    )


@admin.register(FileDownload)
class FileDownloadAdmin(admin.ModelAdmin):
    """Admin interface for FileDownload model"""
    
    list_display = ['file', 'downloaded_by', 'downloaded_at', 'download_size']
    list_filter = ['downloaded_at']
    search_fields = ['file__original_filename', 'downloaded_by__username']
    readonly_fields = ['file', 'downloaded_by', 'downloaded_at', 'download_size']
    ordering = ['-downloaded_at']
