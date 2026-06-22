@echo off
REM Starting USB Security Monitoring System
REM This script starts both Django backend and the USB monitor

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║     USB SECURITY MONITORING SYSTEM - STARTUP            ║
echo ║     All systems ready for live monitoring               ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Check if backend directory exists
if not exist "backend" (
    echo [-] Error: backend directory not found!
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Set Python executable path
set PYTHON_EXE="%cd%\.venv\Scripts\python.exe"

echo [*] Python environment ready
echo.

REM Start Django backend in new window
echo [*] Starting Django backend on http://127.0.0.1:8000...
start "Django Backend" cmd /k "cd backend && !PYTHON_EXE! manage.py runserver"

REM Wait for Django to start
echo [*] Waiting for Django to start (5 seconds)...
timeout /t 5 /nobreak

REM Test API connectivity
echo [*] Testing API connectivity...
"%PYTHON_EXE%" -c "import requests; requests.get('http://127.0.0.1:8000/api/security/event/', timeout=3)" >nul 2>&1

if !errorlevel! equ 0 (
    echo [+] Django backend is running successfully
    echo.
    
    REM Start monitor in new window
    echo [*] Starting USB Security Monitor...
    echo.
    start "USB Security Monitor" cmd /k "cd backend\scripts && !PYTHON_EXE! smart_usb_monitor.py"
    
    echo.
    echo ╔══════════════════════════════════════════════════════════╗
    echo ║ SYSTEM STARTED SUCCESSFULLY!                             ║
    echo ║                                                          ║
    echo ║ Django Backend:   http://127.0.0.1:8000                 ║
    echo ║ Monitor Status:   Running (see separate window)          ║
    echo ║ Events API:       /api/security/event/                   ║
    echo ║ Dashboard:        /api/security/admin/dashboard/         ║
    echo ║                                                          ║
    echo ║ Ready to monitor USB devices!                            ║
    echo ║ Insert a USB device to test the system.                  ║
    echo ╚══════════════════════════════════════════════════════════╝
    echo.
    
    pause
) else (
    echo [-] Failed to start Django backend
    echo Please check port 8000 is not already in use:
    echo     netstat -ano ^| findstr :8000
    pause
    exit /b 1
)
