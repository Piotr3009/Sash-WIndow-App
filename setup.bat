@echo off
REM Sash Window App - Setup Script for Windows
REM This script sets up the development environment

echo ==========================================
echo Sash Window App - Setup Script
echo ==========================================
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.10 or higher.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo Virtual environment created successfully!
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated!
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed successfully!
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo .env file created. Please edit it with your Supabase credentials if needed.
) else (
    echo .env file already exists. Skipping.
)
echo.

REM Create output directory
echo Creating output directory...
if not exist output mkdir output
echo Output directory created!
echo.

echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo To run the application:
echo   1. Activate the virtual environment: venv\Scripts\activate.bat
echo   2. Run the app: python main_gui.py
echo.
echo For development:
echo   - Install dev dependencies: pip install -e ".[dev]"
echo   - Run tests: pytest
echo.
pause
