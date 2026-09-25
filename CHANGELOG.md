# Changelog

## 3.0.1 (2026-09-25)

- README in English and Russian with a short description on top.
- Proprietary license text.
- Release workflow: tag-driven PyInstaller build for Windows and Linux, notes from this file. Release files are now `TelegramDownloader_Windows.zip` and `TelegramDownloader_Linux.tar.gz`.

## 3.0 (2026-09-03)

- Personal one-to-one chats: incoming and outgoing messages on their own sides, avatars, sender names, reply quotes, grouping of consecutive messages.
- Search across all pages of the archive through `search_index.js`, with jump to the message.
- Existing archives can be enriched with profiles and names without downloading media again.
- Tuned download delays, option to skip large files, `start.bat` fix.
- New app icon.

## 2.1 (2026-07-03)

- Build through `flet pack`; interface fixes; HTML generated while the download runs; f-string syntax fix.

## 2.0 (2026-07-02)

- Text posts are downloaded, not only media.
- Offline HTML viewer styled like Telegram Web: dark theme, search, pages, lightbox, collapsible comments.
- All posts, media, comments and metadata go to `channel_data.json`.
- Key-based translations with a language selector in settings.

## 1.0.0 (2026-06-23)

First release.
