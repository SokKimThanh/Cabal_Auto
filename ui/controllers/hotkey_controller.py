from typing import Any, Dict, Callable, Optional, Tuple
import threading
import logging

from lib.events.ui_dispatcher import UIDispatcher

logger = logging.getLogger(__name__)

try:
    import win32gui
    import win32con
    import win32api
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    logger.warning("[Hotkeys] pywin32 not available — global hotkeys disabled")


MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000


def _parse_hotkey(s: str) -> Tuple[int, int]:
    """Convert 'ctrl+shift+r' -> (modifiers, virtual_key_code)."""
    mods = 0
    vk = 0
    for p in s.lower().split("+"):
        p = p.strip()
        if not p:
            continue
        if p in ("ctrl", "control"):
            mods |= MOD_CONTROL
        elif p == "shift":
            mods |= MOD_SHIFT
        elif p in ("alt", "menu"):
            mods |= MOD_ALT
        elif p in ("win", "super", "cmd", "windows"):
            mods |= MOD_WIN
        elif p.startswith("f") and p[1:].isdigit():
            n = int(p[1:])
            if not (1 <= n <= 24):
                raise ValueError(f"Invalid F-key: {p}")
            vk = 0x70 + (n - 1)
        elif p == "space":
            vk = 0x20
        elif p == "tab":
            vk = 0x09
        elif p in ("enter", "return"):
            vk = 0x0D
        elif p in ("esc", "escape"):
            vk = 0x1B
        elif len(p) == 1:
            vk = ord(p.upper())
        else:
            raise ValueError(f"Unknown key: {p}")

    if vk == 0:
        raise ValueError(f"No key found in hotkey: {s}")

    return mods | MOD_NOREPEAT, vk


class HotkeyController:
    """Global hotkey controller using Windows RegisterHotKey API.

    This avoids ctypes callbacks entirely by receiving WM_HOTKEY messages
    through a hidden window on a dedicated thread. Safe with Tkinter on
    all supported Python versions.
    """

    def __init__(self, parent: Any, hunt_cfg: dict = None):
        self.parent = parent
        self._thread: Optional[threading.Thread] = None
        self._thread_id: int = 0
        self._thread_ready = threading.Event()
        self._stop_event = threading.Event()
        self._hwnd = None
        self._hwnd_lock = threading.Lock()
        self._wnd_class = None  # keep reference
        self._hotkey_callbacks: Dict[int, Callable] = {}
        self._hotkey_names: Dict[int, str] = {}
        self._next_id = 1
        self._registered_signature = None
        self._hotkeys_registered_ok = False
        self._failed_hotkeys: Dict[str, str] = {}
        self._registered_hotkey_handlers: Dict[str, int] = {}

    def register_all(self, force: bool = False) -> None:
        if not HAS_WIN32:
            logger.warning("[Hotkeys] pywin32 not available — cannot register global hotkeys")
            self._hotkeys_registered_ok = False
            return

        if hasattr(self.parent, "state_controller"):
            hotkey_cfg = self.parent.state_controller.get_hunt_config_value("global_hotkeys", {})
        else:
            hotkey_cfg = getattr(self.parent, "hunt_cfg", {}).get("global_hotkeys", {})

        try:
            signature = tuple(sorted((k, str(v)) for k, v in hotkey_cfg.items()))
        except Exception:
            signature = None

        if (not force and signature is not None
                and self._registered_signature == signature
                and self._hotkeys_registered_ok):
            return

        if not hotkey_cfg.get("enabled", True):
            logger.info("[Hotkeys] Global hotkeys disabled by user")
            self._hotkeys_registered_ok = False
            return

        self.unregister_all()

        mapping = [
            (hotkey_cfg.get("start_key", "ctrl+shift+r"), self.on_hunt_start),
            (hotkey_cfg.get("stop_key", "ctrl+shift+e"), self.on_hunt_stop),
            (hotkey_cfg.get("library_manager_key", "ctrl+shift+l"), self.on_library_manager),
            (hotkey_cfg.get("vision_wizard_key", "ctrl+shift+v"), self.on_vision_wizard),
            (hotkey_cfg.get("monster_editor_key", "ctrl+shift+m"), self.on_monster_editor),
            (hotkey_cfg.get("build_manager_key", "ctrl+b"), self.on_build_manager),
            (hotkey_cfg.get("add_template_key", "ctrl+shift+t"), self.on_add_template),
        ]

        self._hotkey_callbacks.clear()
        self._hotkey_names.clear()
        self._registered_hotkey_handlers.clear()
        self._failed_hotkeys.clear()
        self._next_id = 1

        for hotkey_str, callback in mapping:
            try:
                # validate parse here to report failures early
                _parse_hotkey(hotkey_str)
                hk_id = self._next_id
                self._next_id += 1
                self._hotkey_callbacks[hk_id] = callback
                self._hotkey_names[hk_id] = hotkey_str
                self._registered_hotkey_handlers[hotkey_str] = hk_id
            except Exception as e:
                self._failed_hotkeys[hotkey_str] = repr(e)
                logger.error(f"[Hotkeys] Parse error for {hotkey_str}: {e}")

        self._stop_event.clear()
        self._thread_ready.clear()
        self._thread = threading.Thread(
            target=self._message_loop_thread,
            name="Win32HotkeyListener",
            daemon=True,
        )
        self._thread.start()

        self._thread_ready.wait(timeout=3.0)

        self._registered_signature = signature
        self._hotkeys_registered_ok = len(self._failed_hotkeys) == 0 and len(self._hotkey_callbacks) > 0

        try:
            if hasattr(self.parent, "after"):
                self.parent.after(150, self.update_diagnostics_ui_state)
        except Exception:
            pass

    def unregister_all(self) -> None:
        self._stop_event.set()
        if self._thread_id:
            try:
                win32api.PostThreadMessage(self._thread_id, win32con.WM_QUIT, 0, 0)
            except Exception:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None
        self._thread_id = 0
        with self._hwnd_lock:
            self._hwnd = None
        self._hotkey_callbacks.clear()
        self._hotkey_names.clear()
        self._registered_hotkey_handlers.clear()
        self._registered_signature = None
        self._hotkeys_registered_ok = False

    def _message_loop_thread(self) -> None:
        """Dedicated thread: create hidden window, register hotkeys, pump messages."""
        self._thread_id = win32api.GetCurrentThreadId()
        wc_name = f"CabalAutoHotkeyWin_{id(self)}"

        try:
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._wnd_proc
            wc.lpszClassName = wc_name
            wc.hInstance = win32api.GetModuleHandle(None)
            self._wnd_class = wc
            try:
                win32gui.RegisterClass(wc)
            except Exception as e:
                logger.debug(f"[Hotkeys] RegisterClass: {e}")

            hwnd = win32gui.CreateWindow(
                wc_name, "CabalAutoHotkey", 0,
                0, 0, 0, 0,
                0, 0, wc.hInstance, None,
            )
            with self._hwnd_lock:
                self._hwnd = hwnd

            # register hotkeys (must be done from this thread)
            failed_ids = []
            for hk_id, hotkey_str in list(self._hotkey_names.items()):
                try:
                    mods, vk = _parse_hotkey(hotkey_str)
                    if win32gui.RegisterHotKey(hwnd, hk_id, mods, vk):
                        logger.info(f"[Hotkeys] Registered: {hotkey_str} (id={hk_id})")
                    else:
                        err = win32api.GetLastError()
                        self._failed_hotkeys[hotkey_str] = f"RegisterHotKey err {err}"
                        failed_ids.append(hk_id)
                        logger.error(f"[Hotkeys] RegisterHotKey failed for {hotkey_str}: err {err}")
                except Exception as e:
                    self._failed_hotkeys[hotkey_str] = repr(e)
                    failed_ids.append(hk_id)
                    logger.error(f"[Hotkeys] Register error for {hotkey_str}: {e}")

            for hk_id in failed_ids:
                self._hotkey_callbacks.pop(hk_id, None)
                self._hotkey_names.pop(hk_id, None)

            self._thread_ready.set()

            # pump messages until WM_QUIT
            try:
                win32gui.PumpMessages()
            except Exception as e:
                logger.error(f"[Hotkeys] PumpMessages error: {e}")

            # cleanup
            for hk_id in list(self._hotkey_names.keys()):
                try:
                    win32gui.UnregisterHotKey(hwnd, hk_id)
                except Exception:
                    pass
            try:
                win32gui.DestroyWindow(hwnd)
            except Exception:
                pass

        except Exception as e:
            logger.error(f"[Hotkeys] Message loop thread crashed: {e}")
            self._thread_ready.set()

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_HOTKEY:
            callback = self._hotkey_callbacks.get(wparam)
            if callback:
                try:
                    UIDispatcher.post(callback)
                except Exception as e:
                    logger.error(f"[Hotkeys] WM_HOTKEY dispatch failed: {e}")
            return 0
        elif msg == win32con.WM_CLOSE:
            win32gui.DestroyWindow(hwnd)
            return 0
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    # ------------------------------------------------------------------
    # Callbacks (giữ nguyên từ bản pynput)
    # ------------------------------------------------------------------

    def on_vision_wizard(self, *_args) -> None:
        def _do():
            if (hasattr(self.parent, "monster_manager_controller")
                    and self.parent.monster_manager_controller):
                self.parent.window_controller.open_vision_wizard()
        UIDispatcher.post(_do)

    def on_monster_editor(self, *_args) -> None:
        def _do():
            if (hasattr(self.parent, "monster_manager_controller")
                    and self.parent.monster_manager_controller):
                self.parent.monster_manager_controller.open_window()
        UIDispatcher.post(_do)

    def on_library_manager(self, *_args) -> None:
        def _do():
            try:
                existing = getattr(self.parent, "library_manager_win", None)
                if existing is not None and getattr(existing, "winfo_exists", lambda: False)():
                    if existing.winfo_viewable():
                        try:
                            existing.withdraw()
                        except Exception:
                            pass
                    else:
                        try:
                            existing.deiconify()
                            existing.lift()
                            existing.focus_force()
                        except Exception:
                            pass
                    return
                if hasattr(self.parent, "library_manager_controller"):
                    self.parent.library_manager_controller.open_library_manager()
            except Exception as e:
                print(f"[Hotkeys] Library Manager error: {e}")
        UIDispatcher.post(_do)

    def on_hunt_start(self, *_args) -> None:
        def _fire():
            app = self.parent
            hc = getattr(app, "hunt_controller", None)
            if hc is None:
                return
            try:
                if app.state_controller.is_bot_running():
                    return
                hc.request_start_hunt()
            except Exception as e:
                print(f"[Hotkeys] on_hunt_start error: {e}")
        UIDispatcher.post(_fire)

    def on_hunt_stop(self, *_args) -> None:
        def _fire():
            app = self.parent
            hc = getattr(app, "hunt_controller", None)
            if hc is None:
                return
            try:
                if not app.state_controller.is_bot_running():
                    return
                hc.request_stop_hunt()
            except Exception as e:
                print(f"[Hotkeys] on_hunt_stop error: {e}")
        UIDispatcher.post(_fire)

    def on_build_manager(self, *_args) -> None:
        def _do():
            if hasattr(self.parent, "switch_view"):
                self.parent.switch_view("build_manager")
        UIDispatcher.post(_do)

    def on_add_template(self, *_args) -> None:
        def _do():
            import os
            from lib.system.window_manager import WindowManager
            from lib.events.event_bus import EventBus, VisionAddTemplateEvent
            wm = WindowManager()
            fg_hwnd = wm.get_foreground_window()
            if fg_hwnd:
                info = wm.get_window_info(fg_hwnd)
                if info:
                    if info.pid == os.getpid():
                        UIDispatcher.post(lambda: EventBus.trigger(VisionAddTemplateEvent()))
                        return
                    target_hwnd = None
                    if hasattr(self.parent, "state_controller"):
                        target_hwnd = self.parent.state_controller.get_hunt_config_value("window_hwnd")
                    if target_hwnd and info.hwnd == target_hwnd:
                        UIDispatcher.post(lambda: EventBus.trigger(VisionAddTemplateEvent()))
                        return
                    return
            UIDispatcher.post(lambda: EventBus.trigger(VisionAddTemplateEvent()))
        UIDispatcher.post(_do)

    def update_diagnostics_ui_state(self) -> None:
        def _do():
            try:
                has_failed = bool(self._failed_hotkeys)
                enabled = self._hotkeys_registered_ok
                lang = getattr(self.parent, "lang", "vi")
                count = len(self._hotkey_callbacks) if enabled else 0
                sc = getattr(self.parent, "state_controller", None)
                if not sc:
                    return
                if enabled and not has_failed:
                    txt = ("All hotkeys registered successfully"
                           if lang == "en" else
                           "Tất cả phím tắt đã đăng ký thành công")
                    sc.set_ui_var('hotkey_status', f"✅ {txt}")
                    detail = (f"{count} hotkeys active"
                              if lang == "en" else
                              f"{count} phím tắt đang hoạt động")
                    sc.set_ui_var('hotkey_status_detail', f"   {detail}")
                elif has_failed:
                    sc.set_ui_var('hotkey_status', f"⚠️ {len(self._failed_hotkeys)} failed")
                else:
                    txt = ("Hotkeys not available"
                           if lang == "en" else
                           "Phím tắt không khả dụng")
                    sc.set_ui_var('hotkey_status', f"❌ {txt}")
            except Exception:
                pass
        UIDispatcher.post(_do)
