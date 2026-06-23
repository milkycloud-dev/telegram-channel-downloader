from i18n import t, set_lang, get_lang
import flet as ft
import asyncio
import os
import io
import time
from datetime import datetime
from PIL import Image
from scraper_core import ScraperCore, ScraperStats, format_size, format_duration

class TelegramScraperFlet:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Telegram Channel Downloader"
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

        # UI State
        self.stat_labels = {}
        self.log_entries = []

        self.build_ui()
        self.load_settings()
        
        # Check authorization on startup
        self.page.run_task(self.check_auth_on_startup)

    async def check_auth_on_startup(self, *args):
        try:
            await self.scraper.connect()
            if await self.scraper.is_authorized():
                me = await self.scraper.client.get_me()
                phone = f" (+{me.phone})" if getattr(me, 'phone', None) else ""
                self.lbl_auth_status.value = f"✅ Авторизован{phone} (Сохранено)"
                self.lbl_auth_status.color = ft.colors.GREEN_400
                self.img_qr.visible = False
                self.write_auth_log("Авторизация загружена из кэша.")
            else:
                self.lbl_auth_status.value = "Ожидание авторизации"
                self.lbl_auth_status.color = ft.colors.GREY_400
            self.page.update()
        except Exception as e:
            self.write_auth_log(f"Ошибка проверки авторизации: {e}")

    def bind_callbacks(self):
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

    def build_ui(self):
        def change_lang(e, lang):
            from i18n import set_lang
            set_lang(lang)
            self.page.controls.clear()
            self.build_ui()
            self.page.update()

        btn_ru = ft.TextButton("🇷🇺", on_click=lambda e: change_lang(e, "ru"))
        btn_en = ft.TextButton("🇬🇧", on_click=lambda e: change_lang(e, "en"))

        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.icons.TELEGRAM, size=30, color=ft.colors.BLUE_400),
                    ft.Text(t("Telegram Channel Downloader"), size=24, weight=ft.FontWeight.BOLD, font_family="InterBold"),
                ], alignment=ft.MainAxisAlignment.START, expand=1),
                ft.Row([btn_ru, btn_en], alignment=ft.MainAxisAlignment.END)
            ]),
            padding=15,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=ft.border_radius.only(bottom_left=15, bottom_right=15)
        )

        # Tabs
        self.tabs = ft.Tabs(
            selected_index=1,
            animation_duration=300,
            tabs=[
                ft.Tab(text=t("🔐 Авторизация"), content=self.build_auth_tab()),
                ft.Tab(text=t("📥 Скачивание"), content=self.build_download_tab()),
                ft.Tab(text=t("📡 Live"), content=self.build_live_tab()),
                ft.Tab(text=t("📜 Ссылки"), content=self.build_links_tab()),
                ft.Tab(text=t("⚙️ Настройки"), content=self.build_settings_tab()),
            ],
            expand=1,
        )

        # Global Status Bar
        self.lbl_global_status = ft.Text(t("Ожидание..."), size=14, color=ft.colors.ON_SURFACE_VARIANT)
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
        self.img_qr = ft.Image(width=200, height=200, visible=False)
        self.lbl_auth_status = ft.Text(t("Статус: Ожидание авторизации"), size=16, color=ft.colors.GREY_400)
        
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
                ft.Text(t("Авторизация Telegram"), size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.ElevatedButton(t("🔑 Начать авторизацию"), on_click=self.on_auth, icon=ft.icons.LOGIN, bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE),
                    ft.ElevatedButton(t("🚪 Выйти"), on_click=self.on_logout, icon=ft.icons.LOGOUT, color=ft.colors.RED_400),
                ]),
                self.lbl_auth_status,
                ft.Container(self.img_qr, alignment=ft.alignment.center, padding=20),
                ft.Text(t("Лог авторизации:"), weight=ft.FontWeight.BOLD),
                log_container
            ], scroll=ft.ScrollMode.AUTO),
            padding=20
        )

    def build_download_tab(self):
        self.pb_main = ft.ProgressBar(value=0, height=10, color=ft.colors.GREEN_400, bgcolor=ft.colors.SURFACE_VARIANT)
        self.lbl_progress = ft.Text(t("Общий прогресс: 0 / 0 сообщений"), size=14)
        self.active_downloads_column = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.active_bars = {}
        
        prog_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(t("Общий прогресс канала"), weight=ft.FontWeight.BOLD, size=16),
                    self.pb_main,
                    self.lbl_progress,
                    ft.Divider(height=1, color=ft.colors.OUTLINE),
                    ft.Text(t("Активные загрузки"), weight=ft.FontWeight.BOLD, size=16),
                    self.active_downloads_column
                ]),
                padding=20
            ),
            elevation=4
        )

        # Stats Grid
        stats_keys = [
            ("total_msgs", "Всего сообщений"),
            ("processed", "Обработано"),
            ("total_files", "Всего файлов"),
            ("total_size", "Общий размер"),
            ("photos", "📷 Фото"),
            ("videos", "🎬 Видео"),
            ("elapsed", "⏱ Время работы"),
            ("speed", "🚀 Скорость"),
            ("eta", "⏳ Осталось"),
        ]
        
        grid_items = []
        for key, title in stats_keys:
            val_text = ft.Text(t("0"), size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400)
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

        # Controls
        controls = ft.Row([
            ft.ElevatedButton(t("Старт"), on_click=self.on_start_dl, icon=ft.icons.PLAY_ARROW, bgcolor=ft.colors.GREEN_600, color=ft.colors.WHITE),
            ft.ElevatedButton(t("Стоп"), on_click=self.on_stop_dl, icon=ft.icons.STOP, bgcolor=ft.colors.RED_600, color=ft.colors.WHITE),
            ft.ElevatedButton(t("Сброс прогресса"), on_click=self.on_reset, icon=ft.icons.REFRESH, color=ft.colors.ORANGE_400),
        ])

        # Live Log
        self.live_log_list = ft.ListView(expand=True, spacing=2, auto_scroll=True)
        live_log_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(t("🟢 System Log (События скачивания)"), weight=ft.FontWeight.BOLD),
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
                ft.Text(t("📊 Статистика"), size=18, weight=ft.FontWeight.BOLD),
                stats_grid,
                live_log_card
            ]),
            padding=20,
            expand=True
        )

    def build_live_tab(self):
        # Live Monitor UI
        controls = ft.Row([
            ft.ElevatedButton(t("📡 Запустить Мониторинг"), on_click=self.on_live, icon=ft.icons.RADAR, bgcolor=ft.colors.PURPLE_500, color=ft.colors.WHITE),
            ft.ElevatedButton(t("⏹ Остановить"), on_click=self.on_stop_dl, icon=ft.icons.STOP, color=ft.colors.RED_400),
        ])
        
        self.monitor_log_list = ft.ListView(expand=True, spacing=5, auto_scroll=True)
        monitor_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(t("Активность в реальном времени"), weight=ft.FontWeight.BOLD),
                    ft.Container(self.monitor_log_list, expand=True)
                ]),
                padding=10,
                expand=True
            ),
            expand=True
        )

        return ft.Container(
            content=ft.Column([
                ft.Text(t("Live Мониторинг"), size=20, weight=ft.FontWeight.BOLD),
                ft.Text(t("Здесь вы можете сканировать канал на пропущенные файлы и докачивать их."), color=ft.colors.GREY_400),
                controls,
                ft.Row([
                    ft.ElevatedButton(t("🔍 Искать пропущенные"), on_click=self.on_scan_missing, icon=ft.icons.SEARCH, color=ft.colors.BLUE_400),
                    ft.ElevatedButton(t("📥 Докачать пропущенные"), on_click=self.on_download_missing, icon=ft.icons.DOWNLOAD, color=ft.colors.GREEN_400),
                ]),
                monitor_card
            ]),
            padding=20,
            expand=True
        )

    def build_links_tab(self):
        self.links_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(t("Тип"))),
                ft.DataColumn(ft.Text(t("Пост #"))),
                ft.DataColumn(ft.Text(t("Файл"))),
                ft.DataColumn(ft.Text(t("Ссылка"))),
                ft.DataColumn(ft.Text(t("Размер"))),
                ft.DataColumn(ft.Text(t("Время")))
            ],
            rows=[]
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(t("Лог скачанных файлов"), size=20, weight=ft.FontWeight.BOLD),
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
        self.inp_api_id = ft.TextField(label=t("API ID"))
        self.inp_api_hash = ft.TextField(label=t("API Hash"), password=True, can_reveal_password=True)
        self.inp_channel_id = ft.TextField(label=t("Channel ID / Username"))
        
        # We don't have AskDirectory in pure Flet out of the box easily without FilePicker
        # I'll use FilePicker
        self.file_picker = ft.FilePicker(on_result=self.on_dir_picked)
        self.page.overlay.append(self.file_picker)
        
        self.inp_dl_dir = ft.TextField(label=t("Download Directory"), expand=True)
        btn_pick_dir = ft.IconButton(icon=ft.icons.FOLDER_OPEN, on_click=lambda _: self.file_picker.get_directory_path())

        btn_save = ft.ElevatedButton(t("💾 Сохранить"), on_click=self.on_save_settings, bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)

        return ft.Container(
            content=ft.Column([
                ft.Text(t("Настройки API"), size=18, weight=ft.FontWeight.BOLD),
                self.inp_api_id,
                self.inp_api_hash,
                ft.Divider(),
                ft.Text(t("Настройки Канала"), size=18, weight=ft.FontWeight.BOLD),
                self.inp_channel_id,
                ft.Row([self.inp_dl_dir, btn_pick_dir]),
                btn_save
            ], scroll=ft.ScrollMode.AUTO),
            padding=20
        )

    def load_settings(self):
        cfg = self.scraper.config
        self.inp_api_id.value = str(cfg.get("api_id", ""))
        self.inp_api_hash.value = cfg.get("api_hash", "")
        self.inp_channel_id.value = str(cfg.get("channel_id", ""))
        
        ch_state = cfg.get("channels", {}).get(str(self.inp_channel_id.value), {})
        self.inp_dl_dir.value = ch_state.get("download_dir", "downloads")
        self.page.update()

    def on_save_settings(self, e):
        cfg = self.scraper.config
        cfg["api_id"] = int(self.inp_api_id.value) if self.inp_api_id.value.isdigit() else 0
        cfg["api_hash"] = self.inp_api_hash.value
        cfg["channel_id"] = self.inp_channel_id.value
        
        ch_state = cfg.setdefault("channels", {}).setdefault(str(self.inp_channel_id.value), {})
        ch_state["download_dir"] = self.inp_dl_dir.value
        
        from scraper_core import save_config
        save_config(cfg)
        self.write_log("Настройки сохранены", ft.colors.GREEN_400)
        self.page.snack_bar = ft.SnackBar(ft.Text(t("Настройки сохранены!")))
        self.page.snack_bar.open = True
        self.page.update()

    def on_dir_picked(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.inp_dl_dir.value = e.path
            self.page.update()

    def write_log(self, text, color=ft.colors.GREY_300):
        ts = datetime.now().strftime("%H:%M:%S")
        self.live_log_list.controls.append(ft.Text(f"[{ts}] {text}", color=color, size=12, font_family="Consolas"))
        if len(self.live_log_list.controls) > 200:
            self.live_log_list.controls.pop(0)
        self.page.update()

    def write_monitor_log(self, text, color=ft.colors.GREEN_300):
        if not hasattr(self, 'monitor_log_list'):
            return
        ts = datetime.now().strftime("%H:%M:%S")
        self.monitor_log_list.controls.append(ft.Text(f"[{ts}] {text}", color=color, size=14, font_family="Consolas"))
        if len(self.monitor_log_list.controls) > 100:
            self.monitor_log_list.controls.pop(0)
        self.page.update()

    def write_auth_log(self, text):
        ts = datetime.now().strftime("%H:%M:%S")
        self.txt_auth_log.controls.append(ft.Text(f"[{ts}] {text}", size=12))
        self.page.update()

    # Callbacks
    def cb_status(self, text):
        self.lbl_global_status.value = text
        self.write_log(text)
        self.write_monitor_log(text)
        self.page.update()

    def cb_progress(self, prefix, frac, done, total):
        from scraper_core import format_size
        
        if prefix not in self.active_bars:
            pb = ft.ProgressBar(value=0, height=10, color=ft.colors.BLUE_400, bgcolor=ft.colors.SURFACE_VARIANT)
            lbl = ft.Text(f"Файл #{prefix}: 0 / 0", size=14)
            row = ft.Column([lbl, pb], spacing=2)
            self.active_bars[prefix] = {"pb": pb, "lbl": lbl, "row": row}
            self.active_downloads_column.controls.append(row)
            
        bar_data = self.active_bars[prefix]
        bar_data["pb"].value = frac
        bar_data["lbl"].value = f"Файл #{prefix}: {format_size(done)} / {format_size(total)}"
        self.page.update()

    def cb_progress_overall(self, frac, done, total):
        self.pb_main.value = frac
        self.lbl_progress.value = f"Общий прогресс: {done} / {total} сообщений"
        self.page.update()

    def cb_progress_end(self, prefix):
        if prefix in self.active_bars:
            row = self.active_bars[prefix]["row"]
            if row in self.active_downloads_column.controls:
                self.active_downloads_column.controls.remove(row)
            del self.active_bars[prefix]
            self.page.update()

    def cb_error(self, text):
        self.lbl_global_status.value = f"❌ {text}"
        self.lbl_global_status.color = ft.colors.RED_400
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка: {text}"), bgcolor=ft.colors.RED_800)
        self.page.snack_bar.open = True
        self.write_log(f"[ОШИБКА] {text}", ft.colors.RED_400)
        self.write_monitor_log(f"[ОШИБКА] {text}", ft.colors.RED_400)
        
        # Save to error.log
        try:
            with open("error.log", "a", encoding="utf-8") as f:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{ts}] {text}\n")
        except:
            pass
            
        self.page.update()

    def cb_log(self, entry):
        if isinstance(entry, dict):
            if "msg" in entry:
                # Live/System Log info
                self.write_log(entry["msg"])
                self.write_monitor_log(entry["msg"])
            elif "link" in entry:
                # Add to Links Table
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
        import qrcode
        qr = qrcode.make(url)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        import base64
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        self.img_qr.src_base64 = b64
        self.img_qr.visible = True
        self.write_auth_log("Отсканируйте QR код в приложении Telegram (Settings -> Devices -> Link Desktop Device)")
        self.page.update()

    def cb_complete(self, dummy=None):
        self.write_log("Скачивание завершено", ft.colors.GREEN_400)
        self.cb_status("Ожидание")

    def cb_stats(self, stats: ScraperStats):
        sl = self.stat_labels
        sl["total_msgs"].value = str(stats.total_channel_msgs)
        sl["processed"].value = str(stats.processed_msgs)
        sl["total_files"].value = str(stats.total_files)
        sl["total_size"].value = format_size(stats.total_size_bytes)
        sl["photos"].value = str(stats.photos)
        sl["videos"].value = str(stats.videos)
        
        elapsed = time.time() - stats.start_time if stats.start_time else 0
        sl["elapsed"].value = format_duration(elapsed)
        
        if stats.processed_msgs > 0 and stats.total_channel_msgs > 0 and elapsed > 0:
            file_rate = stats.total_files / (elapsed / 60)
            sl["speed"].value = f"{file_rate:.1f} ф/мин"
            
            rem = stats.total_channel_msgs - stats.processed_msgs
            eta = (rem / stats.processed_msgs) * elapsed
            sl["eta"].value = format_duration(eta)
        self.page.update()

    def cb_request_input(self, prompt, callback):
        # Simple dialog for 2FA password
        def on_submit(e):
            val = inp.value
            dlg.open = False
            self.page.update()
            callback(val)

        inp = ft.TextField(label=prompt, password=True)
        dlg = ft.AlertDialog(
            title=ft.Text(t("Требуется ввод")),
            content=inp,
            actions=[ft.TextButton(t("ОК"), on_click=on_submit)]
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    # Button Handlers
    async def on_auth(self, e):
        self.lbl_auth_status.value = "Подключение..."
        self.write_auth_log("Запрос авторизации...")
        self.page.update()
        
        try:
            ok = await self.scraper.authorize()
            if ok:
                me = await self.scraper.client.get_me()
                phone = f" (+{me.phone})" if getattr(me, 'phone', None) else ""
                self.lbl_auth_status.value = f"✅ Авторизован{phone}"
                self.lbl_auth_status.color = ft.colors.GREEN_400
                self.img_qr.visible = False
                self.write_auth_log("Успешная авторизация!")
            else:
                self.lbl_auth_status.value = "❌ Ошибка авторизации"
                self.lbl_auth_status.color = ft.colors.RED_400
        except Exception as err:
            self.write_auth_log(f"Ошибка: {err}")
        self.page.update()

    async def on_logout(self, e):
        await self.scraper.disconnect()
        # Clean session
        try:
            if os.path.exists("telegram_session.session"):
                os.remove("telegram_session.session")
            if os.path.exists("telegram_session.session-journal"):
                os.remove("telegram_session.session-journal")
            self.write_auth_log("Сессия удалена. Выполнен выход из аккаунта.")
        except Exception as ex:
            self.write_auth_log(f"Ошибка при удалении сессии: {ex}")
        
        self.lbl_auth_status.value = "Ожидание авторизации"
        self.lbl_auth_status.color = ft.colors.GREY_400
        self.page.update()

    async def on_start_dl(self, e):
        asyncio.create_task(self.scraper.start_download())

    async def on_stop_dl(self, e):
        await self.scraper.stop()

    async def on_live(self, e):
        asyncio.create_task(self.scraper.start_monitor())
        
    async def on_scan_missing(self, e):
        asyncio.create_task(self.scraper.scan_missing_posts())
        
    async def on_download_missing(self, e):
        asyncio.create_task(self.scraper.download_missing_posts())

    async def on_reset(self, e):
        cb_delete_files = ft.Checkbox(label=t("Удалить все скачанные медиафайлы"), value=False)
        
        def do_reset(ev):
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
                    try: os.remove(history_path)
                    except: pass
                
                # Optionally delete media files
                if cb_delete_files.value and os.path.exists(dl_dir):
                    try:
                        for filename in os.listdir(dl_dir):
                            file_path = os.path.join(dl_dir, filename)
                            if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                import shutil
                                shutil.rmtree(file_path)
                        self.write_log("Скачанные файлы удалены.", ft.colors.ORANGE_400)
                    except Exception as err:
                        self.write_log(f"Ошибка удаления файлов: {err}", ft.colors.RED_400)
                        
                self.write_log("Прогресс канала и история сброшены!", ft.colors.ORANGE_400)
            
        dlg = ft.AlertDialog(
            title=ft.Text(t("Сброс прогресса")),
            content=ft.Column([
                ft.Text(t("Вы уверены, что хотите начать скачивание этого канала с самого начала?")),
                cb_delete_files
            ], tight=True),
            actions=[
                ft.TextButton(t("Отмена"), on_click=lambda e: setattr(dlg, 'open', False) or self.page.update()),
                ft.TextButton(t("Сбросить"), on_click=do_reset, style=ft.ButtonStyle(color=ft.colors.RED_400))
            ]
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

async def main(page: ft.Page):
    app = TelegramScraperFlet(page)

if __name__ == "__main__":
    ft.app(target=main)
