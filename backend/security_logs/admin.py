"""
Django admin configuration for Security Log models (Transparent Mode)
✅ Event logging - No image data
"""
from django.contrib import admin
from .models import USBActivityLog, SecurityAlert, SystemLog


@admin.register(USBActivityLog)
class USBActivityLogAdmin(admin.ModelAdmin):
    """
    Admin interface for USB Activity Logs
    Transparent mode - shows event data only
    """
    
    list_display = ['id', 'user', 'action', 'device_name', 'device_path', 'timestamp']
    list_filter = ['action', 'device_type', 'timestamp']
    search_fields = ['user__username', 'device_name', 'device_id', 'device_path']
    readonly_fields = ['user', 'timestamp']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Action', {'fields': ('action',)}),
        ('Device Info', {
            'fields': ('device_name', 'device_type', 'device_id', 'device_path'),
            'description': '✅ Device information only - no personal data captured'
        }),
        ('System Info', {'fields': ('hostname', 'system_type', 'system_info')}),
        ('Timestamp', {'fields': ('timestamp', 'connection_duration')}),
        ('Notes', {'fields': ('notes',)}),
    )
    
    def has_add_permission(self, request):
        """Admin cannot manually add USB logs - only via API"""
        return False


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    """Admin interface for Security Alerts"""
    
    list_display = ['id', 'alert_type', 'user', 'severity', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_resolved', 'created_at']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['created_at', 'resolved_at', 'usb_log']
    ordering = ['-created_at']


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    """Admin interface for System Logs"""
    
    list_display = ['log_type', 'user', 'action', 'is_success', 'timestamp']
    list_filter = ['log_type', 'is_success', 'timestamp']
    search_fields = ['user__username', 'action', 'ip_address']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
