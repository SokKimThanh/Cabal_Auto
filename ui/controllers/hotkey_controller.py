from typing import Any

try:
    import keyboard
except ImportError:
    keyboard = None


class HotkeyController:
    """Controller for global hotkey management."""

    def __init__(self, parent: Any, hunt_cfg: dict = None):
        self.parent = parent
        # Removed cached hunt_cfg

        # Track registered handlers for proper cleanup
        self._global_start_hotkey = None
        self._global_stop_hotkey = None
        self._global_library_hotkey = None
        self._global_vision_hotkey = None
        self._global_monster_hotkey = None
        self._global_build_hotkey = None

        # Track fallback tkinter bindings
        self._hotkey_fallback_bound = []

        # Track registration status
        self._registered_hotkey_handlers = {}
        self._failed_hotkeys = {}
        self._hotkeys_registered_ok = False

    def register_all(self) -> None:
        """Registers all global hotkeys from config. Fallbacks to Tkinter bindings if keyboard module missing."""
        if hasattr(self.parent, "state_controller") and hasattr(self.parent.state_controller, "hunt_cfg"):
            hotkey_cfg = self.parent.state_controller.get_hunt_config_value("global_hotkeys", {})
        else:
            hotkey_cfg = getattr(self.parent, "hunt_cfg", {}).get("global_hotkeys", {})

        if not hotkey_cfg.get("enabled", True):
            print("[Hotkeys] Global hotkeys disabled by user")
            self._hotkeys_registered_ok = False
            return

        self._registered_hotkey_handlers = {}
        self._failed_hotkeys = {}
        self._hotkeys_registered_ok = False

        try:
            if keyboard is None:
                print(
                    "[Hotkeys] Warning: 'keyboard' module not available. "
                    "Global background hotkeys will not work. Using focused-only fallback."
                )

                # Fallback: Bind to Tkinter root window directly
                # Convert hotkey strings like 'ctrl+shift+r' to Tkinter format '<Control-Shift-R>'
                def _to_tk_seq(h):
                    parts = h.lower().split("+")
                    tk_parts = []
                    for p in parts:
                        p = p.strip()
                        if p in ("ctrl", "control"):
                            tk_parts.append("Control")
                        elif p in ("shift",):
                            tk_parts.append("Shift")
                        elif p in ("alt", "menu"):
                            tk_parts.append("Alt")
                        elif len(p) == 1:
                            tk_parts.append(p.upper())
                        elif p.startswith("f") and p[1:].isdigit():
                            tk_parts.append(p.upper())
                        else:
                            tk_parts.append(p)
                    return f"<{'-'.join(tk_parts)}>"

                seq_start = _to_tk_seq(hotkey_cfg.get("start_key", "ctrl+shift+r"))
                seq_stop = _to_tk_seq(hotkey_cfg.get("stop_key", "ctrl+shift+e"))
                seq_lib = _to_tk_seq(
                    hotkey_cfg.get("library_manager_key", "ctrl+shift+l")
                )
                seq_vision = _to_tk_seq(
                    hotkey_cfg.get("vision_wizard_key", "ctrl+shift+v")
                )

                try:
                    # Unbind any previously-bound fallback sequences to avoid duplicates
                    for s in list(self._hotkey_fallback_bound):
                        try:
                            self.parent.unbind_all(s)
                        except Exception:
                            pass
                    self._hotkey_fallback_bound = []

                    # Bind to all widgets (works when app is focused)
                    self.parent.bind_all(
                        seq_start,
                        lambda e: self.on_hunt_start(),
                        add="+",
                    )
                    self._hotkey_fallback_bound.append(seq_start)
                    self.parent.bind_all(
                        seq_stop,
                        lambda e: self.on_hunt_stop(),
                        add="+",
                    )
                    self._hotkey_fallback_bound.append(seq_stop)
                    self.parent.bind_all(
                        seq_lib,
                        lambda e: self.on_library_manager(),
                        add="+",
                    )
                    self._hotkey_fallback_bound.append(seq_lib)
                    # Sprint 22: Vision Wizard fallback
                    self.parent.bind_all(
                        seq_vision,
                        lambda e: self.on_vision_wizard(),
                        add="+",
                    )
                    self._hotkey_fallback_bound.append(seq_vision)
                    print(
                        f"[Hotkeys] Fallback (focused) hotkeys bound: {', '.join(self._hotkey_fallback_bound)}"
                    )
                    try:
                        self.update_diagnostics_ui_state()
                    except Exception:
                        pass
                except Exception as _bind_e:
                    print(
                        f"[Hotkeys] Failed to bind fallback focused hotkeys: {_bind_e}"
                    )

                return

            # Get hotkey config
            start_key = hotkey_cfg.get("start_key", "ctrl+shift+r")
            stop_key = hotkey_cfg.get("stop_key", "ctrl+shift+e")
            library_key = hotkey_cfg.get("library_manager_key", "ctrl+shift+l")
            vision_key = hotkey_cfg.get("vision_wizard_key", "ctrl+shift+v")
            monster_key = hotkey_cfg.get("monster_editor_key", "ctrl+shift+m")
            build_key = hotkey_cfg.get("build_manager_key", "ctrl+b")
            add_template_key = hotkey_cfg.get("add_template_key", "ctrl+shift+t")

            # Unregister old hotkeys first (in case of re-registration)
            self.unregister_all()

            # Register new hotkeys
            try:
                self._global_start_hotkey = keyboard.add_hotkey(
                    start_key,
                    self.on_hunt_start,
                    suppress=False,
                )
                self._registered_hotkey_handlers[start_key] = self._global_start_hotkey
            except Exception as e:
                print(f"Failed to register start hotkey '{start_key}': {e}")
                self._failed_hotkeys[start_key] = repr(e)
                self._global_start_hotkey = None

            try:
                self._global_stop_hotkey = keyboard.add_hotkey(
                    stop_key, self.on_hunt_stop, suppress=False
                )
                self._registered_hotkey_handlers[stop_key] = self._global_stop_hotkey
            except Exception as e:
                print(f"Failed to register stop hotkey '{stop_key}': {e}")
                self._failed_hotkeys[stop_key] = repr(e)
                self._global_stop_hotkey = None

            try:
                self._global_library_hotkey = keyboard.add_hotkey(
                    library_key,
                    self.on_library_manager,
                    suppress=False,
                )
                self._registered_hotkey_handlers[library_key] = (
                    self._global_library_hotkey
                )
            except Exception as e:
                print(f"Failed to register library hotkey '{library_key}': {e}")
                self._failed_hotkeys[library_key] = repr(e)
                self._global_library_hotkey = None

            try:
                self._global_vision_hotkey = keyboard.add_hotkey(
                    vision_key,
                    self.on_vision_wizard,
                    suppress=False,
                )
                self._registered_hotkey_handlers[vision_key] = (
                    self._global_vision_hotkey
                )
            except Exception as e:
                print(f"Failed to register vision hotkey '{vision_key}': {e}")
                self._failed_hotkeys[vision_key] = repr(e)
                self._global_vision_hotkey = None

            try:
                self._global_monster_hotkey = keyboard.add_hotkey(
                    monster_key,
                    self.on_monster_editor,
                    suppress=False,
                )
                self._registered_hotkey_handlers[monster_key] = (
                    self._global_monster_hotkey
                )
            except Exception as e:
                print(f"Failed to register monster editor hotkey '{monster_key}': {e}")
                self._failed_hotkeys[monster_key] = repr(e)
                self._global_monster_hotkey = None

            try:
                self._global_build_hotkey = keyboard.add_hotkey(
                    build_key,
                    self.on_build_manager,
                    suppress=False,
                )
                self._registered_hotkey_handlers[build_key] = (
                    self._global_build_hotkey
                )
            except Exception as e:
                print(f"Failed to register build manager hotkey '{build_key}': {e}")
                self._failed_hotkeys[build_key] = repr(e)
                self._global_build_hotkey = None

            try:
                self._global_add_template_hotkey = keyboard.add_hotkey(
                    add_template_key,
                    self.on_add_template,
                    suppress=False,
                )
                self._registered_hotkey_handlers[add_template_key] = (
                    self._global_add_template_hotkey
                )
            except Exception as e:
                print(f"Failed to register add template hotkey '{add_template_key}': {e}")
                self._failed_hotkeys[add_template_key] = repr(e)
                self._global_add_template_hotkey = None

            self._hotkeys_registered_ok = len(self._failed_hotkeys) == 0

            # Log successful registration
            registered = []
            if self._global_start_hotkey:
                registered.append(f"Start={start_key}")
            if self._global_stop_hotkey:
                registered.append(f"Stop={stop_key}")
            if self._global_library_hotkey:
                registered.append(f"Library={library_key}")
            if self._global_vision_hotkey:
                registered.append(f"Vision={vision_key}")
            if self._global_monster_hotkey:
                registered.append(f"Monster={monster_key}")
            if self._global_build_hotkey:
                registered.append(f"Build={build_key}")

            if registered:
                print(f"Global hotkeys registered: {', '.join(registered)}")

            if not self._hotkeys_registered_ok:
                print(f"Some hotkeys failed to register: {self._failed_hotkeys}")

            # Update UI
            try:
                if hasattr(self.parent, "after"):
                    self.parent.after(150, self.update_diagnostics_ui_state)
                else:
                    self.update_diagnostics_ui_state()
            except Exception:
                pass

        except Exception as e:
            print(f"Error registering global hotkeys: {e}")
            self._hotkeys_registered_ok = False
            # Update UI to show error state
            try:
                if hasattr(self.parent, "after"):
                    self.parent.after(150, self.update_diagnostics_ui_state)
                else:
                    self.update_diagnostics_ui_state()
            except Exception:
                pass

    def unregister_all(self) -> None:
        """Unregister global hotkeys to clean up resources."""
        try:
            if hasattr(self.parent, "unbind_all"):
                for seq in list(self._hotkey_fallback_bound):
                    try:
                        self.parent.unbind_all(seq)
                    except Exception:
                        pass
            self._hotkey_fallback_bound = []
            self._registered_hotkey_handlers = {}

            if keyboard is None:
                return

            if self._global_start_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_start_hotkey)
                except Exception as e:
                    print(f"Error unregistering start hotkey: {e}")
                finally:
                    self._global_start_hotkey = None

            if self._global_stop_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_stop_hotkey)
                except Exception as e:
                    print(f"Error unregistering stop hotkey: {e}")
                finally:
                    self._global_stop_hotkey = None

            if self._global_library_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_library_hotkey)
                except Exception as e:
                    print(f"Error unregistering library hotkey: {e}")
                finally:
                    self._global_library_hotkey = None

            if self._global_vision_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_vision_hotkey)
                except Exception as e:
                    print(f"Error unregistering vision hotkey: {e}")
                finally:
                    self._global_vision_hotkey = None

            if self._global_monster_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_monster_hotkey)
                except Exception as e:
                    print(f"Error unregistering monster hotkey: {e}")
                finally:
                    self._global_monster_hotkey = None

            if self._global_build_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_build_hotkey)
                except Exception as e:
                    print(f"Error unregistering build hotkey: {e}")
                finally:
                    self._global_build_hotkey = None
        except Exception as e:
            print(f"Error in unregister_all: {e}")
            try:
                if hasattr(self.parent, "_hotkey_diag_var"):
                    self.parent._hotkey_diag_var.set(str(e))
            except Exception:
                pass

    def on_vision_wizard(self, *_args) -> None:
        if (
            hasattr(self.parent, "monster_manager_controller")
            and self.parent.monster_manager_controller
        ):
            if hasattr(self.parent, "after"):
                self.parent.after(0, self.parent.window_controller.open_vision_wizard)
            else:
                self.parent.window_controller.open_vision_wizard()

    def on_monster_editor(self, *_args) -> None:
        if (
            hasattr(self.parent, "monster_manager_controller")
            and self.parent.monster_manager_controller
        ):
            if hasattr(self.parent, "after"):
                self.parent.after(0, self.parent.monster_manager_controller.open_window)
            else:
                self.parent.monster_manager_controller.open_window()

    def on_setup_wizard(self, *_args) -> None:
        try:
            print("[Hotkeys] Setup Wizard hotkey pressed")
            if hasattr(self.parent, "state_controller") and hasattr(self.parent.state_controller, "hunt_cfg"):
                current_mode = self.parent.state_controller.get_hunt_config_value("ui_mode", "beginner")
            else:
                current_mode = getattr(self.parent, "hunt_cfg", {}).get("ui_mode", "beginner")

            if current_mode != "beginner":
                print(f"[Hotkeys] Setup Wizard blocked - current mode: {current_mode}")
                return

            existing = (
                getattr(self.parent, "_setup_wizard_win", None)
                or getattr(self.parent, "setup_wizard_win", None)
                or getattr(self.parent, "_setup_wizard", None)
            )
            try:
                if (
                    existing is not None
                    and getattr(existing, "winfo_exists", lambda: False)()
                ):
                    win = getattr(existing, "dialog", existing)
                    if win.winfo_viewable():
                        try:
                            win.withdraw()
                        except Exception:
                            try:
                                win.iconify()
                            except Exception:
                                pass
                    else:
                        try:
                            win.deiconify()
                            win.lift()
                            win.focus_force()
                            try:
                                win.attributes("-topmost", True)
                                if hasattr(win, "after"):
                                    win.after(
                                        120, lambda: win.attributes("-topmost", False)
                                    )
                            except Exception:
                                pass
                        except Exception:
                            try:
                                win.lift()
                                win.focus_force()
                            except Exception:
                                pass
                    return
            except Exception:
                pass

            print("[Hotkeys] Opening Setup Wizard directly from hotkey")
            if hasattr(self.parent, "after") and hasattr(
                self.parent, "window_controller"
            ):
                self.parent.after(
                    0,
                    lambda: self.parent.window_controller.on_setup_wizard(
                        hide_parent=False
                    ),
                )
        except Exception as e:
            print(f"[Hotkeys] Error opening Setup Wizard: {e}")

    def on_library_manager(self, *_args) -> None:
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

            if hasattr(self.parent, "after") and hasattr(
                self.parent, "library_manager_controller"
            ):
                self.parent.after(
                    0, self.parent.library_manager_controller.open_library_manager
                )
        except Exception as e:
            print(f"[Hotkeys] Error opening Library Manager: {e}")

    def on_hunt_start(self, *_args) -> None:
        if hasattr(self.parent, "on_hunt_start"):
            if hasattr(self.parent, "after"):
                self.parent.after(0, self.parent.on_hunt_start)
            else:
                self.parent.on_hunt_start()

    def on_hunt_stop(self, *_args) -> None:
        if hasattr(self.parent, "on_hunt_stop"):
            if hasattr(self.parent, "after"):
                self.parent.after(0, self.parent.on_hunt_stop)
            else:
                self.parent.on_hunt_stop()


    def on_build_manager(self, *_args) -> None:
        if hasattr(self.parent, "switch_view"):
            if hasattr(self.parent, "after"):
                self.parent.after(0, lambda: self.parent.switch_view("build_manager"))
            else:
                self.parent.switch_view("build_manager")

    def on_add_template(self, *_args) -> None:
        import os
        from lib.system.window_manager import WindowManager
        from lib.events.event_bus import EventBus, VisionAddTemplateEvent

        wm = WindowManager()
        fg_hwnd = wm.get_foreground_window()
        if fg_hwnd:
            info = wm.get_window_info(fg_hwnd)
            if info:
                app_pid = os.getpid()
                # DO NOT capture if the foreground window is the bot's own UI
                if info.pid == app_pid:
                    print(f"[Hotkeys] Add Template blocked: Active window is the bot tool (PID: {info.pid}).")
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

        # Fallback if window info couldn't be retrieved
        EventBus.trigger(VisionAddTemplateEvent())

    def update_diagnostics_ui_state(self) -> None:
        """Update the hotkey status UI variables based on registration state."""
        try:
            # Determine current state
            has_import_error = (
                hasattr(self.parent, "_hotkey_import_diag") and self.parent._hotkey_import_diag
            )
            has_failed_hotkeys = bool(self._failed_hotkeys)
            hotkeys_enabled = self._hotkeys_registered_ok

            lang = getattr(self.parent, "lang", "vi")

            # Count actual registered hotkeys (not bindings)
            registered_count = 0
            hotkey_details = []

            if self._global_start_hotkey is not None:
                registered_count += 1
                hotkey_details.append("Start" if lang == "en" else "Bắt đầu")
            if self._global_stop_hotkey is not None:
                registered_count += 1
                hotkey_details.append("Stop" if lang == "en" else "Dừng")
            if self._global_library_hotkey is not None:
                registered_count += 1
                hotkey_details.append("Library" if lang == "en" else "Thư viện")
            if self._global_vision_hotkey is not None:
                registered_count += 1
                hotkey_details.append("Vision" if lang == "en" else "Thị giác")

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

                # Show count and active hotkeys list
                detail_text = (
                    f"{registered_count} hotkeys active"
                    if lang == "en"
                    else f"{registered_count} phím tắt đang hoạt động"
                )
                if hotkey_details:
                    detail_text += f": {', '.join(hotkey_details)}"
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
                        "The 'keyboard' package is not installed in your Python environment."
                        if lang == "en"
                        else "Gói 'keyboard' chưa được cài đặt trong Python của bạn."
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
