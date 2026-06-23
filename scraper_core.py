"""
Telegram Media Scraper — Core Engine / Движок парсинга
=====================================================
Асинхронный движок для скачивания ВСЕХ типов медиа из Telegram-каналов
и комментариев с поддержкой:
  - Шифрованного соединения (MTProto — как в оф. Telegram)
  - Устойчивости к обрывам сети (автоматический реконнект и повтор)
  - Проверки целостности скачанных файлов
  - Скачивания в максимальном качестве
  - Раздельных папок для каждого канала

Async engine for downloading ALL media types from Telegram channels
and comments. Supports: MTProto encryption, network resilience,
file integrity checks, max quality downloads, per-channel directories.
"""

import os
import json
import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from telethon import TelegramClient, errors
from telethon.tl.types import (
    MessageMediaWebPage,       # Ссылки-превью / Link previews
    MessageMediaPoll,          # Опросы / Polls
    MessageMediaGeo,           # Геолокация / Geolocation
    MessageMediaGeoLive,       # Живая геолокация / Live geolocation
    MessageMediaContact,       # Контакты / Contacts
    MessageMediaDice,          # Кости/эмодзи / Dice/emoji
    MessageMediaVenue,         # Места / Venues
    DocumentAttributeAnimated, # Атрибут GIF-анимации / GIF animation attribute
    DocumentAttributeFilename, # Имя файла документа / Document filename attribute
)


# ═══════════════════════════════════════════════════════════════════
#  КОНФИГУРАЦИЯ / CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    # --- Telegram API ---
    "api_id": 2040,
    "api_hash": "b18441a1ff607e10a989891a5462e627",
    "phone": "",

    # --- Текущий канал / Current channel ---
    "channel_id": 1890961508,
    "download_dir": "downloads",  # Директория по умолчанию / Default directory

    # --- Задержки (сек) / Delays (seconds) ---
    "delay_between_posts": 1.0,       # Рекомендуемая: 0.5-2.0 / Recommended: 0.5-2.0
    "delay_between_comments": 0.5,    # Рекомендуемая: 0.3-1.0 / Recommended: 0.3-1.0
    "flood_wait_multiplier": 1.5,     # Множитель при FloodWait / FloodWait multiplier
    "subscribe_interval": 60,         # Интервал мониторинга (сек) / Monitoring interval (sec)

    # --- Сетевая устойчивость / Network resilience ---
    "max_retries": 30,                # Макс. попыток скачивания / Max download retries
    "network_check_interval": 5,      # Интервал проверки сети (сек) / Network check interval (sec)

    # --- Состояние каналов / Per-channel state ---
    # Автоматически заполняется при работе / Populated automatically
    # "channels": { "channel_id": { "download_dir": "...", "last_msg_id": 0, "post_counter": 0, "processed_msgs": 0 } }
    "channels": {},
}

# Типы медиа, которые нельзя скачать как файл
# Media types that cannot be downloaded as files
_SKIP_MEDIA = (
    MessageMediaWebPage,
    MessageMediaPoll,
    MessageMediaGeo,
    MessageMediaGeoLive,
    MessageMediaContact,
    MessageMediaDice,
    MessageMediaVenue,
    type(None),
)


def load_config() -> dict:
    """
    Загрузить конфиг из файла или вернуть дефолтный.
    Load config from file or return defaults.
    Handles migration from old single-channel format.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        cfg = DEFAULT_CONFIG.copy()
        cfg.update(saved)
        
        # Если api_id или api_hash пустые, подставляем дефолтные (Telegram Desktop)
        if not cfg.get("api_id") or str(cfg.get("api_id")) == "0" or not cfg.get("api_hash"):
            cfg["api_id"] = 2040
            cfg["api_hash"] = "b18441a1ff607e10a989891a5462e627"

        # Миграция старого формата / Migrate old format
        if "last_downloaded_msg_id" in cfg:
            cid = str(cfg.get("channel_id", 0))
            ch = cfg.setdefault("channels", {}).setdefault(cid, {})
            ch.setdefault("last_msg_id", cfg.pop("last_downloaded_msg_id", 0))
            ch.setdefault("post_counter", cfg.pop("post_counter", 0))
            ch.setdefault("processed_msgs", cfg.pop("total_processed_msgs", 0))
            ch.setdefault("download_dir", cfg.get("download_dir", "downloads"))
            save_config(cfg)

        return cfg
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict):
    """Сохранить конфиг в файл. / Save config to file."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_channel_state(config: dict) -> dict:
    """
    Получить состояние текущего канала (папка, прогресс).
    Get state for the currently selected channel (dir, progress).
    Creates default state if channel not yet tracked.
    """
    cid = str(config.get("channel_id", 0))
    channels = config.setdefault("channels", {})
    if cid not in channels:
        # Для нового канала создаём подпапку / Create subfolder for new channel
        default_dir = os.path.join(
            config.get("download_dir", "downloads"), f"channel_{cid}"
        )
        channels[cid] = {
            "download_dir": default_dir,
            "last_msg_id": 0,
            "post_counter": 0,
            "processed_msgs": 0,
        }
    return channels[cid]


# ═══════════════════════════════════════════════════════════════════
#  СТАТИСТИКА / STATISTICS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ScraperStats:
    """Статистика скачивания. / Download statistics."""
    total_channel_msgs: int = 0      # Всего сообщений / Total messages
    processed_msgs: int = 0          # Обработано / Processed
    downloaded_post_files: int = 0   # Файлов из постов / Files from posts
    downloaded_comment_files: int = 0 # Файлов из комментов / Files from comments
    total_files: int = 0             # Всего файлов / Total files
    total_size_bytes: int = 0        # Общий размер / Total size
    # Разбивка по типам / Breakdown by type
    photos: int = 0
    videos: int = 0
    documents: int = 0
    voices: int = 0
    video_notes: int = 0
    audio_files: int = 0
    stickers: int = 0
    gifs: int = 0
    # Прогресс / Progress
    start_time: float = 0.0
    current_post_num: int = 0
    current_post_comments_total: int = 0
    current_post_comments_done: int = 0
    # Сетевая устойчивость / Network resilience
    retries_total: int = 0           # Всего повторных попыток / Total retries
    integrity_failures: int = 0       # Сбоев целостности / Integrity failures


# ═══════════════════════════════════════════════════════════════════
#  КЛАССИФИКАЦИЯ МЕДИА / MEDIA CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════

# Маппинг типа медиа → поле статистики / Media type → stats field mapping
_TYPE_TO_STAT = {
    "photo": "photos",
    "video": "videos",
    "document": "documents",
    "voice": "voices",
    "video_note": "video_notes",
    "audio": "audio_files",
    "sticker": "stickers",
    "gif": "gifs",
}

# Человекочитаемые метки / Human-readable labels
_TYPE_LABELS = {
    "photo": "📷 Фото",
    "video": "🎬 Видео",
    "document": "📄 Документ",
    "voice": "🎤 Голосовое",
    "video_note": "🔵 Кружок",
    "audio": "🎵 Аудио",
    "sticker": "🏷 Стикер",
    "gif": "🎞 GIF",
    "unknown": "❓ Неизвестно",
}


def classify_media(message) -> str | None:
    """
    Определить тип медиа в сообщении.
    Classify the media type in a Telegram message.
    Returns: type string or None if no recognizable media.
    """
    if message.photo:
        return "photo"
    if message.video_note:      # Проверяем ДО video / Check BEFORE video
        return "video_note"
    if message.voice:           # Проверяем ДО audio / Check BEFORE audio
        return "voice"
    if message.video:
        return "video"
    if message.audio:
        return "audio"
    if message.sticker:
        return "sticker"
    if message.document:
        doc = message.document
        # GIF — это документ с атрибутом Animated / GIF is a document with Animated attr
        if any(isinstance(a, DocumentAttributeAnimated) for a in (doc.attributes or [])):
            return "gif"
        return "document"
    return None


# ═══════════════════════════════════════════════════════════════════
#  ФОРМАТИРОВАНИЕ / FORMATTING HELPERS
# ═══════════════════════════════════════════════════════════════════

def format_size(size_bytes: int) -> str:
    """Форматировать размер файла. / Format file size."""
    if size_bytes < 1024:
        return f"{size_bytes} Б"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} КБ"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} МБ"
    else:
        return f"{size_bytes / 1024 ** 3:.2f} ГБ"


def format_duration(seconds: float) -> str:
    """Форматировать длительность в ЧЧ:ММ:СС. / Format duration as HH:MM:SS."""
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


# ═══════════════════════════════════════════════════════════════════
#  ДВИЖОК ПАРСИНГА / SCRAPER ENGINE
# ═══════════════════════════════════════════════════════════════════

class ScraperCore:
    """
    Асинхронный движок скачивания медиа из Telegram-канала.
    Async engine for downloading media from a Telegram channel.

    Возможности / Features:
    - MTProto шифрование (как в оф. Telegram) / MTProto encryption
    - Автоматическое переподключение / Auto-reconnect
    - Повтор скачивания при ошибках (до max_retries раз) / Retry on errors
    - Проверка целостности файлов / File integrity verification
    - Скачивание в максимальном качестве / Max quality downloads
    - Раздельные папки для каждого канала / Per-channel directories
    """

    def __init__(self):
        self.config: dict = load_config()
        self.client: TelegramClient | None = None
        self.stats = ScraperStats()
        self._stop = asyncio.Event()
        self.is_running = False
        self.is_subscribing = False

        # Коллбэки — устанавливаются GUI-ом / Callbacks — set by GUI
        self.on_log = None            # (dict) -> None
        self.on_progress = None       # (float, int, int) -> None — fraction, done, total
        self.on_stats = None          # (ScraperStats) -> None
        self._dl_semaphore = None
        self._dl_tasks = []
        self.on_status = None         # (str) -> None
        self.on_complete = None       # () -> None
        self.on_error = None          # (str) -> None
        self.on_qr_url = None         # (str) -> None
        self.request_input = None     # async (title, prompt) -> str | None

    def _get_history_file(self, channel_id):
        return os.path.join(os.path.dirname(__file__), f"history_{channel_id}.txt")

    def _load_downloaded_ids(self, channel_id) -> set:
        path = self._get_history_file(channel_id)
        if not os.path.exists(path):
            return set()
        ids = set()
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        ids.add(line)
        except:
            pass
        return ids

    def _mark_as_downloaded(self, channel_id, msg_id):
        path = self._get_history_file(channel_id)
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"{msg_id}\n")
        except:
            pass

    # ── Подключение / Авторизация ─────────────────────────────
    #    Connection / Authorization

    def _make_client(self) -> TelegramClient:
        """
        Создать клиент Telethon с защищённым соединением.
        Create Telethon client with secure connection settings.

        БЕЗОПАСНОСТЬ / SECURITY:
        Telethon использует протокол MTProto — тот же протокол шифрования,
        что и официальные приложения Telegram. Все данные шифруются
        между клиентом и серверами Telegram.

        Telethon uses the MTProto protocol — the same encryption protocol
        as official Telegram apps. All data is encrypted between the
        client and Telegram servers.
        """
        return TelegramClient(
            "telegram_session",
            int(self.config["api_id"]),
            self.config["api_hash"],
            # === Настройки безопасности и надёжности ===
            # === Security and reliability settings ===
            connection_retries=10,    # Автоповтор подключения / Auto-retry connection
            retry_delay=2,            # Задержка между попытками (сек) / Delay between retries
            auto_reconnect=True,      # Автопереподключение при обрыве / Auto-reconnect on drop
            request_retries=5,        # Повтор неудачных API-запросов / Retry failed API requests
            flood_sleep_threshold=60, # Авто-ожидание FloodWait до 60с / Auto-wait FloodWait up to 60s
        )

    async def connect(self):
        """Подключиться к Telegram (MTProto). / Connect to Telegram (MTProto)."""
        self.client = self._make_client()
        await self.client.connect()

    async def is_authorized(self) -> bool:
        """Проверить авторизацию. / Check authorization status."""
        if self.client is None or not self.client.is_connected():
            return False
        return await self.client.is_user_authorized()

    async def authorize(self) -> bool:
        """
        Полный цикл авторизации с диалогами для кода и 2FA.
        Full authorization flow with code and 2FA dialogs.
        """
        if self.client is None:
            await self.connect()

        if await self.client.is_user_authorized():
            self._emit("on_status", "✅ Уже авторизован / Already authorized")
            return True

        self._emit("on_status", "⏳ Требуется авторизация / Auth required...")

        # Запрашиваем выбор метода / Request method selection
        auth_method = await self.request_input("Авторизация", "AUTH_MODE")
        if not auth_method:
            return False

        if auth_method == "QR":
            try:
                qr_login = await self.client.qr_login()
                self._emit("on_qr_url", qr_login.url)
                
                # Wait for user to scan QR code / authorize via browser (timeout 120s)
                try:
                    await asyncio.wait_for(qr_login.wait(), timeout=120)
                except asyncio.TimeoutError:
                    self._emit("on_auth_error", "Время ожидания авторизации истекло / Auth timeout")
                    return False
            except errors.SessionPasswordNeededError:
                pwd = await self.request_input("Двухфакторная аутентификация", "Введите пароль 2FA:")
                if not pwd: return False
                try:
                    await self.client.sign_in(password=pwd)
                except Exception as e:
                    self._emit("on_auth_error", f"Ошибка 2FA (QR): {e}")
                    return False
            except Exception as e:
                self._emit("on_auth_error", f"Ошибка QR авторизации / QR Auth error: {e}")
                return False
        else:
            # Phone auth
            phone = self.config.get("phone", "").strip()
            if not phone:
                phone = await self.request_input("Телефон", "Введите номер телефона (с +):")
                if not phone: return False

            try:
                res = await self.client.send_code_request(phone)
            except Exception as e:
                self._emit("on_auth_error", f"Ошибка отправки кода / Code send error: {e}")
                return False

            code = await self.request_input("Код подтверждения", "Введите код из Telegram:")
            if not code: return False

            try:
                await self.client.sign_in(phone, code.strip(), phone_code_hash=res.phone_code_hash)
            except errors.SessionPasswordNeededError:
                pwd = await self.request_input("Двухфакторная аутентификация", "Введите пароль 2FA:")
                if not pwd: return False
                try:
                    await self.client.sign_in(password=pwd)
                except Exception as e:
                    self._emit("on_auth_error", f"Ошибка 2FA: {e}")
                    return False
            except Exception as e:
                self._emit("on_auth_error", f"Ошибка входа / Login error: {e}")
                return False

        self._emit("on_status", "✅ Авторизация успешна! / Authorization successful!")
        return True

    async def disconnect(self):
        """Отключиться от Telegram. / Disconnect from Telegram."""
        if self.client and self.client.is_connected():
            await self.client.disconnect()

    # ── Скачивание / Download ─────────────────────────────────

    async def start_download(self):
        """
        Запустить полное скачивание канала.
        Start full channel download.
        """
        self._stop.clear()
        self.is_running = True
        self.stats = ScraperStats()
        self.stats.start_time = time.time()

        try:
            await self._run_download()
        except asyncio.CancelledError:
            self._emit("on_status", "⏹ Остановлено / Stopped")
        except Exception as e:
            self._emit("on_error", f"Критическая ошибка / Critical error: {e}")
        finally:
            self.is_running = False
            self._emit("on_complete")

    async def stop(self):
        """Остановить текущую операцию. / Stop current operation."""
        self._stop.set()
        self.is_subscribing = False

    async def start_monitor(self):
        """
        Режим Live-мониторинга. Ищет новые посты, но не скачивает их автоматически.
        Live-monitor mode. Finds new posts but doesn't auto-download them.
        """
        self._stop.clear()
        self.is_subscribing = True
        self.is_running = True
        
        interval = float(self.config.get("subscribe_interval", 600))

        try:
            while not self._stop.is_set() and self.is_subscribing:
                self._emit("on_status", "🔄 Проверка новых постов... / Checking for new posts...")
                await self._check_new_posts()
                
                if self._stop.is_set() or not self.is_subscribing:
                    break
                
                self._emit("on_status", f"⏳ Ожидание {interval} сек... / Waiting {interval} sec...")
                
                waited = 0
                while waited < interval:
                    if self._stop.is_set() or not self.is_subscribing:
                        break
                    await asyncio.sleep(1)
                    waited += 1

        except asyncio.CancelledError:
            self._emit("on_status", "⏹ Мониторинг остановлен / Monitoring stopped")
        except Exception as e:
            self._emit("on_error", f"Ошибка мониторинга / Monitor error: {e}")
        finally:
            self.is_subscribing = False
            self.is_running = False
            self._emit("on_complete")

    async def scan_missing_posts(self):
        """Сканирует канал и ищет сообщения, которых нет в базе."""
        channel = await self._resolve_channel()
        if not channel: return
        downloaded_ids = self._load_downloaded_ids(channel.id)
        
        self.is_running = True
        self._stop.clear()
        self._emit("on_status", "🔍 Сканирование канала на пропущенные файлы... / Scanning for missing files...")
        
        missing_count = 0
        total_count = 0
        try:
            async for message in self.client.iter_messages(channel):
                if self._stop.is_set():
                    break
                total_count += 1
                if str(message.id) not in downloaded_ids and not message.action:
                    if self._has_downloadable_media(message) or (message.replies and message.replies.replies > 0):
                        missing_count += 1
                        
            if not self._stop.is_set():
                self._emit("on_status", f"📊 Найдено {missing_count} пропущенных постов (Всего в истории скачано: {len(downloaded_ids)})")
                self._emit("on_log", {"level": "INFO", "msg": f"Сканирование завершено. Пропущено: {missing_count} шт."})
        except Exception as e:
            self._emit("on_error", f"Ошибка сканирования: {e}")
        finally:
            self.is_running = False

    async def download_missing_posts(self):
        """Скачивает только пропущенные сообщения."""
        channel = await self._resolve_channel()
        if not channel: return
        downloaded_ids = self._load_downloaded_ids(channel.id)
        
        ch_state = get_channel_state(self.config)
        dl_dir = ch_state.get("download_dir", "downloads")
        os.makedirs(dl_dir, exist_ok=True)
        
        self.is_running = True
        self._stop.clear()
        
        self._dl_semaphore = asyncio.Semaphore(3)
        self._dl_tasks = []
        
        self._emit("on_status", "🔍 Поиск пропущенных постов для скачивания...")
        missing_msgs = []
        try:
            async for message in self.client.iter_messages(channel):
                if self._stop.is_set(): break
                if str(message.id) not in downloaded_ids and not message.action:
                    if self._has_downloadable_media(message) or (message.replies and message.replies.replies > 0):
                        missing_msgs.append(message)
                        
            if not missing_msgs:
                self._emit("on_status", "✅ Пропущенных постов не найдено!")
                return
                
            self._emit("on_status", f"📥 Начинаем докачку {len(missing_msgs)} постов...")
            
            # Скачиваем в обратном порядке (от старых к новым)
            total_missing = len(missing_msgs)
            for i, message in enumerate(reversed(missing_msgs), 1):
                if self._stop.is_set(): break
                
                self._emit("on_status", f"Докачка {i}/{total_missing} (Пост #{message.id})")
                prefix = f"missing_{message.id}"
                
                if self._has_downloadable_media(message):
                    await self._dispatch_download(message, prefix, dl_dir, is_comment=False)
                    
                if message.replies and message.replies.replies > 0:
                    await self._process_comments(channel, message, message.id, dl_dir)
                    
            if self._dl_tasks:
                self._emit("on_status", "⏳ Докачиваем медиа...")
                await asyncio.gather(*self._dl_tasks, return_exceptions=True)
                self._dl_tasks.clear()
                
            if not self._stop.is_set():
                self._emit("on_status", "✅ Докачка завершена!")
                
        except Exception as e:
            self._emit("on_error", f"Ошибка докачки: {e}")
        finally:
            self.is_running = False
            self._emit("on_complete")

    async def _check_new_posts(self):
        """Проверка и скачивание новых постов в Live-режиме. / Check and download new posts in Live mode."""
        channel = await self._resolve_channel()
        if channel is None: return

        ch_state = get_channel_state(self.config)
        dl_dir = ch_state.get("download_dir", "downloads")
        os.makedirs(dl_dir, exist_ok=True)
        
        last_msg_id = ch_state.get("last_msg_id", 0)
        post_counter = ch_state.get("post_counter", 0)

        if last_msg_id == 0:
            self._emit("on_status", "Внимание: Это первый запуск! Рекомендуется сделать полный дамп канала через вкладку Download.")

        new_count = 0
        last_grouped_id = None
        album_index = 0

        messages_to_download = []
        try:
            async for message in self.client.iter_messages(channel, min_id=last_msg_id, reverse=True):
                if self._stop.is_set() or not self.is_subscribing:
                    break
                messages_to_download.append(message)
        except Exception as e:
            self._emit("on_error", f"Ошибка проверки новых постов: {e}")
            return
            
        if not messages_to_download:
            return

        self._dl_semaphore = asyncio.Semaphore(3)
        self._dl_tasks = []

        for message in messages_to_download:
            if self._stop.is_set():
                break
                
            if message.grouped_id:
                if message.grouped_id != last_grouped_id:
                    post_counter += 1
                    last_grouped_id = message.grouped_id
                    album_index = 1
                else:
                    album_index += 1
            else:
                post_counter += 1
                last_grouped_id = None
                album_index = 0
                
            has_media = self._has_downloadable_media(message)
            if has_media:
                pfx = f"{post_counter}-{album_index}" if message.grouped_id else f"{post_counter}"
                await self._dispatch_download(message, pfx, dl_dir)
                new_count += 1
            else:
                self._emit("on_log", {"msg": f"Пропуск поста #{post_counter} (нет медиа и комментариев)"})
                
            ch_state["last_msg_id"] = message.id
            ch_state["post_counter"] = post_counter
            ch_state["processed_msgs"] = ch_state.get("processed_msgs", 0) + 1

        if self._dl_tasks:
            await asyncio.gather(*self._dl_tasks, return_exceptions=True)
            self._dl_tasks.clear()
            
        from scraper_core import save_config
        save_config(self.config)
        
        if new_count > 0:
            self._emit("on_status", f"✅ Скачано {new_count} новых файлов! / Downloaded {new_count} new files!")



    async def _run_download(self):
        """
        Основной цикл скачивания: итерация по всем сообщениям канала
        от первого к последнему, скачивание медиа и комментариев.
        Main download loop: iterate all channel messages from oldest
        to newest, downloading media and comments.
        """
        channel = await self._resolve_channel()
        if channel is None:
            return

        # Получаем состояние канала / Get channel state
        ch_state = get_channel_state(self.config)
        dl_dir = ch_state.get("download_dir", "downloads")
        os.makedirs(dl_dir, exist_ok=True)

        # Общее количество сообщений для прогресс-бара / Total messages for progress bar
        total_info = await self.client.get_messages(channel, limit=0)
        self.stats.total_channel_msgs = total_info.total
        title = getattr(channel, "title", str(channel.id))
        self._emit(
            "on_status",
            f"Канал: {title} — {total_info.total} сообщений / messages"
        )

        # Настраиваем семафор для 3 параллельных скачиваний
        self._dl_semaphore = asyncio.Semaphore(3)
        self._dl_tasks = []

        # Восстановление прогресса / Resume progress
        post_counter = ch_state.get("post_counter", 0)
        last_msg_id = ch_state.get("last_msg_id", 0)
        previously_processed = ch_state.get("processed_msgs", 0)
        last_grouped_id = None
        album_index = 0
        processed_this_run = 0

        if last_msg_id > 0:
            self._emit(
                "on_status",
                f"▶ Продолжение с поста #{post_counter}, сообщение #{last_msg_id}"
                f" / Resuming from post #{post_counter}, msg #{last_msg_id}"
            )

        # Итерация от старого к новому / Iterate oldest to newest
        iter_kw = {"reverse": True}
        if last_msg_id > 0:
            iter_kw["min_id"] = last_msg_id

        async for message in self.client.iter_messages(channel, **iter_kw):
            if self._stop.is_set():
                self._emit("on_status", "⏹ Остановлено пользователем / Stopped by user")
                break

            processed_this_run += 1
            total_done = previously_processed + processed_this_run
            self.stats.processed_msgs = total_done

            # Пропускаем сервисные сообщения / Skip service messages
            if message.action:
                self._update_progress(total_done)
                continue

            # ── Нумерация (с поддержкой альбомов) ──
            # ── Numbering (with album support) ──
            if message.grouped_id:
                if message.grouped_id != last_grouped_id:
                    post_counter += 1
                    last_grouped_id = message.grouped_id
                    album_index = 1
                    is_first_in_group = True
                else:
                    album_index += 1
                    is_first_in_group = False
            else:
                post_counter += 1
                last_grouped_id = None
                album_index = 0
                is_first_in_group = True

            self.stats.current_post_num = post_counter
            self._emit(
                "on_status",
                f"📥 Пост #{post_counter} (сообщение {total_done}/{self.stats.total_channel_msgs})"
            )

            # ── Скачивание медиа поста / Download post media ──
            has_media = self._has_downloadable_media(message)
            if has_media:
                prefix = (
                    f"{post_counter}-{album_index}"
                    if message.grouped_id
                    else f"{post_counter}"
                )
                await self._dispatch_download(message, prefix, dl_dir, is_comment=False)

            # ── Скачивание комментариев / Download comments ──
            has_comments = is_first_in_group and message.replies and message.replies.replies > 0
            if has_comments:
                await self._process_comments(channel, message, post_counter, dl_dir)

            if not has_media and not has_comments:
                self._emit("on_log", {"msg": f"Пропуск поста #{post_counter} (нет медиа и комментариев)"})

            # ── Сохранение состояния / Save state ──
            ch_state["last_msg_id"] = message.id
            ch_state["post_counter"] = post_counter
            ch_state["processed_msgs"] = total_done
            save_config(self.config)

            self._update_progress(total_done)
            await asyncio.sleep(self.config.get("delay_between_posts", 1.0))

        # Дожидаемся всех активных фоновых загрузок
        if self._dl_tasks:
            self._emit("on_status", "⏳ Докачиваем медиа... / Waiting for downloads to finish...")
            await asyncio.gather(*self._dl_tasks, return_exceptions=True)
            self._dl_tasks.clear()

        self._emit("on_status", "✅ Скачивание завершено! / Download complete!")
        self._emit("on_log", {"level": "INFO", "msg": "Автоматический переход в Live-мониторинг..."})
        self._emit("on_complete", None)
        
        # Автоматический запуск мониторинга
        await self.start_monitor()

    async def _dispatch_download(self, message, prefix, dl_dir, is_comment=False):
        """Обертка для постановки в очередь с семафором."""
        await self._dl_semaphore.acquire()
        
        async def _task():
            try:
                await self._download_file(message, prefix, dl_dir, is_comment=is_comment)
            finally:
                self._dl_semaphore.release()
                
        # Удаляем завершенные задачи из списка, чтобы не было утечек памяти
        self._dl_tasks = [t for t in self._dl_tasks if not t.done()]
        self._dl_tasks.append(asyncio.create_task(_task()))

    async def _process_comments(self, channel, message, post_counter: int, dl_dir: str):
        """
        Скачать медиа из комментариев к посту.
        Download media from post comments.
        """
        self.stats.current_post_comments_total = message.replies.replies
        self.stats.current_post_comments_done = 0

        comment_file_idx = 0
        try:
            async for comment in self.client.iter_messages(
                channel, reply_to=message.id, reverse=True
            ):
                if self._stop.is_set():
                    break

                self.stats.current_post_comments_done += 1

                if self._has_downloadable_media(comment):
                    comment_file_idx += 1
                    prefix = f"{post_counter}_{comment_file_idx}"
                    await self._download_file(comment, prefix, dl_dir, is_comment=True)

                await asyncio.sleep(
                    self.config.get("delay_between_comments", 0.5)
                )

        except errors.FloodWaitError as e:
            await self._handle_flood(e)
        except Exception as e:
            self._emit(
                "on_error",
                f"Ошибка комментариев поста #{post_counter} / Comment error: {e}"
            )
            
        # Отмечаем пост как проработанный (даже если у него нет медиа, комментарии мы проверили)
        if hasattr(message, "id") and self.config.get("channel_id"):
            self._mark_as_downloaded(self.config["channel_id"], str(message.id))

    # ── Скачивание с повторами и проверкой / Download with retry & integrity ──

    async def _download_file(
        self, message, prefix: str, dl_dir: str, *, is_comment: bool
    ):
        """
        Скачать один медиафайл с полной обработкой ошибок:
        - Повтор при ошибках сети (до max_retries раз)
        - Ожидание восстановления сети
        - Проверка целостности скачанного файла
        - Автоматическая перекачка повреждённых файлов

        Download a single media file with full error handling:
        - Retry on network errors (up to max_retries times)
        - Wait for network recovery
        - Verify downloaded file integrity
        - Auto-redownload corrupted files

        КАЧЕСТВО / QUALITY:
        Telethon скачивает фото и видео в максимальном доступном качестве.
        Для фото — наибольший доступный размер (PhotoSize).
        Для видео — оригинальный файл без сжатия.

        Telethon downloads photos and videos at maximum available quality.
        Photos: largest available PhotoSize.
        Videos: original file without compression.
        """
        file_path = os.path.join(dl_dir, prefix)
        max_retries = self.config.get("max_retries", 30)
        
        mtype = classify_media(message) or "файл"
        target_name_gen = "комментария" if is_comment else "поста"
        target_name_nom = "комментарий" if is_comment else "пост"
        
        # Подробный лог старта скачивания
        self._emit("on_log", {"msg": f"⬇️ Начато скачивание {target_name_gen} #{prefix} ({mtype})..."})
        
        def progress_cb(received, total):
            if self._stop.is_set():
                raise asyncio.CancelledError()
            if total > 0 and self.on_progress:
                frac = received / total
                self._emit("on_progress", prefix, frac, received, total)

        for attempt in range(1, max_retries + 1):
            try:
                # Проверяем соединение / Check connection
                if not self.client.is_connected():
                    await self._wait_for_network()

                # Скачиваем медиа (максимальное качество по умолчанию)
                # Download media (max quality by default)
                downloaded = await self.client.download_media(
                    message, file=file_path, progress_callback=progress_cb
                )

                if not downloaded:
                    raise Exception("download_media returned False")
                    
                self._emit("on_progress_end", prefix)

                # ── Проверка целостности / Integrity check ──
                if not self._verify_file(downloaded, message):
                    self.stats.integrity_failures += 1
                    # Удаляем повреждённый файл / Remove corrupt file
                    try:
                        os.remove(downloaded)
                    except OSError:
                        pass
                    raise RuntimeError(
                        f"Целостность файла нарушена / File integrity failed: {downloaded}"
                    )

                # ── Успешно скачано / Successfully downloaded ──
                fsize = os.path.getsize(downloaded)
                mtype = classify_media(message) or "unknown"
                
                # Подробный лог успешного скачивания
                self._emit("on_log", {"msg": f"✅ Успешно скачан {target_name_nom} #{prefix} ({mtype}, {format_size(fsize)})"})

                # Обновляем статистику / Update statistics
                self.stats.total_files += 1
                self.stats.total_size_bytes += fsize
                if is_comment:
                    self.stats.downloaded_comment_files += 1
                else:
                    self.stats.downloaded_post_files += 1

                if mtype in _TYPE_TO_STAT:
                    attr = _TYPE_TO_STAT[mtype]
                    setattr(self.stats, attr, getattr(self.stats, attr) + 1)

                # Лог-запись со ссылкой / Log entry with link
                channel_id = self.config["channel_id"]
                link = f"https://t.me/c/{channel_id}/{message.id}"

                entry = {
                    "num": prefix,
                    "type": "Комментарий" if is_comment else "Пост",
                    "file": os.path.basename(downloaded),
                    "media_type": _TYPE_LABELS.get(mtype, mtype),
                    "link": link,
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "size": format_size(fsize),
                    "size_bytes": fsize,
                }
                self._emit("on_log", entry)
                self._emit("on_stats", self.stats)
                
                # Записываем в базу загрузок
                channel_id = self.config["channel_id"]
                history_id = f"c{message.id}" if is_comment else str(message.id)
                self._mark_as_downloaded(channel_id, history_id)
                
                return  # Успех / Success

            except errors.FloodWaitError as e:
                # FloodWait — не считается как попытка / Not counted as an attempt
                await self._handle_flood(e)
                continue

            except (ConnectionError, OSError, TimeoutError, ConnectionResetError) as e:
                # Ошибка сети — ждём и повторяем / Network error — wait and retry
                self.stats.retries_total += 1
                if attempt >= max_retries:
                    self._emit(
                        "on_error",
                        f"❌ Не удалось скачать {prefix} после {max_retries} попыток: {e}"
                    )
                    self._emit("on_progress_end", prefix)
                    return

                wait = min(2 ** min(attempt, 6), 60)  # Макс 60 сек / Max 60 sec
                self._emit(
                    "on_status",
                    f"📡 Ошибка сети ({attempt}/{max_retries}): {e}. "
                    f"Повтор через {wait}с / Retry in {wait}s..."
                )
                await self._wait_for_network(max_wait=wait)

            except Exception as e:
                # Любая другая ошибка / Any other error
                self.stats.retries_total += 1
                if attempt >= max_retries:
                    self._emit(
                        "on_error",
                        f"❌ Не удалось скачать {prefix} после {max_retries} попыток: {e}"
                    )
                    self._emit("on_progress_end", prefix)
                    return

                wait = min(2 ** min(attempt, 5), 30)
                self._emit(
                    "on_status",
                    f"⚠️ Ошибка ({attempt}/{max_retries}): {e}. "
                    f"Повтор через {wait}с / Retry in {wait}s..."
                )
                await asyncio.sleep(wait)

    def _verify_file(self, filepath: str, message) -> bool:
        """
        Проверка целостности скачанного файла.
        Verify downloaded file integrity.

        Проверки / Checks:
        1. Файл существует / File exists
        2. Размер > 0 / Size > 0
        3. Для документов/видео: размер совпадает с ожидаемым / For docs/video: size matches expected
        """
        if not os.path.exists(filepath):
            return False

        file_size = os.path.getsize(filepath)
        if file_size == 0:
            return False

        # Для документов (видео, аудио, файлы) — точная проверка размера
        # For documents (video, audio, files) — exact size check
        if message.document and message.document.size:
            expected = message.document.size
            if file_size != expected:
                self._emit(
                    "on_status",
                    f"⚠️ Размер не совпадает: {file_size} ≠ {expected} байт"
                    f" / Size mismatch: {file_size} ≠ {expected} bytes"
                )
                return False

        return True

    # ── Сетевая устойчивость / Network resilience ─────────────

    async def _wait_for_network(self, max_wait: int = 300):
        """
        Ожидание восстановления сетевого соединения.
        Wait until network connection is restored.

        Периодически пытается переподключиться к Telegram.
        Periodically attempts to reconnect to Telegram.

        Args:
            max_wait: Максимальное время ожидания (сек) / Max wait time (sec)
        """
        interval = self.config.get("network_check_interval", 5)
        waited = 0

        while waited < max_wait:
            if self._stop.is_set():
                return

            try:
                if not self.client.is_connected():
                    await self.client.connect()

                # Проверяем, что соединение действительно работает
                # Verify the connection actually works
                if await self.client.is_user_authorized():
                    return  # Соединение восстановлено / Connection restored
                return  # Подключены, но не авторизованы — продолжаем

            except Exception:
                self._emit(
                    "on_status",
                    f"📡 Ожидание сети ({waited}с)... / Waiting for network ({waited}s)..."
                )
                await asyncio.sleep(interval)
                waited += interval

    async def _reconnect(self):
        """
        Безопасное переподключение к Telegram.
        Safely reconnect to Telegram.
        """
        try:
            if self.client.is_connected():
                await self.client.disconnect()
        except Exception:
            pass

        try:
            await self.client.connect()
        except Exception:
            # Полное пересоздание клиента / Full client recreation
            self.client = self._make_client()
            await self.client.connect()



    # ── Вспомогательные методы / Helper methods ───────────────

    @staticmethod
    def _has_downloadable_media(message) -> bool:
        """Есть ли скачиваемое медиа. / Check if message has downloadable media."""
        return message.media is not None and not isinstance(
            message.media, _SKIP_MEDIA
        )

    async def _resolve_channel(self):
        """
        Получить сущность канала по ID.
        Resolve channel entity by ID.
        """
        cid = self.config.get("channel_id", 0)
        # Telegram channel IDs have -100 prefix internally
        try:
            return await self.client.get_entity(int(f"-100{cid}"))
        except Exception:
            pass
        try:
            return await self.client.get_entity(cid)
        except Exception as e:
            self._emit("on_error", f"Канал {cid} не найден / Channel not found: {e}")
            return None

    async def _handle_flood(self, exc: errors.FloodWaitError):
        """
        Обработка FloodWait от Telegram.
        Handle Telegram's FloodWait error.
        """
        mult = self.config.get("flood_wait_multiplier", 1.5)
        wait = int(exc.seconds * mult)
        self._emit(
            "on_status",
            f"⚠️ FloodWait — пауза {wait}с... / FloodWait — pausing {wait}s..."
        )
        await asyncio.sleep(wait)

    def _update_progress(self, done: int):
        """Обновить прогресс-бар и предиктор размера. / Update progress and size predictor."""
        total = self.stats.total_channel_msgs
        frac = done / total if total > 0 else 0.0
        self._emit("on_progress_overall", frac, done, total)

        # Предиктор размера каждые 100 сообщений
        if done > 0 and done % 100 == 0 and self.stats.total_files > 0:
            import shutil
            avg_size = self.stats.total_size_bytes / self.stats.total_files
            files_per_msg = self.stats.total_files / done
            predicted_total_files = total * files_per_msg
            predicted_size = predicted_total_files * avg_size
            
            try:
                ch_state = get_channel_state(self.config)
                dl_dir = ch_state.get("download_dir", "downloads")
                os.makedirs(dl_dir, exist_ok=True)
                free_space = shutil.disk_usage(dl_dir).free
                
                # Если прогноз больше свободного места, логируем
                if predicted_size > free_space:
                    from util import format_size
                    self._emit("on_log", {
                        "level": "WARN",
                        "msg": f"⚠️ Ожидаемый размер: {format_size(predicted_size)}. Свободно: {format_size(free_space)}."
                    })
            except Exception:
                pass

    def _emit(self, name: str, *args):
        """
        Вызвать коллбэк по имени (thread-safe обёртка на стороне GUI).
        Invoke callback by name (thread-safe wrapper is on the GUI side).
        """
        cb = getattr(self, name, None)
        if cb:
            cb(*args)
