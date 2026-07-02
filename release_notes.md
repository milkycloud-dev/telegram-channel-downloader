# Release Notes — v2.0

## Telegram Secret Channel Downloader v2.0

Major release with complete rebrand, new features, and codebase overhaul.

### 🚀 New Features

* **Text Post Downloading:** The tool now downloads ALL content types — not just media. Text-only posts are saved alongside media files and included in the HTML viewer.
* **Offline HTML Viewer:** Generate a self-contained HTML archive styled like Telegram Web with dark theme, search, pagination, image lightbox, and collapsible comments. All paths are relative for full portability.
* **Complete Content Backup:** Posts, media, comments, metadata — everything is captured and stored in a structured `channel_data.json` for programmatic access.

### 🔧 Improvements

* **Full English Translation:** All code strings translated to English using a key-based i18n system. Russian available as a secondary language.
* **English-Only Code Comments:** Every function documented with English docstrings. All Russian comments replaced.
* **Code Cleanup:** Removed dead code (`main.py` that referenced non-existent `gui_app`), unused imports, and legacy patterns.
* **Key-Based i18n:** Migrated from Russian-first `t("Русский текст")` to proper key-based `t('key')` approach with `lang.json` persistence.
* **Language Selector:** Added language dropdown to Settings tab with instant hot-swap.
* **Rebranding:** Project renamed to "Telegram Secret Channel Downloader" to better reflect capabilities with private/secret channels.
* **Updated README:** Complete bilingual README with features, usage guide, and legal disclaimer.

### ⚠️ Breaking Changes

* i18n system is completely rewritten — custom translations from v1.x are not compatible.
* `main.py` entry point removed — use `main_flet.py` directly.
