# Release Notes — v3.0

## Telegram Channel & Chat Downloader v3.0

Major release introducing personal 1-on-1 chats & direct messages export, authentic Telegram Web/Desktop dialogue styling with interlocutor separation, global cross-page archive search, and brand-new visual identity.

### 🚀 New Features

* **Personal Chats & Direct Messages (Личные диалоги):** Full support for downloading and viewing 1-on-1 personal dialogues with complete interlocutor separation:
  * Incoming messages styled on the left in dark slate bubbles (`#182533`) with interlocutor profile avatars and sender names.
  * Outgoing messages styled on the right in signature Telegram blue (`#2b5278`) with delivery status double checkmarks (`✓✓`).
  * Reply quotes connecting messages directly to original parent messages.
  * Grouping for consecutive messages with adaptive corners and spacing matching Telegram Desktop.
* **Global Cross-Page Archive Search:** Instant full-text search across all messages spanning every page in the archive (`search_index.js`). Displays match counts, highlights search terms in real-time, and provides one-click navigation to the exact message on any page with animated pulse highlight.
* **New App Logo & Icon:** Fresh, modern cyberpunk/fintech styled application logo featuring a 3D faceted origami paper plane, neon download arrow, and dialogue speech bubble inside a sleek rounded squircle.

### 🔧 Improvements

* **In-Place Chat Enrichment:** Enhanced existing exported archives in-place with user profiles, interlocutor names, and delivery status without re-downloading media.
* **Optimized Search Index:** Generates lightweight, offline-safe `search_index.js` (< 2MB for 13,000+ messages) that bypasses local `file:///` CORS restrictions and executes in under 5ms.
* **Updated Documentation:** Comprehensive bilingual README (English first, Russian second) with updated screenshots, feature lists, and directory structure.

---

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
