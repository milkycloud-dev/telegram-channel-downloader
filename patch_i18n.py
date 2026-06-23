import re
with open('i18n.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_keys = {
    'Всего сообщений': 'Total messages',
    'Обработано': 'Processed',
    'Всего файлов': 'Total files',
    'Общий размер': 'Total size',
    '📷 Фото': '📷 Photos',
    '🎬 Видео': '🎬 Videos',
    '⏱ Время работы': '⏱ Elapsed',
    '🚀 Скорость': '🚀 Speed',
    '⏳ Осталось': '⏳ ETA',
    'Общий прогресс:': 'Overall progress:',
    'сообщений': 'messages',
    'Авторизован': 'Authorized',
    'Сохранено': 'Saved',
    'Ожидание авторизации': 'Waiting for authorization',
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
