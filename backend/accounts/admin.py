"""
Django admin configuration for User models
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserActivity


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('name', 'mobile', 'role', 'avatar', 'bio', 'is_verified', 'last_login_ip')}),
    )
    
    list_display = ['username', 'name', 'email', 'mobile', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_verified', 'created_at']
    search_fields = ['username', 'name', 'email', 'mobile']
    ordering = ['-created_at']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin interface for UserActivity model"""
    
    list_display = ['user', 'action', 'ip_address', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'user__email', 'ip_address']
    readonly_fields = ['user', 'action', 'ip_address', 'user_agent', 'timestamp']
    ordering = ['-timestamp']
