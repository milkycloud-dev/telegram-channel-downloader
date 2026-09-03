@echo off
chcp 65001 >nul
cd /d "%~dp0"

title Telegram Secret Channel Downloader

echo ========================================================
echo    Telegram Secret Channel Downloader - Launcher
echo ========================================================
echo.

:: Detect Python executable
set "PYTHON_EXE="

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_EXE=python"
) else (
    py -3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=py -3"
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python is not installed or not added to PATH!
    echo Please install Python 3.10+ from https://www.python.org
    echo and make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Quick check if dependencies are already installed
%PYTHON_EXE% -c "import flet, telethon, qrcode, PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Missing dependencies detected. Installing requirements...
    %PYTHON_EXE% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Failed to install required packages!
        pause
        exit /b 1
    )
)

echo Starting application...
echo.
%PYTHON_EXE% main_flet.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application stopped with exit code %errorlevel%.
    pause
)
