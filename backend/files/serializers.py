"""
Serializers for file management
"""
from rest_framework import serializers
from .models import FileUpload, FileDownload
from accounts.serializers import UserSerializer


class FileUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for file uploads
    """
    user = UserSerializer(read_only=True)
    file_size_display = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()
    
    class Meta:
        model = FileUpload
        fields = [
            'id', 'user', 'original_filename', 'file_size', 'file_size_display',
            'mime_type', 'file_extension', 'scope', 'downloads', 'is_encrypted',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'file_size', 'downloads', 'is_encrypted', 'created_at', 'updated_at']
    
    def get_file_size_display(self, obj):
        """Get human-readable file size"""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    
    def get_file_extension(self, obj):
        """Get file extension"""
        return obj.get_file_extension()


class FileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating file uploads
    """
    class Meta:
        model = FileUpload
        fields = ['file', 'original_filename', 'scope']
    
    def validate_file(self, value):
        """Validate file size"""
        max_size = 100 * 1024 * 1024  # 100MB
        if value.size > max_size:
            raise serializers.ValidationError(f"File size exceeds {max_size/1024/1024}MB limit")
        return value


class FileDownloadSerializer(serializers.ModelSerializer):
    """
    Serializer for file download records
    """
    file = FileUploadSerializer(read_only=True)
    downloaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = FileDownload
        fields = ['id', 'file', 'downloaded_by', 'downloaded_at', 'download_size']
