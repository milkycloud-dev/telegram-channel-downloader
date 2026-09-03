<div align="center">
  <img src="assets/icon.png" width="140" height="140" alt="Telegram Channel & Chat Downloader Icon" style="border-radius: 28px; box-shadow: 0 8px 24px rgba(0,0,0,0.35);">
  
  # Telegram Channel & Chat Downloader

  ![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
  ![License](https://img.shields.io/badge/License-Proprietary-red.svg)
  ![OS](https://img.shields.io/badge/OS-Windows%20%7C%20Linux-lightgrey.svg)
  ![Version](https://img.shields.io/badge/Version-3.0-green.svg)
  
  [English](#english) | [Русский](#русский)
</div>

---

<a name="english"></a>
## English

**Telegram Channel & Chat Downloader** is a comprehensive desktop application for complete backup, export, and offline archiving of Telegram channels, groups, and **personal 1-on-1 chats (direct messages)** — including secret and restricted channels you have access to.

Unlike basic scrapers that only grab standalone files, this tool preserves the entire conversation ecosystem: text posts, media attachments (photos, videos, documents, voice notes, video circles, stickers, GIFs), comments, reply chains, and interlocutor metadata. It then compiles everything into an authentic, standalone **offline HTML archive** styled identically to Telegram Web and Desktop.

### Key Features

* **Channels, Groups & Personal Chats:** Download content from public and private channels, supergroups, and personal 1-on-1 dialogues.
* **Authentic Telegram Dialogue Styling:** Direct messages are exported with complete interlocutor separation:
  * **Incoming messages:** Displayed on the left in dark slate bubbles (`#182533`), featuring the interlocutor's avatar and colored sender name.
  * **Outgoing messages:** Positioned on the right in signature Telegram blue bubbles (`#2b5278`) with delivery status checkmarks (`✓✓`).
  * **Reply chains:** Visual quote bars linking directly to the original message.
  * **Consecutive message grouping:** Adaptive spacing and tail styling matching Telegram Desktop.
* **Global Cross-Page Archive Search:** Instant full-text search across all downloaded messages, spanning across every page of the archive (`search_index.js`). Highlights matched keywords and provides direct one-click navigation to the exact message on any page with an animated pulse highlight.
* **Complete Offline Portability:** Generates self-contained HTML pages with relative paths. Works out of the box directly from your file manager via `file:///` without needing a local web server or internet connection.
* **Full Media Backup:** Downloads high-resolution photos, videos, voice messages (`.ogg`), video notes, audio files, and documents with built-in interactive lightbox preview and media players.
* **High Performance & Resilience:**
  * Multi-threaded asynchronous downloads (`asyncio`) with parallel worker queues.
  * Native MTProto protocol encryption via Telethon.
  * Smart rate-limiting with organic humanized delays, jitter, and automatic FloodWait handling.
  * Resume capability: Automatically picks up from the last downloaded message ID.
* **Bilingual Modern UI:** English and Russian interface with live statistics, progress tracking, and instant theme switching built on Flet (Flutter for Python).

### Quick Start

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

### Usage Workflow

1. **Authorize** — Open the Authorization tab and log in via QR code or phone number.
2. **Configure** — On the Settings tab, enter the Channel/User ID or username and set the destination folder.
3. **Download** — Click Start on the Download tab to begin the backup process.
4. **Generate & View** — Click "Generate HTML" to compile the offline archive, then click "Open HTML" to browse.
5. **Live Monitoring** — Use the Live tab to automatically capture new posts and messages as they appear.

### Archive Folder Structure

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

### License

This software is distributed under a Proprietary Software License. See `LICENSE` for details.

---

<a name="русский"></a>
## Русский

**Telegram Channel & Chat Downloader** — мощное десктопное приложение для полного резервного копирования, экспорта и оффлайн-архивирования Telegram-каналов, групп и **личных чатов (диалогов один на один)**, включая приватные и закрытые каналы, к которым у вас есть доступ.

В отличие от обычных парсеров, программа сохраняет полную экосистему переписки: тексты сообщений, медиавложения (фото, видео, документы, голосовые сообщения, видеокружки, стикеры, GIF), ветки комментариев, цитаты ответов и данные собеседников. Затем всё компилируется в автономный **оффлайн HTML-архив**, визуально неотличимый от Telegram Web и Desktop.

### Ключевые возможности

* **Каналы, группы и личные диалоги:** Загрузка постов и переписок из публичных и закрытых каналов, супергрупп и личных чатов.
* **Аутентичный стиль диалогов Telegram:** Личные чаты экспортируются с полноценным разделением собеседников:
  * **Входящие сообщения:** Располагаются слева в тёмно-серых бабблах (`#182533`) с аватаркой собеседника и цветным именем автора.
  * **Исходящие сообщения:** Располагаются справа в фирменных сине-зелёных бабблах Telegram (`#2b5278`) со значками доставки (`✓✓`).
  * **Цитирование ответов:** Интерактивные блоки реплаев с полосой цитирования и переходом к исходному сообщению.
  * **Группировка подряд идущих сообщений:** Адаптивные отступы и скругления углов бабблов в точности как в Telegram Desktop.
* **Глобальный межистраничный поиск по архиву:** Мгновенный полнотекстовый поиск по всем сообщениям переписки сквозь все страницы архива (`search_index.js`). Подсвечивает ключевые слова и позволяет в один клик перейти к нужному сообщению на любой странице с плавной анимацией подсветки.
* **Полная оффлайн-автономность:** Генерирует полностью автономные HTML-страницы с относительными путями. Архив открывается напрямую через браузер по `file:///` и корректно работает без интернета и локальных веб-серверов.
* **Полная выгрузка медиа:** Сохраняет оригинальные фото, видео, аудиозаписи, голосовые сообщения (`.ogg`), видеокружки и файлы с удобным просмотром через встроенный лайтбокс и медиаплееры.
* **Высокая скорость и отказоустойчивость:**
  * Асинхронная загрузка (`asyncio`) с очередями параллельных задач.
  * Официальный криптографический протокол MTProto через библиотеку Telethon.
  * Защита от ограничений: органические задержки, джиттер и автообработка FloodWait.
  * Докачка и возобновление: запоминает ID последнего сообщения и продолжает с места остановки.
* **Двуязычный интерфейс:** Поддержка английского и русского языков с мгновенным переключением, живой статистикой и прогресс-барами на Flet (Flutter для Python).

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

1. **Авторизация** — Перейдите на вкладку Authorization и выполните вход по QR-коду или номеру телефона.
2. **Настройка** — Во вкладке Settings укажите ID канала/пользователя или username, а также папку для сохранения.
3. **Скачивание** — Нажмите Start во вкладке Download для запуска полной выгрузки.
4. **Просмотр** — Нажмите «Generate HTML» для генерации оффлайн-архива, затем «Open HTML» для открытия в браузере.
5. **Мониторинг** — Используйте вкладку Live для автоматического отслеживания и скачивания новых сообщений в реальном времени.

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

### Лицензия

Программное обеспечение распространяется на условиях проприетарной лицензии. Подробности в файле `LICENSE`.
