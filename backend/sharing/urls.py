"""
URL routes for file sharing
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FileShareViewSet, ShareNotificationViewSet, AdminShareListView

router = DefaultRouter()
router.register(r'', FileShareViewSet, basename='fileshare')

urlpatterns = [
    path('admin/all/', AdminShareListView.as_view(), name='admin_shares'),
    path('notifications/', ShareNotificationViewSet.as_view(), name='notifications'),
]

urlpatterns += router.urls
