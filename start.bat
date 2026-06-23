@echo off
chcp 65001 >nul
echo ========================================================
echo         Telegram Media Scraper v5.0 - Launcher
echo ========================================================
echo.

:: Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден! Установите Python и добавьте его в PATH.
    pause
    exit /b
)

:: Установка основных зависимостей
echo Установка/проверка базовых библиотек (Flet, Telethon и др.)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Ошибка установки библиотек!
    pause
    exit /b
)

:: Попытка установить cryptg (опционально)
echo.
echo Попытка установки cryptg (оптимизатор скорости)...
pip install cryptg --quiet
if %errorlevel% neq 0 (
    echo [INFO] Библиотека cryptg не установлена (нет готового wheel/компилятора).
    echo [INFO] Программа будет работать стабильно, но чуть медленнее.
) else (
    echo [INFO] Библиотека cryptg успешно установлена!
)

echo.
echo Запускаем приложение...
start pythonw main_flet.py
exit
