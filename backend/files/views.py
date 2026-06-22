"""
Views for file upload and management
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminUser
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import FileUpload, FileDownload
from .serializers import FileUploadSerializer, FileCreateSerializer, FileDownloadSerializer


class FileUploadViewSet(viewsets.ModelViewSet):
    """
    File Upload management
    GET /api/files/          - List user's files
    POST /api/files/         - Upload new file
    GET /api/files/{id}/     - Get file details
    DELETE /api/files/{id}/  - Delete file
    """
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get files accessible to user"""
        from sharing.models import FileShare
        from django.db.models import Q
        
        if self.request.user.is_admin:
            # Admins can see all files
            return FileUpload.objects.all()
        
        # Users can see:
        # 1. Their own files
        # 2. Files explicitly shared with them (verified)
        # Note: We hide public files from the "Recent Files" list for privacy 
        # unless they are the owner or admin.
        own_files = FileUpload.objects.filter(user=self.request.user)
        
        # Get file IDs from verified shares
        shared_file_ids = FileShare.objects.filter(
            receiver=self.request.user,
            is_verified=True
        ).values_list('file_id', flat=True)
        
        # Return combined own and shared files
        return FileUpload.objects.filter(
            Q(id__in=own_files) | 
            Q(id__in=shared_file_ids)
        )
    
    def get_serializer_class(self):
        """Use different serializer for create"""
        if self.action == 'create':
            return FileCreateSerializer
        return FileUploadSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Upload new file with security scanning
        POST /api/files/upload/
        """
        from .scanner import MalwareScanner

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Get validated data
            file_obj_data = serializer.validated_data
            file = file_obj_data['file']

            # SECURITY SCAN: Malware and Corruption Check
            # Requirement: Scanner must run before saving
            is_safe, error_message = MalwareScanner.scan_file(file)
            
            if not is_safe:
                # Requirement: Reject upload if malicious
                print(f"[!] MALICIOUS UPLOAD REJECTED: {file.name} - Reason: {error_message}")
                
                # Optional: Log attempt
                MalwareScanner.log_attempt(request.user, file.name, error_message)
                
                return Response(
                    {'error': f'Upload Rejected: {error_message}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create file object
            file_obj = FileUpload.objects.create(
                user=request.user,
                original_filename=file_obj_data['original_filename'],
                file=file,
                file_size=file.size,
                mime_type=file.content_type or 'application/octet-stream',
                scope=file_obj_data['scope']
            )
            
            return Response(
                {
                    'message': 'File uploaded successfully!',
                    'file': FileUploadSerializer(file_obj).data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print(f"File upload error: {str(e)}")
            return Response(
                {'error': f'File upload failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download file
        GET /api/files/{id}/download/
        
        User can download if:
        - They own the file
        - They are admin
        - File is public
        - They have a verified file share
        """
        file_obj = self.get_object()
        
        # Check permissions
        can_download = False
        
        # Owner can always download
        if file_obj.user == request.user:
            can_download = True
        
        # Admin can always download
        elif request.user.is_admin:
            can_download = True
        
        # Public files can be downloaded by anyone
        elif file_obj.scope == 'public':
            can_download = True
        
        # Check if file is shared and verified with this user
        elif file_obj.scope == 'private':
            from sharing.models import FileShare
            share = FileShare.objects.filter(
                file=file_obj,
                receiver=request.user,
                is_verified=True
            ).first()
            if share:
                can_download = True
        
        if not can_download:
            return Response(
                {'error': 'You do not have permission to download this file.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Check if encrypted file exists
            if file_obj.is_encrypted and file_obj.encrypted_file:
                # Return the encrypted content directly as requested
                file_obj.encrypted_file.seek(0)
                file_content = file_obj.encrypted_file.read()
                filename = f"{file_obj.original_filename}.enc"
                mime_type = 'text/plain' # Use text/plain so it can be viewed in browser/notepad as 'encrypted format'
            else:
                # Fallback to original if not encrypted
                file_obj.file.seek(0)
                file_content = file_obj.file.read()
                filename = file_obj.original_filename
                mime_type = file_obj.mime_type
            
            # Create download record
            FileDownload.objects.create(
                file=file_obj,
                downloaded_by=request.user,
                download_size=len(file_content)
            )
            
            # Increment download counter
            file_obj.downloads += 1
            file_obj.save(update_fields=['downloads'])
            
            # Return file
            response = FileResponse(
                [file_content] if isinstance(file_content, bytes) else file_content,
                content_type=mime_type
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        except Exception as e:
            print(f"Download error: {e}")
            return Response(
                {'error': 'Failed to download file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Delete file"""
        file_obj = self.get_object()
        
        # Check permissions
        if file_obj.user != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You do not have permission to delete this file.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Delete file from storage
        if file_obj.file:
            file_obj.file.delete()
        if file_obj.encrypted_file:
            file_obj.encrypted_file.delete()
        
        file_obj.delete()
        
        return Response(
            {'message': 'File deleted successfully!'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get file statistics"""
        queryset = self.get_queryset()
        
        total_files = queryset.count()
        total_size = sum(f.file_size for f in queryset)
        total_downloads = sum(f.downloads for f in queryset)
        public_files = queryset.filter(scope='public').count()
        
        return Response({
            'total_files': total_files,
            'total_size': total_size,
            'total_downloads': total_downloads,
            'public_files': public_files,
            'private_files': total_files - public_files
        })


class FileSearchView(generics.ListAPIView):
    """
    Search files by filename
    GET /api/files/search/?q=filename
    """
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Search files"""
        queryset = FileUpload.objects.all()
        
        if self.request.user.is_admin:
            pass
        else:
            queryset = queryset.filter(user=self.request.user)
        
        search_query = self.request.query_params.get('q')
        if search_query:
            queryset = queryset.filter(original_filename__icontains=search_query)
        
        return queryset


class AdminFileListView(generics.ListAPIView):
    """
    Admin: List all files
    GET /api/files/admin/all/
    """
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
