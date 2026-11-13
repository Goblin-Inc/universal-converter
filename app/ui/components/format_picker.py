"""
FormatPicker — ряд кнопок-chips для выбора целевого формата.

Emits:
    format_selected(str)   — когда пользователь нажимает на chip
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal


class FormatPicker(QWidget):
    format_selected = Signal(str)   # например "WEBP"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._selected: str | None = None
        self._chips: dict[str, QPushButton] = {}
        self._build_ui()
        self.setVisible(False)

    def _build_ui(self) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        label = QLabel("Convert to")
        label.setObjectName("label_subtext")
        label.setFixedWidth(80)

        # Прокручиваемая область chips (для случаев с >6 форматами)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFixedHeight(44)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._chip_container = QWidget()
        self._chip_container.setStyleSheet("background: transparent;")
        self._chip_layout = QHBoxLayout(self._chip_container)
        self._chip_layout.setContentsMargins(0, 4, 0, 4)
        self._chip_layout.setSpacing(8)
        self._chip_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._chip_layout.addStretch()

        scroll.setWidget(self._chip_container)

        outer.addWidget(label, alignment=Qt.AlignVCenter)
        outer.addWidget(scroll, stretch=1)

    def set_formats(self, formats: list[str]) -> None:
        """Заменить chips под новый список форматов."""
        # Очистить старые chips
        for chip in self._chips.values():
            chip.deleteLater()
        self._chips.clear()
        self._selected = None

        # Убрать stretch перед добавлением
        stretch_item = self._chip_layout.takeAt(self._chip_layout.count() - 1)

        for fmt in formats:
            btn = QPushButton(fmt)
            btn.setObjectName("format_chip")
            btn.setCheckable(False)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(32)
            btn.clicked.connect(lambda checked, f=fmt: self._select(f))
            self._chips[fmt] = btn
            self._chip_layout.addWidget(btn)

        self._chip_layout.addStretch()
        self.setVisible(bool(formats))

    def _select(self, fmt: str) -> None:
        # Снять выделение с предыдущего
        if self._selected and self._selected in self._chips:
            prev = self._chips[self._selected]
            prev.setProperty("selected", "false")
            prev.style().unpolish(prev)
            prev.style().polish(prev)

        # Выделить новый
        self._selected = fmt
        chip = self._chips[fmt]
        chip.setProperty("selected", "true")
        chip.style().unpolish(chip)
        chip.style().polish(chip)

        self.format_selected.emit(fmt)

    @property
    def selected_format(self) -> str | None:
        return self._selected
