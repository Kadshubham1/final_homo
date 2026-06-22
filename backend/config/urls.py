"""
URL Configuration for Homomorphic Secure File Sharing System
Main URL router
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from security_logs.views import LiveEventsAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/files/', include('files.urls')),
    path('api/sharing/', include('sharing.urls')),
    path('api/security/', include('security_logs.urls')),
    path('api/admin/live-events/', LiveEventsAPIView.as_view(), name='live-events'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "🔐 Homomorphic Secure File Sharing - Admin Panel"
admin.site.site_title = "SFS Admin"
