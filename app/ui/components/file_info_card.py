"""
FileInfoCard — показывает информацию о выбранном файле.

Отображает: имя, размер, категорию, иконку типа.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from app.core.utils.file_type import FileCategory, CATEGORY_LABELS


CATEGORY_ICONS = {
    FileCategory.IMAGE:    "🖼",
    FileCategory.VIDEO:    "🎬",
    FileCategory.AUDIO:    "🎵",
    FileCategory.DOCUMENT: "📄",
    FileCategory.DATA:     "📊",
    FileCategory.UNKNOWN:  "📁",
}


def _human_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.0f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


class FileInfoCard(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("file_info_card")
        self._build_ui()
        self.setVisible(False)

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Иконка
        self._icon = QLabel("📁")
        self._icon.setFixedSize(40, 40)
        self._icon.setAlignment(Qt.AlignCenter)
        self._icon.setStyleSheet("font-size: 24px;")

        # Текстовый блок
        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        self._name_label = QLabel()
        self._name_label.setObjectName("label_filename")

        self._meta_label = QLabel()
        self._meta_label.setObjectName("label_subtext")

        text_col.addWidget(self._name_label)
        text_col.addWidget(self._meta_label)

        # Бейдж категории
        self._category_badge = QLabel()
        self._category_badge.setObjectName("label_category")
        self._category_badge.setAlignment(Qt.AlignCenter)

        layout.addWidget(self._icon)
        layout.addLayout(text_col, stretch=1)
        layout.addWidget(self._category_badge, alignment=Qt.AlignVCenter)

    def set_files(self, paths: list[Path], category: FileCategory) -> None:
        """Обновить карточку под выбранные файлы."""
        count = len(paths)
        first = paths[0]

        self._icon.setText(CATEGORY_ICONS.get(category, "📁"))

        if count == 1:
            self._name_label.setText(first.name)
            try:
                size = _human_size(first.stat().st_size)
            except OSError:
                size = "—"
            self._meta_label.setText(f"{size}  ·  {first.parent}")
        else:
            self._name_label.setText(f"{count} files selected")
            names = ", ".join(p.name for p in paths[:2])
            if count > 2:
                names += f" and {count - 2} more"
            self._meta_label.setText(names)

        self._category_badge.setText(CATEGORY_LABELS.get(category, "Unknown"))
        self.setVisible(True)
