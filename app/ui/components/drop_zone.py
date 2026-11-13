"""
DropZone — the central Drag & Drop area.

Emits:
    files_dropped(list[Path])   — when user drops files or a folder
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from app.config import ALL_SUPPORTED


class DropZone(QWidget):
    files_dropped = Signal(list)   # list[Path]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("drop_zone")
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._build_ui()

    # ── UI ──────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 40, 40, 40)

        icon = QLabel("⬆")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 36px; color: #C8C6C0;")

        heading = QLabel("Drop files here")
        heading.setObjectName("label_heading")
        heading.setAlignment(Qt.AlignCenter)

        sub = QLabel("or click to browse — images, video, audio, documents, data")
        sub.setObjectName("label_subtext")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)

        btn = QPushButton("Choose files")
        btn.setObjectName("btn_secondary")
        btn.setFixedWidth(140)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._open_dialog)

        layout.addWidget(icon)
        layout.addWidget(heading)
        layout.addWidget(sub)
        layout.addSpacing(8)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

    # ── Drag & Drop ────────────────────────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("drag_active", "true")
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, _event) -> None:
        self.setProperty("drag_active", "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent) -> None:
        self.setProperty("drag_active", "false")
        self.style().unpolish(self)
        self.style().polish(self)

        paths: list[Path] = []
        for url in event.mimeData().urls():
            p = Path(url.toLocalFile())
            if p.is_dir():
                paths.extend(self._collect_from_dir(p))
            elif p.suffix.lower() in ALL_SUPPORTED:
                paths.append(p)

        if paths:
            self.files_dropped.emit(paths)

    # ── File dialog ────────────────────────────────────────────────────────────

    def _open_dialog(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select files",
            "",
            "Supported files (*.*)",
        )
        valid = [Path(p) for p in paths if Path(p).suffix.lower() in ALL_SUPPORTED]
        if valid:
            self.files_dropped.emit(valid)

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _collect_from_dir(directory: Path) -> list[Path]:
        return [
            f for f in directory.rglob("*")
            if f.is_file() and f.suffix.lower() in ALL_SUPPORTED
        ]
