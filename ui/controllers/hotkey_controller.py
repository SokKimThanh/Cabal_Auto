import os
import hashlib
import json
from typing import Any, Optional, Dict
from lib.events.ui_dispatcher import UIDispatcher

try:
    from pynput import keyboard as pynput_keyboard
except ImportError:
    pynput_keyboard = None


def _to_pynput(hotkey_str: str) -> str:
    """Convert 'ctrl+shift+r' → '<ctrl>+<shift>+r'."""
    parts = []
    for p in hotkey_str.lower().split("+"):
        p = p.strip()
        if p in ("ctrl", "control"):
            parts.append("<ctrl>")
        elif p in ("shift",):
            parts.append("<shift>")
        elif p in ("alt", "menu"):
            parts.append("<alt>")
        elif p in ("win", "super", "cmd"):
            parts.append("<cmd>")
        elif p.startswith("f") and p[1:].isdigit():
            parts.append(f"<{p}>")
        else:
            parts.append(p)
    return "+".join(parts)


class HotkeyController:
    """
    Manages global and local hotkeys for the Cabal Auto application.
    Migrated from `keyboard` to `pynput` for Python 3.13+ thread safety.
    """

    def __init__(self, parent: Any) -> None:
        self.parent = parent

        self._pynput_listener: Optional["pynput_keyboard.GlobalHotKeys"] = None

        self._registered_signature: Optional[str] = None
        self._hotkey_fallback_bound: bool = False

        self._registered_hotkey_handlers: Dict[str, Any] = {}
        self._failed_hotkeys: list[str] = []
        self._hotkeys_registered_ok: bool = False

    def _generate_hotkey_signature(self, hotkeys: dict) -> str:
        """Create a hash signature of the current hotkeys configuration."""
        try:
            hotkey_str = json.dumps(hotkeys, sort_keys=True)
            return hashlib.md5(hotkey_str.encode('utf-8')).hexdigest()
        except Exception:
            return ""

    def register_all(self, force: bool = False) -> None:
        """Register all global hotkeys based on app config using pynput."""
        state_controller = getattr(self.parent, "state_controller", None)
        if not state_controller:
            print("[Hotkeys] Cannot register: state_controller not ready")
            return

        app_config = getattr(state_controller, "app_config", {})
        hotkeys = app_config.get("hotkeys", {})

        signature = self._generate_hotkey_signature(hotkeys)

        if not force and signature == self._registered_signature and self._hotkeys_registered_ok:
            # Idempotent - ignore duplicate calls if config hasn't changed
            return

        print("[Hotkeys] Registering hotkeys via pynput...")

        if pynput_keyboard is None:
            print("[Hotkeys] Warning: 'pynput' module not available.")
            if hasattr(self.parent, "_hotkey_import_diag"):
                self.parent._hotkey_import_diag = True
            self._hotkeys_registered_ok = False
            self.update_diagnostics_ui_state()
            return

        self.unregister_all()

        self._failed_hotkeys = []

        start_key = hotkeys.get("start", "ctrl+shift+r")
        stop_key = hotkeys.get("stop", "ctrl+shift+e")
        library_key = hotkeys.get("library", "ctrl+shift+l")
        vision_key = hotkeys.get("vision", "ctrl+shift+v")
        monster_key = hotkeys.get("monster", "ctrl+shift+m")
        build_key = hotkeys.get("build", "ctrl+b")
        add_template_key = hotkeys.get("add_template", "ctrl+shift+t")

        hotkeys_map = {}

        def safe_add(key_str: str, callback: Any, name: str):
            if not key_str:
                return
            try:
                pynput_str = _to_pynput(key_str)
                hotkeys_map[pynput_str] = callback
            except Exception as e:
                print(f"[Hotkeys] Failed to map '{name}' ({key_str}): {e}")
                self._failed_hotkeys.append(name)

        safe_add(start_key, self.on_hunt_start, "Start")
        safe_add(stop_key, self.on_hunt_stop, "Stop")
        safe_add(library_key, self.on_library_manager, "Library")
        safe_add(vision_key, self.on_vision_wizard, "Vision")
        safe_add(monster_key, self.on_monster_editor, "Monster")
        safe_add(build_key, self.on_build_manager, "Build")
        safe_add(add_template_key, self.on_add_template, "Add Template")

        if hotkeys_map:
            try:
                self._pynput_listener = pynput_keyboard.GlobalHotKeys(hotkeys_map)
                self._pynput_listener.start()
                self._hotkeys_registered_ok = True
                self._registered_signature = signature
                self._registered_hotkey_handlers = dict(hotkeys_map)

                print(f"[Hotkeys] Global hotkeys registered: {len(hotkeys_map)} active")
                if self._failed_hotkeys:
                    print(f"[Hotkeys] Failed to register: {', '.join(self._failed_hotkeys)}")
            except Exception as e:
                print(f"[Hotkeys] Error creating pynput listener: {e}")
                self._hotkeys_registered_ok = False
                self._registered_signature = None
        else:
            self._hotkeys_registered_ok = True
            self._registered_signature = signature
            print("[Hotkeys] No global hotkeys configured.")

        # Schedule UI update
        if hasattr(self.parent, "root") and hasattr(self.parent.root, "after"):
            self.parent.root.after(150, self.update_diagnostics_ui_state)
        else:
            self.update_diagnostics_ui_state()

    def unregister_all(self) -> None:
        """Unregister all global and local hotkeys."""
        print("[Hotkeys] Unregistering all hotkeys...")

        if hasattr(self.parent, "root") and self._hotkey_fallback_bound:
            try:
                root = self.parent.root
                root.unbind_all("<Control-Shift-R>")
                root.unbind_all("<Control-Shift-E>")
                root.unbind_all("<Control-Shift-L>")
                root.unbind_all("<Control-Shift-V>")
                root.unbind_all("<Control-Shift-M>")
                root.unbind_all("<Control-B>")
                root.unbind_all("<Control-b>")
                self._hotkey_fallback_bound = False
            except Exception as e:
                print(f"[Hotkeys] Error unbinding Tkinter fallbacks: {e}")

        if self._pynput_listener is not None:
            try:
                self._pynput_listener.stop()
            except Exception as e:
                print(f"[Hotkeys] Error stopping pynput listener: {e}")
            finally:
                self._pynput_listener = None

        self._registered_hotkey_handlers.clear()
        self._registered_signature = None
        self._hotkeys_registered_ok = False
        print("[Hotkeys] Unregistration complete.")

    def on_vision_wizard(self, *_args) -> None:
        def _do_vision_wizard():
            try:
                print("[Hotkeys] Vision Wizard hotkey pressed")

                # Try opening library manager and letting it handle Vision Wizard
                if hasattr(self.parent, "library_manager_controller"):
                    self.parent.library_manager_controller.open_library_manager()

                    if hasattr(self.parent, "library_manager_win"):
                        existing = self.parent.library_manager_win
                        if existing and getattr(existing, "winfo_exists", lambda: False)():
                            # Deiconify/lift if needed
                            try:
                                if not existing.winfo_viewable():
                                    existing.deiconify()
                                existing.lift()
                                existing.focus_force()
                            except Exception:
                                pass

                            # Delegate to library manager to show Vision Wizard
                            if hasattr(existing, "open_vision_wizard"):
                                existing.open_vision_wizard()
                                return

                print("[Hotkeys] Fallback: Opening Setup Wizard directly")
                if hasattr(self.parent, "window_controller"):
                    self.parent.window_controller.on_setup_wizard(hide_parent=False)
            except Exception as e:
                print(f"[Hotkeys] Error opening Vision Wizard: {e}")

        UIDispatcher.post(_do_vision_wizard)

    def on_monster_editor(self, *_args) -> None:
        def _do_monster_editor():
            try:
                print("[Hotkeys] Monster Editor hotkey pressed")

                # Check for existing standalone monster manager
                existing = getattr(self.parent, "monster_manager_win", None)
                if (
                    existing is not None
                    and getattr(existing, "winfo_exists", lambda: False)()
                ):
                    if existing.winfo_viewable():
                        try:
                            existing.withdraw()
                        except Exception:
                            try:
                                existing.iconify()
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

                # If missing, try opening via Library Manager
                if hasattr(self.parent, "library_manager_controller"):
                    self.parent.library_manager_controller.open_library_manager()
                    if hasattr(self.parent, "library_manager_win"):
                        lib_win = self.parent.library_manager_win
                        if lib_win and getattr(lib_win, "winfo_exists", lambda: False)():
                            # Switch to Monsters tab
                            if hasattr(lib_win, "notebook"):
                                try:
                                    # Find the monster tab
                                    for i, tab_id in enumerate(lib_win.notebook.tabs()):
                                        if "monster" in str(tab_id).lower() or "quái" in str(lib_win.notebook.tab(tab_id, "text")).lower():
                                            lib_win.notebook.select(tab_id)
                                            break
                                except Exception:
                                    pass

                            try:
                                if not lib_win.winfo_viewable():
                                    lib_win.deiconify()
                                lib_win.lift()
                                lib_win.focus_force()
                            except Exception:
                                pass
                            return

            except Exception as e:
                print(f"[Hotkeys] Error handling Monster Editor hotkey: {e}")

        UIDispatcher.post(_do_monster_editor)

    def on_library_manager(self, *_args) -> None:
        def _do_library_manager():
            try:
                print("[Hotkeys] Library Manager hotkey pressed")
                existing = getattr(self.parent, "library_manager_win", None)
                if (
                    existing is not None
                    and getattr(existing, "winfo_exists", lambda: False)()
                ):
                    if existing.winfo_viewable():
                        try:
                            existing.withdraw()
                        except Exception:
                            try:
                                existing.iconify()
                            except Exception:
                                pass
                    else:
                        try:
                            existing.deiconify()
                            existing.lift()
                            existing.focus_force()
                        except Exception:
                            try:
                                existing.lift()
                                existing.focus_force()
                            except Exception:
                                pass
                    return

                if hasattr(self.parent, "library_manager_controller"):
                    self.parent.library_manager_controller.open_library_manager()
            except Exception as e:
                print(f"[Hotkeys] Error opening Library Manager: {e}")

        UIDispatcher.post(_do_library_manager)

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
        def _do_build_manager():
            if hasattr(self.parent, "switch_view"):
                self.parent.switch_view("build_manager")
        UIDispatcher.post(_do_build_manager)

    def on_add_template(self, *_args) -> None:
        def _do_add_template():
            import os
            from lib.system.window_manager import WindowManager
            from lib.events.event_bus import EventBus, VisionAddTemplateEvent

            wm = WindowManager()
            fg_hwnd = wm.get_foreground_window()
            if fg_hwnd:
                info = wm.get_window_info(fg_hwnd)
                if info:
                    app_pid = os.getpid()
                    if info.pid == app_pid:
                        EventBus.trigger(VisionAddTemplateEvent())
                        return

                    # Check if it matches configured cabal window
                    target_hwnd = None
                    if hasattr(self.parent, "state_controller"):
                        target_hwnd = self.parent.state_controller.get_hunt_config_value("window_hwnd")

                    if target_hwnd and info.hwnd == target_hwnd:
                        EventBus.trigger(VisionAddTemplateEvent())
                        return

                    # If neither the bot app nor the target game, ignore the hotkey
                    print(f"[Hotkeys] Add Template blocked: Active window (PID: {info.pid}, HWND: {info.hwnd}) is not the tool or game.")
                    return

            EventBus.trigger(VisionAddTemplateEvent())

        UIDispatcher.post(_do_add_template)

    def update_diagnostics_ui_state(self) -> None:
        """Update the hotkey status UI variables based on registration state."""
        def _do_update():
            try:
                # Determine current state
                has_import_error = (
                    hasattr(self.parent, "_hotkey_import_diag") and self.parent._hotkey_import_diag
                )
                has_failed_hotkeys = bool(self._failed_hotkeys)
                hotkeys_enabled = self._hotkeys_registered_ok

                lang = getattr(self.parent, "lang", "vi")

                registered_count = len(self._registered_hotkey_handlers) if self._hotkeys_registered_ok else 0

                state_controller = getattr(self.parent, "state_controller", None)
                if not state_controller:
                    return

                # State 1: Success - All hotkeys registered
                if hotkeys_enabled and not has_failed_hotkeys and not has_import_error:
                    # Green success state
                    success_text = (
                        "All hotkeys registered successfully"
                        if lang == "en"
                        else "Tất cả phím tắt đã đăng ký thành công"
                    )
                    state_controller.set_ui_var('hotkey_status', f"✅ {success_text}")

                    # Show count
                    detail_text = (
                        f"{registered_count} hotkeys active"
                        if lang == "en"
                        else f"{registered_count} phím tắt đang hoạt động"
                    )
                    state_controller.set_ui_var('hotkey_status_detail', f"   {detail_text}")

                # State 2: Partial failure - Some hotkeys failed
                elif has_failed_hotkeys and not has_import_error:
                    # Orange warning state
                    failed_count = len(self._failed_hotkeys)
                    warning_text = (
                        f"{failed_count} hotkey(s) failed to register"
                        if lang == "en"
                        else f"{failed_count} phím tắt đăng ký thất bại"
                    )
                    state_controller.set_ui_var('hotkey_status', f"{warning_text}")

                    # Show guidance
                    guidance = (
                        "Try changing the conflicting hotkey, then click Apply."
                        if lang == "en"
                        else "Thử đổi phím tắt bị xung đột, sau đó nhấn Áp dụng."
                    )
                    state_controller.set_ui_var('hotkey_status_detail', f"   {guidance}")

                # State 3: Complete failure - Import error or no hotkeys registered
                else:
                    # Red error state
                    error_text = (
                        "Hotkeys not available"
                        if lang == "en"
                        else "Phím tắt không khả dụng"
                    )
                    state_controller.set_ui_var('hotkey_status', f"❌ {error_text}")

                    # Show explanation
                    if has_import_error:
                        explanation = (
                            "The 'pynput' package is not installed in your Python environment."
                            if lang == "en"
                            else "Gói 'pynput' chưa được cài đặt trong Python của bạn."
                        )
                    else:
                        explanation = (
                            "Failed to register global hotkeys."
                            if lang == "en"
                            else "Không thể đăng ký phím tắt toàn cục."
                        )
                    state_controller.set_ui_var('hotkey_status_detail', f"   {explanation}")

            except Exception as e:
                # Fallback: show basic error
                try:
                    state_controller = getattr(self.parent, "state_controller", None)
                    if state_controller:
                        state_controller.set_ui_var('hotkey_status', f"Error updating status: {e}")
                except Exception:
                    pass

        UIDispatcher.post(_do_update)
