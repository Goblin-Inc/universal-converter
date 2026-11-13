"""
MainWindow — главное окно приложения.

Состояния экрана:
  IDLE      — пустой экран с DropZone
  PICKED    — файл выбран, показаны FileInfoCard + FormatPicker + кнопка Convert
  CONVERTING — идёт конвертация, показаны JobCard'ы с прогрессом

Layout:
  ┌─────────┬────────────────────────────────────────────────┐
  │ sidebar │  header                                        │
  │         ├────────────────────────────────────────────────┤
  │  ⇄      │  [DropZone]  (IDLE)                           │
  │  ⏰     │  или                                           │
  │  ⚙      │  [FileInfoCard]                               │
  │         │  [FormatPicker]                               │
  │         │  [Convert btn]                                │
  │         │  [JobList]                                    │
  └─────────┴────────────────────────────────────────────────┘
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QScrollArea, QSizePolicy, QFrame,
)
from PySide6.QtCore import Qt, Slot

from app.config import WINDOW_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from app.core.conversion_manager import ConversionManager
from app.core.utils.file_type import (
    detect_category, get_output_formats, CATEGORY_LABELS, FileCategory,
)
from app.models.job import ConversionJob, JobStatus
from app.ui.components.drop_zone import DropZone
from app.ui.components.file_info_card import FileInfoCard
from app.ui.components.format_picker import FormatPicker
from app.ui.components.job_card import JobCard


class MainWindow(QMainWindow):
    def __init__(self, manager: ConversionManager | None = None) -> None:
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(920, 640)

        self._manager = manager or ConversionManager(self)
        self._manager.job_started.connect(self._on_job_started)
        self._manager.job_progress.connect(self._on_job_progress)
        self._manager.job_finished.connect(self._on_job_finished)
        self._manager.job_failed.connect(self._on_job_failed)

        # Состояние
        self._pending_paths: list[Path] = []
        self._pending_category: FileCategory = FileCategory.UNKNOWN
        self._job_cards: dict[str, JobCard] = {}

        self._load_stylesheet()
        self._build_ui()

    # ── Stylesheet ─────────────────────────────────────────────────────────────

    def _load_stylesheet(self) -> None:
        qss_path = Path(__file__).parent.parent / "styles" / "main.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._make_sidebar())
        root_layout.addWidget(self._make_content(), stretch=1)

    # ── Sidebar ────────────────────────────────────────────────────────────────

    def _make_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignTop)

        items = [
            ("⇄", "Convert", True),
            ("⏰", "History", False),
            ("⚙", "Settings", False),
        ]
        for icon, tip, active in items:
            lbl = QLabel(icon)
            lbl.setToolTip(tip)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedSize(56, 48)
            color = "#1C1C1A" if active else "#B4B2A9"
            lbl.setStyleSheet(f"font-size: 18px; color: {color};")
            layout.addWidget(lbl)

        layout.addStretch()
        return sidebar

    # ── Content area ───────────────────────────────────────────────────────────

    def _make_content(self) -> QWidget:
        content = QWidget()
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(32, 28, 32, 28)
        self._content_layout.setSpacing(0)

        # Header
        self._content_layout.addLayout(self._make_header())
        self._content_layout.addSpacing(24)

        # ── Drop zone (состояние IDLE) ─────────────────────────────────────────
        self._drop_zone = DropZone()
        self._drop_zone.files_dropped.connect(self._on_files_dropped)
        self._content_layout.addWidget(self._drop_zone, stretch=1)

        # ── Панель после выбора файла (состояние PICKED / CONVERTING) ──────────
        self._picker_panel = self._make_picker_panel()
        self._picker_panel.setVisible(False)
        self._content_layout.addWidget(self._picker_panel)

        # ── Очередь заданий ────────────────────────────────────────────────────
        self._content_layout.addSpacing(8)
        self._job_list_widget, self._job_list_layout = self._make_job_list()
        self._content_layout.addWidget(self._job_list_widget)

        return content

    def _make_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        title = QLabel("Universal Converter")
        title.setObjectName("label_heading")

        self._convert_another_btn = QPushButton("+ New file")
        self._convert_another_btn.setObjectName("btn_secondary")
        self._convert_another_btn.setCursor(Qt.PointingHandCursor)
        self._convert_another_btn.setFixedHeight(36)
        self._convert_another_btn.setVisible(False)
        self._convert_another_btn.clicked.connect(self._reset_to_idle)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self._convert_another_btn)
        return layout

    def _make_picker_panel(self) -> QWidget:
        """Панель: FileInfoCard + FormatPicker + кнопка Convert."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Карточка файла
        self._file_info = FileInfoCard()
        self._file_info.setStyleSheet(
            "#file_info_card { background: #FFFFFF; border: 1px solid #DDDBD6;"
            "border-radius: 12px; }"
        )
        layout.addWidget(self._file_info)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #EEECEA;")
        layout.addWidget(line)

        # Выбор формата
        self._format_picker = FormatPicker()
        self._format_picker.format_selected.connect(self._on_format_selected)
        layout.addWidget(self._format_picker)

        # Кнопка Convert
        btn_row = QHBoxLayout()
        self._convert_btn = QPushButton("Convert")
        self._convert_btn.setCursor(Qt.PointingHandCursor)
        self._convert_btn.setFixedHeight(44)
        self._convert_btn.setFixedWidth(160)
        self._convert_btn.setEnabled(False)
        self._convert_btn.clicked.connect(self._on_convert_clicked)

        self._convert_hint = QLabel("Select a format to continue")
        self._convert_hint.setObjectName("label_subtext")

        btn_row.addWidget(self._convert_btn)
        btn_row.addSpacing(16)
        btn_row.addWidget(self._convert_hint, alignment=Qt.AlignVCenter)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        return panel

    def _make_job_list(self) -> tuple[QScrollArea, QVBoxLayout]:
        """Прокручиваемый список JobCard."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setVisible(False)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        job_layout = QVBoxLayout(container)
        job_layout.setContentsMargins(0, 0, 0, 0)
        job_layout.setSpacing(8)
        job_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(container)
        return scroll, job_layout

    # ── Логика переходов состояний ─────────────────────────────────────────────

    def _show_picker(self) -> None:
        """Переключиться в состояние PICKED."""
        self._drop_zone.setVisible(False)
        self._picker_panel.setVisible(True)
        self._convert_another_btn.setVisible(True)

    def _reset_to_idle(self) -> None:
        """Вернуться в состояние IDLE."""
        self._pending_paths = []
        self._pending_category = FileCategory.UNKNOWN

        self._drop_zone.setVisible(True)
        self._picker_panel.setVisible(False)
        self._convert_another_btn.setVisible(False)
        self._convert_btn.setEnabled(False)
        self._convert_hint.setText("Select a format to continue")
        self._format_picker.setVisible(False)

    # ── Slots ──────────────────────────────────────────────────────────────────

    @Slot(list)
    def _on_files_dropped(self, paths: list[Path]) -> None:
        self._pending_paths = paths
        self._pending_category = detect_category(paths[0])

        self._file_info.set_files(paths, self._pending_category)

        formats = get_output_formats(self._pending_category)
        self._format_picker.set_formats(formats)

        self._convert_btn.setEnabled(False)
        self._convert_hint.setText("Select a format to continue")

        self._show_picker()

    @Slot(str)
    def _on_format_selected(self, fmt: str) -> None:
        self._convert_btn.setEnabled(True)
        count = len(self._pending_paths)
        noun = "file" if count == 1 else "files"
        self._convert_hint.setText(f"Ready to convert {count} {noun} → {fmt}")

    @Slot()
    def _on_convert_clicked(self) -> None:
        fmt = self._format_picker.selected_format
        if not fmt or not self._pending_paths:
            return

        self._convert_btn.setEnabled(False)
        self._convert_btn.setText("Converting…")
        self._job_list_widget.setVisible(True)

        for path in self._pending_paths:
            job = ConversionJob(
                source_path=path,
                output_format=fmt,
                category=self._pending_category,
            )
            card = JobCard(job)
            card.setStyleSheet(
                "JobCard { background: #FFFFFF; border: 1px solid #DDDBD6;"
                "border-radius: 10px; }"
            )
            self._job_cards[job.id] = card
            self._job_list_layout.addWidget(card)
            self._manager.submit(job)

    @Slot(str)
    def _on_job_started(self, job_id: str) -> None:
        card = self._job_cards.get(job_id)
        if card:
            card.set_status(JobStatus.RUNNING)

    @Slot(str, int)
    def _on_job_progress(self, job_id: str, value: int) -> None:
        card = self._job_cards.get(job_id)
        if card:
            card.set_progress(value)

    @Slot(str)
    def _on_job_finished(self, job_id: str) -> None:
        card = self._job_cards.get(job_id)
        if card:
            card.set_status(JobStatus.DONE)
        self._check_all_done()

    @Slot(str, str)
    def _on_job_failed(self, job_id: str, error: str) -> None:
        card = self._job_cards.get(job_id)
        if card:
            card.set_status(JobStatus.FAILED)
        self._check_all_done()

    def _check_all_done(self) -> None:
        """Разблокировать кнопку когда все задания завершены."""
        all_done = all(
            self._manager.get_job(jid).status
            in (JobStatus.DONE, JobStatus.FAILED, JobStatus.CANCELLED)
            for jid in self._job_cards
        )
        if all_done:
            self._convert_btn.setEnabled(True)
            self._convert_btn.setText("Convert again")
