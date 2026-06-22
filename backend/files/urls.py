"""
URL routes for file management
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FileUploadViewSet, FileSearchView, AdminFileListView

router = DefaultRouter()
router.register(r'', FileUploadViewSet, basename='file')

urlpatterns = [
    path('search/', FileSearchView.as_view(), name='file_search'),
    path('admin/all/', AdminFileListView.as_view(), name='admin_files'),
]

urlpatterns += router.urls
