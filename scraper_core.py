"""
Telegram Secret Channel Downloader — Core Engine
=================================================
Async engine for downloading ALL content types from Telegram channels:
posts (text + media), comments, and metadata. Supports:
  - MTProto encrypted connection (same as official Telegram)
  - Network resilience with auto-reconnect and retry
  - File integrity verification
  - Max quality media downloads
  - Per-channel download directories
  - Structured data export to channel_data.json for offline HTML viewer
"""

import os
import json
import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from i18n import t
from telethon import TelegramClient, errors
from telethon.tl.types import (
    MessageMediaWebPage,       # Link previews
    MessageMediaPoll,          # Polls
    MessageMediaGeo,           # Geolocation
    MessageMediaGeoLive,       # Live geolocation
    MessageMediaContact,       # Contacts
    MessageMediaDice,          # Dice/emoji
    MessageMediaVenue,         # Venues
    DocumentAttributeAnimated, # GIF animation attribute
    DocumentAttributeFilename, # Document filename attribute
)


# ═══════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    # --- Telegram API ---
    "api_id": 2040,
    "api_hash": "b18441a1ff607e10a989891a5462e627",
    "phone": "",

    # --- Current channel ---
    "channel_id": 0,
    "download_dir": "downloads",

    # --- Delays (seconds) ---
    "delay_between_posts": 1.0,
    "delay_between_comments": 0.5,
    "flood_wait_multiplier": 1.5,
    "subscribe_interval": 60,

    # --- Network resilience ---
    "max_retries": 30,
    "network_check_interval": 5,

    # --- Per-channel state (populated automatically) ---
    "channels": {},
}

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
    Load configuration from file or return defaults.

    Handles migration from old single-channel format to per-channel state.
    Falls back to Telegram Desktop API credentials if none provided.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        cfg = DEFAULT_CONFIG.copy()
        cfg.update(saved)

        # Fall back to Telegram Desktop credentials if empty
        if not cfg.get("api_id") or str(cfg.get("api_id")) == "0" or not cfg.get("api_hash"):
            cfg["api_id"] = 2040
            cfg["api_hash"] = "b18441a1ff607e10a989891a5462e627"

        # Migrate old single-channel format to per-channel state
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
    """Save configuration dictionary to the config file."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_channel_state(config: dict) -> dict:
    """
    Get the state for the currently selected channel.

    Returns a dict with download_dir, last_msg_id, post_counter,
    and processed_msgs. Creates default state if the channel is new.
    """
    cid = str(config.get("channel_id", 0))
    channels = config.setdefault("channels", {})
    if cid not in channels:
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
#  STATISTICS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ScraperStats:
    """Tracks download statistics for a scraping session."""
    total_channel_msgs: int = 0
    processed_msgs: int = 0
    downloaded_post_files: int = 0
    downloaded_comment_files: int = 0
    total_files: int = 0
    total_size_bytes: int = 0
    text_posts: int = 0
    # Breakdown by media type
    photos: int = 0
    videos: int = 0
    documents: int = 0
    voices: int = 0
    video_notes: int = 0
    audio_files: int = 0
    stickers: int = 0
    gifs: int = 0
    # Progress tracking
    start_time: float = 0.0
    current_post_num: int = 0
    current_post_comments_total: int = 0
    current_post_comments_done: int = 0
    # Network resilience counters
    retries_total: int = 0
    integrity_failures: int = 0


# ═══════════════════════════════════════════════════════════════════
#  MEDIA CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════

# Mapping of media type string to ScraperStats field name
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

# Mapping of media type string to i18n translation key
_TYPE_LABEL_KEYS = {
    "photo": "media_photo",
    "video": "media_video",
    "document": "media_document",
    "voice": "media_voice",
    "video_note": "media_video_note",
    "audio": "media_audio",
    "sticker": "media_sticker",
    "gif": "media_gif",
    "unknown": "media_unknown",
    "text": "media_text",
}


def classify_media(message) -> str | None:
    """
    Classify the media type in a Telegram message.

    Checks message attributes in priority order to correctly identify
    video notes before videos, and voice messages before audio.

    Returns:
        Media type string ('photo', 'video', etc.) or None if no media.
    """
    if message.photo:
        return "photo"
    if message.video_note:
        return "video_note"
    if message.voice:
        return "voice"
    if message.video:
        return "video"
    if message.audio:
        return "audio"
    if message.sticker:
        return "sticker"
    if message.document:
        doc = message.document
        if any(isinstance(a, DocumentAttributeAnimated) for a in (doc.attributes or [])):
            return "gif"
        return "document"
    return None


# ═══════════════════════════════════════════════════════════════════
#  FORMATTING HELPERS
# ═══════════════════════════════════════════════════════════════════

def format_size(size_bytes: int) -> str:
    """Format a byte count into a human-readable size string."""
    if size_bytes < 1024:
        return t("size_b", size_bytes)
    elif size_bytes < 1024 ** 2:
        return t("size_kb", size_bytes / 1024)
    elif size_bytes < 1024 ** 3:
        return t("size_mb", size_bytes / 1024 ** 2)
    else:
        return t("size_gb", size_bytes / 1024 ** 3)


def format_duration(seconds: float) -> str:
    """Format a duration in seconds to HH:MM:SS string."""
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


# ═══════════════════════════════════════════════════════════════════
#  SCRAPER ENGINE
# ═══════════════════════════════════════════════════════════════════

class ScraperCore:
    """
    Async engine for downloading all content from a Telegram channel.

    Features:
    - MTProto encryption (same as official Telegram apps)
    - Auto-reconnect on network drops
    - Retry on download errors (up to max_retries)
    - File integrity verification
    - Max quality media downloads
    - Per-channel download directories
    - Structured data collection for offline HTML viewer
    """

    def __init__(self):
        """Initialize the scraper with default config and empty state."""
        self.config: dict = load_config()
        self.client: TelegramClient | None = None
        self.stats = ScraperStats()
        self._stop = asyncio.Event()
        self.is_running = False
        self.is_subscribing = False

        # Collected post data for HTML export
        self.posts_data: list[dict] = []

        # Callbacks set by the GUI layer
        self.on_log = None            # (dict) -> None
        self.on_progress = None       # (prefix, frac, done, total) -> None
        self.on_stats = None          # (ScraperStats) -> None
        self._dl_semaphore = None
        self._dl_tasks = []
        self.on_status = None         # (str) -> None
        self.on_complete = None       # () -> None
        self.on_error = None          # (str) -> None
        self.on_qr_url = None         # (str) -> None
        self.request_input = None     # async (title, prompt) -> str | None

    def _get_history_file(self, channel_id) -> str:
        """Return the path to the download history file for a channel."""
        return os.path.join(os.path.dirname(__file__), f"history_{channel_id}.txt")

    def _load_downloaded_ids(self, channel_id) -> set:
        """
        Load the set of already-downloaded message IDs from the history file.

        Returns an empty set if the file doesn't exist or can't be read.
        """
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
        except Exception:
            pass
        return ids

    def _mark_as_downloaded(self, channel_id, msg_id):
        """Append a message ID to the download history file."""
        path = self._get_history_file(channel_id)
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"{msg_id}\n")
        except Exception:
            pass

    # ── Connection / Authorization ──────────────────────────────

    def _make_client(self) -> TelegramClient:
        """
        Create a Telethon client with secure connection settings.

        Uses the MTProto protocol — the same encryption as official
        Telegram apps. All data is encrypted between client and servers.
        """
        return TelegramClient(
            "telegram_session",
            int(self.config["api_id"]),
            self.config["api_hash"],
            connection_retries=10,
            retry_delay=2,
            auto_reconnect=True,
            request_retries=5,
            flood_sleep_threshold=60,
        )

    async def connect(self):
        """Establish connection to Telegram via MTProto."""
        self.client = self._make_client()
        await self.client.connect()

    async def is_authorized(self) -> bool:
        """Check if the current session is authorized."""
        if self.client is None or not self.client.is_connected():
            return False
        return await self.client.is_user_authorized()

    async def authorize(self) -> bool:
        """
        Run the full authorization flow.

        Supports both QR code and phone number authentication,
        including two-factor authentication (2FA).
        """
        if self.client is None:
            await self.connect()

        if await self.client.is_user_authorized():
            self._emit("on_status", t("already_authorized"))
            return True

        self._emit("on_status", t("auth_required"))

        # Request auth method selection from the GUI
        auth_method = await self.request_input(t("auth_title"), "AUTH_MODE")
        if not auth_method:
            return False

        if auth_method == "QR":
            try:
                qr_login = await self.client.qr_login()
                self._emit("on_qr_url", qr_login.url)

                try:
                    await asyncio.wait_for(qr_login.wait(), timeout=120)
                except asyncio.TimeoutError:
                    self._emit("on_auth_error", t("auth_timeout"))
                    return False
            except errors.SessionPasswordNeededError:
                pwd = await self.request_input(t("2fa_title"), t("2fa_prompt"))
                if not pwd:
                    return False
                try:
                    await self.client.sign_in(password=pwd)
                except Exception as e:
                    self._emit("on_auth_error", f"{t('2fa_error_qr')} {e}")
                    return False
            except Exception as e:
                self._emit("on_auth_error", f"{t('qr_auth_error')} {e}")
                return False
        else:
            # Phone number authentication
            phone = self.config.get("phone", "").strip()
            if not phone:
                phone = await self.request_input(t("phone_title"), t("phone_prompt"))
                if not phone:
                    return False

            try:
                res = await self.client.send_code_request(phone)
            except Exception as e:
                self._emit("on_auth_error", f"{t('code_send_error')} {e}")
                return False

            code = await self.request_input(t("code_title"), t("code_prompt"))
            if not code:
                return False

            try:
                await self.client.sign_in(phone, code.strip(), phone_code_hash=res.phone_code_hash)
            except errors.SessionPasswordNeededError:
                pwd = await self.request_input(t("2fa_title"), t("2fa_prompt"))
                if not pwd:
                    return False
                try:
                    await self.client.sign_in(password=pwd)
                except Exception as e:
                    self._emit("on_auth_error", f"{t('2fa_error')} {e}")
                    return False
            except Exception as e:
                self._emit("on_auth_error", f"{t('login_error')} {e}")
                return False

        self._emit("on_status", t("auth_success_full"))
        return True

    async def disconnect(self):
        """Disconnect from Telegram gracefully."""
        if self.client and self.client.is_connected():
            await self.client.disconnect()

    # ── Download Operations ─────────────────────────────────────

    async def start_download(self):
        """
        Start the full channel download process.

        Initializes statistics, runs the main download loop,
        and handles cancellation and errors gracefully.
        """
        self._stop.clear()
        self.is_running = True
        self.stats = ScraperStats()
        self.stats.start_time = time.time()
        self.posts_data = []

        try:
            await self._run_download()
        except asyncio.CancelledError:
            self._emit("on_status", t("stopped"))
        except Exception as e:
            self._emit("on_error", t("critical_error", e))
        finally:
            self.is_running = False
            self._emit("on_complete")

    async def stop(self):
        """Signal all running operations to stop."""
        self._stop.set()
        self.is_subscribing = False

    async def start_monitor(self):
        """
        Start live monitoring mode.

        Periodically checks for new posts in the channel and downloads
        them automatically. Runs until stopped by the user.
        """
        self._stop.clear()
        self.is_subscribing = True
        self.is_running = True

        interval = float(self.config.get("subscribe_interval", 600))

        try:
            while not self._stop.is_set() and self.is_subscribing:
                self._emit("on_status", t("checking_new_posts"))
                await self._check_new_posts()

                if self._stop.is_set() or not self.is_subscribing:
                    break

                self._emit("on_status", t("monitor_waiting", interval))

                waited = 0
                while waited < interval:
                    if self._stop.is_set() or not self.is_subscribing:
                        break
                    await asyncio.sleep(1)
                    waited += 1

        except asyncio.CancelledError:
            self._emit("on_status", t("monitor_stopped"))
        except Exception as e:
            self._emit("on_error", t("monitor_error", e))
        finally:
            self.is_subscribing = False
            self.is_running = False
            self._emit("on_complete")

    async def scan_missing_posts(self):
        """
        Scan the channel and count messages not in the download history.

        Reports the number of missing posts without downloading them.
        """
        channel = await self._resolve_channel()
        if not channel:
            return
        downloaded_ids = self._load_downloaded_ids(channel.id)

        self.is_running = True
        self._stop.clear()
        self._emit("on_status", t("scanning_missing"))

        missing_count = 0
        try:
            async for message in self.client.iter_messages(channel):
                if self._stop.is_set():
                    break
                if str(message.id) not in downloaded_ids and not message.action:
                    if self._has_downloadable_media(message) or \
                       message.text or \
                       (message.replies and message.replies.replies > 0):
                        missing_count += 1

            if not self._stop.is_set():
                self._emit("on_status", t("scan_result", missing_count, len(downloaded_ids)))
                self._emit("on_log", {"level": "INFO", "msg": t("scan_complete_log", missing_count)})
        except Exception as e:
            self._emit("on_error", t("scan_error", e))
        finally:
            self.is_running = False

    async def download_missing_posts(self):
        """
        Download only messages that are missing from the download history.

        Iterates all channel messages, skips already-downloaded ones,
        and downloads the rest in chronological order.
        """
        channel = await self._resolve_channel()
        if not channel:
            return
        downloaded_ids = self._load_downloaded_ids(channel.id)

        ch_state = get_channel_state(self.config)
        dl_dir = ch_state.get("download_dir", "downloads")
        os.makedirs(dl_dir, exist_ok=True)

        self.is_running = True
        self._stop.clear()
        self._dl_semaphore = asyncio.Semaphore(3)
        self._dl_tasks = []

        self._emit("on_status", t("searching_missing"))
        missing_msgs = []
        try:
            async for message in self.client.iter_messages(channel):
                if self._stop.is_set():
                    break
                if str(message.id) not in downloaded_ids and not message.action:
                    if self._has_downloadable_media(message) or \
                       message.text or \
                       (message.replies and message.replies.replies > 0):
                        missing_msgs.append(message)

            if not missing_msgs:
                self._emit("on_status", t("no_missing"))
                return

            self._emit("on_status", t("downloading_missing", len(missing_msgs)))

            total_missing = len(missing_msgs)
            for i, message in enumerate(reversed(missing_msgs), 1):
                if self._stop.is_set():
                    break

                self._emit("on_status", t("downloading_missing_item", i, total_missing, message.id))
                prefix = f"missing_{message.id}"

                # Save text content
                if message.text:
                    self._collect_post_data(message, prefix, dl_dir, is_comment=False)

                if self._has_downloadable_media(message):
                    await self._dispatch_download(message, prefix, dl_dir, is_comment=False)

                if message.replies and message.replies.replies > 0:
                    await self._process_comments(channel, message, message.id, dl_dir)

            if self._dl_tasks:
                self._emit("on_status", t("downloading_missing_media"))
                await asyncio.gather(*self._dl_tasks, return_exceptions=True)
                self._dl_tasks.clear()

            if not self._stop.is_set():
                self._emit("on_status", t("downloading_missing_done"))
                self._save_channel_data(dl_dir)

        except Exception as e:
            self._emit("on_error", t("downloading_missing_error", e))
        finally:
            self.is_running = False
            self._emit("on_complete")

    async def _check_new_posts(self):
        """
        Check for and download new posts in live monitoring mode.

        Only processes messages newer than the last saved message ID.
        """
        channel = await self._resolve_channel()
        if channel is None:
            return

        ch_state = get_channel_state(self.config)
        dl_dir = ch_state.get("download_dir", "downloads")
        os.makedirs(dl_dir, exist_ok=True)

        last_msg_id = ch_state.get("last_msg_id", 0)
        post_counter = ch_state.get("post_counter", 0)

        if last_msg_id == 0:
            self._emit("on_status", t("first_run_warning"))

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
            self._emit("on_error", t("monitor_error", e))
            return

        if not messages_to_download:
            return

        self._dl_semaphore = asyncio.Semaphore(3)
        self._dl_tasks = []

        for message in messages_to_download:
            if self._stop.is_set():
                break

            # Album numbering
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

            # Save text content for all posts
            if message.text:
                pfx = f"{post_counter}-{album_index}" if message.grouped_id else f"{post_counter}"
                self._collect_post_data(message, pfx, dl_dir, is_comment=False)

            if has_media:
                pfx = f"{post_counter}-{album_index}" if message.grouped_id else f"{post_counter}"
                await self._dispatch_download(message, pfx, dl_dir)
                new_count += 1
            elif not message.text:
                self._emit("on_log", {"msg": t("skipping_post", post_counter)})

            ch_state["last_msg_id"] = message.id
            ch_state["post_counter"] = post_counter
            ch_state["processed_msgs"] = ch_state.get("processed_msgs", 0) + 1

        if self._dl_tasks:
            await asyncio.gather(*self._dl_tasks, return_exceptions=True)
            self._dl_tasks.clear()

        save_config(self.config)
        self._save_channel_data(dl_dir)

        if new_count > 0:
            self._emit("on_status", t("new_files_downloaded", new_count))

    async def _run_download(self):
        """
        Main download loop: iterate all channel messages from oldest
        to newest, downloading media, saving text, and processing comments.

        Supports resume from the last saved position.
        """
        channel = await self._resolve_channel()
        if channel is None:
            return

        ch_state = get_channel_state(self.config)
        dl_dir = ch_state.get("download_dir", "downloads")
        os.makedirs(dl_dir, exist_ok=True)

        # Get total message count for progress bar
        total_info = await self.client.get_messages(channel, limit=0)
        self.stats.total_channel_msgs = total_info.total
        title = getattr(channel, "title", str(channel.id))
        self._emit("on_status", t("channel_info", title, total_info.total))

        # Semaphore for 3 parallel downloads
        self._dl_semaphore = asyncio.Semaphore(3)
        self._dl_tasks = []

        # Resume progress
        post_counter = ch_state.get("post_counter", 0)
        last_msg_id = ch_state.get("last_msg_id", 0)
        previously_processed = ch_state.get("processed_msgs", 0)
        last_grouped_id = None
        album_index = 0
        processed_this_run = 0

        if last_msg_id > 0:
            self._emit("on_status", t("resuming", post_counter, last_msg_id))

        # Iterate oldest to newest
        iter_kw = {"reverse": True}
        if last_msg_id > 0:
            iter_kw["min_id"] = last_msg_id

        async for message in self.client.iter_messages(channel, **iter_kw):
            if self._stop.is_set():
                self._emit("on_status", t("stopped_by_user"))
                break

            processed_this_run += 1
            total_done = previously_processed + processed_this_run
            self.stats.processed_msgs = total_done

            # Skip service messages (join, leave, pin, etc.)
            if message.action:
                self._update_progress(total_done)
                continue

            # Post numbering with album support
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
                t("processing_post", post_counter, total_done, self.stats.total_channel_msgs)
            )

            # Collect text content for all posts
            if message.text:
                prefix = (
                    f"{post_counter}-{album_index}"
                    if message.grouped_id
                    else f"{post_counter}"
                )
                self._collect_post_data(message, prefix, dl_dir, is_comment=False)
                if not self._has_downloadable_media(message):
                    self.stats.text_posts += 1

            # Download media if present
            has_media = self._has_downloadable_media(message)
            if has_media:
                prefix = (
                    f"{post_counter}-{album_index}"
                    if message.grouped_id
                    else f"{post_counter}"
                )
                await self._dispatch_download(message, prefix, dl_dir, is_comment=False)

            # Process comments (only for first message in album group)
            has_comments = is_first_in_group and message.replies and message.replies.replies > 0
            if has_comments:
                await self._process_comments(channel, message, post_counter, dl_dir)

            if not has_media and not has_comments and not message.text:
                self._emit("on_log", {"msg": t("skipping_post", post_counter)})

            # Save state after each message
            ch_state["last_msg_id"] = message.id
            ch_state["post_counter"] = post_counter
            ch_state["processed_msgs"] = total_done
            save_config(self.config)

            self._update_progress(total_done)
            await asyncio.sleep(self.config.get("delay_between_posts", 1.0))

        # Wait for all pending background downloads
        if self._dl_tasks:
            self._emit("on_status", t("waiting_downloads"))
            await asyncio.gather(*self._dl_tasks, return_exceptions=True)
            self._dl_tasks.clear()

        # Save structured data for HTML export
        self._save_channel_data(dl_dir)

        self._emit("on_status", t("download_complete"))
        self._emit("on_log", {"level": "INFO", "msg": t("auto_monitor")})
        self._emit("on_complete", None)

        # Auto-start monitoring after download completes
        await self.start_monitor()

    # ── Data Collection ─────────────────────────────────────────

    def _collect_post_data(self, message, prefix: str, dl_dir: str, *, is_comment: bool):
        """
        Collect structured post/comment data for the HTML viewer.

        Stores message text, metadata, and media file references
        in self.posts_data for later JSON export.
        """
        post_entry = {
            "msg_id": message.id,
            "prefix": prefix,
            "date": message.date.isoformat() if message.date else "",
            "text": message.text or "",
            "is_comment": is_comment,
            "views": getattr(message, "views", 0) or 0,
            "forwards": getattr(message, "forwards", 0) or 0,
            "media_type": classify_media(message),
            "media_files": [],
        }

        # Check if we already have this post (update rather than duplicate)
        for existing in self.posts_data:
            if existing["msg_id"] == message.id:
                existing.update(post_entry)
                return

        self.posts_data.append(post_entry)

    def _save_channel_data(self, dl_dir: str):
        """
        Save collected post data to channel_data.json in the download directory.

        This JSON file is consumed by the HTML generator to create
        the offline viewer.
        """
        data_path = os.path.join(dl_dir, "channel_data.json")
        try:
            # Merge with existing data if present
            existing_data = []
            if os.path.exists(data_path):
                with open(data_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)

            # Merge: update existing entries, add new ones
            existing_ids = {p["msg_id"] for p in existing_data}
            for post in self.posts_data:
                if post["msg_id"] in existing_ids:
                    for i, ep in enumerate(existing_data):
                        if ep["msg_id"] == post["msg_id"]:
                            existing_data[i] = post
                            break
                else:
                    existing_data.append(post)

            # Sort by msg_id
            existing_data.sort(key=lambda p: p["msg_id"])

            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ── Download Dispatch ───────────────────────────────────────

    async def _dispatch_download(self, message, prefix, dl_dir, is_comment=False):
        """
        Queue a download task with semaphore-based concurrency limiting.

        Creates an async task that acquires the semaphore before downloading,
        ensuring no more than 3 simultaneous downloads.
        """
        await self._dl_semaphore.acquire()

        async def _task():
            try:
                await self._download_file(message, prefix, dl_dir, is_comment=is_comment)
            finally:
                self._dl_semaphore.release()

        # Clean up completed tasks to prevent memory leaks
        self._dl_tasks = [t_task for t_task in self._dl_tasks if not t_task.done()]
        self._dl_tasks.append(asyncio.create_task(_task()))

    async def _process_comments(self, channel, message, post_counter: int, dl_dir: str):
        """
        Download media and collect text from comments on a post.

        Iterates all replies to a message, downloading media files
        and collecting text content for the HTML viewer.
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

                # Collect comment text
                if comment.text:
                    self._collect_post_data(comment, f"{post_counter}_c{comment.id}", dl_dir, is_comment=True)

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
            self._emit("on_error", t("comment_error", post_counter, e))

        # Mark post as processed even if it has no media (comments were checked)
        if hasattr(message, "id") and self.config.get("channel_id"):
            self._mark_as_downloaded(self.config["channel_id"], str(message.id))

    # ── File Download with Retry and Integrity Check ────────────

    async def _download_file(
        self, message, prefix: str, dl_dir: str, *, is_comment: bool
    ):
        """
        Download a single media file with full error handling.

        Features:
        - Retry on network errors up to max_retries times
        - Wait for network recovery before retrying
        - Verify downloaded file integrity (size check)
        - Auto-redownload corrupted files
        - Max quality: Telethon downloads largest PhotoSize and original video
        """
        file_path = os.path.join(dl_dir, prefix)
        max_retries = self.config.get("max_retries", 30)

        mtype = classify_media(message) or "unknown"
        source_key = "source_comment" if is_comment else "source_post"

        self._emit("on_log", {"msg": t("download_started", t(source_key), prefix, t(_TYPE_LABEL_KEYS.get(mtype, "media_unknown")))})

        def progress_cb(received, total):
            """Report download progress and check for stop signal."""
            if self._stop.is_set():
                raise asyncio.CancelledError()
            if total > 0 and self.on_progress:
                frac = received / total
                self._emit("on_progress", prefix, frac, received, total)

        for attempt in range(1, max_retries + 1):
            try:
                # Verify connection before attempting download
                if not self.client.is_connected():
                    await self._wait_for_network()

                # Download media at maximum quality
                downloaded = await self.client.download_media(
                    message, file=file_path, progress_callback=progress_cb
                )

                if not downloaded:
                    raise Exception("download_media returned False")

                self._emit("on_progress_end", prefix)

                # Verify file integrity
                if not self._verify_file(downloaded, message):
                    self.stats.integrity_failures += 1
                    try:
                        os.remove(downloaded)
                    except OSError:
                        pass
                    raise RuntimeError(t("integrity_failed", downloaded))

                # Successfully downloaded
                fsize = os.path.getsize(downloaded)
                mtype = classify_media(message) or "unknown"

                self._emit("on_log", {
                    "msg": t("download_success", t(source_key), prefix,
                             t(_TYPE_LABEL_KEYS.get(mtype, "media_unknown")), format_size(fsize))
                })

                # Update statistics
                self.stats.total_files += 1
                self.stats.total_size_bytes += fsize
                if is_comment:
                    self.stats.downloaded_comment_files += 1
                else:
                    self.stats.downloaded_post_files += 1

                if mtype in _TYPE_TO_STAT:
                    attr = _TYPE_TO_STAT[mtype]
                    setattr(self.stats, attr, getattr(self.stats, attr) + 1)

                # Update post data with downloaded file info
                for post in self.posts_data:
                    if post["msg_id"] == message.id:
                        post["media_files"].append(os.path.basename(downloaded))
                        break

                # Log entry with link
                channel_id = self.config["channel_id"]
                link = f"https://t.me/c/{channel_id}/{message.id}"

                entry = {
                    "num": prefix,
                    "type": t("type_comment") if is_comment else t("type_post"),
                    "file": os.path.basename(downloaded),
                    "media_type": t(_TYPE_LABEL_KEYS.get(mtype, "media_unknown")),
                    "link": link,
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "size": format_size(fsize),
                    "size_bytes": fsize,
                }
                self._emit("on_log", entry)
                self._emit("on_stats", self.stats)

                # Record in download history
                channel_id = self.config["channel_id"]
                history_id = f"c{message.id}" if is_comment else str(message.id)
                self._mark_as_downloaded(channel_id, history_id)

                return  # Success

            except errors.FloodWaitError as e:
                await self._handle_flood(e)
                continue

            except (ConnectionError, OSError, TimeoutError, ConnectionResetError) as e:
                self.stats.retries_total += 1
                if attempt >= max_retries:
                    self._emit("on_error", t("download_failed", prefix, max_retries, e))
                    self._emit("on_progress_end", prefix)
                    return

                wait = min(2 ** min(attempt, 6), 60)
                self._emit("on_status", t("network_error", attempt, max_retries, e, wait))
                await self._wait_for_network(max_wait=wait)

            except Exception as e:
                self.stats.retries_total += 1
                if attempt >= max_retries:
                    self._emit("on_error", t("download_failed", prefix, max_retries, e))
                    self._emit("on_progress_end", prefix)
                    return

                wait = min(2 ** min(attempt, 5), 30)
                self._emit("on_status", t("general_error", attempt, max_retries, e, wait))
                await asyncio.sleep(wait)

    def _verify_file(self, filepath: str, message) -> bool:
        """
        Verify the integrity of a downloaded file.

        Checks:
        1. File exists on disk
        2. File size is greater than zero
        3. For documents/videos: actual size matches expected size
        """
        if not os.path.exists(filepath):
            return False

        file_size = os.path.getsize(filepath)
        if file_size == 0:
            return False

        # Exact size check for documents (video, audio, files)
        if message.document and message.document.size:
            expected = message.document.size
            if file_size != expected:
                self._emit("on_status", t("size_mismatch", file_size, expected))
                return False

        return True

    # ── Network Resilience ──────────────────────────────────────

    async def _wait_for_network(self, max_wait: int = 300):
        """
        Wait until the network connection to Telegram is restored.

        Periodically attempts to reconnect, with the interval defined
        in config. Times out after max_wait seconds.
        """
        interval = self.config.get("network_check_interval", 5)
        waited = 0

        while waited < max_wait:
            if self._stop.is_set():
                return

            try:
                if not self.client.is_connected():
                    await self.client.connect()

                if await self.client.is_user_authorized():
                    return
                return  # Connected but not authorized — continue anyway

            except Exception:
                self._emit("on_status", t("waiting_network", waited))
                await asyncio.sleep(interval)
                waited += interval

    async def _reconnect(self):
        """
        Safely reconnect to Telegram.

        First attempts a clean disconnect/reconnect cycle. If that fails,
        recreates the entire client instance.
        """
        try:
            if self.client.is_connected():
                await self.client.disconnect()
        except Exception:
            pass

        try:
            await self.client.connect()
        except Exception:
            self.client = self._make_client()
            await self.client.connect()

    # ── Helper Methods ──────────────────────────────────────────

    @staticmethod
    def _has_downloadable_media(message) -> bool:
        """Check if a message contains media that can be downloaded as a file."""
        return message.media is not None and not isinstance(
            message.media, _SKIP_MEDIA
        )

    async def _resolve_channel(self):
        """
        Resolve a channel entity by its ID from the config.

        Tries the -100 prefix format first (internal Telegram channel ID),
        then falls back to direct ID lookup.
        """
        cid = self.config.get("channel_id", 0)
        try:
            return await self.client.get_entity(int(f"-100{cid}"))
        except Exception:
            pass
        try:
            return await self.client.get_entity(cid)
        except Exception as e:
            self._emit("on_error", t("channel_not_found", cid, e))
            return None

    async def _handle_flood(self, exc: errors.FloodWaitError):
        """
        Handle Telegram's FloodWait rate-limiting error.

        Waits for the required duration multiplied by the configured
        multiplier to avoid hitting the limit again immediately.
        """
        mult = self.config.get("flood_wait_multiplier", 1.5)
        wait = int(exc.seconds * mult)
        self._emit("on_status", t("flood_wait", wait))
        await asyncio.sleep(wait)

    def _update_progress(self, done: int):
        """
        Update the overall progress bar and estimate remaining size.

        Also checks disk space every 100 messages and warns if
        the estimated total download size exceeds free space.
        """
        total = self.stats.total_channel_msgs
        frac = done / total if total > 0 else 0.0
        self._emit("on_progress_overall", frac, done, total)

        # Size predictor every 100 messages
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

                if predicted_size > free_space:
                    self._emit("on_log", {
                        "level": "WARN",
                        "msg": t("size_warning", format_size(int(predicted_size)), format_size(free_space))
                    })
            except Exception:
                pass

    def _emit(self, name: str, *args):
        """
        Invoke a callback by name with the given arguments.

        The GUI layer registers callbacks on this object. This method
        provides a safe way to call them without checking for None.
        """
        cb = getattr(self, name, None)
        if cb:
            cb(*args)
