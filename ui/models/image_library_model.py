import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable
import threading
from PIL import Image

from lib.managers.icon_file_manager import get_icons_directory

class ImageLibraryModel:
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
    SUPPORTED_EXTENSIONS = {'.png', '.ico'}

    def __init__(self):
        self._image_list_cache: List[str] = []
        self._lock = threading.Lock()
        self._is_scanning = False

    def get_cached_list(self) -> List[str]:
        with self._lock:
            return list(self._image_list_cache)

    def scan_async(self, callback: Callable[[List[str], Optional[str]], None]):
        """Scan directory in background to prevent UI freeze."""
        if self._is_scanning:
            return

        def _scan_thread():
            self._is_scanning = True
            error_msg = None
            new_list = []
            try:
                icons_dir = get_icons_directory()
                if not icons_dir.exists():
                    error_msg = f"Directory not found: {icons_dir}"
                else:
                    for entry in icons_dir.iterdir():
                        if entry.is_file() and entry.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                            new_list.append(entry.name)
                    new_list.sort(key=str.lower)
                    with self._lock:
                        self._image_list_cache = new_list
            except PermissionError:
                error_msg = "Permission denied when reading icon directory."
            except Exception as e:
                error_msg = f"Error scanning directory: {str(e)}"
            finally:
                self._is_scanning = False
                callback(new_list, error_msg)

        threading.Thread(target=_scan_thread, daemon=True).start()

    def search(self, query: str) -> List[str]:
        """Case-insensitive search in cached list."""
        if not query:
            return self.get_cached_list()

        query = query.lower()
        with self._lock:
            return [name for name in self._image_list_cache if query in name.lower()]

    def validate_file(self, filepath: str) -> Tuple[bool, str]:
        """Validate file existence, extension, size, and real image integrity."""
        path = Path(filepath)
        if not path.exists():
            return False, "File không tồn tại hoặc đã bị xoá."

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return False, "Chỉ hỗ trợ file .png và .ico."

        try:
            if path.stat().st_size > self.MAX_FILE_SIZE_BYTES:
                return False, "File ảnh quá lớn (vượt quá 10MB)."
        except OSError:
            return False, "Không thể đọc thông tin file."

        # Validate real image
        try:
            with Image.open(path) as img:
                img.verify()
        except Exception:
            return False, "File ảnh bị lỗi hoặc không đúng định dạng."

        return True, ""

    def sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from filename."""
        # Replace invalid chars with underscore
        clean_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return clean_name

    def check_name_collision(self, original_filename: str) -> bool:
        """Return True if filename already exists in assets directory."""
        clean_name = self.sanitize_filename(original_filename)
        icons_dir = get_icons_directory()
        return (icons_dir / clean_name).exists()

    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename like name_1.png if name.png exists."""
        clean_name = self.sanitize_filename(original_filename)
        path = Path(clean_name)
        stem = path.stem
        ext = path.suffix

        icons_dir = get_icons_directory()
        counter = 1
        new_name = clean_name
        while (icons_dir / new_name).exists():
            new_name = f"{stem}_{counter}{ext}"
            counter += 1
        return new_name

    def import_image(self, source_path: str, target_filename: str, overwrite: bool = False) -> Tuple[bool, Optional[str], str]:
        """
        Copy file to assets directory.
        Returns: (success, final_filename_if_success, error_message)
        """
        is_valid, msg = self.validate_file(source_path)
        if not is_valid:
            return False, None, msg

        source_p = Path(source_path)
        icons_dir = get_icons_directory()
        target_path = icons_dir / target_filename

        # Prevent self-copying
        try:
            if target_path.exists() and os.path.normcase(os.path.abspath(str(source_p.resolve()))) == os.path.normcase(os.path.abspath(str(target_path.resolve()))):
                return True, target_filename, ""
        except Exception:
            pass # Ignore resolution errors, just proceed

        try:
            shutil.copy2(source_path, target_path)


            # Invalidate cache so next search/scan sees it
            with self._lock:
                if target_filename not in self._image_list_cache:
                    self._image_list_cache.append(target_filename)
                    self._image_list_cache.sort(key=str.lower)

            return True, target_filename, ""

        except PermissionError:
            return False, None, "Không có quyền ghi vào thư mục assets."
        except OSError as e:
            if e.errno == 28: # ENOSPC
                return False, None, "Ổ đĩa đầy, không thể copy file."
            return False, None, f"Lỗi hệ thống khi copy file: {str(e)}"
        except Exception as e:
            return False, None, f"Lỗi không xác định khi import: {str(e)}"

    def remove_file(self, filename: str) -> bool:
        """Used for rollback if DB update fails."""
        try:
            icons_dir = get_icons_directory()
            target_path = icons_dir / filename
            if target_path.exists():
                os.remove(target_path)
                with self._lock:
                    if filename in self._image_list_cache:
                        self._image_list_cache.remove(filename)
                return True
        except Exception:
            pass
        return False
