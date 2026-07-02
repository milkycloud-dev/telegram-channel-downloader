@echo off
chcp 65001 >nul
echo ========================================================
echo    Telegram Secret Channel Downloader v2.0 - Launcher
echo ========================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python and add it to PATH.
    pause
    exit /b
)

:: Install core dependencies
echo Installing/checking core libraries (Flet, Telethon, etc.)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Library installation failed!
    pause
    exit /b
)

:: Try to install cryptg (optional speed optimizer)
echo.
echo Attempting to install cryptg (speed optimizer)...
pip install cryptg --quiet
if %errorlevel% neq 0 (
    echo [INFO] cryptg not installed (no pre-built wheel/compiler available).
    echo [INFO] The application will work fine, just slightly slower.
) else (
    echo [INFO] cryptg installed successfully!
)

echo.
echo Starting application...
start pythonw main_flet.py
exit
