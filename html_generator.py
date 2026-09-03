"""
HTML Offline Viewer Generator for Telegram Secret Channel & Chat Downloader.

Generates self-contained HTML archives styled authentically like Telegram Web / Desktop
for offline browsing of downloaded channels, groups, and personal chats (direct messages).
Features full global cross-page archive search via offline-safe search_index.js.
All media and asset paths are relative to ensure portability when the folder is moved.
"""

import os
import json
import re
from datetime import datetime


# Telegram Web-inspired authentic dark theme CSS
_CSS = """
:root {
    --bg-primary: #0e1621;
    --bg-secondary: #0e1621;
    --bg-header: #17212b;
    --bg-message-in: #182533;
    --bg-message-in-hover: #1f2d3d;
    --bg-message-out: #2b5278;
    --bg-message-out-hover: #325e89;
    --text-primary: #f5f5f5;
    --text-secondary: #708499;
    --text-time-in: #708499;
    --text-time-out: #7ea8d6;
    --text-link: #6ab2f2;
    --text-link-out: #9ad0ff;
    --accent: #3390ec;
    --accent-hover: #4ea4f6;
    --border: #1c2a38;
    --green: #4fae4e;
    --red: #e53935;
    --code-bg: #111a24;
    --code-bg-out: #204060;
    --scrollbar: #243444;
    --shadow: rgba(0, 0, 0, 0.3);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background-color: var(--bg-secondary);
    background-image: radial-gradient(circle at 50% 50%, rgba(30, 44, 60, 0.35) 0%, rgba(14, 22, 33, 0.95) 100%);
    background-attachment: fixed;
    color: var(--text-primary);
    line-height: 1.5;
    min-height: 100vh;
}

/* Header */
.header {
    background: rgba(23, 33, 43, 0.95);
    padding: 12px 24px;
    position: sticky;
    top: 0;
    z-index: 100;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    box-shadow: 0 2px 10px var(--shadow);
    backdrop-filter: blur(12px);
}

.header-left {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
}

.channel-avatar, .header-avatar-img {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    object-fit: cover;
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
}

.channel-info {
    flex: 1;
    min-width: 0;
}

.channel-name {
    font-size: 17px;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.chat-type-badge {
    font-size: 11px;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 10px;
    background: rgba(51, 144, 236, 0.18);
    color: var(--accent);
    letter-spacing: 0.2px;
}

.channel-meta {
    font-size: 13px;
    color: var(--text-secondary);
    display: flex;
    gap: 8px;
    align-items: center;
}

/* Header Controls */
.header-controls {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
}

.search-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.search-input {
    width: 250px;
    padding: 8px 32px 8px 14px;
    background: #111b26;
    border: 1px solid var(--border);
    border-radius: 18px;
    color: var(--text-primary);
    font-size: 13.5px;
    outline: none;
    transition: all 0.2s;
}

.search-input:focus {
    border-color: var(--accent);
    width: 320px;
    background: #172433;
}

.search-clear-btn {
    position: absolute;
    right: 12px;
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 14px;
    display: none;
    line-height: 1;
}

.search-clear-btn:hover {
    color: var(--text-primary);
}

.btn-header {
    background: #1b2836;
    border: 1px solid var(--border);
    color: var(--text-primary);
    padding: 7px 12px;
    border-radius: 8px;
    font-size: 13px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s;
    text-decoration: none;
}

.btn-header:hover {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
}

/* Main chat container */
.chat-container {
    max-width: 820px;
    margin: 0 auto;
    padding: 16px 16px 40px;
    display: flex;
    flex-direction: column;
}

/* Sticky Date divider */
.date-divider {
    text-align: center;
    padding: 14px 0 8px;
    position: sticky;
    top: 68px;
    z-index: 20;
    pointer-events: none;
}

.date-divider span {
    pointer-events: auto;
    background: rgba(16, 26, 36, 0.85);
    backdrop-filter: blur(8px);
    color: #7fa1c1;
    padding: 4px 16px;
    border-radius: 14px;
    font-size: 12.5px;
    font-weight: 500;
    display: inline-block;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.04);
}

/* Message Rows & Interlocutors */
.msg-row {
    display: flex;
    margin-bottom: 3px;
    width: 100%;
    position: relative;
}

.msg-row.outgoing {
    justify-content: flex-end;
}

.msg-row.incoming {
    justify-content: flex-start;
    align-items: flex-start;
    gap: 8px;
}

.msg-row.channel-post {
    justify-content: center;
}

.msg-row.first-in-group {
    margin-top: 8px;
}

/* Avatar for incoming messages */
.msg-peer-avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 600;
    color: white;
    margin-top: 2px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.25);
}

.msg-avatar-spacer {
    width: 34px;
    flex-shrink: 0;
}

/* Message Bubble */
.message {
    max-width: 76%;
    min-width: 90px;
    border-radius: 16px;
    padding: 7px 12px 6px;
    position: relative;
    box-shadow: 0 1px 2px var(--shadow);
    transition: background 0.15s ease;
    word-wrap: break-word;
    word-break: break-word;
}

.msg-row.channel-post .message {
    max-width: 100%;
    width: 100%;
    background: var(--bg-message-in);
}

.msg-row.incoming .message {
    background: var(--bg-message-in);
    color: var(--text-primary);
    border-bottom-left-radius: 4px;
}

.msg-row.incoming .message:hover {
    background: var(--bg-message-in-hover);
}

.msg-row.outgoing .message {
    background: var(--bg-message-out);
    color: #ffffff;
    border-bottom-right-radius: 4px;
}

.msg-row.outgoing .message:hover {
    background: var(--bg-message-out-hover);
}

/* Sender Author Header */
.msg-author {
    font-size: 13.5px;
    font-weight: 600;
    margin-bottom: 3px;
    color: #6ab2f2;
    cursor: default;
}

/* Reply Quote */
.msg-reply {
    border-left: 3px solid var(--accent);
    background: rgba(0, 0, 0, 0.18);
    border-radius: 4px;
    padding: 4px 8px;
    margin-bottom: 6px;
    font-size: 12.5px;
    cursor: pointer;
    text-decoration: none;
    display: block;
    color: inherit;
    transition: background 0.15s;
}

.msg-reply:hover {
    background: rgba(0, 0, 0, 0.28);
}

.msg-row.outgoing .msg-reply {
    border-left-color: #9ad0ff;
    background: rgba(0, 0, 0, 0.14);
}

.msg-reply-name {
    font-weight: 600;
    color: var(--accent);
    font-size: 12px;
    margin-bottom: 1px;
}

.msg-row.outgoing .msg-reply-name {
    color: #9ad0ff;
}

.msg-reply-text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    opacity: 0.85;
}

/* Message Text */
.message-text {
    font-size: 15px;
    line-height: 1.55;
    word-wrap: break-word;
    white-space: pre-wrap;
    margin-bottom: 2px;
}

.msg-row.incoming .message-text a {
    color: var(--text-link);
    text-decoration: none;
}

.msg-row.outgoing .message-text a {
    color: var(--text-link-out);
    text-decoration: none;
}

.message-text a:hover {
    text-decoration: underline;
}

.msg-row.incoming .message-text code {
    background: var(--code-bg);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

.msg-row.outgoing .message-text code {
    background: var(--code-bg-out);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

.message-text pre {
    background: var(--code-bg);
    padding: 10px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 6px 0;
    font-size: 13px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

/* Media styling */
.message-media {
    margin: 4px -4px 4px;
    border-radius: 8px;
    overflow: hidden;
}

.message-media img {
    width: 100%;
    max-height: 480px;
    object-fit: contain;
    display: block;
    border-radius: 8px;
    cursor: pointer;
    transition: opacity 0.2s;
}

.message-media img:hover {
    opacity: 0.92;
}

.message-media video {
    width: 100%;
    max-height: 480px;
    border-radius: 8px;
    display: block;
    background: #000;
}

.message-media audio {
    width: 100%;
    margin: 4px 0;
    min-width: 240px;
}

.message-media .file-link {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 8px;
    text-decoration: none;
    color: inherit;
    transition: background 0.2s;
}

.message-media .file-link:hover {
    background: rgba(0, 0, 0, 0.35);
}

.file-icon {
    font-size: 26px;
    flex-shrink: 0;
}

.file-info {
    overflow: hidden;
}

.file-name {
    font-size: 13.5px;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.file-size {
    font-size: 11.5px;
    opacity: 0.7;
}

/* Time & checkmarks */
.msg-meta {
    float: right;
    margin-left: 10px;
    margin-top: 4px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    line-height: 1;
    user-select: none;
}

.msg-row.incoming .msg-meta {
    color: var(--text-time-in);
}

.msg-row.outgoing .msg-meta {
    color: var(--text-time-out);
}

.msg-check {
    font-size: 12px;
    color: inherit;
}

.message-views {
    font-size: 11px;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 3px;
    margin-right: 6px;
}

/* Comments section */
.comments-toggle {
    background: none;
    border: none;
    color: var(--accent);
    font-size: 13.5px;
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
    padding-left: 14px;
    border-left: 2px solid var(--accent);
    margin: 8px 0 4px 6px;
}

.comments-section.open {
    display: block;
}

.comment {
    background: rgba(0, 0, 0, 0.25);
    border-radius: 8px;
    padding: 6px 10px;
    margin-bottom: 4px;
    font-size: 13.5px;
}

.comment-text {
    line-height: 1.5;
    word-wrap: break-word;
    white-space: pre-wrap;
}

/* Global Search Results View */
.search-results-container {
    display: none;
    margin-bottom: 24px;
}

.search-summary {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(23, 33, 43, 0.95);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px 18px;
    margin-bottom: 14px;
    font-size: 13.5px;
    color: var(--text-primary);
    box-shadow: 0 2px 8px var(--shadow);
}

.search-cards-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.search-card {
    background: var(--bg-message-in);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px 16px;
    box-shadow: 0 1px 4px var(--shadow);
    transition: transform 0.1s, border-color 0.15s;
}

.search-card:hover {
    border-color: var(--accent);
}

.search-card-out {
    border-left: 4px solid var(--accent);
}

.search-card-in {
    border-left: 4px solid #6ab2f2;
}

.search-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 12.5px;
    margin-bottom: 6px;
}

.search-card-sender {
    font-weight: 600;
    color: var(--accent);
    font-size: 13.5px;
}

.badge-out {
    background: rgba(51, 144, 236, 0.15);
    color: var(--accent);
    padding: 2px 7px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 500;
}

.badge-in {
    background: rgba(112, 132, 153, 0.2);
    color: var(--text-secondary);
    padding: 2px 7px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 500;
}

.search-card-date {
    color: var(--text-secondary);
    margin-left: auto;
}

.search-card-page {
    background: #101921;
    color: #7fa1c1;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 11.5px;
}

.search-card-text {
    font-size: 14.5px;
    line-height: 1.5;
    color: var(--text-primary);
    word-break: break-word;
    margin-bottom: 8px;
    white-space: pre-wrap;
    max-height: 140px;
    overflow: hidden;
    text-overflow: ellipsis;
}

.search-card-footer {
    display: flex;
    justify-content: flex-end;
}

.btn-jump {
    background: #172433;
    border: 1px solid var(--border);
    color: var(--accent);
    padding: 5px 14px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 500;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.15s;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.btn-jump:hover {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
}

mark.search-highlight {
    background: rgba(255, 214, 0, 0.45);
    color: #ffffff;
    font-weight: 600;
    border-radius: 3px;
    padding: 0 3px;
}

@keyframes pulseHighlight {
    0% { box-shadow: 0 0 0 0 rgba(51, 144, 236, 0.9); }
    50% { box-shadow: 0 0 20px 6px rgba(51, 144, 236, 0.95); }
    100% { box-shadow: 0 0 0 0 rgba(51, 144, 236, 0); }
}

.msg-highlight-pulse .message {
    animation: pulseHighlight 2.5s ease-in-out;
    border: 1px solid var(--accent) !important;
}

/* Pagination Bar */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 6px;
    padding: 24px 16px;
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
    font-size: 13.5px;
    text-decoration: none;
    transition: all 0.2s;
}

.pagination a {
    background: #17212b;
    border: 1px solid var(--border);
    color: var(--text-primary);
}

.pagination a:hover {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
}

.pagination .current {
    background: var(--accent);
    color: white;
    font-weight: 600;
}

.pagination-jump {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-left: 12px;
    font-size: 13px;
    color: var(--text-secondary);
}

.pagination-jump input {
    width: 50px;
    padding: 6px 8px;
    background: #17212b;
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text-primary);
    font-size: 13px;
    text-align: center;
    outline: none;
}

.pagination-jump input:focus {
    border-color: var(--accent);
}

/* Footer */
.footer {
    text-align: center;
    padding: 24px;
    color: var(--text-secondary);
    font-size: 12.5px;
    border-top: 1px solid var(--border);
    margin-top: 20px;
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

/* Image lightbox */
.lightbox {
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.92);
    z-index: 1000;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(8px);
}

.lightbox.open {
    display: flex;
}

.lightbox img {
    max-width: 94%;
    max-height: 94%;
    object-fit: contain;
    border-radius: 8px;
    box-shadow: 0 4px 30px rgba(0,0,0,0.8);
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 7px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: var(--scrollbar);
    border-radius: 4px;
}

/* Responsive */
@media (max-width: 680px) {
    .header { padding: 10px 14px; flex-wrap: wrap; }
    .header-controls { width: 100%; justify-content: space-between; margin-top: 6px; }
    .search-wrapper { width: 100%; }
    .search-input { width: 100%; }
    .search-input:focus { width: 100%; }
    .chat-container { padding: 10px 8px 30px; }
    .message { max-width: 88%; }
}
"""

# JavaScript for global cross-page search, lightbox, and quick pagination
_JS = """
var searchTimeout = null;

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
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(_executeSearch, 150);
}

function clearSearch() {
    var input = document.getElementById('searchInput');
    if (input) input.value = '';
    _executeSearch();
}

function _executeSearch() {
    var input = document.getElementById('searchInput');
    var query = (input ? input.value : '').toLowerCase().trim();
    var clearBtn = document.getElementById('searchClearBtn');
    if (clearBtn) clearBtn.style.display = query ? 'block' : 'none';

    var localRows = document.querySelectorAll('.msg-row');
    var localDividers = document.querySelectorAll('.date-divider');
    var paginationBar = document.querySelector('.pagination');
    var globalContainer = document.getElementById('globalSearchResults');
    var noResults = document.getElementById('noResults');

    if (!query) {
        if (globalContainer) {
            globalContainer.innerHTML = '';
            globalContainer.style.display = 'none';
        }
        if (noResults) noResults.style.display = 'none';
        localRows.forEach(function(row) { row.style.display = ''; });
        localDividers.forEach(function(d) { d.style.display = ''; });
        if (paginationBar) paginationBar.style.display = '';
        return;
    }

    // Global Archive Search across all pages
    if (window.__ARCHIVE_INDEX__ && window.__ARCHIVE_INDEX__.length > 0) {
        localRows.forEach(function(row) { row.style.display = 'none'; });
        localDividers.forEach(function(d) { d.style.display = 'none'; });
        if (paginationBar) paginationBar.style.display = 'none';
        if (noResults) noResults.style.display = 'none';

        var terms = query.split(/\\s+/).filter(Boolean);
        var matches = [];
        for (var i = 0; i < window.__ARCHIVE_INDEX__.length; i++) {
            var item = window.__ARCHIVE_INDEX__[i];
            var targetStr = (item.t + ' ' + item.s).toLowerCase();
            var allMatch = true;
            for (var t = 0; t < terms.length; t++) {
                if (targetStr.indexOf(terms[t]) === -1) {
                    allMatch = false;
                    break;
                }
            }
            if (allMatch) {
                matches.push(item);
                if (matches.length >= 300) break;
            }
        }

        renderGlobalSearchResults(matches, query, terms);
    } else {
        // Fallback to local page search
        var found = 0;
        localRows.forEach(function(row) {
            var text = row.textContent.toLowerCase();
            if (text.indexOf(query) !== -1) {
                row.style.display = '';
                found++;
            } else {
                row.style.display = 'none';
            }
        });
        localDividers.forEach(function(d) { d.style.display = 'none'; });
        if (noResults) {
            noResults.style.display = (found === 0) ? 'block' : 'none';
        }
    }
}

function _escapeHtmlStr(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function _highlightTerms(text, terms) {
    if (!text) return '';
    var escaped = _escapeHtmlStr(text);
    terms.forEach(function(term) {
        if (!term) return;
        var safe = term.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
        var regex = new RegExp('(' + safe + ')', 'gi');
        escaped = escaped.replace(regex, '<mark class="search-highlight">$1</mark>');
    });
    return escaped;
}

function renderGlobalSearchResults(matches, query, terms) {
    var container = document.getElementById('globalSearchResults');
    if (!container) return;
    container.style.display = 'block';

    var totalArchive = window.__ARCHIVE_INDEX__.length;
    var count = matches.length;
    var limitNotice = count >= 300 ? ' (показаны первые 300)' : '';

    var headerHtml = '<div class="search-summary">' +
        '<span>🔍 Найдено <strong>' + count + '</strong> сообщений во всем архиве (' + totalArchive + ' постов)' + limitNotice + ' по запросу "<em>' + _escapeHtmlStr(query) + '</em>"</span>' +
        '<button class="btn-header" style="padding: 4px 10px; font-size: 12px;" onclick="clearSearch()">✕ Очистить поиск</button>' +
        '</div>';

    if (count === 0) {
        container.innerHTML = headerHtml + '<div class="no-results" style="display:block">Сообщения не найдены во всем архиве</div>';
        return;
    }

    var cardsHtml = '';
    var curPage = window.__CURRENT_PAGE__ || 1;

    for (var i = 0; i < matches.length; i++) {
        var m = matches[i];
        var isOut = m.o;
        var senderName = m.s || (isOut ? 'Вы' : 'Собеседник');
        var rowClass = isOut ? 'search-card search-card-out' : 'search-card search-card-in';
        var highlighted = _highlightTerms(m.t, terms);
        var targetPage = m.p;
        var pageUrl = (targetPage === 1 ? 'index.html' : 'page_' + targetPage + '.html') + '#msg-' + m.id;
        var isCurrentPage = (curPage === targetPage);

        var actionBtn = isCurrentPage ?
            '<button class="btn-jump" onclick="jumpToLocalMsg(' + m.id + ')">К сообщению на этой стр. ↓</button>' :
            '<a href="' + pageUrl + '" class="btn-jump">Открыть на стр. ' + targetPage + ' →</a>';

        var dirBadge = isOut ? '<span class="badge-out">Исходящее</span>' : '<span class="badge-in">Входящее</span>';

        cardsHtml += '<div class="' + rowClass + '">' +
            '<div class="search-card-header">' +
                '<span class="search-card-sender">' + _escapeHtmlStr(senderName) + '</span>' +
                dirBadge +
                '<span class="search-card-date">' + (m.d || '') + '</span>' +
                '<span class="search-card-page">Стр. ' + targetPage + '</span>' +
            '</div>' +
            '<div class="search-card-text">' + (highlighted || '<em>[Медиасообщение без текста]</em>') + '</div>' +
            '<div class="search-card-footer">' + actionBtn + '</div>' +
        '</div>';
    }

    container.innerHTML = headerHtml + '<div class="search-cards-list">' + cardsHtml + '</div>';
}

function jumpToLocalMsg(msgId) {
    clearSearch();
    var el = document.getElementById('msg-' + msgId);
    if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.classList.add('msg-highlight-pulse');
        setTimeout(function() { el.classList.remove('msg-highlight-pulse'); }, 2500);
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

function jumpToPage(total) {
    var input = document.getElementById('pageJumpInput');
    if (!input) return;
    var p = parseInt(input.value, 10);
    if (p >= 1 && p <= total) {
        window.location.href = (p === 1) ? 'index.html' : 'page_' + p + '.html';
    } else {
        alert('Пожалуйста, введите номер страницы от 1 до ' + total);
    }
}

function reverseOrder() {
    var container = document.querySelector('.chat-container');
    if (!container) return;
    var elements = Array.from(container.children).filter(function(el) {
        return el.id !== 'noResults' && el.id !== 'globalSearchResults';
    });
    elements.reverse().forEach(function(el) {
        container.appendChild(el);
    });
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeLightbox();
        clearSearch();
    }
});

window.addEventListener('DOMContentLoaded', function() {
    if (window.location.hash) {
        var targetId = window.location.hash.substring(1);
        var el = document.getElementById(targetId);
        if (el) {
            setTimeout(function() {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                el.classList.add('msg-highlight-pulse');
                setTimeout(function() { el.classList.remove('msg-highlight-pulse'); }, 250);
            }, 250);
        }
    }
});
"""


def _escape_html(text: str) -> str:
    """Escape special HTML characters in text content."""
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _format_text(text: str) -> str:
    """
    Convert plain text to HTML with Telegram-style formatting.
    Handles links, code blocks, bold, linebreaks.
    """
    if not text:
        return ""

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
    Render HTML for media attachments:
    photos, videos, audio players, or documents.
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
                f'Ваш браузер не поддерживает видео.'
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
                f'<div class="file-size">{ext.upper()[1:]} Файл</div>'
                f'</div></a></div>'
            )

    return "\n".join(html_parts)


def _render_comments(comments: list) -> str:
    """Render HTML for the comments section of a post."""
    if not comments:
        return ""

    html = (
        f'<button class="comments-toggle" onclick="toggleComments(this)">'
        f'▶ {len(comments)} комментари{"й" if len(comments) == 1 else "ев"}</button>'
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
        text_div = f'<div class="comment-text">{text}</div>' if text else ""
        time_span = f'<span class="msg-meta">{date_str}</span>' if date_str else ""

        html += (
            f'<div class="comment">'
            f'{text_div}'
            f'{media_html}'
            f'{time_span}'
            f'</div>'
        )

    html += '</div>'
    return html


def generate_channel_html(dl_dir: str, channel_name: str = "Chat") -> str | None:
    """
    Generate an offline HTML archive for a downloaded channel, group, or personal chat.

    Reads channel_data.json and chat_meta.json (if available) from the download directory,
    identifies interlocutors, incoming vs outgoing messages, avatars, produces
    index.html and paginated pages, and writes search_index.js for global cross-page search.
    All media paths are relative.

    Args:
        dl_dir: Path to the download directory.
        channel_name: Display name or identifier for the chat.

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

    # Load optional chat metadata
    chat_meta = {}
    meta_path = os.path.join(dl_dir, "chat_meta.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                chat_meta = json.load(f)
        except Exception:
            pass

    # Check for avatar files
    peer_avatar_file = None
    for av in ("peer_avatar.jpg", "avatar.jpg", "peer_avatar.png", "avatar.png"):
        if os.path.exists(os.path.join(dl_dir, av)):
            peer_avatar_file = av
            break

    # Determine display title
    display_title = (
        chat_meta.get("peer_name")
        or chat_meta.get("peer_username")
        or channel_name
        or "Chat"
    )
    if display_title.isdigit() and chat_meta.get("peer_username"):
        display_title = chat_meta["peer_username"]

    # Detect chat mode: is it a direct dialogue?
    has_out_flag = any("out" in p for p in all_posts)
    unique_senders = {p.get("sender_id") for p in all_posts if p.get("sender_id") is not None}
    is_dialog = chat_meta.get("is_dialog", False) or (has_out_flag and len(unique_senders) <= 2)

    # Separate posts and comments
    posts = [p for p in all_posts if not p.get("is_comment")]
    comments_by_parent = {}

    for c in all_posts:
        if c.get("is_comment"):
            prefix = c.get("prefix", "")
            parent_id = prefix.split("_")[0] if "_" in prefix else ""
            comments_by_parent.setdefault(parent_id, []).append(c)

    # Sort posts: newest first (reverse=True) consistent with previous version
    posts.sort(key=lambda p: p.get("msg_id", 0), reverse=True)

    # Build reply lookup table (id -> text snippet, sender)
    msg_lookup = {}
    for p in posts:
        msg_lookup[p.get("msg_id")] = {
            "text": (p.get("text") or "").strip()[:60],
            "sender_name": p.get("sender_name") or ("Вы" if p.get("out") else display_title),
            "out": p.get("out", False)
        }

    # Pagination: 100 posts per page
    posts_per_page = 100
    total_pages = max(1, (len(posts) + posts_per_page - 1) // posts_per_page)

    # Generate search_index.js for global cross-page search across all messages
    index_items = []
    for idx, p in enumerate(posts):
        p_num = (idx // posts_per_page) + 1
        dt_str = ""
        if p.get("date"):
            try:
                dt_str = datetime.fromisoformat(p["date"]).strftime("%d.%m.%Y %H:%M")
            except Exception:
                dt_str = p.get("date", "")[:16]

        text_content = (p.get("text") or "").strip()
        index_items.append({
            "id": p.get("msg_id"),
            "p": p_num,
            "d": dt_str,
            "s": p.get("sender_name") or ("Вы" if p.get("out") else display_title),
            "o": bool(p.get("out", False)),
            "t": text_content[:400]
        })

    index_path = os.path.join(dl_dir, "search_index.js")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("window.__ARCHIVE_INDEX__ = " + json.dumps(index_items, ensure_ascii=False) + ";\n")

    generated_files = []

    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * posts_per_page
        end_idx = start_idx + posts_per_page
        page_posts = posts[start_idx:end_idx]

        filename = "index.html" if page_num == 1 else f"page_{page_num}.html"
        filepath = os.path.join(dl_dir, filename)

        html = _build_page_html(
            page_posts,
            comments_by_parent,
            msg_lookup,
            display_title,
            chat_meta,
            peer_avatar_file,
            is_dialog,
            page_num,
            total_pages,
            len(posts)
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        generated_files.append(filepath)

    return generated_files[0] if generated_files else None


def _build_page_html(
    posts: list,
    comments_by_parent: dict,
    msg_lookup: dict,
    channel_name: str,
    chat_meta: dict,
    peer_avatar_file: str | None,
    is_dialog: bool,
    page_num: int,
    total_pages: int,
    total_posts: int
) -> str:
    """Build the complete HTML string for a single page with Telegram styling and global search."""
    first_letter = channel_name[0].upper() if channel_name else "T"

    # Header Avatar
    if peer_avatar_file:
        avatar_html = f'<img src="./{peer_avatar_file}" alt="{_escape_html(channel_name)}" class="header-avatar-img">'
    else:
        avatar_html = f'<div class="channel-avatar">{first_letter}</div>'

    # Badges and subtitle
    if is_dialog:
        badge_text = "Личный диалог"
        out_cnt = chat_meta.get("outgoing_count", sum(1 for p in posts if p.get("out")))
        in_cnt = chat_meta.get("incoming_count", sum(1 for p in posts if not p.get("out")))
        meta_text = f"{total_posts} сообщений ({in_cnt} вх., {out_cnt} исх.) • Офлайн архив"
    else:
        badge_text = "Канал"
        meta_text = f"{total_posts} постов • Офлайн архив"

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_escape_html(channel_name)} — Telegram Архив</title>
<style>{_CSS}</style>
<script>window.__CURRENT_PAGE__ = {page_num};</script>
<script src="./search_index.js" defer></script>
</head>
<body>

<div class="header">
    <div class="header-left">
        {avatar_html}
        <div class="channel-info">
            <div class="channel-name">
                <span>{_escape_html(channel_name)}</span>
                <span class="chat-type-badge">{badge_text}</span>
            </div>
            <div class="channel-meta">{meta_text}</div>
        </div>
    </div>
    <div class="header-controls">
        <div class="search-wrapper">
            <input type="text" id="searchInput" class="search-input"
                   placeholder="🔍 Поиск во всем архиве ({total_posts} постов)..." oninput="searchPosts()">
            <button id="searchClearBtn" class="search-clear-btn" onclick="clearSearch()" title="Очистить поиск">✕</button>
        </div>
        <button class="btn-header" onclick="reverseOrder()" title="Изменить порядок (сначала новые / старые)">
            ↕ Порядок
        </button>
    </div>
</div>

<div class="chat-container">
<div id="globalSearchResults" class="search-results-container"></div>
<div id="noResults" class="no-results" style="display:none">Сообщения не найдены</div>
"""

    current_date = None
    prev_sender_id = None
    prev_is_out = None

    for i, post in enumerate(posts):
        # Date divider
        post_date = ""
        time_str = ""
        if post.get("date"):
            try:
                dt = datetime.fromisoformat(post["date"])
                post_date = dt.strftime("%d %B %Y")
                time_str = dt.strftime("%H:%M")
            except Exception:
                pass

        if post_date and post_date != current_date:
            current_date = post_date
            html += f'<div class="date-divider"><span>{post_date}</span></div>\n'
            prev_sender_id = None
            prev_is_out = None

        # Determine message direction and classes
        is_out = bool(post.get("out", False))
        sender_id = post.get("sender_id")
        sender_name = post.get("sender_name") or ("Вы" if is_out else channel_name)

        if not is_dialog:
            row_class = "msg-row channel-post"
        elif is_out:
            row_class = "msg-row outgoing"
        else:
            row_class = "msg-row incoming"

        # Check if first in consecutive group
        is_first_in_group = (is_out != prev_is_out) or (sender_id != prev_sender_id)
        if is_first_in_group:
            row_class += " first-in-group"

        prev_is_out = is_out
        prev_sender_id = sender_id

        # Text & Media
        text_html = _format_text(post.get("text", "")) if post.get("text") else ""
        media_html = _render_media(post.get("media_files", []), post.get("media_type"))

        # Reply Quote
        reply_html = ""
        reply_to_id = post.get("reply_to_msg_id")
        if reply_to_id and reply_to_id in msg_lookup:
            rep_info = msg_lookup[reply_to_id]
            rep_text = rep_info["text"] or "Медиафайл"
            rep_sender = rep_info["sender_name"]
            reply_html = (
                f'<a href="#msg-{reply_to_id}" class="msg-reply">'
                f'<div class="msg-reply-name">{_escape_html(rep_sender)}</div>'
                f'<div class="msg-reply-text">{_escape_html(rep_text)}</div>'
                f'</a>'
            )

        # Author header for incoming messages
        author_html = ""
        if is_dialog and not is_out and is_first_in_group:
            author_html = f'<div class="msg-author">{_escape_html(sender_name)}</div>'
        elif not is_dialog and sender_name and sender_name != channel_name and is_first_in_group:
            author_html = f'<div class="msg-author">{_escape_html(sender_name)}</div>'

        # Incoming peer mini-avatar
        avatar_col = ""
        if is_dialog and not is_out:
            if is_first_in_group:
                if peer_avatar_file:
                    avatar_col = f'<img src="./{peer_avatar_file}" class="msg-peer-avatar" alt="">'
                else:
                    avatar_col = f'<div class="msg-peer-avatar">{first_letter}</div>'
            else:
                avatar_col = '<div class="msg-avatar-spacer"></div>'

        # Views (for channels)
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

        # Checkmarks for outgoing
        check_html = '<span class="msg-check" title="Доставлено">✓✓</span>' if is_out else ""

        # Comments
        prefix = post.get("prefix", str(post.get("msg_id", "")))
        post_comments = comments_by_parent.get(prefix, [])
        comments_html = _render_comments(post_comments)

        msg_id_anchor = f'id="msg-{post.get("msg_id")}"'

        html += f"""<div class="{row_class}" {msg_id_anchor}>
{avatar_col}
<div class="message">
    {author_html}
    {reply_html}
    {f'<div class="message-text">{text_html}</div>' if text_html else ''}
    {media_html}
    {comments_html}
    <div class="msg-meta">
        {views_html}
        <span>{time_str}</span>
        {check_html}
    </div>
</div>
</div>
"""

    # Pagination
    if total_pages > 1:
        html += '<div class="pagination">\n'

        # Previous
        if page_num > 1:
            prev_link = "index.html" if page_num == 2 else f"page_{page_num - 1}.html"
            html += f'<a href="./{prev_link}">‹ Назад</a>\n'

        # Page numbers with smart ellipsis
        pages_to_show = set()
        pages_to_show.update([1, 2, total_pages - 1, total_pages])
        pages_to_show.update(range(max(1, page_num - 2), min(total_pages + 1, page_num + 3)))
        sorted_pages = sorted([p for p in pages_to_show if 1 <= p <= total_pages])

        last_p = 0
        for p in sorted_pages:
            if last_p != 0 and p - last_p > 1:
                html += '<span>…</span>\n'
            link = "index.html" if p == 1 else f"page_{p}.html"
            if p == page_num:
                html += f'<span class="current">{p}</span>\n'
            else:
                html += f'<a href="./{link}">{p}</a>\n'
            last_p = p

        # Next
        if page_num < total_pages:
            next_link = f"page_{page_num + 1}.html"
            html += f'<a href="./{next_link}">Вперед ›</a>\n'

        # Quick Jump
        html += f"""
        <div class="pagination-jump">
            <span>Стр:</span>
            <input type="number" id="pageJumpInput" min="1" max="{total_pages}" value="{page_num}"
                   onkeydown="if(event.key==='Enter') jumpToPage({total_pages})">
            <button class="btn-header" style="padding: 4px 8px; font-size: 12px;" onclick="jumpToPage({total_pages})">Go</button>
        </div>
        """

        html += '</div>\n'

    html += f"""</div>

<div class="footer">
    Создано с помощью <a href="https://github.com/milkycloud-dev/telegram-channel-downloader" target="_blank">
    Telegram Channel & Chat Downloader</a> • {datetime.now().strftime("%d.%m.%Y %H:%M")}
</div>

<div class="lightbox" id="lightbox" onclick="closeLightbox()">
    <img id="lightboxImg" src="" alt="Preview">
</div>

<script>{_JS}</script>
</body>
</html>"""

    return html
