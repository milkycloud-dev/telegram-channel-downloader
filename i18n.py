import json
import os

current_lang = "ru"

TRANSLATIONS = {
    "en": {
        "🔐 Авторизация": "🔐 Authorization",
        "📥 Скачивание": "📥 Download",
        "📡 Live": "📡 Live",
        "📜 Ссылки": "📜 Links",
        "⚙️ Настройки": "⚙️ Settings",
        
        "Авторизация Telegram": "Telegram Authorization",
        "✅ Авторизован": "✅ Authorized",
        "Ожидание авторизации": "Waiting for authorization",
        "Ошибка проверки авторизации:": "Authorization check error:",
        "Авторизация загружена из кэша.": "Authorization loaded from cache.",
        
        "🔑 Авторизоваться": "🔑 Authorize",
        "🚪 Выйти из аккаунта": "🚪 Log Out",
        "Статус:": "Status:",
        
        "Общий прогресс канала": "Overall Channel Progress",
        "Общий прогресс: 0 / 0 сообщений": "Overall progress: 0 / 0 messages",
        "Активные загрузки": "Active Downloads",
        
        "▶ Начать": "▶ Start",
        "⏹ Остановить": "⏹ Stop",
        "📡 Мониторинг": "📡 Monitor",
        "🔍 Сканировать новые": "🔍 Scan New",
        "💾 Докачать файлы": "💾 Download Files",
        "🔄 Сбросить прогресс": "🔄 Reset Progress",
        "ID Канала (например: t.me/mychannel или 123456)": "Channel ID (e.g. t.me/mychannel or 123456)",
        
        "Ожидание...": "Waiting...",
        
        "Скачивание завершено": "Download complete",
        "Ожидание": "Waiting",
        "Отсканируйте QR код в приложении Telegram (Settings -> Devices -> Link Desktop Device)": "Scan QR code in Telegram App (Settings -> Devices -> Link Desktop Device)",
        
        "📊 Статистика": "📊 Statistics",
        "Всего сообщений:": "Total Messages:",
        "Обраработано:": "Processed:",
        "Скачано файлов:": "Files Downloaded:",
        "Общий размер:": "Total Size:",
        "Фотографий:": "Photos:",
        "Видео:": "Videos:",
        "Время работы:": "Elapsed Time:",
        "Скорость:": "Speed:",
        "Осталось времени:": "ETA:",
        
        "Удалить все скачанные медиафайлы": "Delete all downloaded media files",
        "Сброс прогресса": "Reset Progress",
        "Вы уверены, что хотите начать скачивание этого канала с самого начала?": "Are you sure you want to restart downloading this channel from the beginning?",
        "Отмена": "Cancel",
        "Сбросить": "Reset",
        
        "Настройки базы данных и задержек": "Database and Delays Settings",
        "Задержка между постами (сек):": "Delay between posts (sec):",
        "Подписываться на новые посты каждые (сек):": "Monitor for new posts every (sec):",
        "Таймаут (сек):": "Timeout (sec):",
        "Множитель FloodWait:": "FloodWait Multiplier:",
        "Удалять историю скачанного при сбросе (история хранится в SQLite)": "Delete download history on reset (stored in SQLite)",
        "💾 Сохранить настройки": "💾 Save Settings",
        
        "Тип": "Type",
        "Номер": "Number",
        "Файл": "File",
        "Ссылка": "Link",
        "Размер": "Size",
        "Время": "Time",
        "Скопировано в буфер обмена: ": "Copied to clipboard: "
    }
}

def t(text: str) -> str:
    global current_lang
    if current_lang == "ru":
        return text
    return TRANSLATIONS.get("en", {}).get(text, text)

def set_lang(lang: str):
    global current_lang
    current_lang = lang

def get_lang() -> str:
    return current_lang
