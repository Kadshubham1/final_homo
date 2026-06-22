@echo off
REM ==========================================
REM EMAIL SETUP - Run this to configure Gmail
REM ==========================================

echo.
echo ======================================
echo  SECURE FILE SHARING - EMAIL SETUP
echo ======================================
echo.

REM First, remind user to get Gmail App Password
echo STEP 1: Get Gmail App Password
echo ========================================
echo 1. Go to: https://myaccount.google.com/apppasswords
echo 2. Select: Mail + Windows Computer
echo 3. Copy the 16-character password
echo.

setlocal enabledelayedexpansion

REM Get Gmail email from user
set /p EMAIL_USER="Enter your Gmail address (e.g., name@gmail.com): "
REM Get Gmail app password from user
set /p EMAIL_PASS="Enter your Gmail App Password (16 characters): "

echo.
echo ========================================
echo Setting environment variables...
echo ========================================

REM Set environment variables
set EMAIL_HOST_USER=%EMAIL_USER%
set EMAIL_HOST_PASSWORD=%EMAIL_PASS%
set EMAIL_HOST=smtp.gmail.com
set EMAIL_PORT=587
set EMAIL_USE_TLS=True

echo ✓ EMAIL_HOST_USER = %EMAIL_HOST_USER%
echo ✓ EMAIL_HOST_PASSWORD = (hidden)
echo ✓ EMAIL_HOST = smtp.gmail.com
echo ✓ EMAIL_PORT = 587
echo ✓ EMAIL_USE_TLS = True

echo.
echo ========================================
echo Starting Django with email support...
echo ========================================
echo.

REM Change to backend directory and start Django
cd backend
python manage.py runserver

REM Keep window open
pause
