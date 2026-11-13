"""
ImageConverter — конвертация изображений через Pillow.

Поддерживает: PNG, JPG/JPEG, WEBP, ICO, BMP, TIFF, GIF.
Особые случаи:
  - ICO требует конкретный список размеров
  - GIF сохраняет палитру через квантизацию
  - SVG → растр не поддерживается (требует cairosvg, добавим в v2)
  - EXIF сохраняется по умолчанию, кроме случаев когда формат его не поддерживает
"""

from __future__ import annotations

import os
from pathlib import Path

from app.core.converters.base import BaseConverter, ConversionError, ProgressCallback
from app.core.utils.file_type import FileCategory
from app.models.job import ConversionJob
from app.config import DEFAULT_IMAGE_QUALITY


# Пилоу-форматы по расширению выходного файла
_FORMAT_MAP: dict[str, str] = {
    "jpg":  "JPEG",
    "jpeg": "JPEG",
    "png":  "PNG",
    "webp": "WEBP",
    "ico":  "ICO",
    "bmp":  "BMP",
    "tiff": "TIFF",
    "tif":  "TIFF",
    "gif":  "GIF",
}

# Форматы, которые поддерживают прозрачность (RGBA)
_SUPPORTS_ALPHA = {"PNG", "WEBP", "GIF", "ICO"}

# ICO: стандартные размеры
_ICO_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


class ImageConverter(BaseConverter):
    """Конвертер изображений на базе Pillow."""

    def can_handle(self, job: ConversionJob) -> bool:
        return job.category == FileCategory.IMAGE

    def convert(
        self,
        job: ConversionJob,
        on_progress: ProgressCallback | None = None,
    ) -> Path:
        try:
            from PIL import Image
        except ImportError:
            raise ConversionError(
                "Pillow не установлен. Запустите: pip install Pillow"
            )

        src = job.source_path
        if not src.exists():
            raise ConversionError(f"Файл не найден: {src}")

        # Входной формат SVG Pillow не читает
        if src.suffix.lower() == ".svg":
            raise ConversionError(
                "Конвертация SVG пока не поддерживается (требует cairosvg)"
            )

        out_ext = job.output_format.lower()
        pil_format = _FORMAT_MAP.get(out_ext)
        if pil_format is None:
            raise ConversionError(f"Неизвестный формат: {job.output_format}")

        # Путь для сохранения
        out_dir = job.output_dir or src.parent
        out_path = out_dir / f"{src.stem}.{out_ext}"
        # Не перезаписываем оригинал если расширения совпадают
        if out_path.resolve() == src.resolve():
            out_path = out_dir / f"{src.stem}_converted.{out_ext}"

        if on_progress:
            on_progress(10)

        try:
            img: Image.Image = Image.open(src)
        except Exception as exc:
            raise ConversionError(f"Не удалось открыть файл: {exc}") from exc

        if on_progress:
            on_progress(30)

        # Сохраняем EXIF если есть и формат поддерживает
        exif_data = None
        if pil_format in ("JPEG", "WEBP", "TIFF"):
            exif_data = img.info.get("exif")

        # Режим изображения
        img = self._prepare_mode(img, pil_format)

        if on_progress:
            on_progress(60)

        # Параметры сохранения
        save_kwargs = self._build_save_kwargs(job, img, pil_format, exif_data)

        try:
            img.save(out_path, format=pil_format, **save_kwargs)
        except Exception as exc:
            raise ConversionError(f"Ошибка при сохранении: {exc}") from exc

        if on_progress:
            on_progress(100)

        job.output_path = out_path
        return out_path

    # ── Вспомогательные методы ─────────────────────────────────────────────────

    @staticmethod
    def _prepare_mode(img, pil_format: str):
        """Привести режим изображения к совместимому с целевым форматом."""
        from PIL import Image

        if pil_format == "JPEG":
            # JPEG не поддерживает прозрачность — конвертируем на белый фон
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                if img.mode in ("RGBA", "LA"):
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                return background
            return img.convert("RGB") if img.mode != "RGB" else img

        if pil_format == "ICO":
            # ICO лучше работает с RGBA
            return img.convert("RGBA") if img.mode != "RGBA" else img

        if pil_format == "BMP":
            return img.convert("RGB") if img.mode not in ("RGB", "RGBA") else img

        if pil_format == "GIF":
            # GIF — только палитра (P) или L
            if img.mode == "RGBA":
                # Квантизуем с прозрачностью
                return img.convert("P", palette=Image.ADAPTIVE)
            return img.convert("P") if img.mode not in ("P", "L") else img

        return img

    @staticmethod
    def _build_save_kwargs(
        job: ConversionJob,
        img,
        pil_format: str,
        exif_data: bytes | None,
    ) -> dict:
        kwargs: dict = {}
        quality = job.image_quality or DEFAULT_IMAGE_QUALITY

        if pil_format == "JPEG":
            kwargs["quality"] = quality
            kwargs["optimize"] = True
            if exif_data:
                kwargs["exif"] = exif_data

        elif pil_format == "WEBP":
            kwargs["quality"] = quality
            kwargs["method"] = 6        # лучшее сжатие, чуть медленнее
            if exif_data:
                kwargs["exif"] = exif_data

        elif pil_format == "PNG":
            # PNG lossless; compress_level 0-9
            kwargs["optimize"] = True

        elif pil_format == "ICO":
            kwargs["sizes"] = _ICO_SIZES

        elif pil_format == "TIFF":
            kwargs["compression"] = "lzw"
            if exif_data:
                kwargs["exif"] = exif_data

        elif pil_format == "GIF":
            kwargs["optimize"] = True

        return kwargs
