"""
Data models for conversion jobs.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

from app.core.utils.file_type import FileCategory


class JobStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    DONE = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class ConversionJob:
    """Represents a single file conversion task."""

    source_path: Path
    output_format: str
    category: FileCategory

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = JobStatus.PENDING
    progress: int = 0          # 0–100
    output_path: Path | None = None
    error_message: str = ""

    # Optional per-job settings (overrides global config)
    image_quality: int | None = None
    output_dir: Path | None = None

    @property
    def source_name(self) -> str:
        return self.source_path.name

    @property
    def target_name(self) -> str:
        stem = self.source_path.stem
        ext = self.output_format.lower()
        return f"{stem}.{ext}"
