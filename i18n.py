"""
Internationalization (i18n) module for Telegram Secret Channel Downloader.

Uses a key-based translation approach where English is the primary language
and Russian is provided as a translation. Language preference is persisted
to lang.json.

Usage:
    from i18n import t, set_lang, get_lang
    set_lang('ru')  # Switch to Russian
    print(t('app_title'))  # -> "Telegram Secret Channel Downloader"
    print(t('downloading_post', 5, 100))  # -> "Downloading post 5/100"
"""

import json
import os

_current_lang = "en"

_TRANSLATIONS = {
    "en": {
        # ── App ──
        "app_title": "Telegram Secret Channel Downloader",

        # ── Tabs ──
        "tab_auth": "🔐 Authorization",
        "tab_download": "📥 Download",
        "tab_live": "📡 Live",
        "tab_links": "📜 Links",
        "tab_settings": "⚙️ Settings",

        # ── Auth Tab ──
        "auth_title": "Telegram Authorization",
        "btn_authorize": "🔑 Authorize",
        "btn_logout": "🚪 Log Out",
        "auth_status_waiting": "Waiting for authorization",
        "auth_status_authorized": "✅ Authorized",
        "auth_status_saved": "Saved",
        "auth_loaded_cache": "Authorization loaded from cache.",
        "auth_check_error": "Authorization check error:",
        "auth_connecting": "Connecting...",
        "auth_requesting": "Authorization request...",
        "auth_success": "Successful authorization!",
        "auth_error": "Authorization error",
        "auth_log_title": "Authorization log:",
        "scan_qr_hint": "Scan QR code in Telegram App (Settings -> Devices -> Link Desktop Device)",
        "session_deleted": "Session deleted. Logged out.",
        "session_delete_error": "Error deleting session:",
        "already_authorized": "✅ Already authorized",
        "auth_required": "⏳ Authorization required...",
        "auth_timeout": "Authorization timeout",
        "2fa_title": "Two-Factor Authentication",
        "2fa_prompt": "Enter 2FA password:",
        "2fa_error": "2FA error:",
        "2fa_error_qr": "2FA error (QR):",
        "qr_auth_error": "QR authorization error:",
        "phone_title": "Phone",
        "phone_prompt": "Enter phone number (with +):",
        "code_send_error": "Code send error:",
        "code_title": "Confirmation Code",
        "code_prompt": "Enter code from Telegram:",
        "login_error": "Login error:",
        "auth_success_full": "✅ Authorization successful!",
        "input_required": "Input required",
        "btn_ok": "OK",

        # ── Download Tab ──
        "overall_channel_progress": "Overall Channel Progress",
        "overall_progress_fmt": "Overall progress: {0} / {1} messages",
        "active_downloads": "Active Downloads",
        "file_progress_fmt": "File #{0}: {1} / {2}",
        "btn_start": "Start",
        "btn_stop": "Stop",
        "btn_skip_active": "⏭ Skip Active",
        "btn_skip_file": "Skip this file",
        "btn_reset": "Reset Progress",
        "btn_generate_html": "📄 Regenerate HTML",
        "btn_open_html": "🌐 Open HTML",
        "statistics_title": "📊 Statistics",
        "stat_total_msgs": "Total messages",
        "stat_processed": "Processed",
        "stat_total_files": "Total files",
        "stat_total_size": "Total size",
        "stat_photos": "📷 Photos",
        "stat_videos": "🎬 Videos",
        "stat_elapsed": "⏱ Elapsed",
        "stat_speed": "🚀 Speed",
        "stat_eta": "⏳ ETA",
        "stat_text_posts": "📝 Text posts",
        "speed_fmt": "{0:.1f} f/min",
        "system_log_title": "🟢 System Log",
        "waiting": "Waiting...",

        # ── Live Tab ──
        "live_title": "Live Monitoring",
        "live_description": "Monitor channel for new posts and scan for missing files.",
        "btn_start_monitor": "📡 Start Monitoring",
        "btn_scan_missing": "🔍 Scan Missing",
        "btn_download_missing": "📥 Download Missing",
        "realtime_activity": "Real-time Activity",

        # ── Links Tab ──
        "links_title": "Downloaded Files Log",
        "col_type": "Type",
        "col_post_num": "Post #",
        "col_file": "File",
        "col_link": "Link",
        "col_size": "Size",
        "col_time": "Time",

        # ── Settings Tab ──
        "api_settings": "API Settings",
        "api_id_label": "API ID",
        "api_hash_label": "API Hash",
        "channel_settings": "Channel Settings",
        "channel_id_label": "Channel ID / Username",
        "download_dir_label": "Download Directory",
        "btn_save": "💾 Save",
        "settings_saved": "Settings saved",
        "settings_saved_snack": "Settings saved!",
        "language_label": "Language",
        "delays_settings": "Delays & File Limits",
        "delay_posts_label": "Delay for media posts (sec)",
        "delay_text_label": "Delay for text messages (sec)",
        "max_file_size_label": "Max file size in MB (0 = no limit)",
        "max_retries_label": "Max download retries",

        # ── Reset Dialog ──
        "reset_title": "Reset Progress",
        "reset_confirm": "Are you sure you want to restart downloading this channel from the beginning?",
        "reset_delete_files": "Delete all downloaded media files",
        "btn_cancel": "Cancel",
        "btn_reset_confirm": "Reset",
        "reset_files_deleted": "Downloaded files deleted.",
        "reset_files_error": "Error deleting files:",
        "reset_complete": "Channel progress and history reset!",

        # ── Scraper Core: Status Messages ──
        "stopped": "⏹ Stopped",
        "stopped_by_user": "⏹ Stopped by user",
        "critical_error": "Critical error: {0}",
        "channel_info": "Channel: {0} — {1} messages",
        "resuming": "▶ Resuming from post #{0}, msg #{1}",
        "processing_post": "📥 Post #{0} (message {1}/{2})",
        "skipping_post": "Skipping post #{0} (no media or comments)",
        "waiting_downloads": "⏳ Waiting for downloads to finish...",
        "download_complete": "✅ Download complete!",
        "auto_monitor": "Automatic switch to Live monitoring...",
        "download_finished": "Download complete",

        # ── Scraper Core: Monitor ──
        "checking_new_posts": "🔄 Checking for new posts...",
        "monitor_waiting": "⏳ Waiting {0} sec...",
        "monitor_stopped": "⏹ Monitoring stopped",
        "monitor_error": "Monitor error: {0}",
        "new_files_downloaded": "✅ Downloaded {0} new files!",
        "first_run_warning": "Note: First run! Full dump via Download tab is recommended.",

        # ── Scraper Core: Scan/Missing ──
        "scanning_missing": "🔍 Scanning for missing files...",
        "scan_result": "📊 Found {0} missing posts (Total downloaded: {1})",
        "scan_complete_log": "Scan complete. Missing: {0}",
        "scan_error": "Scan error: {0}",
        "searching_missing": "🔍 Searching for missing posts...",
        "no_missing": "✅ No missing posts found!",
        "downloading_missing": "📥 Downloading {0} missing posts...",
        "downloading_missing_item": "Downloading {0}/{1} (Post #{2})",
        "downloading_missing_media": "⏳ Downloading media...",
        "downloading_missing_done": "✅ Download of missing posts complete!",
        "downloading_missing_error": "Download error: {0}",

        # ── Scraper Core: File Download ──
        "download_started": "⬇️ Downloading {0} #{1} ({2})...",
        "download_success": "✅ Downloaded {0} #{1} ({2}, {3})",
        "download_failed": "❌ Failed to download {0} after {1} attempts: {2}",
        "download_skipped_by_user": "⏭ File #{0} skipped by user",
        "download_skipped_size": "⏭ {0} #{1} skipped: size {2} exceeds {3} MB limit",
        "download_unavailable": "⚠️ File #{0} unavailable or restricted in Telegram. Skipped.",
        "skipping_file_action": "⏭ Skipping file #{0}...",
        "integrity_failed": "File integrity failed: {0}",
        "size_mismatch": "⚠️ Size mismatch: {0} ≠ {1} bytes",
        "network_error": "📡 Network error ({0}/{1}): {2}. Retry in {3}s...",
        "general_error": "⚠️ Error ({0}/{1}): {2}. Retry in {3}s...",
        "flood_wait": "⚠️ FloodWait — pausing {0}s...",
        "waiting_network": "📡 Waiting for network ({0}s)...",
        "comment_error": "Comment error for post #{0}: {1}",
        "channel_not_found": "Channel {0} not found: {1}",
        "source_post": "post",
        "source_comment": "comment",
        "type_post": "Post",
        "type_comment": "Comment",
        "size_warning": "⚠️ Estimated size: {0}. Free space: {1}.",

        # ── Scraper Core: HTML ──
        "generating_html": "📄 Generating offline HTML viewer...",
        "html_generated": "✅ HTML viewer generated: {0}",
        "html_error": "HTML generation error: {0}",

        # ── Media Types ──
        "media_photo": "📷 Photo",
        "media_video": "🎬 Video",
        "media_document": "📄 Document",
        "media_voice": "🎤 Voice",
        "media_video_note": "🔵 Video Note",
        "media_audio": "🎵 Audio",
        "media_sticker": "🏷 Sticker",
        "media_gif": "🎞 GIF",
        "media_unknown": "❓ Unknown",
        "media_text": "📝 Text",

        # ── Size Units ──
        "size_b": "{0} B",
        "size_kb": "{0:.1f} KB",
        "size_mb": "{0:.1f} MB",
        "size_gb": "{0:.2f} GB",

        # ── Error ──
        "error_prefix": "ERROR",
        "error_snack": "Error: {0}",
    },
    "ru": {
        # ── App ──
        "app_title": "Telegram Secret Channel Downloader",

        # ── Tabs ──
        "tab_auth": "🔐 Авторизация",
        "tab_download": "📥 Скачивание",
        "tab_live": "📡 Live",
        "tab_links": "📜 Ссылки",
        "tab_settings": "⚙️ Настройки",

        # ── Auth Tab ──
        "auth_title": "Авторизация Telegram",
        "btn_authorize": "🔑 Авторизоваться",
        "btn_logout": "🚪 Выйти",
        "auth_status_waiting": "Ожидание авторизации",
        "auth_status_authorized": "✅ Авторизован",
        "auth_status_saved": "Сохранено",
        "auth_loaded_cache": "Авторизация загружена из кэша.",
        "auth_check_error": "Ошибка проверки авторизации:",
        "auth_connecting": "Подключение...",
        "auth_requesting": "Запрос авторизации...",
        "auth_success": "Успешная авторизация!",
        "auth_error": "Ошибка авторизации",
        "auth_log_title": "Лог авторизации:",
        "scan_qr_hint": "Отсканируйте QR код в приложении Telegram (Настройки -> Устройства -> Подключить устройство)",
        "session_deleted": "Сессия удалена. Выполнен выход из аккаунта.",
        "session_delete_error": "Ошибка при удалении сессии:",
        "already_authorized": "✅ Уже авторизован",
        "auth_required": "⏳ Требуется авторизация...",
        "auth_timeout": "Время ожидания авторизации истекло",
        "2fa_title": "Двухфакторная аутентификация",
        "2fa_prompt": "Введите пароль 2FA:",
        "2fa_error": "Ошибка 2FA:",
        "2fa_error_qr": "Ошибка 2FA (QR):",
        "qr_auth_error": "Ошибка QR авторизации:",
        "phone_title": "Телефон",
        "phone_prompt": "Введите номер телефона (с +):",
        "code_send_error": "Ошибка отправки кода:",
        "code_title": "Код подтверждения",
        "code_prompt": "Введите код из Telegram:",
        "login_error": "Ошибка входа:",
        "auth_success_full": "✅ Авторизация успешна!",
        "input_required": "Требуется ввод",
        "btn_ok": "ОК",

        # ── Download Tab ──
        "overall_channel_progress": "Общий прогресс канала",
        "overall_progress_fmt": "Общий прогресс: {0} / {1} сообщений",
        "active_downloads": "Активные загрузки",
        "file_progress_fmt": "Файл #{0}: {1} / {2}",
        "btn_start": "Старт",
        "btn_stop": "Стоп",
        "btn_skip_active": "⏭ Пропустить активные",
        "btn_skip_file": "Пропустить этот файл",
        "btn_reset": "Сброс прогресса",
        "btn_generate_html": "📄 Перегенерировать HTML",
        "btn_open_html": "🌐 Открыть HTML",
        "statistics_title": "📊 Статистика",
        "stat_total_msgs": "Всего сообщений",
        "stat_processed": "Обработано",
        "stat_total_files": "Всего файлов",
        "stat_total_size": "Общий размер",
        "stat_photos": "📷 Фото",
        "stat_videos": "🎬 Видео",
        "stat_elapsed": "⏱ Время работы",
        "stat_speed": "🚀 Скорость",
        "stat_eta": "⏳ Осталось",
        "stat_text_posts": "📝 Текстовые",
        "speed_fmt": "{0:.1f} ф/мин",
        "system_log_title": "🟢 Системный лог",
        "waiting": "Ожидание...",

        # ── Live Tab ──
        "live_title": "Live Мониторинг",
        "live_description": "Мониторинг канала на новые посты и поиск пропущенных файлов.",
        "btn_start_monitor": "📡 Запустить мониторинг",
        "btn_scan_missing": "🔍 Искать пропущенные",
        "btn_download_missing": "📥 Докачать пропущенные",
        "realtime_activity": "Активность в реальном времени",

        # ── Links Tab ──
        "links_title": "Лог скачанных файлов",
        "col_type": "Тип",
        "col_post_num": "Пост #",
        "col_file": "Файл",
        "col_link": "Ссылка",
        "col_size": "Размер",
        "col_time": "Время",

        # ── Settings Tab ──
        "api_settings": "Настройки API",
        "api_id_label": "API ID",
        "api_hash_label": "API Hash",
        "channel_settings": "Настройки канала",
        "channel_id_label": "Channel ID / Username",
        "download_dir_label": "Директория загрузки",
        "btn_save": "💾 Сохранить",
        "settings_saved": "Настройки сохранены",
        "settings_saved_snack": "Настройки сохранены!",
        "language_label": "Язык",
        "delays_settings": "Задержки и лимиты файлов",
        "delay_posts_label": "Задержка для медиа-постов (сек)",
        "delay_text_label": "Задержка для текста (сек)",
        "max_file_size_label": "Макс. размер файла в МБ (0 = без лимита)",
        "max_retries_label": "Количество попыток скачивания",

        # ── Reset Dialog ──
        "reset_title": "Сброс прогресса",
        "reset_confirm": "Вы уверены, что хотите начать скачивание этого канала с самого начала?",
        "reset_delete_files": "Удалить все скачанные медиафайлы",
        "btn_cancel": "Отмена",
        "btn_reset_confirm": "Сбросить",
        "reset_files_deleted": "Скачанные файлы удалены.",
        "reset_files_error": "Ошибка удаления файлов:",
        "reset_complete": "Прогресс канала и история сброшены!",

        # ── Scraper Core: Status Messages ──
        "stopped": "⏹ Остановлено",
        "stopped_by_user": "⏹ Остановлено пользователем",
        "critical_error": "Критическая ошибка: {0}",
        "channel_info": "Канал: {0} — {1} сообщений",
        "resuming": "▶ Продолжение с поста #{0}, сообщение #{1}",
        "processing_post": "📥 Пост #{0} (сообщение {1}/{2})",
        "skipping_post": "Пропуск поста #{0} (нет медиа и комментариев)",
        "waiting_downloads": "⏳ Докачиваем медиа...",
        "download_complete": "✅ Скачивание завершено!",
        "auto_monitor": "Автоматический переход в Live-мониторинг...",
        "download_finished": "Скачивание завершено",

        # ── Scraper Core: Monitor ──
        "checking_new_posts": "🔄 Проверка новых постов...",
        "monitor_waiting": "⏳ Ожидание {0} сек...",
        "monitor_stopped": "⏹ Мониторинг остановлен",
        "monitor_error": "Ошибка мониторинга: {0}",
        "new_files_downloaded": "✅ Скачано {0} новых файлов!",
        "first_run_warning": "Внимание: Первый запуск! Рекомендуется сделать полный дамп через вкладку Download.",

        # ── Scraper Core: Scan/Missing ──
        "scanning_missing": "🔍 Сканирование канала на пропущенные файлы...",
        "scan_result": "📊 Найдено {0} пропущенных постов (Всего скачано: {1})",
        "scan_complete_log": "Сканирование завершено. Пропущено: {0}",
        "scan_error": "Ошибка сканирования: {0}",
        "searching_missing": "🔍 Поиск пропущенных постов для скачивания...",
        "no_missing": "✅ Пропущенных постов не найдено!",
        "downloading_missing": "📥 Начинаем докачку {0} постов...",
        "downloading_missing_item": "Докачка {0}/{1} (Пост #{2})",
        "downloading_missing_media": "⏳ Докачиваем медиа...",
        "downloading_missing_done": "✅ Докачка завершена!",
        "downloading_missing_error": "Ошибка докачки: {0}",

        # ── Scraper Core: File Download ──
        "download_started": "⬇️ Начато скачивание {0} #{1} ({2})...",
        "download_success": "✅ Успешно скачан {0} #{1} ({2}, {3})",
        "download_failed": "❌ Не удалось скачать {0} после {1} попыток: {2}",
        "download_skipped_by_user": "⏭ Файл #{0} пропущен пользователем",
        "download_skipped_size": "⏭ {0} #{1} пропущен: размер {2} превышает лимит {3} МБ",
        "download_unavailable": "⚠️ Файл #{0} недоступен или защищен в Telegram. Пропущен.",
        "skipping_file_action": "⏭ Пропуск файла #{0}...",
        "integrity_failed": "Целостность файла нарушена: {0}",
        "size_mismatch": "⚠️ Размер не совпадает: {0} ≠ {1} байт",
        "network_error": "📡 Ошибка сети ({0}/{1}): {2}. Повтор через {3}с...",
        "general_error": "⚠️ Ошибка ({0}/{1}): {2}. Повтор через {3}с...",
        "flood_wait": "⚠️ FloodWait — пауза {0}с...",
        "waiting_network": "📡 Ожидание сети ({0}с)...",
        "comment_error": "Ошибка комментариев поста #{0}: {1}",
        "channel_not_found": "Канал {0} не найден: {1}",
        "source_post": "пост",
        "source_comment": "комментарий",
        "type_post": "Пост",
        "type_comment": "Комментарий",
        "size_warning": "⚠️ Ожидаемый размер: {0}. Свободно: {1}.",

        # ── Scraper Core: HTML ──
        "generating_html": "📄 Генерация HTML для оффлайн просмотра...",
        "html_generated": "✅ HTML создан: {0}",
        "html_error": "Ошибка генерации HTML: {0}",

        # ── Media Types ──
        "media_photo": "📷 Фото",
        "media_video": "🎬 Видео",
        "media_document": "📄 Документ",
        "media_voice": "🎤 Голосовое",
        "media_video_note": "🔵 Кружок",
        "media_audio": "🎵 Аудио",
        "media_sticker": "🏷 Стикер",
        "media_gif": "🎞 GIF",
        "media_unknown": "❓ Неизвестно",
        "media_text": "📝 Текст",

        # ── Size Units ──
        "size_b": "{0} Б",
        "size_kb": "{0:.1f} КБ",
        "size_mb": "{0:.1f} МБ",
        "size_gb": "{0:.2f} ГБ",

        # ── Error ──
        "error_prefix": "ОШИБКА",
        "error_snack": "Ошибка: {0}",
    },
}


def set_lang(lang_code: str):
    """Set the active language and persist to lang.json."""
    global _current_lang
    if lang_code in _TRANSLATIONS:
        _current_lang = lang_code
        try:
            with open("lang.json", "w") as f:
                json.dump({"lang": lang_code}, f)
        except Exception:
            pass


def t(key: str, *args) -> str:
    """
    Translate a key to the current language.

    Args:
        key: Translation key string.
        *args: Optional positional arguments for string formatting.

    Returns:
        Translated string, or the key itself if not found.
    """
    text = _TRANSLATIONS.get(_current_lang, {}).get(key, key)
    if args:
        try:
            return text.format(*args)
        except Exception:
            return text
    return text


def get_lang() -> str:
    """Return the current language code."""
    return _current_lang


# Load persisted language on import
try:
    if os.path.exists("lang.json"):
        with open("lang.json", "r") as f:
            data = json.load(f)
            if "lang" in data and data["lang"] in _TRANSLATIONS:
                _current_lang = data["lang"]
except Exception:
    pass
