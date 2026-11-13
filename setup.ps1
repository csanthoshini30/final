# Aircraft Predictive Maintenance System - PowerShell Setup
# Run: .\setup.ps1

Write-Host ""
Write-Host "Aircraft Predictive Maintenance System - SETUP" -ForegroundColor Cyan
Write-Host "(Binary Wheels - No Compilation Required)" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Python found" -ForegroundColor Green
Write-Host ""

# Create virtual environment
Write-Host "[2/4] Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create venv" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Virtual environment created" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "[3/4] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "OK - Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "[4/4] Installing dependencies (2-3 minutes)..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel -q
python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Installation had issues, but continuing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. python training\train_all.py  (train models)" -ForegroundColor White
Write-Host "2. streamlit run dashboard\app.py  (start dashboard)" -ForegroundColor White
Write-Host ""
