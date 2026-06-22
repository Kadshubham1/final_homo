"""
Views for file sharing with OTP verification
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from accounts.permissions import IsAdminUser
from .models import FileShare, ShareNotification
from .serializers import (
    FileShareSerializer, FileShareCreateSerializer,
    OTPVerificationSerializer, ResendOTPSerializer,
    ShareNotificationSerializer
)
from files.models import FileUpload
from accounts.models import User


class FileShareViewSet(viewsets.ModelViewSet):
    """
    File Sharing endpoints with OTP verification
    """
    serializer_class = FileShareSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get shares for current user (sent or received)"""
        user = self.request.user
        return FileShare.objects.filter(Q(sender=user) | Q(receiver=user))
    
    def get_serializer_class(self):
        """Use different serializer for create"""
        if self.action == 'create':
            return FileShareCreateSerializer
        return FileShareSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Share file with another user
        POST /api/sharing/
        
        Creates a new file share and generates OTP
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file_id = serializer.validated_data['file_id']
        receiver_id = serializer.validated_data['receiver_id']
        message = serializer.validated_data.get('message', '')
        
        # Get file
        file_obj = get_object_or_404(FileUpload, id=file_id)
        
        # Check if user owns the file
        if file_obj.user != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You can only share your own files.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get receiver
        receiver = get_object_or_404(User, id=receiver_id)
        
        # Check if already shared
        existing_share = FileShare.objects.filter(
            file=file_obj,
            sender=request.user,
            receiver=receiver
        ).first()
        
        if existing_share:
            if existing_share.is_verified:
                return Response(
                    {'error': 'File already shared with this user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # Return existing share
                return Response(
                    {
                        'message': 'Share request already pending for this user.',
                        'share': FileShareSerializer(existing_share).data,
                        'otp': existing_share.otp  # Show OTP for testing
                    },
                    status=status.HTTP_200_OK
                )
        
        # Create new share
        file_share = FileShare.objects.create(
            file=file_obj,
            sender=request.user,
            receiver=receiver,
            message=message
        )
        
        # Create notification
        ShareNotification.objects.create(
            file_share=file_share,
            receiver=receiver
        )
        
        return Response(
            {
                'message': f'File shared with {receiver.name or receiver.username}. OTP sent!',
                'share': FileShareSerializer(file_share).data,
                'otp': file_share.otp  # For development/testing - hide in production
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Get files shared by user"""
        shares = FileShare.objects.filter(sender=request.user)
        serializer = FileShareSerializer(shares, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def received(self, request):
        """Get files shared with user"""
        shares = FileShare.objects.filter(receiver=request.user)
        serializer = FileShareSerializer(shares, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        """
        Verify OTP for file sharing
        POST /api/sharing/verify_otp/
        
        Body: {"share_id": 1, "otp": "123456"}
        """
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        share_id = serializer.validated_data['share_id']
        otp = serializer.validated_data['otp']
        
        # Get share
        file_share = get_object_or_404(FileShare, id=share_id)
        
        # Check if user is receiver
        if file_share.receiver != request.user:
            return Response(
                {'error': 'You are not the receiver of this file share.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verify OTP
        result = file_share.verify_otp(otp)
        
        return Response(
            {
                'success': result['success'],
                'message': result['message'],
                'share': FileShareSerializer(file_share).data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def resend_otp(self, request):
        """
        Resend OTP
        POST /api/sharing/resend_otp/
        
        Body: {"share_id": 1}
        """
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        share_id = serializer.validated_data['share_id']
        
        # Get share
        file_share = get_object_or_404(FileShare, id=share_id)
        
        # Check permissions
        if file_share.receiver != request.user and file_share.sender != request.user:
            return Response(
                {'error': 'You do not have permission to resend OTP.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Resend OTP
        result = file_share.resend_otp()
        
        if result['success']:
            return Response(
                {
                    'success': True,
                    'message': result['message'],
                    'otp': result['otp'],  # For testing
                    'share': FileShareSerializer(file_share).data
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'success': False,
                    'message': result['message']
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ShareNotificationViewSet(generics.ListAPIView):
    """
    View share notifications
    GET /api/sharing/notifications/
    """
    serializer_class = ShareNotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for current user"""
        return ShareNotification.objects.filter(receiver=self.request.user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Marked as read.'})


class AdminShareListView(generics.ListAPIView):
    """
    Admin: View all file shares
    GET /api/sharing/admin/all/
    """
    queryset = FileShare.objects.all()
    serializer_class = FileShareSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
