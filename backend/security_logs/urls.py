"""
URL routes for security logging (Transparent Mode)
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    USBActivityLogViewSet, SecurityAlertViewSet, SystemLogViewSet,
    AuthorizedUSBViewSet, SecurityEventViewSet, AdminSecurityDashboard
)

router = DefaultRouter()
router.register(r'usb-log', USBActivityLogViewSet, basename='usb_activity_log')
router.register(r'alerts', SecurityAlertViewSet, basename='security_alert')
router.register(r'system-logs', SystemLogViewSet, basename='system_log')
router.register(r'authorized-usb', AuthorizedUSBViewSet, basename='authorized_usb')
router.register(r'event', SecurityEventViewSet, basename='security_event')

urlpatterns = [
    path('admin/dashboard/', AdminSecurityDashboard.as_view(), name='admin_security_dashboard'),
] + router.urls
