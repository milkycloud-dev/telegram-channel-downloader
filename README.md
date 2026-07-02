<div align="center">
  <img src="assets/icon.png" width="128" height="128" alt="Telegram Secret Channel Downloader Icon">
  
  # Telegram Secret Channel Downloader

  ![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
  ![License](https://img.shields.io/badge/License-Proprietary-red.svg)
  ![OS](https://img.shields.io/badge/OS-Windows%20%7C%20Linux-lightgrey.svg)
  ![Version](https://img.shields.io/badge/Version-2.0-green.svg)
  
  [English](#english) | [Русский](#русский)
</div>

---

<a name="english"></a>
## English

**Telegram Secret Channel Downloader** is a powerful desktop tool for complete backup and archival of Telegram channels — including **private and secret channels** you have access to.

Unlike basic scrapers, this tool downloads **everything**: text posts, media files (photos, videos, documents, voice messages, video notes, stickers, GIFs), and comments — then generates a beautiful **offline HTML viewer** styled like Telegram Web for convenient browsing without an internet connection.

### Key Features

* **Secret & Private Channels:** Download content from any channel you have access to, including invite-only and restricted channels. Uses your authorized Telegram account via the official MTProto protocol.
* **Full Content Backup:** Downloads not just media, but also **text posts** and **comments** — preserving the complete channel history.
* **Offline HTML Viewer:** Generates a self-contained HTML archive styled like Telegram Web with dark theme, search, pagination, and image lightbox. All links are relative — the archive works perfectly when moved to another location.
* **Async Architecture:** Built on `asyncio` with up to 3 parallel downloads for maximum throughput.
* **MTProto Encryption:** Uses the same cryptographic protocol as official Telegram apps (via Telethon library).
* **Live Monitoring:** Real-time channel monitoring with automatic download of new posts.
* **Fault Tolerance:** Auto-reconnect on network drops, retry with exponential backoff, FloodWait handling.
* **Resume Support:** Tracks download progress per channel — resume from where you left off after restart.
* **Bilingual UI:** English and Russian interface with instant language switching.
* **Modern GUI:** Built with Flet (Flutter for Python) with real-time progress bars, statistics, and system logs.

### Quick Start

1. **Python 3.11+** is required.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main_flet.py
   ```
4. **Windows users** can also use the launcher script:
   ```bash
   start.bat
   ```

### Usage

1. **Authorize** — Go to the Authorization tab and log in via QR code or phone number.
2. **Configure** — In Settings, enter the Channel ID or username and set the download directory.
3. **Download** — Click Start on the Download tab to begin full channel backup.
4. **View Offline** — Click "Generate HTML" to create the offline viewer, then "Open HTML" to browse.
5. **Monitor** — Use the Live tab to watch for new posts in real-time.

### Output Structure

```
downloads/
├── channel_12345/
│   ├── 1.jpg              # Post media files
│   ├── 2.mp4
│   ├── 3_1.jpg            # Comment media
│   ├── channel_data.json  # Structured post data
│   ├── index.html         # Offline viewer (page 1)
│   └── page_2.html        # Offline viewer (page 2)
```

### Disclaimer

> **USE AT YOUR OWN RISK.** The author(s) of this software bear **NO responsibility** for any consequences arising from the use of this tool, including but not limited to:
> - Telegram account restrictions or bans
> - Violation of Telegram Terms of Service
> - Copyright infringement claims
> - Data loss or corruption
> - Legal consequences in your jurisdiction
>
> This software is provided **"as is"** for **educational and research purposes only**. The application uses the official Telegram API protocol and does not bypass any security measures. However, automated access to Telegram channels may violate their Terms of Service. **You are solely responsible for ensuring your use complies with all applicable laws, regulations, and terms of service.**
>
> By using this software, you acknowledge that you understand and accept these risks.

### License

This software is distributed under a Proprietary Software License. See the `LICENSE` file for details.

---

<a name="русский"></a>
## Русский

**Telegram Secret Channel Downloader** — мощный десктопный инструмент для полного бэкапа и архивирования Telegram-каналов, включая **приватные и секретные каналы**, к которым у вас есть доступ.

В отличие от простых скраперов, этот инструмент скачивает **всё**: текстовые посты, медиафайлы (фото, видео, документы, голосовые сообщения, видеокружки, стикеры, GIF), а также комментарии — и генерирует красивый **оффлайн HTML-просмотрщик** в стиле Telegram Web для удобного просмотра без интернета.

### Ключевые возможности

* **Секретные и приватные каналы:** Скачивание контента из любых каналов, к которым у вас есть доступ, включая каналы по приглашениям и с ограниченным доступом. Использует ваш авторизованный аккаунт через официальный протокол MTProto.
* **Полный бэкап контента:** Скачивает не только медиа, но и **текстовые посты** и **комментарии** — сохраняя полную историю канала.
* **Оффлайн HTML-просмотрщик:** Генерирует самодостаточный HTML-архив в стиле Telegram Web с тёмной темой, поиском, пагинацией и лайтбоксом для изображений. Все ссылки относительные — архив корректно работает при перемещении в другую папку.
* **Асинхронная архитектура:** Построен на `asyncio` с параллельной загрузкой до 3 файлов одновременно.
* **Шифрование MTProto:** Использует тот же криптографический протокол, что и официальные приложения Telegram (библиотека Telethon).
* **Live-мониторинг:** Мониторинг канала в реальном времени с автоматической загрузкой новых постов.
* **Отказоустойчивость:** Автопереподключение при обрывах сети, повторные попытки с экспоненциальной задержкой, обработка FloodWait.
* **Возобновление загрузки:** Отслеживает прогресс скачивания для каждого канала — продолжает с того места, где остановились.
* **Двуязычный интерфейс:** Английский и русский с мгновенным переключением.
* **Современный GUI:** Построен на Flet (Flutter для Python) с прогресс-барами, статистикой и системными логами в реальном времени.

### Быстрый старт

1. Требуется **Python 3.11+**.
2. Установка зависимостей:
   ```bash
   pip install -r requirements.txt
   ```
3. Запуск приложения:
   ```bash
   python main_flet.py
   ```
4. **Пользователи Windows** также могут использовать скрипт запуска:
   ```bash
   start.bat
   ```

### Использование

1. **Авторизация** — Перейдите на вкладку Authorization и войдите через QR-код или номер телефона.
2. **Настройка** — В настройках укажите ID канала или username и директорию для загрузки.
3. **Скачивание** — Нажмите Start на вкладке Download для полного бэкапа канала.
4. **Просмотр оффлайн** — Нажмите «Generate HTML» для создания просмотрщика, затем «Open HTML» для просмотра.
5. **Мониторинг** — Используйте вкладку Live для отслеживания новых постов в реальном времени.

### Отказ от ответственности

> **ИСПОЛЬЗУЙТЕ НА СВОЙ СТРАХ И РИСК.** Автор(ы) данного программного обеспечения **НЕ НЕСУТ НИКАКОЙ ОТВЕТСТВЕННОСТИ** за любые последствия, возникшие в результате использования этого инструмента, включая, но не ограничиваясь:
> - Ограничения или блокировка аккаунта Telegram
> - Нарушение Условий использования Telegram
> - Претензии о нарушении авторских прав
> - Потеря или повреждение данных
> - Юридические последствия в вашей юрисдикции
>
> Данное ПО предоставляется **«как есть»** исключительно в **образовательных и исследовательских целях**. Приложение использует официальный протокол Telegram API и не обходит никакие системы защиты. Тем не менее, автоматизированный доступ к каналам Telegram может нарушать их Условия использования. **Вы несёте полную ответственность за соблюдение всех применимых законов, правил и условий использования.**
>
> Используя данное ПО, вы подтверждаете, что понимаете и принимаете эти риски.

### Лицензия

Программное обеспечение распространяется на условиях проприетарной лицензии. Подробности в файле `LICENSE`.
