"""
Universal Converter — entry point.

Здесь регистрируются все конвертеры. Чтобы добавить новый —
импортируй его и вызови manager.register_converter() до window.show().
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.core.conversion_manager import ConversionManager
from app.core.converters.image_converter import ImageConverter
from app.ui.views.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Universal Converter")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("UniversalConverter")

    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # ── Регистрация конвертеров ────────────────────────────────────────────────
    manager = ConversionManager()
    manager.register_converter(ImageConverter())
    # manager.register_converter(VideoConverter())    # Этап 4
    # manager.register_converter(AudioConverter())    # Этап 4
    # manager.register_converter(DocumentConverter()) # Этап 4
    # manager.register_converter(DataConverter())     # Этап 4

    window = MainWindow(manager)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
