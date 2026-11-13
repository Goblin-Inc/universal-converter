"""
ConversionManager — central coordinator.

Responsibilities:
  - Maintain the queue of ConversionJob objects.
  - Route each job to the correct BaseConverter.
  - Run jobs on a QThreadPool worker so the UI stays responsive.
  - Emit Qt signals for progress / completion / failure.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, Slot

from app.models.job import ConversionJob, JobStatus
from app.core.converters.base import BaseConverter, ConversionError


# ── Worker ─────────────────────────────────────────────────────────────────────

class _ConversionWorker(QRunnable):
    """Runs a single job on the thread pool."""

    def __init__(
        self,
        job: ConversionJob,
        converter: BaseConverter,
        signals: "_WorkerSignals",
    ) -> None:
        super().__init__()
        self.job = job
        self.converter = converter
        self.signals = signals
        self.setAutoDelete(True)

    @Slot()
    def run(self) -> None:
        self.job.status = JobStatus.RUNNING
        self.signals.started.emit(self.job.id)

        try:
            output = self.converter.convert(
                self.job,
                on_progress=lambda p: self.signals.progress.emit(self.job.id, p),
            )
            self.job.output_path = output
            self.job.status = JobStatus.DONE
            self.job.progress = 100
            self.signals.finished.emit(self.job.id)
        except ConversionError as exc:
            self.job.status = JobStatus.FAILED
            self.job.error_message = str(exc)
            self.signals.failed.emit(self.job.id, str(exc))


class _WorkerSignals(QObject):
    started = Signal(str)           # job_id
    progress = Signal(str, int)     # job_id, 0-100
    finished = Signal(str)          # job_id
    failed = Signal(str, str)       # job_id, error_message


# ── Manager ────────────────────────────────────────────────────────────────────

class ConversionManager(QObject):
    """
    Central coordinator for all conversion operations.

    Signals:
        job_started(job_id)
        job_progress(job_id, percent)
        job_finished(job_id)
        job_failed(job_id, error_message)
    """

    job_started = Signal(str)
    job_progress = Signal(str, int)
    job_finished = Signal(str)
    job_failed = Signal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._converters: list[BaseConverter] = []
        self._jobs: dict[str, ConversionJob] = {}
        self._pool = QThreadPool.globalInstance()

    # ── Public API ─────────────────────────────────────────────────────────────

    def register_converter(self, converter: BaseConverter) -> None:
        """Register a converter. Call this during app startup."""
        self._converters.append(converter)

    def submit(self, job: ConversionJob) -> None:
        """Add a job to the queue and start it immediately."""
        converter = self._find_converter(job)
        if converter is None:
            job.status = JobStatus.FAILED
            job.error_message = f"No converter found for {job.category.name} → {job.output_format}"
            self.job_failed.emit(job.id, job.error_message)
            return

        self._jobs[job.id] = job
        signals = _WorkerSignals()
        signals.started.connect(self.job_started)
        signals.progress.connect(self.job_progress)
        signals.finished.connect(self.job_finished)
        signals.failed.connect(self.job_failed)

        worker = _ConversionWorker(job, converter, signals)
        self._pool.start(worker)

    def get_job(self, job_id: str) -> ConversionJob | None:
        return self._jobs.get(job_id)

    def all_jobs(self) -> list[ConversionJob]:
        return list(self._jobs.values())

    # ── Internal ───────────────────────────────────────────────────────────────

    def _find_converter(self, job: ConversionJob) -> BaseConverter | None:
        for c in self._converters:
            if c.can_handle(job):
                return c
        return None
