"""
Custom permission classes for the accounts app
"""
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Custom permission class to check if user role is 'admin'
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Permission to allow users to edit their own objects or admins to edit any
    """
    def has_object_permission(self, request, view, obj):
        # Allow if user is admin
        if request.user.role == 'admin':
            return True
        # Allow if user is the owner
        return obj.user == request.user or obj.owner == request.user
