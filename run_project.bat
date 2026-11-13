@echo off
REM Aircraft Predictive Maintenance System - Main Run Script

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  Aircraft Predictive Maintenance System                ║
echo ║  Main Run Script                                       ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo.
echo Select operation:
echo [1] Train all models (train_all.py)
echo [2] Run Streamlit Dashboard (dashboard/app.py)
echo [3] Both - Train then Run Dashboard
echo [4] Exit
echo.

set /p choice="Enter your choice [1-4]: "

if "%choice%"=="1" (
    echo.
    echo Starting model training...
    echo This may take several minutes...
    echo.
    python training/train_all.py
    if errorlevel 1 (
        echo [ERROR] Training failed
        pause
        exit /b 1
    )
    echo Training completed successfully!
    pause
) else if "%choice%"=="2" (
    echo.
    echo Starting Streamlit Dashboard...
    echo The dashboard will open in your browser
    echo Press Ctrl+C to stop the server
    echo.
    streamlit run dashboard/app.py
) else if "%choice%"=="3" (
    echo.
    echo Step 1: Training Models
    echo ========================
    python training/train_all.py
    if errorlevel 1 (
        echo [ERROR] Training failed
        pause
        exit /b 1
    )

    echo.
    echo Step 2: Starting Dashboard
    echo ==========================
    echo The dashboard will open in your browser
    echo Press Ctrl+C to stop the server
    echo.
    streamlit run dashboard/app.py
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo [ERROR] Invalid choice
    pause
    exit /b 1
)
