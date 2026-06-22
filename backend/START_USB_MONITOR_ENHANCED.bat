@echo off
REM Start Enhanced USB Monitor
REM This script starts the USB device detection and monitoring system

echo.
echo ========================================================================
echo  STARTING USB DEVICE MONITOR
echo ========================================================================
echo.

REM Get the directory of this script
cd /d "%~dp0\.."

REM Check if Django is running
timeout /t 2 /nobreak > nul
echo [*] Verifying Django backend...
powershell -Command "try { (New-Object System.Net.WebClient).DownloadString('http://localhost:8000/api/security/event/') } catch { Write-Host 'Backend not ready yet' }"

echo.
echo [*] Starting USB Monitor...
python scripts/usb_monitor_enhanced.py

pause
