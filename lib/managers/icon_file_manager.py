import os
import shutil
from pathlib import Path
from typing import Optional
import sys


def get_icons_directory() -> Path:
    """Get the target directory for icon files."""
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).parent
    else:
        # Assuming lib/managers/icon_file_manager.py
        base_dir = Path(__file__).resolve().parents[2]

    icons_dir = base_dir / "assets" / "images" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    return icons_dir


def import_icon_file(source_path: str, target_filename: Optional[str] = None) -> str:
    """
    Import an icon file by copying it to the assets/images/icons/ directory.

    Args:
        source_path: The source file path.
        target_filename: Optional new filename. If None, uses the original filename.

    Returns:
        The new filename.

    Raises:
        FileNotFoundError: If the source file does not exist.
        ValueError: If source_path is empty.
    """
    if not source_path:
        raise ValueError("source_path must not be empty.")

    source_p = Path(source_path)
    if not source_p.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    if target_filename is None:
        target_filename = source_p.name

    icons_dir = get_icons_directory()
    target_path = icons_dir / target_filename

    shutil.copy2(source_path, target_path)

    return target_filename


def delete_icon_file(filename: str) -> bool:
    """
    Delete an icon file from the assets/images/icons/ directory.

    Args:
        filename: The name of the file to delete.

    Returns:
        True if the file was deleted, False if it did not exist.
    """
    if not filename:
        return False

    icons_dir = get_icons_directory()
    target_path = icons_dir / filename

    if target_path.exists():
        try:
            os.remove(target_path)
            return True
        except OSError:
            # Handle cases where file might be in use or permissions are insufficient
            return False

    return False
