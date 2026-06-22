# ==========================================
# Setup Gmail Email - PowerShell Script
# ==========================================
# This script will:
# 1. Ask for Gmail credentials
# 2. Set environment variables
# 3. Start Django with email support

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  SECURE FILE SHARING - EMAIL SETUP" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "STEP 1: Get Gmail App Password" -ForegroundColor Yellow
Write-Host "================================"
Write-Host "1. Go to: https://myaccount.google.com/apppasswords"
Write-Host "2. Login with your Gmail account"
Write-Host "3. Select: Mail + Windows Computer"
Write-Host "4. Click: GENERATE"
Write-Host "5. Copy the 16-character password (remove spaces)`n"

# Get Gmail email
$email = Read-Host "Enter your Gmail address (e.g., name@gmail.com)"

if (-not $email -or $email -notmatch "@gmail\.com$") {
    Write-Host "❌ Invalid Gmail address!" -ForegroundColor Red
    exit 1
}

# Get App Password
$password = Read-Host "Enter your 16-character App Password (will be hidden)" -AsSecureString
$password_plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($password)
)

# Validate password length
if ($password_plain.Length -ne 16) {
    Write-Host "❌ App Password must be exactly 16 characters!" -ForegroundColor Red
    Write-Host "   (Remove any spaces from the password)" -ForegroundColor Yellow
    exit 1
}

# Set environment variables
Write-Host "`nStep 2: Setting Environment Variables" -ForegroundColor Yellow
Write-Host "======================================"

$env:EMAIL_HOST_USER = $email
$env:EMAIL_HOST_PASSWORD = $password_plain
$env:EMAIL_HOST = "smtp.gmail.com"
$env:EMAIL_PORT = "587"
$env:EMAIL_USE_TLS = "True"

Write-Host "✓ EMAIL_HOST_USER = $email" -ForegroundColor Green
Write-Host "✓ EMAIL_HOST_PASSWORD = (hidden)" -ForegroundColor Green
Write-Host "✓ EMAIL_HOST = smtp.gmail.com" -ForegroundColor Green
Write-Host "✓ EMAIL_PORT = 587" -ForegroundColor Green
Write-Host "✓ EMAIL_USE_TLS = True" -ForegroundColor Green

# Start Django
Write-Host "`nStep 3: Starting Django with Email Support" -ForegroundColor Yellow
Write-Host "=========================================="
Write-Host ""

Set-Location backend
python manage.py runserver

Write-Host "`nDjango stopped. Press any key to exit..."
$null = Read-Host
