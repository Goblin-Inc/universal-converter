"""
Abstract base class for all format converters.

Every concrete converter (ImageConverter, VideoConverter, …) must inherit
from BaseConverter and implement `convert()`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

from app.models.job import ConversionJob


ProgressCallback = Callable[[int], None]   # receives 0–100


class BaseConverter(ABC):
    """Interface all converters must satisfy."""

    @abstractmethod
    def can_handle(self, job: ConversionJob) -> bool:
        """Return True if this converter knows how to process the job."""

    @abstractmethod
    def convert(
        self,
        job: ConversionJob,
        on_progress: ProgressCallback | None = None,
    ) -> Path:
        """
        Perform the conversion.

        Args:
            job: The job descriptor. May be mutated (output_path, status).
            on_progress: Optional callback called periodically with 0-100.

        Returns:
            Path to the output file.

        Raises:
            ConversionError: on any failure.
        """


class ConversionError(Exception):
    """Raised when a conversion fails."""
