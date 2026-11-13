"""
File type detection based on extension.
"""

from pathlib import Path
from enum import Enum, auto

from app.config import (
    IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, AUDIO_EXTENSIONS,
    DOCUMENT_EXTENSIONS, DATA_EXTENSIONS,
    IMAGE_OUTPUT_FORMATS, VIDEO_OUTPUT_FORMATS, AUDIO_OUTPUT_FORMATS,
    DOCUMENT_OUTPUT_FORMATS, DATA_OUTPUT_FORMATS,
)


class FileCategory(Enum):
    IMAGE = auto()
    VIDEO = auto()
    AUDIO = auto()
    DOCUMENT = auto()
    DATA = auto()
    UNKNOWN = auto()


def detect_category(path: str | Path) -> FileCategory:
    """Return the FileCategory for a given file path."""
    ext = Path(path).suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return FileCategory.IMAGE
    if ext in VIDEO_EXTENSIONS:
        return FileCategory.VIDEO
    if ext in AUDIO_EXTENSIONS:
        return FileCategory.AUDIO
    if ext in DOCUMENT_EXTENSIONS:
        return FileCategory.DOCUMENT
    if ext in DATA_EXTENSIONS:
        return FileCategory.DATA
    return FileCategory.UNKNOWN


def get_output_formats(category: FileCategory) -> list[str]:
    """Return the list of available output formats for a category."""
    mapping = {
        FileCategory.IMAGE: IMAGE_OUTPUT_FORMATS,
        FileCategory.VIDEO: VIDEO_OUTPUT_FORMATS,
        FileCategory.AUDIO: AUDIO_OUTPUT_FORMATS,
        FileCategory.DOCUMENT: DOCUMENT_OUTPUT_FORMATS,
        FileCategory.DATA: DATA_OUTPUT_FORMATS,
    }
    return mapping.get(category, [])


CATEGORY_LABELS = {
    FileCategory.IMAGE: "Image",
    FileCategory.VIDEO: "Video",
    FileCategory.AUDIO: "Audio",
    FileCategory.DOCUMENT: "Document",
    FileCategory.DATA: "Data / Spreadsheet",
    FileCategory.UNKNOWN: "Unknown",
}
