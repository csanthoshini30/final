@echo off
REM Aircraft Predictive Maintenance System - Setup Script
REM This script sets up the environment and installs dependencies

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  Aircraft Predictive Maintenance System - SETUP        ║
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

REM Upgrade pip
echo [4/4] Installing dependencies...
python -m pip install --upgrade pip setuptools wheel --quiet
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing...
)

REM Install requirements
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  Setup Complete!                                       ║
echo ╠════════════════════════════════════════════════════════╣
echo ║  Next steps:                                           ║
echo ║  1. Place dataset files in: data/                      ║
echo ║  2. Run: python training/train_all.py                  ║
echo ║  3. Run: streamlit run dashboard/app.py                ║
echo ╚════════════════════════════════════════════════════════╝
echo.

pause
