"""
App-wide constants and configuration defaults.
"""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent
RESOURCES_DIR = ROOT_DIR / "resources"

# ── Window ─────────────────────────────────────────────────────────────────────
WINDOW_TITLE = "Universal Converter"
WINDOW_MIN_WIDTH = 780
WINDOW_MIN_HEIGHT = 560

# ── Conversion defaults ────────────────────────────────────────────────────────
DEFAULT_OUTPUT_SAME_DIR = True   # save result next to the source file
DEFAULT_IMAGE_QUALITY = 90       # JPEG/WEBP quality (1–100)
DEFAULT_THREAD_COUNT = 4

# ── Supported formats (used for file-type detection) ──────────────────────────
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".ico",
                    ".bmp", ".tiff", ".tif", ".svg", ".gif"}

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm"}

AUDIO_EXTENSIONS = {".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a"}

DOCUMENT_EXTENSIONS = {".md", ".txt", ".html", ".pdf"}

DATA_EXTENSIONS = {".json", ".yaml", ".yml", ".csv", ".xml", ".xlsx"}

ALL_SUPPORTED = (
    IMAGE_EXTENSIONS
    | VIDEO_EXTENSIONS
    | AUDIO_EXTENSIONS
    | DOCUMENT_EXTENSIONS
    | DATA_EXTENSIONS
)

# ── Output format options per category ────────────────────────────────────────
IMAGE_OUTPUT_FORMATS = ["JPG", "PNG", "WEBP", "ICO", "BMP", "TIFF", "GIF"]
VIDEO_OUTPUT_FORMATS = ["MP4", "MKV", "AVI", "MOV", "WEBM", "GIF"]
AUDIO_OUTPUT_FORMATS = ["MP3", "WAV", "AAC", "OGG", "M4A", "FLAC"]
DOCUMENT_OUTPUT_FORMATS = ["PDF", "HTML"]
DATA_OUTPUT_FORMATS = ["JSON", "YAML", "CSV", "XLSX", "XML"]
