"""
Telegram Secret Channel Downloader — Flet GUI Application.

Main GUI entry point built with Flet (Flutter for Python).
Provides tabs for authorization, downloading, live monitoring,
links log, and settings.
"""

from i18n import t, set_lang, get_lang
import flet as ft
import asyncio
import os
import io
import time
import webbrowser
from datetime import datetime
from PIL import Image
from scraper_core import ScraperCore, ScraperStats, format_size, format_duration
from html_generator import generate_channel_html


class TelegramScraperFlet:
    """Main application class that builds and manages the Flet UI."""

    def __init__(self, page: ft.Page):
        """Initialize the application with page settings and scraper core."""
        self.page = page
        self.page.title = t("app_title")
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_width = 950
        self.page.window_height = 750
        self.page.padding = 0
        self.page.fonts = {
            "Inter": "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Regular.woff2",
            "InterBold": "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Bold.woff2"
        }
        self.page.theme = ft.Theme(font_family="Inter")

        self.scraper = ScraperCore()
        self.bind_callbacks()

        # UI state
        self.stat_labels = {}
        self.log_entries = []

        self.build_ui()
        self.load_settings()

        # Check authorization on startup
        self.page.run_task(self.check_auth_on_startup)

    async def check_auth_on_startup(self, *args):
        """Check if a saved session exists and display auth status."""
        try:
            await self.scraper.connect()
            if await self.scraper.is_authorized():
                me = await self.scraper.client.get_me()
                phone = f" (+{me.phone})" if getattr(me, 'phone', None) else ""
                self.lbl_auth_status.value = f"{t('auth_status_authorized')} {phone} ({t('auth_status_saved')})"
                self.lbl_auth_status.color = ft.colors.GREEN_400
                self.img_qr.visible = False
                self.write_auth_log(t("auth_loaded_cache"))
            else:
                self.lbl_auth_status.value = t("auth_status_waiting")
                self.lbl_auth_status.color = ft.colors.GREY_400
            self.page.update()
        except Exception as e:
            self.write_auth_log(f'{t("auth_check_error")} {e}')

    def bind_callbacks(self):
        """Connect scraper core callbacks to GUI update methods."""
        s = self.scraper
        s.on_status = self.cb_status
        s.on_progress = self.cb_progress
        s.on_error = self.cb_error
        s.on_qr_url = self.cb_qr
        s.on_complete = self.cb_complete
        s.on_progress_end = self.cb_progress_end
        s.on_progress_overall = self.cb_progress_overall
        s.on_log = self.cb_log
        s.on_stats = self.cb_stats
        s.request_input = self.cb_request_input

    async def change_lang(self, e):
        """Handle language dropdown change and rebuild entire UI."""
        set_lang(e.control.value)
        self.page.controls.clear()
        self.build_ui()
        self.load_settings()
        await self._update_auth_status()
        self.page.update()

    async def _update_auth_status(self):
        """Refresh authorization status label after language change."""
        try:
            if self.scraper.client and self.scraper.client.is_connected():
                if await self.scraper.is_authorized():
                    me = await self.scraper.client.get_me()
                    phone = f" (+{me.phone})" if getattr(me, 'phone', None) else ""
                    self.lbl_auth_status.value = f"{t('auth_status_authorized')} {phone}"
                    self.lbl_auth_status.color = ft.colors.GREEN_400
                else:
                    self.lbl_auth_status.value = t("auth_status_waiting")
                    self.lbl_auth_status.color = ft.colors.GREY_400
        except Exception:
            pass

    def build_ui(self):
        """Build the complete application UI with header, tabs, and status bar."""
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.icons.TELEGRAM, size=30, color=ft.colors.BLUE_400),
                    ft.Text(t("app_title"), size=24, weight=ft.FontWeight.BOLD, font_family="InterBold"),
                ], alignment=ft.MainAxisAlignment.START, expand=1),
            ]),
            padding=15,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=ft.border_radius.only(bottom_left=15, bottom_right=15)
        )

        self.tabs = ft.Tabs(
            selected_index=1,
            animation_duration=300,
            tabs=[
                ft.Tab(text=t("tab_auth"), content=self.build_auth_tab()),
                ft.Tab(text=t("tab_download"), content=self.build_download_tab()),
                ft.Tab(text=t("tab_live"), content=self.build_live_tab()),
                ft.Tab(text=t("tab_links"), content=self.build_links_tab()),
                ft.Tab(text=t("tab_settings"), content=self.build_settings_tab()),
            ],
            expand=1,
        )

        # Global status bar at the bottom
        self.lbl_global_status = ft.Text(t("waiting"), size=14, color=ft.colors.ON_SURFACE_VARIANT)
        status_bar = ft.Container(
            content=ft.Row([
                ft.ProgressRing(width=16, height=16, stroke_width=2, color=ft.colors.BLUE_400, visible=False),
                self.lbl_global_status
            ]),
            padding=10,
            bgcolor=ft.colors.SURFACE_VARIANT
        )

        self.page.add(
            ft.Column([header, self.tabs, status_bar], expand=True)
        )

    def build_auth_tab(self):
        """Build the Authorization tab with QR code display and auth log."""
        self.img_qr = ft.Image(width=200, height=200, visible=False)
        self.lbl_auth_status = ft.Text(t("auth_status_waiting"), size=16, color=ft.colors.GREY_400)

        self.txt_auth_log = ft.ListView(expand=True, spacing=5, padding=10)
        log_container = ft.Container(
            content=self.txt_auth_log,
            bgcolor=ft.colors.BACKGROUND,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            height=150
        )

        return ft.Container(
            content=ft.Column([
                ft.Text(t("auth_title"), size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.ElevatedButton(t("btn_authorize"), on_click=self.on_auth, icon=ft.icons.LOGIN, bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE),
                    ft.ElevatedButton(t("btn_logout"), on_click=self.on_logout, icon=ft.icons.LOGOUT, color=ft.colors.RED_400),
                ]),
                self.lbl_auth_status,
                ft.Container(self.img_qr, alignment=ft.alignment.center, padding=20),
                ft.Text(t("auth_log_title"), weight=ft.FontWeight.BOLD),
                log_container
            ], scroll=ft.ScrollMode.AUTO),
            padding=20
        )

    def build_download_tab(self):
        """Build the Download tab with progress bars, stats grid, and controls."""
        self.pb_main = ft.ProgressBar(value=0, height=10, color=ft.colors.GREEN_400, bgcolor=ft.colors.SURFACE_VARIANT)
        self.lbl_progress = ft.Text(t("overall_progress_fmt", 0, 0), size=14)
        self.active_downloads_column = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.active_bars = {}

        prog_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(t("overall_channel_progress"), weight=ft.FontWeight.BOLD, size=16),
                    self.pb_main,
                    self.lbl_progress,
                    ft.Divider(height=1, color=ft.colors.OUTLINE),
                    ft.Text(t("active_downloads"), weight=ft.FontWeight.BOLD, size=16),
                    self.active_downloads_column
                ]),
                padding=20
            ),
            elevation=4
        )

        # Statistics grid
        stats_keys = [
            ("total_msgs", t("stat_total_msgs")),
            ("processed", t("stat_processed")),
            ("total_files", t("stat_total_files")),
            ("total_size", t("stat_total_size")),
            ("photos", t("stat_photos")),
            ("videos", t("stat_videos")),
            ("text_posts", t("stat_text_posts")),
            ("elapsed", t("stat_elapsed")),
            ("speed", t("stat_speed")),
            ("eta", t("stat_eta")),
        ]

        grid_items = []
        for key, title in stats_keys:
            val_text = ft.Text("0", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400)
            self.stat_labels[key] = val_text
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(title, size=12, color=ft.colors.GREY_400),
                        val_text
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=10,
                    width=140
                )
            )
            grid_items.append(card)

        stats_grid = ft.Row(grid_items, wrap=True, alignment=ft.MainAxisAlignment.START)

        # Control buttons
        controls = ft.Row([
            ft.ElevatedButton(t("btn_start"), on_click=self.on_start_dl, icon=ft.icons.PLAY_ARROW, bgcolor=ft.colors.GREEN_600, color=ft.colors.WHITE),
            ft.ElevatedButton(t("btn_stop"), on_click=self.on_stop_dl, icon=ft.icons.STOP, bgcolor=ft.colors.RED_600, color=ft.colors.WHITE),
            ft.ElevatedButton(t("btn_reset"), on_click=self.on_reset, icon=ft.icons.REFRESH, color=ft.colors.ORANGE_400),
            ft.ElevatedButton(t("btn_generate_html"), on_click=self.on_generate_html, icon=ft.icons.ARTICLE, color=ft.colors.TEAL_400),
            ft.ElevatedButton(t("btn_open_html"), on_click=self.on_open_html, icon=ft.icons.OPEN_IN_BROWSER, color=ft.colors.CYAN_400),
        ])

        # Live log
        self.live_log_list = ft.ListView(expand=True, spacing=2, auto_scroll=True)
        live_log_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(t("system_log_title"), weight=ft.FontWeight.BOLD),
                    ft.Container(self.live_log_list, expand=True)
                ]),
                padding=10,
                expand=True
            ),
            expand=True
        )

        return ft.Container(
            content=ft.Column([
                controls,
                prog_card,
                ft.Text(t("statistics_title"), size=18, weight=ft.FontWeight.BOLD),
                stats_grid,
                live_log_card
            ]),
            padding=20,
            expand=True
        )

    def build_live_tab(self):
        """Build the Live Monitoring tab with monitor controls and log."""
        controls = ft.Row([
            ft.ElevatedButton(t("btn_start_monitor"), on_click=self.on_live, icon=ft.icons.RADAR, bgcolor=ft.colors.PURPLE_500, color=ft.colors.WHITE),
            ft.ElevatedButton(t("btn_stop"), on_click=self.on_stop_dl, icon=ft.icons.STOP, color=ft.colors.RED_400),
        ])

        self.monitor_log_list = ft.ListView(expand=True, spacing=5, auto_scroll=True)
        monitor_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(t("realtime_activity"), weight=ft.FontWeight.BOLD),
                    ft.Container(self.monitor_log_list, expand=True)
                ]),
                padding=10,
                expand=True
            ),
            expand=True
        )

        return ft.Container(
            content=ft.Column([
                ft.Text(t("live_title"), size=20, weight=ft.FontWeight.BOLD),
                ft.Text(t("live_description"), color=ft.colors.GREY_400),
                controls,
                ft.Row([
                    ft.ElevatedButton(t("btn_scan_missing"), on_click=self.on_scan_missing, icon=ft.icons.SEARCH, color=ft.colors.BLUE_400),
                    ft.ElevatedButton(t("btn_download_missing"), on_click=self.on_download_missing, icon=ft.icons.DOWNLOAD, color=ft.colors.GREEN_400),
                ]),
                monitor_card
            ]),
            padding=20,
            expand=True
        )

    def build_links_tab(self):
        """Build the Links tab with a data table of downloaded files."""
        self.links_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(t("col_type"))),
                ft.DataColumn(ft.Text(t("col_post_num"))),
                ft.DataColumn(ft.Text(t("col_file"))),
                ft.DataColumn(ft.Text(t("col_link"))),
                ft.DataColumn(ft.Text(t("col_size"))),
                ft.DataColumn(ft.Text(t("col_time")))
            ],
            rows=[]
        )

        return ft.Container(
            content=ft.Column([
                ft.Text(t("links_title"), size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    ft.ListView([self.links_table], expand=True, auto_scroll=True),
                    expand=True,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=5
                )
            ], expand=True),
            padding=20,
            expand=True
        )

    def build_settings_tab(self):
        """Build the Settings tab with API config, channel settings, and language selector."""
        self.inp_api_id = ft.TextField(label=t("api_id_label"))
        self.inp_api_hash = ft.TextField(label=t("api_hash_label"), password=True, can_reveal_password=True)
        self.inp_channel_id = ft.TextField(label=t("channel_id_label"))

        # Directory picker
        self.file_picker = ft.FilePicker(on_result=self.on_dir_picked)
        self.page.overlay.append(self.file_picker)

        self.inp_dl_dir = ft.TextField(label=t("download_dir_label"), expand=True)
        btn_pick_dir = ft.IconButton(icon=ft.icons.FOLDER_OPEN, on_click=lambda _: self.file_picker.get_directory_path())

        # Language selector
        lang_dropdown = ft.Dropdown(
            label=t("language_label"),
            value=get_lang(),
            options=[
                ft.dropdown.Option("en", "English"),
                ft.dropdown.Option("ru", "Русский"),
            ],
            on_change=self.change_lang,
            width=200,
        )

        btn_save = ft.ElevatedButton(t("btn_save"), on_click=self.on_save_settings, bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)

        return ft.Container(
            content=ft.Column([
                ft.Text(t("api_settings"), size=18, weight=ft.FontWeight.BOLD),
                self.inp_api_id,
                self.inp_api_hash,
                ft.Divider(),
                ft.Text(t("channel_settings"), size=18, weight=ft.FontWeight.BOLD),
                self.inp_channel_id,
                ft.Row([self.inp_dl_dir, btn_pick_dir]),
                ft.Divider(),
                lang_dropdown,
                ft.Divider(),
                btn_save
            ], scroll=ft.ScrollMode.AUTO),
            padding=20
        )

    def load_settings(self):
        """Load current settings from the scraper config into the UI fields."""
        cfg = self.scraper.config
        self.inp_api_id.value = str(cfg.get("api_id", ""))
        self.inp_api_hash.value = cfg.get("api_hash", "")
        self.inp_channel_id.value = str(cfg.get("channel_id", ""))

        ch_state = cfg.get("channels", {}).get(str(self.inp_channel_id.value), {})
        self.inp_dl_dir.value = ch_state.get("download_dir", "downloads")
        self.page.update()

    def on_save_settings(self, e):
        """Save UI settings to the config file."""
        cfg = self.scraper.config
        cfg["api_id"] = int(self.inp_api_id.value) if self.inp_api_id.value.isdigit() else 0
        cfg["api_hash"] = self.inp_api_hash.value
        cfg["channel_id"] = self.inp_channel_id.value

        ch_state = cfg.setdefault("channels", {}).setdefault(str(self.inp_channel_id.value), {})
        ch_state["download_dir"] = self.inp_dl_dir.value

        from scraper_core import save_config
        save_config(cfg)
        self.write_log(t("settings_saved"), ft.colors.GREEN_400)
        self.page.snack_bar = ft.SnackBar(ft.Text(t("settings_saved_snack")))
        self.page.snack_bar.open = True
        self.page.update()

    def on_dir_picked(self, e: ft.FilePickerResultEvent):
        """Handle directory picker result."""
        if e.path:
            self.inp_dl_dir.value = e.path
            self.page.update()

    # ── Logging Helpers ─────────────────────────────────────────

    def write_log(self, text, color=ft.colors.GREY_300):
        """Append a timestamped entry to the download log."""
        ts = datetime.now().strftime("%H:%M:%S")
        self.live_log_list.controls.append(ft.Text(f"[{ts}] {text}", color=color, size=12, font_family="Consolas"))
        if len(self.live_log_list.controls) > 200:
            self.live_log_list.controls.pop(0)
        self.page.update()

    def write_monitor_log(self, text, color=ft.colors.GREEN_300):
        """Append a timestamped entry to the monitoring log."""
        if not hasattr(self, 'monitor_log_list'):
            return
        ts = datetime.now().strftime("%H:%M:%S")
        self.monitor_log_list.controls.append(ft.Text(f"[{ts}] {text}", color=color, size=14, font_family="Consolas"))
        if len(self.monitor_log_list.controls) > 100:
            self.monitor_log_list.controls.pop(0)
        self.page.update()

    def write_auth_log(self, text):
        """Append a timestamped entry to the authorization log."""
        ts = datetime.now().strftime("%H:%M:%S")
        self.txt_auth_log.controls.append(ft.Text(f"[{ts}] {text}", size=12))
        self.page.update()

    # ── Scraper Callbacks ───────────────────────────────────────

    def cb_status(self, text):
        """Update global status bar and both log views."""
        self.lbl_global_status.value = text
        self.write_log(text)
        self.write_monitor_log(text)
        self.page.update()

    def cb_progress(self, prefix, frac, done, total):
        """Update or create a per-file progress bar."""
        if prefix not in self.active_bars:
            pb = ft.ProgressBar(value=0, height=10, color=ft.colors.BLUE_400, bgcolor=ft.colors.SURFACE_VARIANT)
            lbl = ft.Text(t("file_progress_fmt", prefix, "0", "0"), size=14)
            row = ft.Column([lbl, pb], spacing=2)
            self.active_bars[prefix] = {"pb": pb, "lbl": lbl, "row": row}
            self.active_downloads_column.controls.append(row)

        bar_data = self.active_bars[prefix]
        bar_data["pb"].value = frac
        bar_data["lbl"].value = t("file_progress_fmt", prefix, format_size(done), format_size(total))
        self.page.update()

    def cb_progress_overall(self, frac, done, total):
        """Update the overall channel progress bar."""
        self.pb_main.value = frac
        self.lbl_progress.value = t("overall_progress_fmt", done, total)
        self.page.update()

    def cb_progress_end(self, prefix):
        """Remove a completed per-file progress bar."""
        if prefix in self.active_bars:
            row = self.active_bars[prefix]["row"]
            if row in self.active_downloads_column.controls:
                self.active_downloads_column.controls.remove(row)
            del self.active_bars[prefix]
            self.page.update()

    def cb_error(self, text):
        """Display an error in the status bar, logs, and snackbar."""
        self.lbl_global_status.value = f"❌ {text}"
        self.lbl_global_status.color = ft.colors.RED_400
        self.page.snack_bar = ft.SnackBar(ft.Text(t("error_snack", text)), bgcolor=ft.colors.RED_800)
        self.page.snack_bar.open = True
        self.write_log(f'[{t("error_prefix")}] {text}', ft.colors.RED_400)
        self.write_monitor_log(f'[{t("error_prefix")}] {text}', ft.colors.RED_400)

        # Persist to error.log
        try:
            with open("error.log", "a", encoding="utf-8") as f:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{ts}] {text}\n")
        except Exception:
            pass

        self.page.update()

    def cb_log(self, entry):
        """Handle structured log entries from the scraper core."""
        if isinstance(entry, dict):
            if "msg" in entry:
                self.write_log(entry["msg"])
                self.write_monitor_log(entry["msg"])
            elif "link" in entry:
                # Add row to links data table
                self.links_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(entry.get("type", ""))),
                        ft.DataCell(ft.Text(str(entry.get("num", "")))),
                        ft.DataCell(ft.Text(entry.get("file", ""))),
                        ft.DataCell(ft.Text(entry.get("link", ""), color=ft.colors.BLUE_400, selectable=True)),
                        ft.DataCell(ft.Text(entry.get("size", ""))),
                        ft.DataCell(ft.Text(entry.get("time", "")))
                    ])
                )
                if len(self.links_table.rows) > 1000:
                    self.links_table.rows.pop(0)
                self.page.update()
        else:
            self.write_log(str(entry))
            self.write_monitor_log(str(entry))

    def cb_qr(self, url):
        """Display a QR code image for Telegram authorization."""
        import qrcode
        qr = qrcode.make(url)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        import base64
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        self.img_qr.src_base64 = b64
        self.img_qr.visible = True
        self.write_auth_log(t("scan_qr_hint"))
        self.page.update()

    def cb_complete(self, dummy=None):
        """Handle download/monitoring completion."""
        self.write_log(t("download_finished"), ft.colors.GREEN_400)
        self.cb_status(t("waiting"))

    def cb_stats(self, stats: ScraperStats):
        """Update statistics display cards with current values."""
        sl = self.stat_labels
        sl["total_msgs"].value = str(stats.total_channel_msgs)
        sl["processed"].value = str(stats.processed_msgs)
        sl["total_files"].value = str(stats.total_files)
        sl["total_size"].value = format_size(stats.total_size_bytes)
        sl["photos"].value = str(stats.photos)
        sl["videos"].value = str(stats.videos)
        sl["text_posts"].value = str(stats.text_posts)

        elapsed = time.time() - stats.start_time if stats.start_time else 0
        sl["elapsed"].value = format_duration(elapsed)

        if stats.processed_msgs > 0 and stats.total_channel_msgs > 0 and elapsed > 0:
            file_rate = stats.total_files / (elapsed / 60)
            sl["speed"].value = t("speed_fmt", file_rate)

            rem = stats.total_channel_msgs - stats.processed_msgs
            eta = (rem / stats.processed_msgs) * elapsed
            sl["eta"].value = format_duration(eta)
        self.page.update()

    async def cb_request_input(self, title, prompt):
        """
        Show an input dialog and return the entered value.

        This is an async function that creates an asyncio.Future,
        displays a Flet dialog, and awaits the user's input.
        Returns the entered string or None if cancelled.
        """
        future = asyncio.get_event_loop().create_future()

        # Special case: auth method selection
        if prompt == "AUTH_MODE":
            def on_qr(e):
                dlg.open = False
                self.page.update()
                if not future.done():
                    future.set_result("QR")

            def on_phone(e):
                dlg.open = False
                self.page.update()
                if not future.done():
                    future.set_result("PHONE")

            dlg = ft.AlertDialog(
                title=ft.Text(title),
                content=ft.Text(t("scan_qr_hint")),
                actions=[
                    ft.TextButton("📱 QR Code", on_click=on_qr),
                    ft.TextButton("📞 Phone", on_click=on_phone),
                ]
            )
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()
            return await future

        # Standard text input dialog
        is_password = "2FA" in prompt or "password" in prompt.lower()
        inp = ft.TextField(label=prompt, password=is_password, can_reveal_password=is_password)

        def on_submit(e):
            val = inp.value
            dlg.open = False
            self.page.update()
            if not future.done():
                future.set_result(val)

        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=inp,
            actions=[ft.TextButton(t("btn_ok"), on_click=on_submit)]
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()
        return await future

    # ── Button Handlers ─────────────────────────────────────────

    async def on_auth(self, e):
        """Start the authorization flow."""
        self.lbl_auth_status.value = t("auth_connecting")
        self.write_auth_log(t("auth_requesting"))
        self.page.update()

        try:
            ok = await self.scraper.authorize()
            if ok:
                me = await self.scraper.client.get_me()
                phone = f" (+{me.phone})" if getattr(me, 'phone', None) else ""
                self.lbl_auth_status.value = f"{t('auth_status_authorized')} {phone}"
                self.lbl_auth_status.color = ft.colors.GREEN_400
                self.img_qr.visible = False
                self.write_auth_log(t("auth_success"))
            else:
                self.lbl_auth_status.value = f'❌ {t("auth_error")}'
                self.lbl_auth_status.color = ft.colors.RED_400
        except Exception as err:
            self.write_auth_log(f'{t("auth_check_error")} {err}')
        self.page.update()

    async def on_logout(self, e):
        """Log out and delete the session file."""
        await self.scraper.disconnect()
        try:
            if os.path.exists("telegram_session.session"):
                os.remove("telegram_session.session")
            if os.path.exists("telegram_session.session-journal"):
                os.remove("telegram_session.session-journal")
            self.write_auth_log(t("session_deleted"))
        except Exception as ex:
            self.write_auth_log(f'{t("session_delete_error")} {ex}')

        self.lbl_auth_status.value = t("auth_status_waiting")
        self.lbl_auth_status.color = ft.colors.GREY_400
        self.page.update()

    async def on_start_dl(self, e):
        """Start the full channel download in a background task."""
        asyncio.create_task(self.scraper.start_download())

    async def on_stop_dl(self, e):
        """Stop any running download or monitoring operation."""
        await self.scraper.stop()

    async def on_live(self, e):
        """Start live monitoring in a background task."""
        asyncio.create_task(self.scraper.start_monitor())

    async def on_scan_missing(self, e):
        """Scan for missing posts in a background task."""
        asyncio.create_task(self.scraper.scan_missing_posts())

    async def on_download_missing(self, e):
        """Download missing posts in a background task."""
        asyncio.create_task(self.scraper.download_missing_posts())

    async def on_generate_html(self, e):
        """Generate the offline HTML viewer from channel data."""
        cfg = self.scraper.config
        ch_state = cfg.get("channels", {}).get(str(cfg.get("channel_id", "")), {})
        dl_dir = ch_state.get("download_dir", "downloads")

        self.write_log(t("generating_html"))
        try:
            channel_name = str(cfg.get("channel_id", "Channel"))
            # Try to get actual channel name if connected
            if self.scraper.client and self.scraper.client.is_connected():
                try:
                    ch = await self.scraper._resolve_channel()
                    if ch:
                        channel_name = getattr(ch, "title", channel_name)
                except Exception:
                    pass

            result = generate_channel_html(dl_dir, channel_name)
            if result:
                self.write_log(t("html_generated", result), ft.colors.GREEN_400)
                self.page.snack_bar = ft.SnackBar(ft.Text(t("html_generated", os.path.basename(result))))
                self.page.snack_bar.open = True
            else:
                self.write_log(t("html_error", "No data found"), ft.colors.ORANGE_400)
        except Exception as ex:
            self.write_log(t("html_error", str(ex)), ft.colors.RED_400)
        self.page.update()

    async def on_open_html(self, e):
        """Open the generated HTML file in the default browser."""
        cfg = self.scraper.config
        ch_state = cfg.get("channels", {}).get(str(cfg.get("channel_id", "")), {})
        dl_dir = ch_state.get("download_dir", "downloads")
        html_path = os.path.join(dl_dir, "index.html")

        if os.path.exists(html_path):
            webbrowser.open(f"file:///{os.path.abspath(html_path)}")
        else:
            self.write_log(t("html_error", "index.html not found"), ft.colors.ORANGE_400)
            self.page.update()

    async def on_reset(self, e):
        """Show a confirmation dialog for resetting channel progress."""
        cb_delete_files = ft.Checkbox(label=t("reset_delete_files"), value=False)

        def do_reset(ev):
            """Execute the progress reset after confirmation."""
            dlg.open = False
            self.page.update()

            cfg = self.scraper.config
            cid = cfg.get("channel_id")
            if cid:
                ch_state = cfg.setdefault("channels", {}).setdefault(str(cid), {})
                dl_dir = ch_state.get("download_dir", "downloads")

                ch_state["last_msg_id"] = 0
                ch_state["post_counter"] = 0
                ch_state["processed_msgs"] = 0
                from scraper_core import save_config
                save_config(cfg)

                # Delete history file
                history_path = os.path.join(os.path.dirname(__file__), f"history_{cid}.txt")
                if os.path.exists(history_path):
                    try:
                        os.remove(history_path)
                    except Exception:
                        pass

                # Optionally delete downloaded files
                if cb_delete_files.value and os.path.exists(dl_dir):
                    try:
                        for filename in os.listdir(dl_dir):
                            file_path = os.path.join(dl_dir, filename)
                            if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                import shutil
                                shutil.rmtree(file_path)
                        self.write_log(t("reset_files_deleted"), ft.colors.ORANGE_400)
                    except Exception as err:
                        self.write_log(f'{t("reset_files_error")} {err}', ft.colors.RED_400)

                self.write_log(t("reset_complete"), ft.colors.ORANGE_400)

        dlg = ft.AlertDialog(
            title=ft.Text(t("reset_title")),
            content=ft.Column([
                ft.Text(t("reset_confirm")),
                cb_delete_files
            ], tight=True),
            actions=[
                ft.TextButton(t("btn_cancel"), on_click=lambda e: setattr(dlg, 'open', False) or self.page.update()),
                ft.TextButton(t("btn_reset_confirm"), on_click=do_reset, style=ft.ButtonStyle(color=ft.colors.RED_400))
            ]
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()


async def main(page: ft.Page):
    """Flet application entry point."""
    app = TelegramScraperFlet(page)


if __name__ == "__main__":
    ft.app(target=main)
