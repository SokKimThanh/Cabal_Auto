"""
Image Handler module for image loading, previewing, and PhotoImage RAM management.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# Project Root Directory
ROOT_DIR = Path(__file__).resolve().parent.parent

try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageTk = None
    ImageDraw = None
    PIL_AVAILABLE = False

class ImageHandler:
    """Handles image loading, thumbnail generation, and PhotoImage caching with memory controls."""

    def __init__(self, max_cache_size: int = 50):
        self._cache: Dict[str, Any] = {}
        self.max_cache_size = max_cache_size

    def get_preview_image(self, path_str: str, size: Tuple[int, int] = (96, 96)) -> Tuple[Optional[Any], Optional[str]]:
        """
        Load and return a PhotoImage preview for Tkinter with placeholder fallback.
        Returns tuple of (PhotoImage or None, error_message or None).
        """
        if not path_str or not path_str.strip():
            return None, "No path provided"

        raw_path = Path(path_str.strip())
        if not raw_path.is_absolute():
            abs_path = (ROOT_DIR / raw_path).resolve()
        else:
            abs_path = raw_path.resolve()

        cache_key = f"{abs_path}_{size[0]}x{size[1]}"
        if cache_key in self._cache:
            return self._cache[cache_key], None

        if not PIL_AVAILABLE:
            return None, "PIL library not installed"

        if not abs_path.exists():
            placeholder = self._create_placeholder(size, "File Missing")
            return placeholder, f"File not found: {abs_path.name}"

        try:
            with Image.open(abs_path) as img:
                img.thumbnail(size)
                photo = ImageTk.PhotoImage(img)

            if len(self._cache) >= self.max_cache_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

            self._cache[cache_key] = photo
            return photo, None
        except Exception as e:
            placeholder = self._create_placeholder(size, "Error")
            return placeholder, f"Failed to read image: {e}"

    def _create_placeholder(self, size: Tuple[int, int], text: str) -> Optional[Any]:
        """Generate a placeholder image when loading fails."""
        if not PIL_AVAILABLE:
            return None
        try:
            img = Image.new("RGB", size, color=(220, 220, 220))
            if ImageDraw:
                draw = ImageDraw.Draw(img)
                draw.rectangle([(0, 0), (size[0] - 1, size[1] - 1)], outline=(180, 180, 180))
                if text:
                    draw.text((4, max(0, size[1] // 2 - 6)), text, fill=(120, 120, 120))
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def clear_cache(self) -> None:
        """Clear cached PhotoImage objects to release memory."""
        self._cache.clear()
