import time
import threading
from typing import Protocol, Set

try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

from lib.system.win_input import _vk_from_str, _scancode_from_vk, EXTENDED_KEYS

class InputBackend(Protocol):
    mode: str

    def tap(self, key: str, press_ms: int = 50) -> bool:
        ...

    def key_down(self, key: str) -> bool:
        ...

    def key_up(self, key: str) -> bool:
        ...

    def close(self) -> None:
        ...

class ForegroundSendInputBackend:
    mode: str = "foreground"

    def tap(self, key: str, press_ms: int = 50) -> bool:
        from lib.system.win_input import tap as win_tap
        try:
            win_tap(key, press_ms)
            return True
        except Exception:
            return False

    def key_down(self, key: str) -> bool:
        from lib.system.win_input import key_down as win_key_down
        try:
            win_key_down(key)
            return True
        except Exception:
            return False

    def key_up(self, key: str) -> bool:
        from lib.system.win_input import key_up as win_key_up
        try:
            win_key_up(key)
            return True
        except Exception:
            return False

    def close(self) -> None:
        pass

class BackgroundWindowMessageBackend(InputBackend):
    mode: str = "background"

    def __init__(self, hwnd: int):
        self.hwnd = hwnd
        self._lock = threading.Lock()
        self._held_keys: Set[str] = set()

    def _make_lparam(self, scancode: int, extended: bool, keydown: bool) -> int:
        repeat_count = 1
        lparam = repeat_count
        lparam |= (scancode << 16)

        if extended:
            lparam |= (1 << 24)

        if not keydown:
            lparam |= (1 << 30)

        if not keydown:
            lparam |= (1 << 31)

        return lparam

    def key_down(self, key: str) -> bool:
        if not WIN32_AVAILABLE or not self.hwnd:
            return False

        with self._lock:
            try:
                vk = _vk_from_str(key)
                sc = _scancode_from_vk(vk)
                extended = key.strip().upper() in EXTENDED_KEYS

                lparam = self._make_lparam(sc, extended, keydown=True)

                win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, vk, lparam)
                self._held_keys.add(key)
                return True
            except Exception:
                return False

    def key_up(self, key: str) -> bool:
        if not WIN32_AVAILABLE or not self.hwnd:
            return False

        with self._lock:
            try:
                vk = _vk_from_str(key)
                sc = _scancode_from_vk(vk)
                extended = key.strip().upper() in EXTENDED_KEYS

                lparam = self._make_lparam(sc, extended, keydown=False)

                win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, vk, lparam)
                self._held_keys.discard(key)
                return True
            except Exception:
                return False

    def tap(self, key: str, press_ms: int = 50) -> bool:
        if not WIN32_AVAILABLE or not self.hwnd:
            return False

        if not self.key_down(key):
            return False

        try:
            time.sleep(max(press_ms, 1) / 1000.0)
        finally:
            return self.key_up(key)

    def close(self) -> None:
        if not WIN32_AVAILABLE or not self.hwnd:
            return

        keys_to_release = list(self._held_keys)
        for key in keys_to_release:
            self.key_up(key)
