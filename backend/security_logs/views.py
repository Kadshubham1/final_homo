"""
Views for security logging and USB detection (Transparent Mode)
✅ Event logging only - No image capture
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from accounts.permissions import IsAdminUser
from accounts.models import User
from django_filters import rest_framework as filters
from django.utils import timezone
from datetime import timedelta
from .models import USBActivityLog, SecurityAlert, SystemLog
from .serializers import (
    USBActivityLogSerializer, USBEventCreateSerializer,
    SecurityAlertSerializer, SystemLogSerializer
)


class USBActivityLogViewSet(viewsets.ModelViewSet):
    """
    Transparent USB Activity Logging
    ✅ Event logging only (no image capture)
    
    Endpoints:
    - GET /api/security/usb-log/              List logs (admin) or user's logs
    - POST /api/security/usb-log/             Log USB event (from monitor)
    - GET /api/security/usb-log/{id}/         Get log details
    - DELETE /api/security/usb-log/{id}/      Delete log entry
    """
    
    serializer_class = USBActivityLogSerializer
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action', 'device_type', 'user']
    search_fields = ['device_name', 'device_id', 'device_path', 'hostname']
    ordering_fields = ['timestamp', 'device_name', 'action']
    ordering = ['-timestamp']
    
    def get_permissions(self):
        """Allow unauthenticated access for creating logs from standalone script"""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """
        Admin users see all logs.
        Regular users see only their own logs.
        """
        user = self.request.user
        
        # Unauthenticated users (if any accidentally reach here) get empty queryset
        if getattr(user, 'is_anonymous', True):
            return USBActivityLog.objects.none()
            
        # Check if admin (role-based)
        if hasattr(user, 'role') and user.role == 'admin':
            return USBActivityLog.objects.all()
        
        # Otherwise, only their own logs
        return USBActivityLog.objects.filter(user=user)
    
    def get_serializer_class(self):
        """Use different serializer for create"""
        if self.action == 'create' or self.action == 'log_event':
            return USBEventCreateSerializer
        return USBActivityLogSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new USB activity log
        POST /api/security/usb-log/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            image = request.FILES.get('image')
            if not image:
                image = serializer.validated_data.get('image', None)
                
            # Determine user
            user = request.user if request.user.is_authenticated else None
            # Extract user_id directly from request.data or serializer
            user_id = request.data.get('user_id') or serializer.validated_data.get('user_id')
            
            if not user and user_id:
                user = User.objects.filter(id=user_id).first()
                
            if not user:
                # Fallback to first superuser or just first user if script didn't send user_id correctly
                user = User.objects.filter(is_superuser=True).first() or User.objects.first()
                
            if not user:
                return Response(
                    {'error': 'No valid user found to attach this log to.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create log entry safely ensuring all fields map
            log_action = request.data.get('action', 'USB Inserted')
            log_device_name = request.data.get('device_name', serializer.validated_data.get('device_name', ''))
            
            log = USBActivityLog.objects.create(
                user=user,
                action=log_action,
                image=image,
                device_name=log_device_name,
                device_path=serializer.validated_data.get('device_path', ''),
                device_id=serializer.validated_data.get('device_id', ''),
                hostname=serializer.validated_data.get('hostname', ''),
                system_type=serializer.validated_data.get('system_type', ''),
                system_info=serializer.validated_data.get('system_info', {}),
                notes=serializer.validated_data.get('notes', '')
            )
            
            return Response(
                {
                    'message': f'✅ {log.action} logged successfully',
                    'id': log.id,
                    'timestamp': log.timestamp.isoformat()
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Failed to log event: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get USB activity summary statistics
        
        Returns:
        - total_events: Total USB events logged
        - insertions: USB insert events
        - removals: USB remove events  
        - unique_devices: Number of unique devices
        """
        queryset = self.get_queryset()
        
        total_events = queryset.count()
        insertions = queryset.filter(action='USB_INSERTED').count()
        removals = queryset.filter(action='USB_REMOVED').count()
        unique_devices = queryset.values('device_id').distinct().count()
        
        # Get recent events (last 24 hours)
        from django.utils import timezone
        from datetime import timedelta
        recent_events = queryset.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        return Response({
            'total_events': total_events,
            'insertions': insertions,
            'removals': removals,
            'unique_devices': unique_devices,
            'recent_events_24h': recent_events,
            'mode': 'transparent'  # Indicate this is transparent logging mode
        })


class SecurityAlertViewSet(viewsets.ModelViewSet):
    """
    Security Alerts endpoints
    
    Alerts can be generated from USB activities for administrative review.
    """
    serializer_class = SecurityAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Admin users see all alerts.
        Regular users see only their own alerts.
        """
        user = self.request.user
        
        # Check if admin
        if hasattr(user, 'role') and user.role == 'admin':
            return SecurityAlert.objects.all()
        
        return SecurityAlert.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def unresolved(self, request):
        """Get unresolved alerts"""
        alerts = self.get_queryset().filter(is_resolved=False)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve alert"""
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.resolution_notes = request.data.get('notes', '')
        alert.save()
        return Response(
            {
                'message': '✅ Alert resolved',
                'alert': SecurityAlertSerializer(alert).data
            }
        )


class SystemLogViewSet(viewsets.ModelViewSet):
    """
    System activity logs for general system operations
    """
    serializer_class = SystemLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['log_type', 'is_success']
    
    def get_queryset(self):
        """
        Admin users see all logs.
        Regular users see only their own logs.
        """
        user = self.request.user
        
        # Check if admin
        if hasattr(user, 'role') and user.role == 'admin':
            return SystemLog.objects.all()
        
        return SystemLog.objects.filter(user=user)


class AdminSecurityDashboard(generics.GenericAPIView):
    """
    Admin Security Dashboard
    GET /api/security/admin/dashboard/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get security dashboard stats"""
        usb_logs = USBActivityLog.objects.all()
        alerts = SecurityAlert.objects.all()
        system_logs = SystemLog.objects.all()
        security_events = SecurityEvent.objects.all()
        
        # USB Stats
        usb_stats = {
            'total_events': usb_logs.count(),
            'insertions': usb_logs.filter(action='USB_INSERTED').count(),
            'removals': usb_logs.filter(action='USB_REMOVED').count(),
            'unauthorized_devices': SecurityEvent.objects.filter(is_authorized=False).count(),
            'high_risk_events': SecurityEvent.objects.filter(is_authorized=False).count(),
            'suspicious_events': SecurityEvent.objects.filter(face_status='Unknown').count(),
        }
        
        # Alert Stats
        alert_stats = {
            'total_alerts': alerts.count(),
            'unresolved_alerts': alerts.filter(is_resolved=False).count(),
            'high_severity': alerts.filter(severity='high').count(),
        }
        
        # System Stats
        system_stats = {
            'total_logs': system_logs.count(),
            'failed_operations': system_logs.filter(is_success=False).count(),
        }
        
        # Security Event Stats
        security_stats = {
            'total_events': security_events.count(),
            'unknown_faces': security_events.filter(face_status='Unknown').count(),
            'recognized_faces': security_events.exclude(face_status='Unknown').count(),
        }
        
        return Response({
            'usb_stats': usb_stats,
            'alert_stats': alert_stats,
            'system_stats': system_stats,
            'security_stats': security_stats
        })


from .models import AuthorizedUSB, SecurityEvent
from .serializers import AuthorizedUSBSerializer, SecurityEventSerializer, SecurityEventCreateSerializer
from django.core.mail import send_mail
from django.conf import settings

class AuthorizedUSBViewSet(viewsets.ModelViewSet):
    """
    Manage authorized USB devices
    """
    serializer_class = AuthorizedUSBSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AuthorizedUSB.objects.all()

class SecurityEventViewSet(viewsets.ModelViewSet):
    """
    Advanced security logging with video
    POST /api/security/event/
    GET /api/security/event/ (to replace live-events logic)
    """
    serializer_class = SecurityEventSerializer
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_authorized', 'face_status']
    search_fields = ['device_name', 'device_id']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
        
    def get_queryset(self):
        return SecurityEvent.objects.all()
        
    def get_serializer_class(self):
        if self.action == 'create':
            return SecurityEventCreateSerializer
        return SecurityEventSerializer
        
    def create(self, request, *args, **kwargs):
        """Create a new security event from USB monitor"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            video = request.FILES.get('video')
            image = request.FILES.get('image')
            
            user_id = request.data.get('user_id')
            user = User.objects.filter(id=user_id).first() if user_id else None
            if not user:
                user = User.objects.filter(is_superuser=True).first() or User.objects.first()
                
            device_id = request.data.get('device_id', '')
            action = request.data.get('action', 'USB Inserted')
            device_name = request.data.get('device_name', '')
            face_status = request.data.get('face_status', 'Unknown')
            
            # Backend authorization evaluation
            is_authorized = AuthorizedUSB.objects.filter(device_id=device_id).exists() if device_id else False
            
            print(f"[*] Creating security event:")
            print(f"    - Action: {action}")
            print(f"    - Device: {device_name} (ID: {device_id})")
            print(f"    - User: {user.username if user else 'System'}")
            print(f"    - Face Status: {face_status}")
            print(f"    - Authorized: {is_authorized}")
            if image:
                print(f"    - Image attached: {image.name}")
            
            # Create event
            event = SecurityEvent.objects.create(
                user=user,
                video=video,
                image=image,
                action=action,
                device_name=device_name,
                device_id=device_id,
                is_authorized=is_authorized,
                face_status=face_status
            )
            
            print(f"[+] Security event saved successfully with ID: {event.id}")
            
            # Alert logic
            if not is_authorized or event.face_status == 'Unknown':
                print(f"[!] ALERT TRIGGERED: Unauthorized USB or Unknown face detected.")
                try:
                    send_mail(
                        subject='⚠️ CRITICAL: Security Breach Detected (USB/Camera)',
                        message=f'Unauthorized USB detected or unknown person captured!\n\nDevice: {event.device_name}\nFace Status: {event.face_status}\nTime: {event.timestamp}\n\nPlease check admin dashboard.',
                        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'admin@sfs.com',
                        recipient_list=[admin_user.email for admin_user in User.objects.filter(is_superuser=True) if admin_user.email],
                        fail_silently=True,
                    )
                    print("[+] Alert email sent to admins")
                except Exception as e:
                    print(f"[-] Could not send email: {e}")
            
            return Response({
                'message': 'Security event logged successfully',
                'id': event.id,
                'timestamp': event.timestamp.isoformat()
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            print(f"[-] Error creating security event: {e}")
            traceback.print_exc()
            return Response(
                {'error': f'Failed to log event: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

from rest_framework.views import APIView

class LiveEventsAPIView(APIView):
    """
    GET /api/admin/live-events/
    Returns latest events without pagination for the live React dashboard.
    """
    permission_classes = [AllowAny] # Allow for easy testing, or use IsAuthenticated based on requirements

    def get(self, request):
        events = SecurityEvent.objects.all().order_by('-timestamp')[:50]
        serializer = SecurityEventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)
