import re

with open('i18n.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_keys = {
    'Язык / Language': 'Language / Язык',
    'Авторизация загружена из кэша.': 'Authorization loaded from cache.',
    'Ошибка проверки авторизации:': 'Authorization check error:',
    'Отсканируйте QR код в приложении Telegram (Settings -> Devices -> Link Desktop Device)': 'Scan the QR code in the Telegram app (Settings -> Devices -> Link Desktop Device)',
    'Запрос авторизации...': 'Authorization request...',
    'Успешная авторизация!': 'Successful authorization!',
    'Ошибка:': 'Error:',
    'Сессия удалена. Выполнен выход из аккаунта.': 'Session deleted. Logged out of account.',
    'Ошибка при удалении сессии:': 'Error deleting session:',
    'Подключение...': 'Connecting...',
    'Ошибка авторизации': 'Authorization error',
    'Файл': 'File',
    'ф/мин': 'f/min',
    'Настройки сохранены': 'Settings saved',
    'ОШИБКА': 'ERROR',
    'Скачивание завершено': 'Download complete',
    'Ожидание': 'Waiting',
    'Скачанные файлы удалены.': 'Downloaded files deleted.',
    'Ошибка удаления файлов:': 'Error deleting files:',
    'Прогресс канала и история сброшены!': 'Channel progress and history reset!',
    'Общие настройки': 'General Settings',
}

lines = content.split('\n')
insert_idx = -1
for i, line in enumerate(lines):
    if '"Настройки": "Settings",' in line:
        insert_idx = i + 1
        break

if insert_idx == -1:
    for i, line in enumerate(lines):
        if '}' in line and '"' in lines[i-1]:
            insert_idx = i
            break

for k, v in new_keys.items():
    if f'"{k}"' not in content:
        lines.insert(insert_idx, f'        "{k}": "{v}",')

with open('i18n.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
