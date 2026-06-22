# Start Full Project - Backend + Frontend

Write-Host "`nStarting Backend (Django)..." -ForegroundColor Yellow
Write-Host "URL: http://localhost:8000`n" -ForegroundColor Gray

Start-Process -NoNewWindow -FilePath "cmd.exe" -ArgumentList "/c cd c:\Users\Admin\Music\updated-homo\updated-homo\backend && python manage.py runserver"

Start-Sleep -Seconds 3

Write-Host "Starting Frontend (React/Vite)..." -ForegroundColor Yellow
Write-Host "URL: http://localhost:5173`n" -ForegroundColor Gray

Start-Process -NoNewWindow -FilePath "cmd.exe" -ArgumentList "/c cd c:\Users\Admin\Music\updated-homo\updated-homo\frontend && npm run dev"

Start-Sleep -Seconds 2

Write-Host "`n===============================================" -ForegroundColor Green
Write-Host "BOTH SERVERS STARTED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "===============================================`n" -ForegroundColor Green

Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend API: http://localhost:8000/api`n" -ForegroundColor White

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Set Gmail credentials (in new PowerShell):" -ForegroundColor Gray
Write-Host "`$env:EMAIL_HOST_USER = 'your-email@gmail.com'" -ForegroundColor Yellow
Write-Host "`$env:EMAIL_HOST_PASSWORD = 'your-16-char-app-password'" -ForegroundColor Yellow
Write-Host "`n2. Test email: python test_email_config.py`n" -ForegroundColor Gray
Write-Host "3. Visit: http://localhost:5173/signup`n" -ForegroundColor Gray
