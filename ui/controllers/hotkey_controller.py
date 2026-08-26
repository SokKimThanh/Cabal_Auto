from typing import Any, Optional

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
        self._global_wizard_hotkey = None
        self._global_library_hotkey = None
        self._global_vision_hotkey = None
        self._global_monster_hotkey = None

        # Track fallback tkinter bindings
        self._hotkey_fallback_bound = []

        # Track registration status
        self._registered_hotkey_handlers = {}
        self._failed_hotkeys = {}
        self._hotkeys_registered_ok = False

    def register_all(self) -> None:
        """Registers all global hotkeys from config. Fallbacks to Tkinter bindings if keyboard module missing."""
        hotkey_cfg = self.parent.hunt_cfg.get("global_hotkeys", {})
        if not hotkey_cfg.get("enabled", True):
            print("[Hotkeys] Global hotkeys disabled by user")
            self.unregister_all()
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
                seq_wiz = _to_tk_seq(hotkey_cfg.get("setup_wizard_key", "ctrl+shift+n"))
                seq_lib = _to_tk_seq(hotkey_cfg.get("library_manager_key", "ctrl+shift+l"))
                seq_vision = _to_tk_seq(hotkey_cfg.get("vision_wizard_key", "ctrl+shift+v"))

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
                    # Wizard only meaningful in beginner mode
                    if self.parent.hunt_cfg.get("ui_mode", "beginner") == "beginner":
                        self.parent.bind_all(
                            seq_wiz,
                            lambda e: self.on_setup_wizard(),
                            add="+",
                        )
                        self._hotkey_fallback_bound.append(seq_wiz)
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
                        if hasattr(self.parent, "_update_hotkey_diagnostics_ui"):
                            self.parent._update_hotkey_diagnostics_ui()
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
            wizard_key = hotkey_cfg.get("setup_wizard_key", "ctrl+shift+n")
            library_key = hotkey_cfg.get("library_manager_key", "ctrl+shift+l")
            vision_key = hotkey_cfg.get("vision_wizard_key", "ctrl+shift+v")
            monster_key = hotkey_cfg.get("monster_editor_key", "ctrl+shift+m")

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

            current_mode = self.parent.hunt_cfg.get("ui_mode", "beginner")
            if current_mode == "beginner":
                try:
                    self._global_wizard_hotkey = keyboard.add_hotkey(
                        wizard_key,
                        self.on_setup_wizard,
                        suppress=False,
                    )
                    self._registered_hotkey_handlers[wizard_key] = self._global_wizard_hotkey
                except Exception as e:
                    print(f"Failed to register wizard hotkey '{wizard_key}': {e}")
                    self._failed_hotkeys[wizard_key] = repr(e)
                    self._global_wizard_hotkey = None
            else:
                self._global_wizard_hotkey = None

            try:
                self._global_library_hotkey = keyboard.add_hotkey(
                    library_key,
                    self.on_library_manager,
                    suppress=False,
                )
                self._registered_hotkey_handlers[library_key] = self._global_library_hotkey
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
                self._registered_hotkey_handlers[vision_key] = self._global_vision_hotkey
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
                self._registered_hotkey_handlers[monster_key] = self._global_monster_hotkey
            except Exception as e:
                print(f"Failed to register monster editor hotkey '{monster_key}': {e}")
                self._failed_hotkeys[monster_key] = repr(e)
                self._global_monster_hotkey = None

            self._hotkeys_registered_ok = len(self._failed_hotkeys) == 0

            # Log successful registration
            registered = []
            if self._global_start_hotkey:
                registered.append(f"Start={start_key}")
            if self._global_stop_hotkey:
                registered.append(f"Stop={stop_key}")
            if self._global_wizard_hotkey:
                registered.append(f"Wizard={wizard_key}")
            if self._global_library_hotkey:
                registered.append(f"Library={library_key}")
            if self._global_vision_hotkey:
                registered.append(f"Vision={vision_key}")
            if self._global_monster_hotkey:
                registered.append(f"Monster={monster_key}")

            if registered:
                print(f"Global hotkeys registered: {', '.join(registered)}")

            if not self._hotkeys_registered_ok:
                print(f"Some hotkeys failed to register: {self._failed_hotkeys}")

            # Update UI
            try:
                if hasattr(self.parent, "after") and hasattr(self.parent, "_update_hotkey_diagnostics_ui"):
                    self.parent.after(150, self.parent._update_hotkey_diagnostics_ui)
                elif hasattr(self.parent, "_update_hotkey_diagnostics_ui"):
                    self.parent._update_hotkey_diagnostics_ui()
            except Exception:
                pass

        except Exception as e:
            print(f"Error registering global hotkeys: {e}")
            self._hotkeys_registered_ok = False
            # Update UI to show error state
            try:
                if hasattr(self.parent, "after") and hasattr(self.parent, "_update_hotkey_diagnostics_ui"):
                    self.parent.after(150, self.parent._update_hotkey_diagnostics_ui)
                elif hasattr(self.parent, "_update_hotkey_diagnostics_ui"):
                    self.parent._update_hotkey_diagnostics_ui()
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

            if self._global_wizard_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_wizard_hotkey)
                except Exception as e:
                    print(f"Error unregistering wizard hotkey: {e}")
                finally:
                    self._global_wizard_hotkey = None

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

        except Exception as e:
            print(f"Error in unregister_all: {e}")
            try:
                if hasattr(self.parent, "_hotkey_diag_var"):
                    self.parent._hotkey_diag_var.set(str(e))
            except Exception:
                pass

    def on_vision_wizard(self, *_args) -> None:
        if hasattr(self.parent, "window_controller"):
            if hasattr(self.parent, "after"):
                self.parent.after(0, self.parent.window_controller.open_vision_wizard)
            else:
                self.parent.window_controller.open_vision_wizard()

    def on_monster_editor(self, *_args) -> None:
        if hasattr(self.parent, "window_controller"):
            if hasattr(self.parent, "after"):
                self.parent.after(0, self.parent.window_controller.open_monster_manager)
            else:
                self.parent.window_controller.open_monster_manager()

    def on_setup_wizard(self, *_args) -> None:
        try:
            print("[Hotkeys] Setup Wizard hotkey pressed")
            current_mode = self.parent.hunt_cfg.get("ui_mode", "beginner")
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
                self.parent, "window_controller"
            ):
                self.parent.after(0, self.parent.window_controller.open_library_manager)
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
