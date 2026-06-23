import re

with open('main_flet.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix f-string syntax errors caused by \'
content = content.replace('f"{t(\\\'Ошибка проверки авторизации:\\\')} {e}"', 'f\'{t("Ошибка проверки авторизации:")} {e}\'')
content = content.replace('f"❌ {t(\\\'Ошибка авторизации\\\')}"', 'f\'❌ {t("Ошибка авторизации")}\'')
content = content.replace('f"{t(\\\'Файл\\\')} #{prefix}: {format_size(done)} / {format_size(total)}"', 'f\'{t("Файл")} #{prefix}: {format_size(done)} / {format_size(total)}\'')
content = content.replace('f"{file_rate:.1f} {t(\\\'ф/мин\\\')}"', 'f\'{file_rate:.1f} {t("ф/мин")}\'')
content = content.replace('f"[{t(\\\'ОШИБКА\\\')}] {text}"', 'f\'[{t("ОШИБКА")}] {text}\'')
content = content.replace('f"{t(\\\'Ошибка:\\\')} {err}"', 'f\'{t("Ошибка:")} {err}\'')
content = content.replace('f"{t(\\\'Ошибка при удалении сессии:\\\')} {ex}"', 'f\'{t("Ошибка при удалении сессии:")} {ex}\'')
content = content.replace('f"{t(\\\'Ошибка удаления файлов:\\\')} {err}"', 'f\'{t("Ошибка удаления файлов:")} {err}\'')

with open('main_flet.py', 'w', encoding='utf-8') as f:
    f.write(content)
