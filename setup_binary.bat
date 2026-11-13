@echo off
REM Aircraft Predictive Maintenance System - Setup Script (Fixed for Windows)
REM This script sets up the environment and installs dependencies with binary wheels only

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  Aircraft Predictive Maintenance System - SETUP        ║
echo ║  (Binary Wheels - No Compilation Required)             ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

echo [1/4] Python version check... OK
echo.

REM Create virtual environment
echo [2/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created successfully
echo.

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo.

REM Upgrade pip (IMPORTANT for binary wheels)
echo [4/4] Upgrading pip and installing dependencies...
python -m pip install --upgrade pip setuptools wheel --quiet

REM Install with binary wheels only (no compilation)
echo Installing packages (using binary wheels only)...
python -m pip install --only-binary :all: -r requirements.txt

if errorlevel 1 (
    echo.
    echo [WARNING] Some packages failed with binary-only mode
    echo [INFO] Retrying with compilation allowed (if needed)...
    python -m pip install -r requirements.txt

    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        echo Please check internet connection and try again
        pause
        exit /b 1
    )
)

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  Setup Complete!                                       ║
echo ║                                                        ║
echo ║  Next steps:                                           ║
echo ║  1. Activate: venv\Scripts\activate.bat                ║
echo ║  2. Train: python training\train_all.py               ║
echo ║  3. Dashboard: streamlit run dashboard\app.py         ║
echo ║                                                        ║
echo ║  Virtual environment ready at: venv\                 ║
echo ║  All dependencies installed                           ║
echo ╚════════════════════════════════════════════════════════╝
echo.

pause
