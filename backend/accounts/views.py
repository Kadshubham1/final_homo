"""
Views for user authentication and management
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import User, UserActivity, OTP
from .permissions import IsAdminUser
from .serializers import (
    UserSerializer, UserDetailSerializer, RegisterSerializer,
    LoginSerializer, TokenSerializer, ChangePasswordSerializer,
    UserActivitySerializer, SignupWithOTPSerializer, VerifyOTPSerializer,
    ResendOTPSerializer
)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class RegisterView(generics.CreateAPIView):
    """
    User Registration endpoint
    POST /api/auth/register/
    
    Creates a new user account
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create new user and return info"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'User registered successfully!',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """
    User Login endpoint
    POST /api/auth/login/
    
    Authenticates user and returns JWT tokens
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Login user and return JWT tokens"""
        import json
        import os
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            action='login',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # SYNC WITH HARDWARE MONITOR
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.active_user.json')
            with open(config_path, 'w') as f:
                json.dump({
                    'id': user.id,
                    'username': user.username,
                    'name': user.name or user.username,
                    'role': user.role
                }, f)
        except Exception as e:
            print(f"Warning: Failed to sync active user to monitor: {e}")
        
        return Response({
            'message': f'Welcome back, {user.name or user.username}!',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserDetailSerializer(user).data
        }, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    """
    User Logout endpoint
    POST /api/auth/logout/
    
    Logs out the user
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Logout user"""
        import os
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            action='logout',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # CLEAR HARDWARE MONITOR SYNC
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.active_user.json')
            if os.path.exists(config_path):
                os.remove(config_path)
        except Exception as e:
            print(f"Warning: Failed to clear monitor sync: {e}")
            
        return Response(
            {'message': 'Logged out successfully!'},
            status=status.HTTP_200_OK
        )


class MeView(generics.RetrieveUpdateAPIView):
    """
    Get/Update current user profile
    GET /api/auth/me/
    PUT /api/auth/me/
    
    Returns current authenticated user details
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Update user profile"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Profile updated successfully!',
            'user': serializer.data
        })


class ChangePasswordView(generics.GenericAPIView):
    """
    Change user password
    POST /api/auth/change-password/
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Change password"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        
        # Verify old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Old password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {'message': 'Password changed successfully!'},
            status=status.HTTP_200_OK
        )


class UserListView(generics.ListAPIView):
    """
    List all users
    GET /api/auth/users/
    
    Authenticated users can view all users for sharing purposes
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter users - exclude current user from list"""
        queryset = User.objects.all().exclude(id=self.request.user.id)
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset


class UserDetailView(generics.RetrieveDestroyAPIView):
    """
    Get/Delete user details (Admin only)
    GET /api/auth/users/{id}/
    DELETE /api/auth/users/{id}/
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def check_permissions(self, request):
        """Check permissions"""
        if request.method in ['DELETE']:
            self.permission_classes = [IsAdminUser]
        elif request.method == 'GET':
            # Users can view themselves, admins can view anyone
            user_id = self.kwargs.get('pk')
            if request.user.id != int(user_id) and not request.user.is_admin:
                self.permission_classes = []
        super().check_permissions(request)


class AdminStatsView(generics.GenericAPIView):
    """
    Get admin statistics
    GET /api/auth/admin/stats/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get admin statistics"""
        total_users = User.objects.count()
        total_admins = User.objects.filter(role='admin').count()
        verified_users = User.objects.filter(is_verified=True).count()
        
        return Response({
            'total_users': total_users,
            'total_admins': total_admins,
            'verified_users': verified_users,
            'regular_users': total_users - total_admins
        })


class SignupWithOTPView(generics.CreateAPIView):
    """
    User Signup with OTP verification
    POST /api/auth/signup-otp/
    
    Creates user account and sends OTP to email
    Request body:
    {
        "email": "user@example.com",
        "password": "password123",
        "password2": "password123",
        "name": "John Doe" (optional)
    }
    
    Response:
    {
        "message": "Signup successful! Check your email for OTP.",
        "user": {...}
    }
    """
    serializer_class = SignupWithOTPSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create user and send OTP"""
        from django.conf import settings
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Get the OTP for testing purposes (development only)
        otp_code = None
        if settings.DEBUG:
            try:
                otp = OTP.objects.get(user=user)
                otp_code = otp.otp_code
            except OTP.DoesNotExist:
                pass
        
        response_data = {
            'message': 'Signup successful! Check your email for OTP verification code.',
            'email': user.email,
            'user': UserSerializer(user).data
        }
        
        # Include OTP in response for development/testing
        if otp_code:
            response_data['otp_code'] = otp_code
            response_data['debug'] = 'This OTP is only visible in development mode'
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class VerifyOTPView(generics.GenericAPIView):
    """
    Verify OTP and activate account
    POST /api/auth/verify-otp/
    
    Validates OTP and marks user as verified
    Request body:
    {
        "email": "user@example.com",
        "otp": "123456"
    }
    
    Response:
    {
        "message": "Email verified successfully!",
        "user": {...},
        "refresh": "...",
        "access": "..."
    }
    """
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Verify OTP and activate user"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        otp = serializer.validated_data['otp']
        
        # Mark user as verified
        user.is_verified = True
        user.save()
        
        # Mark OTP as used
        otp.is_used = True
        otp.save()
        
        # Send verification success email
        from .utils import send_verification_success_email
        send_verification_success_email(user.email, user.name or user.username)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Email verified successfully! Your account is now active.',
            'user': UserDetailSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_200_OK)


class ResendOTPView(generics.GenericAPIView):
    """
    Resend OTP to email
    POST /api/auth/resend-otp/
    
    Regenerates OTP and sends to email (30 second rate limit)
    Request body:
    {
        "email": "user@example.com"
    }
    
    Response:
    {
        "message": "New OTP sent to your email",
        "expires_in": 300
    }
    """
    serializer_class = ResendOTPSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Resend OTP"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        otp = serializer.save()
        
        return Response({
            'message': 'New OTP sent to your email. It will expire in 5 minutes.',
            'expires_in': 300,
            'email': serializer.validated_data['email']
        }, status=status.HTTP_200_OK)
