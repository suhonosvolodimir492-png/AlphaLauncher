"""Точка входа AlphaLauncher. Запуск: python main.py (или AlphaLauncher.exe после сборки)."""
from __future__ import annotations

import logging
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from alphalauncher.auth.accounts import AccountStore
from alphalauncher.config import ACCOUNTS_FILE, APP_NAME, DATA_DIR, LOG_FILE, SETTINGS_FILE
from alphalauncher.services.game_service import GameService
from alphalauncher.settings.settings import SettingsStore
from alphalauncher.ui.main_window import MainWindow
from alphalauncher.ui.theme import build_stylesheet, find_asset


def _setup_logging() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")],
    )


def main() -> int:
    _setup_logging()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyleSheet(build_stylesheet())
    icon = find_asset("icon.ico")
    if icon is not None:
        app.setWindowIcon(QIcon(str(icon)))
    services = GameService(SettingsStore(SETTINGS_FILE), AccountStore(ACCOUNTS_FILE))
    window = MainWindow(services)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
