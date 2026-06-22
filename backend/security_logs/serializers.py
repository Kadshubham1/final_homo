"""
Serializers for security logging (Transparent Mode)
✅ Event logging only - No image capture
"""
from rest_framework import serializers
from .models import USBActivityLog, SecurityAlert, SystemLog
from accounts.serializers import UserSerializer


class USBActivityLogSerializer(serializers.ModelSerializer):
    """
    Serializer for USB Activity Logs
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    
    class Meta:
        model = USBActivityLog
        fields = [
            'id', 'user', 'user_id', 'action', 'image', 'device_name', 'device_type', 
            'device_id', 'device_path', 'hostname', 'system_type', 'system_info',
            'timestamp', 'connection_duration', 'notes'
        ]
        read_only_fields = ['id', 'user', 'timestamp']


class USBEventCreateSerializer(serializers.Serializer):
    """
    Serializer for logging USB events from client
    """
    action = serializers.CharField(max_length=50)
    user_id = serializers.IntegerField(required=False)
    image = serializers.ImageField(required=False, allow_null=True)
    device_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    device_path = serializers.CharField(max_length=500, required=False, allow_blank=True)
    device_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    hostname = serializers.CharField(max_length=255, required=False, allow_blank=True)
    system_type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)


class SecurityAlertSerializer(serializers.ModelSerializer):
    """
    Serializer for Security Alerts
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = SecurityAlert
        fields = [
            'id', 'alert_type', 'user', 'title', 'description',
            'severity', 'is_resolved', 'created_at', 'resolved_at', 'resolution_notes'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class SystemLogSerializer(serializers.ModelSerializer):
    """
    Serializer for System Logs
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = SystemLog
        fields = [
            'id', 'log_type', 'user', 'action', 'details', 'ip_address',
            'is_success', 'error_message', 'timestamp'
        ]
        read_only_fields = ['id', 'user', 'timestamp']


from .models import AuthorizedUSB, SecurityEvent

class AuthorizedUSBSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizedUSB
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class SecurityEventSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    video_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SecurityEvent
        fields = '__all__'
        read_only_fields = ['id', 'user', 'timestamp']
        
    def get_video_url(self, obj):
        if obj.video:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video.url)
            return obj.video.url
        return None
        
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class SecurityEventCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False, allow_null=True)
    video = serializers.FileField(required=False, allow_null=True)
    image = serializers.ImageField(required=False, allow_null=True)
    action = serializers.CharField(max_length=100)
    device_name = serializers.CharField(max_length=255)
    device_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_authorized = serializers.BooleanField(default=False)
    face_status = serializers.CharField(max_length=50, default='Unknown')
