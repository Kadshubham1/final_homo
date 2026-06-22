#!/usr/bin/env python
"""
Create a superuser/admin account for testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import UserActivity

User = get_user_model()

def create_admin():
    # Check if admin exists
    admin_email = 'admin@central.com'
    admin_password = 'admin123'
    
    # Delete existing admin if exists
    try:
        existing_admin = User.objects.get(email=admin_email)
        print(f"[*] Deleting existing admin user: {admin_email}")
        existing_admin.delete()
    except User.DoesNotExist:
        print(f"[*] No existing admin user found")
    
    # Create new admin user
    try:
        admin = User.objects.create_superuser(
            username='admin',
            email=admin_email,
            password=admin_password,
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        print(f"[+] Admin user created successfully!")
        print(f"    Email: {admin_email}")
        print(f"    Password: {admin_password}")
        print(f"    Username: admin")
        print(f"    Role: {admin.role}")
        
    except Exception as e:
        print(f"[-] Error creating admin user: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("Creating Admin User for Testing")
    print("=" * 60)
    create_admin()
    print("=" * 60)
