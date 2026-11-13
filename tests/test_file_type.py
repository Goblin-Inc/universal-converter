"""
Tests for file type detection utility.
Run: pytest tests/
"""

import pytest
from pathlib import Path
from app.core.utils.file_type import detect_category, FileCategory, get_output_formats


@pytest.mark.parametrize("filename,expected", [
    ("photo.png",    FileCategory.IMAGE),
    ("photo.JPG",    FileCategory.IMAGE),
    ("clip.mp4",     FileCategory.VIDEO),
    ("song.flac",    FileCategory.AUDIO),
    ("doc.md",       FileCategory.DOCUMENT),
    ("data.json",    FileCategory.DATA),
    ("file.xyz",     FileCategory.UNKNOWN),
])
def test_detect_category(filename: str, expected: FileCategory) -> None:
    assert detect_category(filename) == expected


def test_image_output_formats_not_empty() -> None:
    formats = get_output_formats(FileCategory.IMAGE)
    assert len(formats) > 0
    assert "JPG" in formats
    assert "WEBP" in formats


def test_unknown_category_returns_empty_formats() -> None:
    assert get_output_formats(FileCategory.UNKNOWN) == []
