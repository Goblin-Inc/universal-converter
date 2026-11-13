"""
JobCard — карточка одного задания в очереди конвертации.

Показывает: имя файла, целевой формат, прогресс-бар, статус.
После завершения — кнопка «Открыть папку».
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QProgressBar, QPushButton,
)
from PySide6.QtCore import Qt, Signal

from app.models.job import ConversionJob, JobStatus


STATUS_ICONS = {
    JobStatus.PENDING:   ("⏳", "#888780"),
    JobStatus.RUNNING:   ("⟳",  "#7F77DD"),
    JobStatus.DONE:      ("✓",  "#1D9E75"),
    JobStatus.FAILED:    ("✗",  "#D85A30"),
    JobStatus.CANCELLED: ("—",  "#888780"),
}


class JobCard(QWidget):
    cancel_requested = Signal(str)   # job_id

    def __init__(self, job: ConversionJob, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._job = job
        self.setObjectName("job_card")
        self.setStyleSheet(
            "JobCard { background: #FFFFFF; border: 1px solid #DDDBD6;"
            " border-radius: 10px; }"
        )
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Статус-иконка
        self._status_icon = QLabel("⏳")
        self._status_icon.setFixedWidth(20)
        self._status_icon.setAlignment(Qt.AlignCenter)
        self._status_icon.setStyleSheet("font-size: 14px;")

        # Центральный блок
        center = QVBoxLayout()
        center.setSpacing(4)

        name_row = QHBoxLayout()
        self._name_label = QLabel(self._job.source_name)
        self._name_label.setStyleSheet("font-size: 13px; font-weight: 500;")

        arrow = QLabel(f"→  {self._job.output_format}")
        arrow.setObjectName("label_subtext")
        arrow.setStyleSheet("font-size: 12px;")

        name_row.addWidget(self._name_label)
        name_row.addSpacing(8)
        name_row.addWidget(arrow)
        name_row.addStretch()

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFixedHeight(4)

        self._status_text = QLabel("Waiting…")
        self._status_text.setObjectName("label_subtext")
        self._status_text.setStyleSheet("font-size: 11px;")

        center.addLayout(name_row)
        center.addWidget(self._progress)
        center.addWidget(self._status_text)

        # Правая панель: кнопка отмены / открыть папку
        self._cancel_btn = QPushButton("✕")
        self._cancel_btn.setObjectName("btn_secondary")
        self._cancel_btn.setFixedSize(28, 28)
        self._cancel_btn.setCursor(Qt.PointingHandCursor)
        self._cancel_btn.setStyleSheet(
            "QPushButton { border-radius: 14px; padding: 0; font-size: 11px; }"
        )
        self._cancel_btn.clicked.connect(
            lambda: self.cancel_requested.emit(self._job.id)
        )

        self._open_btn = QPushButton("Open folder")
        self._open_btn.setObjectName("btn_secondary")
        self._open_btn.setFixedHeight(28)
        self._open_btn.setCursor(Qt.PointingHandCursor)
        self._open_btn.setStyleSheet("font-size: 12px;")
        self._open_btn.setVisible(False)
        self._open_btn.clicked.connect(self._open_output_folder)

        layout.addWidget(self._status_icon)
        layout.addLayout(center, stretch=1)
        layout.addWidget(self._open_btn, alignment=Qt.AlignVCenter)
        layout.addWidget(self._cancel_btn, alignment=Qt.AlignVCenter)

    # ── Public update API ──────────────────────────────────────────────────────

    def set_progress(self, value: int) -> None:
        self._progress.setValue(value)
        self._status_text.setText(f"{value}%")

    def set_status(self, status: JobStatus) -> None:
        icon, color = STATUS_ICONS.get(status, ("?", "#888780"))
        self._status_icon.setText(icon)
        self._status_icon.setStyleSheet(f"font-size: 14px; color: {color};")

        if status == JobStatus.DONE:
            self._progress.setValue(100)
            out = self._job.output_path
            if out:
                self._status_text.setText(f"Saved: {out.name}")
            else:
                self._status_text.setText("Done")
            self._cancel_btn.setVisible(False)
            self._open_btn.setVisible(True)

        elif status == JobStatus.FAILED:
            self._status_text.setText(f"Error: {self._job.error_message}")
            self._cancel_btn.setVisible(False)

        elif status == JobStatus.CANCELLED:
            self._status_text.setText("Cancelled")
            self._cancel_btn.setVisible(False)

        elif status == JobStatus.RUNNING:
            self._status_text.setText("Converting…")

    # ── Actions ───────────────────────────────────────────────────────────────

    def _open_output_folder(self) -> None:
        """Открыть папку с результатом в файловом менеджере."""
        path = self._job.output_path
        if not path:
            return
        folder = path.parent
        try:
            if sys.platform == "win32":
                # Выделяем файл в Explorer
                subprocess.run(["explorer", "/select,", str(path)], check=False)
            elif sys.platform == "darwin":
                subprocess.run(["open", "-R", str(path)], check=False)
            else:
                # Linux — открываем папку
                subprocess.run(["xdg-open", str(folder)], check=False)
        except Exception:
            # Fallback: просто открываем папку
            os.startfile(folder) if sys.platform == "win32" else None
