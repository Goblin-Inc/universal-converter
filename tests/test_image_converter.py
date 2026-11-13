"""
Тесты ImageConverter — проверяем реальную конвертацию через Pillow.
Запуск: pip install Pillow && python -m pytest tests/ -v
"""

from __future__ import annotations

import pytest
from pathlib import Path
import tempfile
import os

from app.core.converters.image_converter import ImageConverter
from app.core.utils.file_type import FileCategory
from app.models.job import ConversionJob, JobStatus


def _make_test_image(path: Path, mode: str = "RGB", size=(100, 100)) -> None:
    """Создать тестовое изображение через Pillow."""
    from PIL import Image
    import random
    img = Image.new(mode, size, color=(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    ) if mode == "RGB" else (128, 128, 128, 200))
    img.save(path)


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


@pytest.fixture()
def converter():
    return ImageConverter()


# ── can_handle ─────────────────────────────────────────────────────────────────

def test_can_handle_image(converter):
    job = ConversionJob(
        source_path=Path("photo.png"),
        output_format="WEBP",
        category=FileCategory.IMAGE,
    )
    assert converter.can_handle(job) is True


def test_cannot_handle_video(converter):
    job = ConversionJob(
        source_path=Path("clip.mp4"),
        output_format="AVI",
        category=FileCategory.VIDEO,
    )
    assert converter.can_handle(job) is False


# ── Базовые конвертации ────────────────────────────────────────────────────────

@pytest.mark.parametrize("out_fmt", ["WEBP", "PNG", "BMP", "TIFF"])
def test_png_to_format(converter, tmp, out_fmt):
    src = tmp / "test.png"
    _make_test_image(src, mode="RGB")

    job = ConversionJob(
        source_path=src,
        output_format=out_fmt,
        category=FileCategory.IMAGE,
        output_dir=tmp,
    )
    result = converter.convert(job)

    assert result.exists()
    assert result.suffix.lower() == f".{out_fmt.lower()}"
    assert job.status != JobStatus.FAILED


def test_png_to_jpg(converter, tmp):
    src = tmp / "test.png"
    _make_test_image(src, mode="RGB")

    job = ConversionJob(
        source_path=src,
        output_format="JPG",
        category=FileCategory.IMAGE,
        output_dir=tmp,
    )
    result = converter.convert(job)
    assert result.exists()
    assert result.suffix.lower() == ".jpg"


def test_rgba_to_jpg_no_crash(converter, tmp):
    """RGBA → JPG должен корректно убирать прозрачность."""
    src = tmp / "transparent.png"
    _make_test_image(src, mode="RGBA")

    job = ConversionJob(
        source_path=src,
        output_format="JPG",
        category=FileCategory.IMAGE,
        output_dir=tmp,
    )
    result = converter.convert(job)
    assert result.exists()


def test_png_to_ico(converter, tmp):
    src = tmp / "icon.png"
    _make_test_image(src, mode="RGB", size=(256, 256))

    job = ConversionJob(
        source_path=src,
        output_format="ICO",
        category=FileCategory.IMAGE,
        output_dir=tmp,
    )
    result = converter.convert(job)
    assert result.exists()
    assert result.suffix.lower() == ".ico"


# ── Прогресс ───────────────────────────────────────────────────────────────────

def test_progress_callback_called(converter, tmp):
    src = tmp / "test.png"
    _make_test_image(src, mode="RGB")

    progress_values = []
    job = ConversionJob(
        source_path=src,
        output_format="WEBP",
        category=FileCategory.IMAGE,
        output_dir=tmp,
    )
    converter.convert(job, on_progress=progress_values.append)

    assert len(progress_values) > 0
    assert progress_values[-1] == 100


# ── Качество ───────────────────────────────────────────────────────────────────

def test_quality_setting_affects_filesize(converter, tmp):
    """Файл с quality=50 должен быть меньше чем с quality=95."""
    src = tmp / "test.png"
    _make_test_image(src, mode="RGB", size=(500, 500))

    job_lo = ConversionJob(
        source_path=src, output_format="JPG",
        category=FileCategory.IMAGE, output_dir=tmp, image_quality=50,
    )
    job_lo.id = "lo"
    result_lo = converter.convert(job_lo)
    # Переименуем чтобы не конфликтовали
    lo_path = tmp / "lo.jpg"
    result_lo.rename(lo_path)

    job_hi = ConversionJob(
        source_path=src, output_format="JPG",
        category=FileCategory.IMAGE, output_dir=tmp, image_quality=95,
    )
    result_hi = converter.convert(job_hi)

    assert lo_path.stat().st_size < result_hi.stat().st_size


# ── Ошибки ─────────────────────────────────────────────────────────────────────

def test_missing_file_raises(converter, tmp):
    from app.core.converters.base import ConversionError
    job = ConversionJob(
        source_path=tmp / "nonexistent.png",
        output_format="WEBP",
        category=FileCategory.IMAGE,
    )
    with pytest.raises(ConversionError):
        converter.convert(job)


def test_unknown_format_raises(converter, tmp):
    from app.core.converters.base import ConversionError
    src = tmp / "test.png"
    _make_test_image(src)

    job = ConversionJob(
        source_path=src,
        output_format="XYZ",
        category=FileCategory.IMAGE,
        output_dir=tmp,
    )
    with pytest.raises(ConversionError):
        converter.convert(job)
