import re

content = open("main_flet.py", "r", encoding="utf-8").read()

content = re.sub(r'ft\.Text\("([^"]+)"', r'ft.Text(t("\1")', content)
content = re.sub(r'label="([^"]+)"', r'label=t("\1")', content)
content = re.sub(r'ft\.ElevatedButton\("([^"]+)"', r'ft.ElevatedButton(t("\1")', content)
content = re.sub(r'ft\.TextButton\("([^"]+)"', r'ft.TextButton(t("\1")', content)
content = re.sub(r'ft\.Tab\(text="([^"]+)"', r'ft.Tab(text=t("\1")', content)

if "from i18n import" not in content:
    content = "from i18n import t, set_lang, get_lang\n" + content

open("main_flet.py", "w", encoding="utf-8").write(content)
print("done")
