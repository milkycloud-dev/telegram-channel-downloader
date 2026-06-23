"""
Telegram Media Scraper — Точка входа.
Запускает GUI-приложение.
"""

from gui_app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
