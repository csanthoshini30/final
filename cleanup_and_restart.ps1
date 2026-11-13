# Cleanup old failed setup and start fresh
# Run: .\cleanup_and_restart.ps1

Write-Host ""
Write-Host "Cleaning up old setup..." -ForegroundColor Cyan
Write-Host ""

# Remove old venv folder
if (Test-Path "venv") {
    Write-Host "Removing old virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
    Write-Host "OK - Old venv removed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting fresh setup..." -ForegroundColor Cyan
Write-Host ""

# Run the new setup script
& ".\setup.ps1"
