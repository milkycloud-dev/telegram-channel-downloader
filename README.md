<p align="center"><img src="assets/icon.png" width="128" height="128" alt="Telegram Channel and Chat Downloader icon"></p>

<h1 align="center">Telegram Channel and Chat Downloader</h1>

<p align="center">Desktop app that backs up Telegram channels, groups and personal chats you have access to, with all media, and turns them into an offline HTML archive that looks like Telegram. Telethon and Flet, Windows and Linux.</p>

<p align="center"><a href="https://github.com/milkycloud-dev/telegram-channel-downloader/actions/workflows/release.yml"><img src="https://github.com/milkycloud-dev/telegram-channel-downloader/actions/workflows/release.yml/badge.svg" alt="Release"></a></p>

<p align="center"><a href="#english">English</a> | <a href="#русский">Русский</a></p>

<a id="english"></a>
## English

The app downloads a channel, group or personal chat through your own Telegram account: text, photos, video, documents, voice and video notes, stickers, GIFs, comments, replies and the other side's profile. From that it builds a set of HTML pages styled like Telegram Web, which open from disk without a server or internet access.

### Features

* **Channels, Groups & Personal Chats:** Download content from public and private channels, supergroups, and personal 1-on-1 dialogues.
* **Telegram dialogue styling:** Direct messages are exported with complete interlocutor separation:
  * **Incoming messages:** Displayed on the left in dark slate bubbles (`#182533`), featuring the interlocutor's avatar and colored sender name.
  * **Outgoing messages:** Positioned on the right in Telegram blue bubbles (`#2b5278`) with delivery status checkmarks (`✓✓`).
  * **Reply chains:** Visual quote bars linking directly to the original message.
  * **Consecutive message grouping:** Adaptive spacing and tail styling matching Telegram Desktop.
* **Global Cross-Page Archive Search:** Instant full-text search across all downloaded messages, spanning across every page of the archive (`search_index.js`). Highlights matched keywords and provides direct one-click navigation to the exact message on any page with an animated pulse highlight.
* **Complete Offline Portability:** Generates self-contained HTML pages with relative paths. Works out of the box directly from your file manager via `file:///` without needing a local web server or internet connection.
* **Full Media Backup:** Downloads high-resolution photos, videos, voice messages (`.ogg`), video notes, audio files, and documents with built-in interactive lightbox preview and media players.
* **Speed and resume:**
  * Multi-threaded asynchronous downloads (`asyncio`) with parallel worker queues.
  * MTProto through Telethon.
  * Rate limiting with random delays and automatic FloodWait handling.
  * Resume capability: Automatically picks up from the last downloaded message ID.
* **Interface:** English and Russian, live statistics, progress bars and a theme switch, built on Flet.

### Quick start

1. **Python 3.11+** is required.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the application:
   ```bash
   python main_flet.py
   ```
4. **Windows users** can also simply double-click:
   ```bash
   start.bat
   ```

### Usage

1. **Authorize.** Open the Authorization tab and log in via QR code or phone number.
2. **Configure.** On the Settings tab, enter the Channel/User ID or username and set the destination folder.
3. **Download.** Click Start on the Download tab to begin the backup process.
4. **Generate & View.** Click "Generate HTML" to compile the offline archive, then click "Open HTML" to browse.
5. **Live Monitoring.** Use the Live tab to automatically capture new posts and messages as they appear.

### Archive folder structure

```
downloads/
└── chat_or_channel_name/
    ├── 1.jpg                 # Downloaded media files
    ├── 2.mp4
    ├── peer_avatar.jpg       # Interlocutor profile photo
    ├── channel_data.json     # Complete structured message dataset
    ├── chat_meta.json        # Dialogue & interlocutor metadata
    ├── search_index.js       # Fast global cross-page search index
    ├── index.html            # Main archive viewer (Page 1)
    ├── page_2.html           # Paginated archive view
    └── ...
```

### Disclaimer

> **USE AT YOUR OWN RISK.** The author(s) bear **NO responsibility** for any consequences arising from the use of this tool, including account restrictions, terms of service violations, or data handling in your jurisdiction. This software is provided **"as is"** for **educational and backup purposes only**. You are solely responsible for compliance with all applicable laws and Telegram Terms of Service.

### Releases

A tag `v*` builds `TelegramDownloader_Windows.zip` and `TelegramDownloader_Linux.tar.gz` with PyInstaller on GitHub Actions and publishes them with the notes from [CHANGELOG.md](CHANGELOG.md).

### License

Proprietary, all rights reserved. Running the official release builds is allowed; see [LICENSE](LICENSE) for the full terms.

<a id="русский"></a>
## Русский

Приложение скачивает канал, группу или личный чат через ваш собственный аккаунт Telegram: текст, фото, видео, документы, голосовые и видеокружки, стикеры, GIF, комментарии, ответы и профиль собеседника. Из этого собирается набор HTML-страниц в стиле Telegram Web, которые открываются с диска без сервера и интернета.

### Возможности

* **Каналы, группы и личные диалоги:** Загрузка постов и переписок из публичных и закрытых каналов, супергрупп и личных чатов.
* **Оформление диалогов как в Telegram:** Личные чаты экспортируются с полноценным разделением собеседников:
  * **Входящие сообщения:** Располагаются слева в тёмно-серых бабблах (`#182533`) с аватаркой собеседника и цветным именем автора.
  * **Исходящие сообщения:** Располагаются справа в синих бабблах Telegram (`#2b5278`) со значками доставки (`✓✓`).
  * **Цитирование ответов:** Интерактивные блоки реплаев с полосой цитирования и переходом к исходному сообщению.
  * **Группировка подряд идущих сообщений:** Адаптивные отступы и скругления углов бабблов в точности как в Telegram Desktop.
* **Глобальный межистраничный поиск по архиву:** Мгновенный полнотекстовый поиск по всем сообщениям переписки сквозь все страницы архива (`search_index.js`). Подсвечивает ключевые слова и позволяет в один клик перейти к нужному сообщению на любой странице с плавной анимацией подсветки.
* **Полная оффлайн-автономность:** Генерирует полностью автономные HTML-страницы с относительными путями. Архив открывается напрямую через браузер по `file:///` и корректно работает без интернета и локальных веб-серверов.
* **Полная выгрузка медиа:** Сохраняет оригинальные фото, видео, аудиозаписи, голосовые сообщения (`.ogg`), видеокружки и файлы с удобным просмотром через встроенный лайтбокс и медиаплееры.
* **Скорость и докачка:**
  * Асинхронная загрузка (`asyncio`) с очередями параллельных задач.
  * MTProto через Telethon.
  * Ограничение частоты: случайные задержки и автоматическая обработка FloodWait.
  * Докачка и возобновление: запоминает ID последнего сообщения и продолжает с места остановки.
* **Интерфейс:** английский и русский, живая статистика, прогресс-бары и переключение темы, на Flet.

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
4. **Для пользователей Windows** доступен удобный запуск:
   ```bash
   start.bat
   ```

### Инструкция по использованию

1. **Авторизация.** Перейдите на вкладку Authorization и выполните вход по QR-коду или номеру телефона.
2. **Настройка.** Во вкладке Settings укажите ID канала/пользователя или username, а также папку для сохранения.
3. **Скачивание.** Нажмите Start во вкладке Download для запуска полной выгрузки.
4. **Просмотр.** Нажмите «Generate HTML» для генерации оффлайн-архива, затем «Open HTML» для открытия в браузере.
5. **Мониторинг.** Используйте вкладку Live для автоматического отслеживания и скачивания новых сообщений в реальном времени.

### Структура директории архива

```
downloads/
└── имя_чата_или_канала/
    ├── 1.jpg                 # Медиафайлы
    ├── 2.mp4
    ├── peer_avatar.jpg       # Аватар собеседника
    ├── channel_data.json     # Полный структурированный массив сообщений
    ├── chat_meta.json        # Метаданные диалога и участников
    ├── search_index.js       # Индекс для глобального сквозного поиска
    ├── index.html            # Главная страница просмотрщика (Стр. 1)
    ├── page_2.html           # Последующие страницы архива
    └── ...
```

### Отказ от ответственности

> **ИСПОЛЬЗУЙТЕ НА СВОЙ СТРАХ И РИСК.** Автор(ы) данного программного обеспечения **НЕ НЕСУТ НИКАКОЙ ОТВЕТСТВЕННОСТИ** за любые возможные последствия его использования, включая блокировки аккаунтов или нарушение правил платформы. ПО предоставляется **«как есть»** исключительно в **образовательных целях и для личного резервного копирования**. Пользователь несет персональную ответственность за соблюдение законодательства и Условий использования Telegram.

### Релизы

Тег `v*` собирает `TelegramDownloader_Windows.zip` и `TelegramDownloader_Linux.tar.gz` через PyInstaller в GitHub Actions и публикует их с описанием из [CHANGELOG.md](CHANGELOG.md).

### Лицензия

Проприетарная, все права защищены. Запуск официальных сборок из релизов разрешён; полные условия в [LICENSE](LICENSE).
