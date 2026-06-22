"""
Utility functions for authentication
"""
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def generate_otp(length=6):
    """
    Generate a random 6-digit OTP
    
    Args:
        length (int): Length of OTP to generate
    
    Returns:
        str: Random OTP code
    """
    digits = string.digits
    otp = ''.join(random.choice(digits) for _ in range(length))
    return otp


def send_otp_email(email, otp_code):
    """
    Send OTP to user's email
    
    Args:
        email (str): User's email address
        otp_code (str): OTP code to send
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        subject = "Your Email Verification OTP - Secure File Sharing"
        
        # Email content
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 40px;
                    border-radius: 8px;
                }}
                .header {{
                    text-align: center;
                    color: #333;
                    margin-bottom: 30px;
                }}
                .otp-box {{
                    background-color: #f0f0f0;
                    text-align: center;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .otp-code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #2563eb;
                    letter-spacing: 4px;
                }}
                .footer {{
                    color: #666;
                    font-size: 12px;
                    margin-top: 20px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Email Verification</h1>
                    <p>Secure File Sharing System</p>
                </div>
                
                <p>Hello,</p>
                <p>Thank you for signing up! To verify your email address, please use the following OTP code:</p>
                
                <div class="otp-box">
                    <div class="otp-code">{otp_code}</div>
                </div>
                
                <p>This OTP is valid for 5 minutes. Do not share it with anyone.</p>
                <p>If you did not sign up for this account, please ignore this email.</p>
                
                <div class="footer">
                    <p>© 2026 Homomorphic Secure File Sharing System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=f"Your OTP code is: {otp_code}\n\nThis code is valid for 5 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"OTP email sent to {email}")
        return True
        
    except Exception as e:
        print(f"Error sending OTP email: {str(e)}")
        return False


def send_verification_success_email(email, name="User"):
    """
    Send verification success email to user
    
    Args:
        email (str): User's email address
        name (str): User's name
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        subject = "Email Verified Successfully - Secure File Sharing"
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 40px;
                    border-radius: 8px;
                }}
                .header {{
                    text-align: center;
                    color: #333;
                    margin-bottom: 30px;
                }}
                .success-message {{
                    background-color: #d4edda;
                    color: #155724;
                    padding: 15px;
                    border-radius: 5px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .footer {{
                    color: #666;
                    font-size: 12px;
                    margin-top: 20px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Email Verified Successfully!</h1>
                </div>
                
                <p>Hello {name},</p>
                <div class="success-message">
                    <h2>✓ Your email has been verified</h2>
                </div>
                
                <p>Your account is now fully activated. You can now:</p>
                <ul>
                    <li>Upload and share files securely</li>
                    <li>Access the admin panel (if authorized)</li>
                    <li>Manage your profile and settings</li>
                </ul>
                
                <p>Welcome to the Secure File Sharing System!</p>
                
                <div class="footer">
                    <p>© 2026 Homomorphic Secure File Sharing System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        send_mail(
            subject=subject,
            message="Your email has been verified successfully. Your account is now active.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"Verification success email sent to {email}")
        return True
        
    except Exception as e:
        print(f"Error sending verification success email: {str(e)}")
        return False
