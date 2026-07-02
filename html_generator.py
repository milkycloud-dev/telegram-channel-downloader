"""
HTML Offline Viewer Generator for Telegram Secret Channel Downloader.

Generates a self-contained HTML archive styled like Telegram Web for
offline browsing of downloaded channel content. All paths are relative
to ensure portability when the folder is moved.
"""

import os
import json
from datetime import datetime


# Telegram Web-inspired dark theme CSS (embedded in HTML for portability)
_CSS = """
:root {
    --bg-primary: #17212b;
    --bg-secondary: #0e1621;
    --bg-message: #182533;
    --bg-message-hover: #1e2c3a;
    --text-primary: #f5f5f5;
    --text-secondary: #708499;
    --text-link: #6ab2f2;
    --accent: #3390ec;
    --accent-hover: #4ea4f6;
    --border: #1f2f3f;
    --green: #4fae4e;
    --red: #e53935;
    --divider: #1c2a38;
    --code-bg: #1e2c3a;
    --scrollbar: #2b3e50;
    --shadow: rgba(0,0,0,0.3);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: var(--bg-secondary);
    color: var(--text-primary);
    line-height: 1.5;
    min-height: 100vh;
}

/* Header */
.header {
    background: var(--bg-primary);
    padding: 16px 24px;
    position: sticky;
    top: 0;
    z-index: 100;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 2px 8px var(--shadow);
}

.channel-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
}

.channel-info {
    flex: 1;
}

.channel-name {
    font-size: 17px;
    font-weight: 600;
    color: var(--text-primary);
}

.channel-meta {
    font-size: 13px;
    color: var(--text-secondary);
}

/* Search */
.search-container {
    padding: 12px 24px;
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border);
}

.search-input {
    width: 100%;
    max-width: 600px;
    padding: 10px 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 22px;
    color: var(--text-primary);
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
}

.search-input:focus {
    border-color: var(--accent);
}

.search-input::placeholder {
    color: var(--text-secondary);
}

/* Main content */
.content {
    max-width: 720px;
    margin: 0 auto;
    padding: 16px;
}

/* Date divider */
.date-divider {
    text-align: center;
    padding: 16px 0 8px;
    position: relative;
}

.date-divider span {
    background: var(--bg-primary);
    color: var(--text-secondary);
    padding: 4px 16px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 500;
    display: inline-block;
}

/* Message bubble */
.message {
    background: var(--bg-message);
    border-radius: 12px;
    padding: 8px 12px 6px;
    margin-bottom: 8px;
    transition: background 0.15s;
    position: relative;
}

.message:hover {
    background: var(--bg-message-hover);
}

.message-text {
    font-size: 15px;
    line-height: 1.6;
    word-wrap: break-word;
    white-space: pre-wrap;
    margin-bottom: 4px;
}

.message-text a {
    color: var(--text-link);
    text-decoration: none;
}

.message-text a:hover {
    text-decoration: underline;
}

.message-text code {
    background: var(--code-bg);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

.message-text pre {
    background: var(--code-bg);
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 8px 0;
    font-size: 13px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

/* Media */
.message-media {
    margin: 6px -4px 4px;
    border-radius: 8px;
    overflow: hidden;
}

.message-media img {
    width: 100%;
    max-height: 500px;
    object-fit: contain;
    display: block;
    border-radius: 8px;
    cursor: pointer;
    transition: opacity 0.2s;
}

.message-media img:hover {
    opacity: 0.9;
}

.message-media video {
    width: 100%;
    max-height: 500px;
    border-radius: 8px;
    display: block;
    background: #000;
}

.message-media audio {
    width: 100%;
    margin: 4px 0;
}

.message-media .file-link {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    background: var(--code-bg);
    border-radius: 8px;
    text-decoration: none;
    color: var(--text-primary);
    transition: background 0.2s;
}

.message-media .file-link:hover {
    background: var(--bg-message-hover);
}

.file-icon {
    font-size: 28px;
    flex-shrink: 0;
}

.file-info {
    overflow: hidden;
}

.file-name {
    font-size: 14px;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.file-size {
    font-size: 12px;
    color: var(--text-secondary);
}

/* Message footer */
.message-footer {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 12px;
    margin-top: 2px;
}

.message-time {
    font-size: 12px;
    color: var(--text-secondary);
}

.message-views {
    font-size: 12px;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 3px;
}

/* Comments section */
.comments-toggle {
    background: none;
    border: none;
    color: var(--accent);
    font-size: 14px;
    cursor: pointer;
    padding: 6px 0;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: color 0.2s;
}

.comments-toggle:hover {
    color: var(--accent-hover);
}

.comments-section {
    display: none;
    padding-left: 16px;
    border-left: 2px solid var(--accent);
    margin: 8px 0 4px 8px;
}

.comments-section.open {
    display: block;
}

.comment {
    background: var(--bg-secondary);
    border-radius: 8px;
    padding: 6px 10px;
    margin-bottom: 4px;
    font-size: 14px;
}

.comment-text {
    line-height: 1.5;
    word-wrap: break-word;
    white-space: pre-wrap;
}

/* Pagination */
.pagination {
    display: flex;
    justify-content: center;
    gap: 8px;
    padding: 24px;
    flex-wrap: wrap;
}

.pagination a, .pagination span {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 36px;
    height: 36px;
    padding: 0 12px;
    border-radius: 8px;
    font-size: 14px;
    text-decoration: none;
    transition: all 0.2s;
}

.pagination a {
    background: var(--bg-message);
    color: var(--text-primary);
}

.pagination a:hover {
    background: var(--accent);
    color: white;
}

.pagination .current {
    background: var(--accent);
    color: white;
    font-weight: 600;
}

/* Footer */
.footer {
    text-align: center;
    padding: 24px;
    color: var(--text-secondary);
    font-size: 13px;
    border-top: 1px solid var(--border);
    margin-top: 16px;
}

.footer a {
    color: var(--accent);
    text-decoration: none;
}

/* No results */
.no-results {
    text-align: center;
    padding: 48px;
    color: var(--text-secondary);
    font-size: 16px;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: var(--scrollbar);
    border-radius: 4px;
}

/* Responsive */
@media (max-width: 600px) {
    .header { padding: 12px 16px; }
    .content { padding: 8px; }
    .search-container { padding: 8px 16px; }
}

/* Image lightbox */
.lightbox {
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.9);
    z-index: 1000;
    cursor: pointer;
    align-items: center;
    justify-content: center;
}

.lightbox.open {
    display: flex;
}

.lightbox img {
    max-width: 95%;
    max-height: 95%;
    object-fit: contain;
}
"""

# JavaScript for search and comment toggling
_JS = """
function toggleComments(btn) {
    var section = btn.nextElementSibling;
    if (section.classList.contains('open')) {
        section.classList.remove('open');
        btn.textContent = btn.textContent.replace('▼', '▶');
    } else {
        section.classList.add('open');
        btn.textContent = btn.textContent.replace('▶', '▼');
    }
}

function searchPosts() {
    var query = document.getElementById('searchInput').value.toLowerCase();
    var messages = document.querySelectorAll('.message');
    var dividers = document.querySelectorAll('.date-divider');
    var noResults = document.getElementById('noResults');
    var found = 0;

    messages.forEach(function(msg) {
        var text = msg.textContent.toLowerCase();
        if (query === '' || text.indexOf(query) !== -1) {
            msg.style.display = '';
            found++;
        } else {
            msg.style.display = 'none';
        }
    });

    dividers.forEach(function(d) { d.style.display = query ? 'none' : ''; });

    if (noResults) {
        noResults.style.display = (found === 0 && query) ? 'block' : 'none';
    }
}

function openLightbox(src) {
    var lb = document.getElementById('lightbox');
    document.getElementById('lightboxImg').src = src;
    lb.classList.add('open');
}

function closeLightbox() {
    document.getElementById('lightbox').classList.remove('open');
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeLightbox();
});
"""


def _escape_html(text: str) -> str:
    """Escape special HTML characters in text content."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _format_text(text: str) -> str:
    """
    Convert plain text to HTML with basic formatting.

    Handles:
    - URLs converted to clickable links
    - Line breaks preserved
    - Code blocks (``` ... ```) formatted
    - Inline code (` ... `) formatted
    """
    import re

    text = _escape_html(text)

    # Code blocks (triple backticks)
    text = re.sub(
        r'```(.*?)```',
        r'<pre>\1</pre>',
        text,
        flags=re.DOTALL
    )

    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # Bold (**text**)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # URLs
    text = re.sub(
        r'(https?://[^\s<]+)',
        r'<a href="\1" target="_blank" rel="noopener">\1</a>',
        text
    )

    return text


def _get_media_extension(filename: str) -> str:
    """Extract the file extension in lowercase."""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def _render_media(media_files: list, media_type: str | None) -> str:
    """
    Render HTML for media attachments.

    Generates appropriate HTML elements based on file type:
    images, videos, audio players, or generic file links.
    All paths are relative for offline portability.
    """
    if not media_files:
        return ""

    html_parts = []
    for fname in media_files:
        ext = _get_media_extension(fname)

        if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"):
            html_parts.append(
                f'<div class="message-media">'
                f'<img src="./{_escape_html(fname)}" alt="Photo" loading="lazy" '
                f'onclick="openLightbox(this.src)">'
                f'</div>'
            )
        elif ext in (".mp4", ".mov", ".avi", ".mkv", ".webm"):
            html_parts.append(
                f'<div class="message-media">'
                f'<video controls preload="metadata">'
                f'<source src="./{_escape_html(fname)}">'
                f'Your browser does not support video playback.'
                f'</video></div>'
            )
        elif ext in (".mp3", ".ogg", ".oga", ".wav", ".flac", ".m4a", ".opus"):
            html_parts.append(
                f'<div class="message-media">'
                f'<audio controls preload="metadata">'
                f'<source src="./{_escape_html(fname)}">'
                f'</audio></div>'
            )
        else:
            icon = "📄"
            if ext in (".pdf",):
                icon = "📕"
            elif ext in (".zip", ".rar", ".7z", ".tar", ".gz"):
                icon = "📦"
            html_parts.append(
                f'<div class="message-media">'
                f'<a href="./{_escape_html(fname)}" class="file-link" download>'
                f'<span class="file-icon">{icon}</span>'
                f'<div class="file-info">'
                f'<div class="file-name">{_escape_html(fname)}</div>'
                f'</div></a></div>'
            )

    return "\n".join(html_parts)


def _render_comments(comments: list) -> str:
    """Render HTML for the comments section of a post."""
    if not comments:
        return ""

    html = (
        f'<button class="comments-toggle" onclick="toggleComments(this)">'
        f'▶ {len(comments)} comment{"s" if len(comments) != 1 else ""}</button>'
        f'<div class="comments-section">'
    )

    for c in comments:
        text = _format_text(c.get("text", "")) if c.get("text") else ""
        date_str = ""
        if c.get("date"):
            try:
                dt = datetime.fromisoformat(c["date"])
                date_str = dt.strftime("%H:%M")
            except Exception:
                pass

        media_html = _render_media(c.get("media_files", []), c.get("media_type"))

        html += (
            f'<div class="comment">'
            f'{f"<div class=\"comment-text\">{text}</div>" if text else ""}'
            f'{media_html}'
            f'{f"<span class=\"message-time\">{date_str}</span>" if date_str else ""}'
            f'</div>'
        )

    html += '</div>'
    return html


def generate_channel_html(dl_dir: str, channel_name: str = "Channel") -> str | None:
    """
    Generate an offline HTML viewer for a downloaded channel.

    Reads channel_data.json from the download directory and produces
    index.html (plus paginated pages if needed). All media links use
    relative paths for full offline portability.

    Args:
        dl_dir: Path to the channel download directory.
        channel_name: Display name for the channel header.

    Returns:
        Path to the generated index.html, or None on error.
    """
    data_path = os.path.join(dl_dir, "channel_data.json")
    if not os.path.exists(data_path):
        return None

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            all_posts = json.load(f)
    except Exception:
        return None

    if not all_posts:
        return None

    # Separate posts and comments
    posts = [p for p in all_posts if not p.get("is_comment")]
    comments_by_parent = {}

    for c in all_posts:
        if c.get("is_comment"):
            # Try to find parent post by prefix pattern (e.g. "5_c123")
            prefix = c.get("prefix", "")
            parent_id = prefix.split("_")[0] if "_" in prefix else ""
            comments_by_parent.setdefault(parent_id, []).append(c)

    # Sort posts by msg_id descending (newest first)
    posts.sort(key=lambda p: p.get("msg_id", 0), reverse=True)

    # Pagination: 100 posts per page
    posts_per_page = 100
    total_pages = max(1, (len(posts) + posts_per_page - 1) // posts_per_page)

    generated_files = []

    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * posts_per_page
        end_idx = start_idx + posts_per_page
        page_posts = posts[start_idx:end_idx]

        filename = "index.html" if page_num == 1 else f"page_{page_num}.html"
        filepath = os.path.join(dl_dir, filename)

        html = _build_page_html(
            page_posts, comments_by_parent, channel_name,
            page_num, total_pages, len(posts)
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        generated_files.append(filepath)

    return generated_files[0] if generated_files else None


def _build_page_html(
    posts: list, comments_by_parent: dict, channel_name: str,
    page_num: int, total_pages: int, total_posts: int
) -> str:
    """
    Build the complete HTML string for a single page.

    Includes embedded CSS and JS, header, search bar, message list
    with date dividers, pagination, and footer.
    """
    first_letter = channel_name[0].upper() if channel_name else "T"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_escape_html(channel_name)} — Offline Viewer</title>
<style>{_CSS}</style>
</head>
<body>

<div class="header">
    <div class="channel-avatar">{first_letter}</div>
    <div class="channel-info">
        <div class="channel-name">{_escape_html(channel_name)}</div>
        <div class="channel-meta">{total_posts} posts • Offline Archive</div>
    </div>
</div>

<div class="search-container">
    <input type="text" id="searchInput" class="search-input"
           placeholder="Search messages..." oninput="searchPosts()">
</div>

<div class="content">
<div id="noResults" class="no-results" style="display:none">No messages found</div>
"""

    # Render messages with date dividers
    current_date = None
    for post in posts:
        # Date divider
        post_date = ""
        time_str = ""
        if post.get("date"):
            try:
                dt = datetime.fromisoformat(post["date"])
                post_date = dt.strftime("%B %d, %Y")
                time_str = dt.strftime("%H:%M")
            except Exception:
                pass

        if post_date and post_date != current_date:
            current_date = post_date
            html += f'<div class="date-divider"><span>{post_date}</span></div>\n'

        # Message content
        text_html = _format_text(post.get("text", "")) if post.get("text") else ""
        media_html = _render_media(post.get("media_files", []), post.get("media_type"))

        views = post.get("views", 0)
        views_html = ""
        if views:
            if views >= 1000000:
                views_str = f"{views / 1000000:.1f}M"
            elif views >= 1000:
                views_str = f"{views / 1000:.1f}K"
            else:
                views_str = str(views)
            views_html = f'<span class="message-views">👁 {views_str}</span>'

        # Comments
        prefix = post.get("prefix", str(post.get("msg_id", "")))
        post_comments = comments_by_parent.get(prefix, [])
        comments_html = _render_comments(post_comments)

        html += f"""<div class="message">
{f'<div class="message-text">{text_html}</div>' if text_html else ''}
{media_html}
{comments_html}
<div class="message-footer">
    {views_html}
    <span class="message-time">{time_str}</span>
</div>
</div>
"""

    # Pagination
    if total_pages > 1:
        html += '<div class="pagination">\n'
        for p in range(1, total_pages + 1):
            link = "index.html" if p == 1 else f"page_{p}.html"
            if p == page_num:
                html += f'<span class="current">{p}</span>\n'
            else:
                html += f'<a href="./{link}">{p}</a>\n'
        html += '</div>\n'

    html += f"""</div>

<div class="footer">
    Generated by <a href="https://github.com/milkycloud-dev/telegram-channel-downloader">
    Telegram Secret Channel Downloader</a> • {datetime.now().strftime("%Y-%m-%d %H:%M")}
</div>

<div class="lightbox" id="lightbox" onclick="closeLightbox()">
    <img id="lightboxImg" src="" alt="Preview">
</div>

<script>{_JS}</script>
</body>
</html>"""

    return html
