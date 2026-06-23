import re

with open('main_flet.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Translate string literals
replacements = [
    # Auth logs
    (r'self\.write_auth_log\("Авторизация загружена из кэша\."\)', r'self.write_auth_log(t("Авторизация загружена из кэша."))'),
    (r'self\.write_auth_log\(f"Ошибка проверки авторизации: \{e\}"\)', r'self.write_auth_log(f"{t(\'Ошибка проверки авторизации:\')} {e}")'),
    (r'self\.write_auth_log\("Отсканируйте QR код в приложении Telegram \(Settings -> Devices -> Link Desktop Device\)"\)', r'self.write_auth_log(t("Отсканируйте QR код в приложении Telegram (Settings -> Devices -> Link Desktop Device)"))'),
    (r'self\.write_auth_log\("Запрос авторизации\.\.\."\)', r'self.write_auth_log(t("Запрос авторизации..."))'),
    (r'self\.write_auth_log\("Успешная авторизация!"\)', r'self.write_auth_log(t("Успешная авторизация!"))'),
    (r'self\.write_auth_log\(f"Ошибка: \{err\}"\)', r'self.write_auth_log(f"{t(\'Ошибка:\')} {err}")'),
    (r'self\.write_auth_log\("Сессия удалена\. Выполнен выход из аккаунта\."\)', r'self.write_auth_log(t("Сессия удалена. Выполнен выход из аккаунта."))'),
    (r'self\.write_auth_log\(f"Ошибка при удалении сессии: \{ex\}"\)', r'self.write_auth_log(f"{t(\'Ошибка при удалении сессии:\')} {ex}")'),

    # Labels and Progress
    (r'self\.lbl_auth_status\.value = "Подключение\.\.\."', r'self.lbl_auth_status.value = t("Подключение...")'),
    (r'self\.lbl_auth_status\.value = "❌ Ошибка авторизации"', r'self.lbl_auth_status.value = f"❌ {t(\'Ошибка авторизации\')}"'),
    (r'bar_data\["lbl"\]\.value = f"Файл #\{prefix\}: \{format_size\(done\)\} / \{format_size\(total\)\}"', r'bar_data["lbl"].value = f"{t(\'Файл\')} #{prefix}: {format_size(done)} / {format_size(total)}"'),
    (r'sl\["speed"\]\.value = f"\{file_rate:\.1f\} ф/мин"', r'sl["speed"].value = f"{file_rate:.1f} {t(\'ф/мин\')}"'),

    # System Logs
    (r'self\.write_log\("Настройки сохранены", ft\.colors\.GREEN_400\)', r'self.write_log(t("Настройки сохранены"), ft.colors.GREEN_400)'),
    (r'self\.write_log\(f"\[ОШИБКА\] \{text\}", ft\.colors\.RED_400\)', r'self.write_log(f"[{t(\'ОШИБКА\')}] {text}", ft.colors.RED_400)'),
    (r'self\.write_monitor_log\(f"\[ОШИБКА\] \{text\}", ft\.colors\.RED_400\)', r'self.write_monitor_log(f"[{t(\'ОШИБКА\')}] {text}", ft.colors.RED_400)'),
    (r'self\.write_log\("Скачивание завершено", ft\.colors\.GREEN_400\)', r'self.write_log(t("Скачивание завершено"), ft.colors.GREEN_400)'),
    (r'self\.cb_status\("Ожидание"\)', r'self.cb_status(t("Ожидание"))'),
    (r'self\.write_log\("Скачанные файлы удалены\.", ft\.colors\.ORANGE_400\)', r'self.write_log(t("Скачанные файлы удалены."), ft.colors.ORANGE_400)'),
    (r'self\.write_log\(f"Ошибка удаления файлов: \{err\}", ft\.colors\.RED_400\)', r'self.write_log(f"{t(\'Ошибка удаления файлов:\')} {err}", ft.colors.RED_400)'),
    (r'self\.write_log\("Прогресс канала и история сброшены!", ft\.colors\.ORANGE_400\)', r'self.write_log(t("Прогресс канала и история сброшены!"), ft.colors.ORANGE_400)'),
]

for old, new in replacements:
    content = re.sub(old, new, content)

# 2. Fix build_settings_tab to include dd_lang
# Find build_settings_tab
settings_start = content.find('def build_settings_tab(self):')
settings_end = content.find('def load_settings(self):', settings_start)
settings_content = content[settings_start:settings_end]

# If dd_lang not in settings, add it
if 'self.dd_lang = ft.Dropdown' not in settings_content:
    replacement_str = '''
        from i18n import get_lang
        self.dd_lang = ft.Dropdown(
            label=t("Язык / Language"),
            value=get_lang(),
            options=[
                ft.dropdown.Option("ru", "Русский"),
                ft.dropdown.Option("en", "English")
            ],
            on_change=lambda e: self.page.run_task(self.change_lang, e),
            width=200
        )
        self.cb_save_history = ft.Checkbox'''
    settings_content = re.sub(r'\n\s*self\.cb_save_history = ft\.Checkbox', replacement_str, settings_content)

    col_replace = '''
                ft.Column([
                    self.dd_lang,
                    self.txt_delay,'''
    settings_content = re.sub(r'\n\s*ft\.Column\(\[\n\s*self\.txt_delay,', col_replace, settings_content)
    
    content = content[:settings_start] + settings_content + content[settings_end:]

# 3. Add change_lang method if missing
if 'async def change_lang(self, e):' not in content:
    method_str = '''
    async def change_lang(self, e):
        from i18n import set_lang
        set_lang(e.control.value)
        self.page.controls.clear()
        self.build_ui()
        self.load_settings()
        await self._update_auth_status()
        self.page.update()
'''
    insert_pos = content.find('    def build_ui(self):')
    content = content[:insert_pos] + method_str + content[insert_pos:]

# 4. Remove flags from build_ui
ui_start = content.find('    def build_ui(self):')
ui_end = content.find('    def build_auth_tab(self):', ui_start)
ui_content = content[ui_start:ui_end]

# remove btn_ru, btn_en and language icon from header
ui_content = re.sub(r'\s*btn_ru = ft\.TextButton.*?\n', '\n', ui_content)
ui_content = re.sub(r'\s*btn_en = ft\.TextButton.*?\n', '\n', ui_content)
ui_content = re.sub(r',\s*ft\.Row\(\[ft\.Icon\(ft\.icons\.LANGUAGE.*?\].*?\)', '', ui_content)

# Remove the inner async def change_lang inside build_ui if it exists
ui_content = re.sub(r'\s*async def change_lang.*?self\.page\.update\(\)', '', ui_content, flags=re.DOTALL)
ui_content = re.sub(r'\s*def change_lang.*?self\.page\.update\(\)', '', ui_content, flags=re.DOTALL)

content = content[:ui_start] + ui_content + content[ui_end:]

# 5. Fix the bad replace previously where cb_save_history was added in on_reset
# 'self.cb_save_history = ft.Checkbox(label=t("Удалять историю скачанного при сбросе (история хранится в SQLite)"), value=False)' inside on_reset
bad_replace = 'self.cb_save_history = ft.Checkbox(label=t("Удалять историю скачанного при сбросе (история хранится в SQLite)"), value=False)'
good_replace = 'cb_delete_files = ft.Checkbox(label=t("Удалить все скачанные медиафайлы"), value=False)'
# Only replace the one inside on_reset
if 'async def on_reset(self, e):' in content:
    reset_start = content.find('async def on_reset(self, e):')
    reset_content = content[reset_start:]
    reset_content = reset_content.replace(bad_replace, good_replace, 1)
    content = content[:reset_start] + reset_content

# 6. Also clean up the wrong dd_lang insertion at line 317 in build_live_tab if it happened
content = re.sub(r'\n\s*ft\.Text\(t\("Общие настройки"\).*?\n\s*self\.dd_lang,', '', content)

with open('main_flet.py', 'w', encoding='utf-8') as f:
    f.write(content)
