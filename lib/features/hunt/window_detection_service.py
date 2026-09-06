import ctypes
import ctypes.wintypes as wintypes
import logging
import sys
from typing import Any, Dict, List, Optional

try:
    import psutil  # type: ignore
except ImportError:
    psutil = None  # type: ignore

from lib.features.hunt.config_validator import normalize_window_bounds_value
from lib.system.window_manager import WindowManager

logger = logging.getLogger(__name__)


class WindowDetectionService:
    """Centralized window detection for Cabal game."""

    def __init__(self):
        """Initialize with WindowManager."""
        self.wm = WindowManager()

    def find_all_cabal_windows(self, filter_text: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find all Cabal windows with optional text filtering.

        Returns:
            List of dicts with keys: hwnd, pid, title, proc, bounds, is_minimized
        """
        windows = self.enumerate_windows_raw()
        results = []
        allowed_processes = ["cabal.exe", "cabalmain.exe"]

        for win in windows:
            info = self.wm.get_window_info(win["hwnd"])
            if not info:
                continue

            if (info.process_name or "").lower() not in allowed_processes:
                continue

            win["proc"] = info.process_name
            win["bounds"] = normalize_window_bounds_value(info.rect)
            win["is_minimized"] = info.is_minimized
            results.append(win)

        if filter_text:
            results = self.filter_windows(results, filter_text)

        results.sort(
            key=lambda item: (
                "cabal" not in item["title"].lower(),
                item["title"].lower(),
                item["pid"],
            )
        )
        return results

    def find_best_cabal_window(self, prefer_current_hwnd: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Auto-detect best Cabal window.

        Priority:
        1. Currently selected window (if still valid)
        2. First window with "Cabal" in title
        3. First cabal.exe process window

        Returns:
            Window dict or None
        """
        windows = self.find_all_cabal_windows()
        if not windows:
            return None

        if prefer_current_hwnd:
            for w in windows:
                if w["hwnd"] == prefer_current_hwnd:
                    return w

        for w in windows:
            if "cabal" in w["title"].lower():
                return w

        return windows[0] if windows else None

    def enumerate_windows_raw(self) -> List[Dict[str, Any]]:
        """Low-level window enumeration using WinAPI."""
        if sys.platform != "win32":
            return []

        try:
            user32 = ctypes.windll.user32
            EnumWindowsProc = ctypes.WINFUNCTYPE(
                ctypes.c_bool, wintypes.HWND, wintypes.LPARAM
            )
            IsWindowVisible = user32.IsWindowVisible
            GetWindowTextW = user32.GetWindowTextW
            GetWindowTextLengthW = user32.GetWindowTextLengthW
            GetWindowThreadProcessId = user32.GetWindowThreadProcessId
            EnumWindows = user32.EnumWindows

            results = []

            def callback(hwnd, lParam):
                try:
                    if not IsWindowVisible(hwnd) and not user32.IsIconic(hwnd):
                        return True
                    length = GetWindowTextLengthW(hwnd)
                    if length == 0:
                        return True
                    buf = ctypes.create_unicode_buffer(length + 1)
                    GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value.strip()
                    if not title:
                        return True

                    pid = wintypes.DWORD()
                    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    pid_val = int(pid.value)

                    proc_name = None
                    try:
                        if psutil:
                            p = psutil.Process(pid_val)
                            proc_name = p.name()
                    except Exception:
                        proc_name = None

                    results.append(
                        {
                            "hwnd": int(hwnd),
                            "pid": pid_val,
                            "title": title,
                            "proc": proc_name,
                        }
                    )
                except Exception:
                    pass
                return True

            try:
                EnumWindows(EnumWindowsProc(callback), 0)
            except Exception as e:
                logger.error(f"Error enumerating windows: {e}")

            return results
        except Exception as e:
            logger.error(f"Error in enumerate_windows_raw: {e}")
            return []

    def filter_windows(self, windows: List[Dict[str, Any]], filter_text: Optional[str]) -> List[Dict[str, Any]]:
        """Filter windows by title/process name."""
        if not filter_text:
            return windows

        filter_text = filter_text.lower()
        return [
            w for w in windows
            if filter_text in w["title"].lower() or (w["proc"] and filter_text in w["proc"].lower())
        ]

    def get_window_bounds(self, hwnd: int) -> Optional[Dict[str, int]]:
        """Get window rectangle and state."""
        info = self.wm.get_window_info(hwnd)
        if info and not info.is_minimized and not info.is_offscreen:
            return info.rect
        return None

    def restore_window_if_minimized(self, hwnd: int) -> bool:
        """Try to restore minimized window."""
        info = self.wm.get_window_info(hwnd)
        if info and (info.is_minimized or info.is_offscreen):
            self.wm.restore(hwnd)
            try:
                import win32gui
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                pass
            new_info = self.wm.get_window_info(hwnd)
            return bool(new_info and not new_info.is_minimized and not new_info.is_offscreen)
        return True
