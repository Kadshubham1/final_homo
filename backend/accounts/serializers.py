"""
Serializers for user authentication and registration
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, UserActivity, OTP


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    Used for displaying user information
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'mobile', 'role', 'avatar', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed user serializer with all information
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'name', 'email', 'mobile', 'role',
            'avatar', 'bio', 'is_verified', 'created_at', 'last_login_ip'
        ]
        read_only_fields = ['id', 'created_at', 'last_login_ip']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    Validates and creates new user account
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'mobile', 'password', 'password2']
    
    def validate_email(self, value):
        email = value.lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('Email already exists.')
        return email
    
    def validate(self, attrs):
        """Validate password match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        
        if User.objects.filter(username__iexact=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'Username already exists.'})
        
        return attrs
    
    def create(self, validated_data):
        """Create new user"""
        user = User.objects.create_user(
            username=validated_data['username'].strip(),
            email=validated_data['email'].lower().strip(),
            name=validated_data.get('name', '').strip(),
            mobile=validated_data.get('mobile', '').strip(),
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    Validates credentials and returns JWT tokens
    """
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Authenticate user by username or email"""
        username_or_email = attrs['username'].strip()
        password = attrs['password']
        user = authenticate(username=username_or_email, password=password)
        
        if not user and '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        
        if not user:
            raise serializers.ValidationError({'error': 'Invalid credentials.'})
        
        attrs['user'] = user
        return attrs


class TokenSerializer(serializers.Serializer):
    """
    Response serializer for JWT tokens
    """
    refresh = serializers.CharField()
    access = serializers.CharField()
    user = UserSerializer()


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for user activity tracking
    """
    class Meta:
        model = UserActivity
        fields = ['id', 'user', 'action', 'ip_address', 'timestamp']


class SignupWithOTPSerializer(serializers.Serializer):
    """
    Serializer for user signup with OTP verification
    Validates email and password, then generates OTP
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value.lower()
    
    def validate(self, attrs):
        """Validate password match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs
    
    def create(self, validated_data):
        """Create user and generate OTP"""
        from .utils import generate_otp, send_otp_email
        from django.utils import timezone
        from datetime import timedelta
        
        # Create user (not verified initially)
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],  # Use email as username
            name=validated_data.get('name', ''),
            password=validated_data['password'],
            is_verified=False
        )
        
        # Generate OTP
        otp_code = generate_otp()
        
        # Create or update OTP record
        otp, _ = OTP.objects.update_or_create(
            user=user,
            defaults={
                'otp_code': otp_code,
                'expires_at': timezone.now() + timedelta(minutes=5),
                'attempts': 0,
                'is_used': False
            }
        )
        
        # Send OTP via email
        send_otp_email(user.email, otp_code)
        
        return user


class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for OTP verification
    Validates OTP and marks user as verified
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    
    def validate(self, attrs):
        """Validate OTP and user"""
        email = attrs['email'].lower()
        otp_code = attrs['otp']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'No account found with this email.'})
        
        try:
            otp = OTP.objects.get(user=user)
        except OTP.DoesNotExist:
            raise serializers.ValidationError({'otp': 'No OTP found. Please request a new one.'})
        
        # Check if OTP is expired
        if otp.is_expired:
            raise serializers.ValidationError({'otp': 'OTP has expired. Please request a new one.'})
        
        # Check if OTP is already used
        if otp.is_used:
            raise serializers.ValidationError({'otp': 'OTP has already been used.'})
        
        # Check if OTP matches
        if otp.otp_code != otp_code:
            otp.attempts += 1
            otp.save()
            
            if otp.attempts >= 3:
                otp.delete()
                raise serializers.ValidationError({'otp': 'Too many failed attempts. Please request a new OTP.'})
            
            raise serializers.ValidationError({'otp': 'Invalid OTP. Please try again.'})
        
        attrs['user'] = user
        attrs['otp'] = otp
        return attrs


class ResendOTPSerializer(serializers.Serializer):
    """
    Serializer for resending OTP
    Implements rate limiting (30 second cooldown)
    """
    email = serializers.EmailField()
    
    def validate(self, attrs):
        """Validate email and check rate limit"""
        from .utils import check_otp_rate_limit
        from django.core.cache import cache
        
        email = attrs['email'].lower()
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'No account found with this email.'})
        
        # Check rate limiting (30 second cooldown)
        cache_key = f"otp_resend_{user.id}"
        if cache.get(cache_key):
            raise serializers.ValidationError({'error': 'Please wait 30 seconds before requesting a new OTP.'})
        
        attrs['user'] = user
        return attrs
    
    def create(self, validated_data):
        """Generate new OTP and send email"""
        from .utils import generate_otp, send_otp_email
        from django.utils import timezone
        from datetime import timedelta
        from django.core.cache import cache
        
        user = validated_data['user']
        
        # Generate new OTP
        otp_code = generate_otp()
        
        # Create or update OTP record
        otp, _ = OTP.objects.update_or_create(
            user=user,
            defaults={
                'otp_code': otp_code,
                'expires_at': timezone.now() + timedelta(minutes=5),
                'attempts': 0,
                'is_used': False
            }
        )
        
        # Send OTP via email
        send_otp_email(user.email, otp_code)
        
        # Set rate limit cooldown (30 seconds)
        cache_key = f"otp_resend_{user.id}"
        cache.set(cache_key, True, 30)
        
        return otp
