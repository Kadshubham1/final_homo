"""
URL routes for authentication endpoints
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, MeView,
    ChangePasswordView, UserListView, UserDetailView, AdminStatsView,
    SignupWithOTPView, VerifyOTPView, ResendOTPView
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # OTP-based signup
    path('signup-otp/', SignupWithOTPView.as_view(), name='signup_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    
    # User Profile
    path('me/', MeView.as_view(), name='user_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Admin
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin_stats'),
]
