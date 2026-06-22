"""
Serializers for file sharing with OTP
"""
from rest_framework import serializers
from .models import FileShare, ShareNotification
from accounts.serializers import UserSerializer
from files.serializers import FileUploadSerializer


class FileShareSerializer(serializers.ModelSerializer):
    """
    Serializer for file sharing
    """
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    file = FileUploadSerializer(read_only=True)
    otp_time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = FileShare
        fields = [
            'id', 'file', 'sender', 'receiver', 'status', 'is_verified',
            'otp_attempts', 'max_otp_attempts', 'otp_expires_at', 'otp_time_remaining',
            'message', 'created_at'
        ]
        read_only_fields = [
            'id', 'file', 'sender', 'receiver', 'status', 'is_verified',
            'otp_attempts', 'otp_expires_at', 'created_at'
        ]
    
    def get_otp_time_remaining(self, obj):
        """Get time remaining for OTP expiry"""
        from django.utils import timezone
        import math
        
        if obj.is_otp_expired():
            return 0
        
        remaining = obj.otp_expires_at - timezone.now()
        minutes = math.ceil(remaining.total_seconds() / 60)
        return max(0, minutes)


class FileShareCreateSerializer(serializers.Serializer):
    """
    Serializer for creating file share
    """
    file_id = serializers.IntegerField()
    receiver_id = serializers.IntegerField()
    message = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate_file_id(self, value):
        """Validate file exists"""
        from files.models import FileUpload
        try:
            FileUpload.objects.get(id=value)
        except FileUpload.DoesNotExist:
            raise serializers.ValidationError("File not found.")
        return value


class OTPVerificationSerializer(serializers.Serializer):
    """
    Serializer for OTP verification
    """
    share_id = serializers.IntegerField()
    otp = serializers.CharField(max_length=10, min_length=6)


class ResendOTPSerializer(serializers.Serializer):
    """
    Serializer for resending OTP
    """
    share_id = serializers.IntegerField()


class ShareNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for share notifications
    """
    file_share = FileShareSerializer(read_only=True)
    
    class Meta:
        model = ShareNotification
        fields = ['id', 'file_share', 'is_read', 'created_at']
