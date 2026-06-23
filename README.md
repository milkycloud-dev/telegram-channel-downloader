<div align="center">
  <img src="assets/icon.png" width="128" height="128" alt="Telegram Channel Downloader Icon">
  
  # Telegram Channel Downloader

  ![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
  ![License](https://img.shields.io/badge/License-Proprietary-red.svg)
  ![OS](https://img.shields.io/badge/OS-Windows%20%7C%20Linux-lightgrey.svg)
  
  [Русский](#русский) | [English](#english)
</div>

---

<a name="русский"></a>
## Русский

**Telegram Channel Downloader** — программное обеспечение для автоматизированного извлечения медиаданных и комментариев из информационных каналов Telegram.

**ВНИМАНИЕ:** Данное программное обеспечение разработано исключительно в образовательных целях. Программа не осуществляет обход систем защиты, использует официальный протокол авторизации и не нарушает правила использования (Terms of Service) мессенджера Telegram. Загрузка данных осуществляется строго в рамках прав доступа, предоставленных авторизованному пользовательскому аккаунту.

### Функциональные возможности
* **Асинхронная архитектура:** Реализация на базе библиотеки asyncio обеспечивает высокопроизводительную обработку данных и поддержку множественных параллельных потоков загрузки.
* **Протокол MTProto:** Взаимодействие с серверами Telegram осуществляется через криптографический протокол MTProto (библиотека Telethon), что гарантирует максимальную скорость и безопасность соединения.
* **Локальная СУБД:** Учет и контроль загруженных медиафайлов ведется посредством легковесной базы данных SQLite, предотвращая дублирование загрузок при повторных сессиях.
* **Live-Мониторинг:** Модуль непрерывного мониторинга позволяет отслеживать целевые каналы в режиме реального времени с мгновенным извлечением нового контента.
* **Динамический графический интерфейс:** Фронтенд приложения построен на базе фреймворка Flet (технология Flutter), обеспечивая информативную визуализацию процессов и детализированное логирование.
* **Отказоустойчивость:** Интегрированы алгоритмы автоматического восстановления соединения при разрывах сети и обработки серверных ограничений (FloodWait).
* **Локализация:** Поддерживается мгновенная смена языковых параметров интерфейса (Русский/English) без потери текущей сессии авторизации.

### Развертывание
1. Требуется наличие установленной среды Python версии 3.11 или выше.
2. Инсталляция зависимостей:
   ```bash
   pip install -r requirements.txt
   ```
3. Запуск исполнительного модуля:
   ```bash
   python main_flet.py
   ```

### Лицензия
Программное обеспечение распространяется на условиях проприетарной лицензии (Proprietary Software License). Детальные условия эксплуатации приведены в файле `LICENSE`.

---

<a name="english"></a>
## English

**Telegram Channel Downloader** is software designed for automated extraction of media data and comments from Telegram channels.

**WARNING:** This software is developed strictly for educational purposes. The application does not bypass any security systems, utilizes the official authorization protocol, and does not violate the Telegram Terms of Service. Data extraction is performed strictly within the access rights granted to the authorized user account.

### Technical Capabilities
* **Asynchronous Architecture:** Implemented utilizing the asyncio library to ensure high-performance data processing and support for multiple parallel download streams.
* **MTProto Protocol:** Communication with Telegram servers is established via the MTProto cryptographic protocol (Telethon library), ensuring maximum speed and connection security.
* **Local DBMS:** Downloaded media files are tracked and controlled through a lightweight SQLite database, preventing duplicate downloads during subsequent sessions.
* **Live Monitoring:** The continuous monitoring module enables real-time tracking of target channels with immediate extraction of new content.
* **Dynamic GUI:** The application frontend is built on the Flet framework (Flutter technology), providing informative process visualization and detailed logging.
* **Fault Tolerance:** Integrated algorithms for automatic connection recovery during network interruptions and server restriction handling (FloodWait).
* **Localization:** Supports instant switching of interface language parameters (Russian/English) without terminating the current authorization session.

### Deployment
1. Python environment version 3.11 or higher is required.
2. Dependency installation:
   ```bash
   pip install -r requirements.txt
   ```
3. Execution:
   ```bash
   python main_flet.py
   ```

### License
This software is distributed under a Proprietary Software License. Detailed operating conditions are provided in the `LICENSE` file.
