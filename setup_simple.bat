@echo off
REM Aircraft Predictive Maintenance System - Simple Setup
REM This is the most reliable approach - works on any Windows system

echo.
echo Cleaning up old setup...
if exist venv (
    echo Deleting old virtual environment...
    rmdir /S /Q venv
    echo Done.
)
echo.

echo Creating fresh virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Installing packages (this may take 2-3 minutes)...
python -m pip install -r requirements.txt

echo.
echo.
echo ==================== SETUP COMPLETE ====================
echo.
echo Next steps:
echo  1. Keep this window open
echo  2. Run: python training\train_all.py
echo  3. Run: streamlit run dashboard\app.py
echo.
echo Virtual environment is ready (venv folder created)
echo.
echo ========================================================
echo.

pause
