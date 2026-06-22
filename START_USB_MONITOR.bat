@echo off
REM USB & Mobile Device Monitor - Windows Batch Startup
REM This ensures the monitor runs from the correct directory

cls
echo.
echo ========================================================================
echo  USB ^& MOBILE DEVICE REAL-TIME MONITOR
echo ========================================================================
echo.
echo Starting monitoring system...
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Check if backend exists
if not exist "%SCRIPT_DIR%backend\scripts\smart_usb_monitor.py" (
    echo ERROR: Monitor script not found!
    echo Expected: %SCRIPT_DIR%backend\scripts\smart_usb_monitor.py
    pause
    exit /b 1
)

REM Check if Django is accessible
echo Checking Django backend...
python -c "import requests; r = requests.get('http://127.0.0.1:8000/api/security/event/', timeout=2); print('[OK] Django is running')" 2>nul
if errorlevel 1 (
    echo WARNING: Django does not appear to be running on port 8000
    echo.
    echo To start Django, open another terminal and run:
    echo   cd backend
    echo   python manage.py runserver
    echo.
    pause
)

echo.
echo ========================================================================
echo STARTING MONITOR
echo ========================================================================
echo.
echo Monitor will run in this window.
echo To stop monitoring: Press Ctrl+C
echo.
echo Directory: %SCRIPT_DIR%backend\scripts
echo Script: smart_usb_monitor.py
echo.
echo ========================================================================
echo.

REM Run the startup script from the project root
cd /d "%SCRIPT_DIR%"
python start_usb_monitor.py

if errorlevel 1 (
    echo.
    echo ERROR: Monitor failed to start
    echo Check the messages above for details
    pause
    exit /b 1
)

exit /b 0
