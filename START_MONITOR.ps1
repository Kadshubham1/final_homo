#!/usr/bin/env powershell
<#
.SYNOPSIS
    USB Security Monitoring System Startup Script
.DESCRIPTION
    Starts Django backend and USB monitoring system
.EXAMPLE
    .\START_MONITOR.ps1
#>

param(
    [switch]$NoWait = $false
)

$ErrorActionPreference = "Continue"

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔" + "="*56 + "╗" -ForegroundColor Cyan
Write-Host "║     USB SECURITY MONITORING SYSTEM - STARTUP            ║" -ForegroundColor Cyan
Write-Host "║     All systems ready for live monitoring               ║" -ForegroundColor Cyan
Write-Host "╚" + "="*56 + "╝" -ForegroundColor Cyan
Write-Host "`n" -ForegroundColor Cyan

# Get script directory
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

# Check if backend exists
if (-not (Test-Path "$scriptDir\backend")) {
    Write-Host "[-] Error: Backend directory not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Python executable
$pythonExe = "$scriptDir\.venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "[-] Python not found at: $pythonExe" -ForegroundColor Red
    Write-Host "[*] Please ensure the virtual environment is activated" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[+] Python environment ready" -ForegroundColor Green
Write-Host "[*] Python: $pythonExe" -ForegroundColor Green
Write-Host "`n" -ForegroundColor Cyan

# Start Django backend
Write-Host "[*] Starting Django backend on http://127.0.0.1:8000..." -ForegroundColor Yellow

$backendJob = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList "manage.py runserver" `
    -WorkingDirectory "$scriptDir\backend" `
    -WindowStyle Normal `
    -PassThru

Write-Host "[+] Django process started (PID: $($backendJob.Id))" -ForegroundColor Green

# Wait for Django to be ready
Write-Host "[*] Waiting 5 seconds for Django to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test API
Write-Host "[*] Testing API connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/security/event/" -TimeoutSec 3 -ErrorAction SilentlyContinue
    Write-Host "[+] Django backend is responding!" -ForegroundColor Green
}
catch {
    Write-Host "[*] API not yet ready, waiting..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

Write-Host "`n" -ForegroundColor Cyan

# Start USB Monitor
Write-Host "[*] Starting USB Security Monitor..." -ForegroundColor Yellow

$monitorJob = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList "smart_usb_monitor.py" `
    -WorkingDirectory "$scriptDir\backend\scripts" `
    -WindowStyle Normal `
    -PassThru

Write-Host "[+] Monitor process started (PID: $($monitorJob.Id))" -ForegroundColor Green

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔" + "="*56 + "╗" -ForegroundColor Green
Write-Host "║  SYSTEM STARTED SUCCESSFULLY!                           ║" -ForegroundColor Green
Write-Host "║                                                         ║" -ForegroundColor Green
Write-Host "║  Django Backend:    http://127.0.0.1:8000              ║" -ForegroundColor Green
Write-Host "║  Monitor Status:    Running (monitor window)            ║" -ForegroundColor Green
Write-Host "║  Events API:        /api/security/event/               ║" -ForegroundColor Green
Write-Host "║  Dashboard:         /api/security/admin/dashboard/     ║" -ForegroundColor Green
Write-Host "║                                                         ║" -ForegroundColor Green
Write-Host "║  🔴 INSERT A USB DEVICE TO BEGIN MONITORING             ║" -ForegroundColor Red
Write-Host "║                                                         ║" -ForegroundColor Green
Write-Host "║  Log files:                                             ║" -ForegroundColor Green
Write-Host "║  - Monitor output appears in its window                 ║" -ForegroundColor Green
Write-Host "║  - Photos: backend/scripts/security_captures/          ║" -ForegroundColor Green
Write-Host "║  - Events: http://127.0.0.1:8000/api/security/event/  ║" -ForegroundColor Green
Write-Host "║                                                         ║" -ForegroundColor Green
Write-Host "║  To exit: Close both windows or press Ctrl+C            ║" -ForegroundColor Green
Write-Host "╚" + "="*56 + "╝" -ForegroundColor Green
Write-Host "`n" -ForegroundColor Cyan

# Keep script running
Write-Host "[*] System monitoring active. Press Ctrl+C to stop all processes..." -ForegroundColor Yellow

try {
    while ($true) {
        # Check if processes are still running
        if ($backendJob.HasExited) {
            Write-Host "[-] Django backend has stopped!" -ForegroundColor Red
            break
        }
        if ($monitorJob.HasExited) {
            Write-Host "[-] Monitor has stopped!" -ForegroundColor Red
            break
        }
        Start-Sleep -Seconds 5
    }
}
catch [System.OperationCanceledException] {
    Write-Host "`n[*] Shutting down..." -ForegroundColor Yellow
    
    # Kill processes
    if (-not $backendJob.HasExited) {
        $backendJob | Stop-Process -Force
        Write-Host "[+] Django backend stopped" -ForegroundColor Green
    }
    if (-not $monitorJob.HasExited) {
        $monitorJob | Stop-Process -Force
        Write-Host "[+] Monitor stopped" -ForegroundColor Green
    }
}

Write-Host "[*] System shutdown complete" -ForegroundColor Yellow
