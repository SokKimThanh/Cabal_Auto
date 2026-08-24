
try:
    import keyboard
except ImportError:
    keyboard = None


class HotkeyManager:
    def __init__(self, app, hunt_cfg):
        self.app = app
        self.hunt_cfg = hunt_cfg

        # Track registered handlers for proper cleanup
        self._global_start_hotkey = None
        self._global_stop_hotkey = None
        self._global_wizard_hotkey = None
        self._global_library_hotkey = None
        self._global_vision_hotkey = None
        self._global_monster_hotkey = None

        # Track fallback tkinter bindings
        self._hotkey_fallback_bound = []

    def register_all(self):
        """Registers all global hotkeys from config. Fallbacks to Tkinter bindings if keyboard module missing."""
        hotkey_cfg = self.hunt_cfg.get("global_hotkeys", {})
        if not hotkey_cfg.get("enabled", True):
            print("[Hotkeys] Global hotkeys disabled by user")
            return

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
                        if p == "ctrl":
                            tk_parts.append("Control")
                        elif p == "shift":
                            tk_parts.append("Shift")
                        elif p == "alt":
                            tk_parts.append("Alt")
                        elif len(p) == 1:
                            tk_parts.append(p.lower())  # use lowercase for letters
                        else:
                            tk_parts.append(p)
                    return f"<{'-'.join(tk_parts)}>"

                hotkey_cfg = self.hunt_cfg.get("global_hotkeys", {})
                seq_start = _to_tk_seq(hotkey_cfg.get("start_key", "ctrl+shift+r"))
                seq_stop = _to_tk_seq(hotkey_cfg.get("stop_key", "ctrl+shift+e"))
                seq_wiz = _to_tk_seq(hotkey_cfg.get("setup_wizard_key", "ctrl+shift+n"))
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
                            self.app.unbind_all(s)
                        except Exception:
                            pass
                    self._hotkey_fallback_bound = []

                    # Bind to all widgets (works when app is focused)
                    self.app.bind_all(
                        seq_start, lambda e: self.app.on_hunt_start(), add="+"
                    )
                    self._hotkey_fallback_bound.append(seq_start)
                    self.app.bind_all(
                        seq_stop, lambda e: self.app.on_hunt_stop(), add="+"
                    )
                    self._hotkey_fallback_bound.append(seq_stop)
                    # Wizard only meaningful in beginner mode
                    if self.hunt_cfg.get("ui_mode", "beginner") == "beginner":
                        self.app.bind_all(
                            seq_wiz,
                            lambda e: self.app._on_setup_wizard_hotkey(),
                            add="+",
                        )
                        self._hotkey_fallback_bound.append(seq_wiz)
                    self.app.bind_all(
                        seq_lib,
                        lambda e: self.app._on_library_manager_hotkey(),
                        add="+",
                    )
                    self._hotkey_fallback_bound.append(seq_lib)
                    # Sprint 22: Vision Wizard fallback
                    self.app.bind_all(
                        seq_vision,
                        lambda e: self.app._on_vision_wizard_hotkey(),
                        add="+",
                    )
                    self._hotkey_fallback_bound.append(seq_vision)
                    print(
                        f"[Hotkeys] Fallback (focused) hotkeys bound: {', '.join(self._hotkey_fallback_bound)}"
                    )
                    try:
                        self.app._update_hotkey_diagnostics_ui()
                    except Exception:
                        pass
                except Exception as _bind_e:
                    print(
                        f"[Hotkeys] Failed to bind fallback focused hotkeys: {_bind_e}"
                    )

                return

            # Get hotkey config (defaults to Ctrl+Shift+R/E if not set)
            hotkey_cfg = self.hunt_cfg.get("global_hotkeys", {})
            if not hotkey_cfg.get("enabled", True):
                print("[Hotkeys] Global hotkeys disabled by user")
                return  # Global hotkeys disabled by user

            start_key = hotkey_cfg.get("start_key", "ctrl+shift+r")
            stop_key = hotkey_cfg.get("stop_key", "ctrl+shift+e")
            wizard_key = hotkey_cfg.get("setup_wizard_key", "ctrl+shift+n")  # NEW
            library_key = hotkey_cfg.get("library_manager_key", "ctrl+shift+l")  # NEW
            vision_key = hotkey_cfg.get(
                "vision_wizard_key", "ctrl+shift+v"
            )  # NEW Sprint 22
            monster_key = hotkey_cfg.get(
                "monster_editor_key", "ctrl+shift+m"
            )  # NEW Monster Editor

            # Unregister old hotkeys first (in case of re-registration)
            self.unregister_all()

            # Register new hotkeys
            try:
                self._global_start_hotkey = keyboard.add_hotkey(
                    start_key,
                    self.app.on_hunt_start,
                    suppress=False,  # Don't suppress the key event
                )
            except Exception as e:
                print(f"Failed to register start hotkey '{start_key}': {e}")
                self._global_start_hotkey = None

            try:
                self._global_stop_hotkey = keyboard.add_hotkey(
                    stop_key, self.app.on_hunt_stop, suppress=False
                )
            except Exception as e:
                print(f"Failed to register stop hotkey '{stop_key}': {e}")
                self._global_stop_hotkey = None

            # NEW: Register Setup Wizard hotkey (only in beginner mode)
            current_mode = self.hunt_cfg.get("ui_mode", "beginner")
            if current_mode == "beginner":
                try:
                    self._global_wizard_hotkey = keyboard.add_hotkey(
                        wizard_key, self.app._on_setup_wizard_hotkey, suppress=False
                    )
                except Exception as e:
                    print(f"Failed to register wizard hotkey '{wizard_key}': {e}")
                    self._global_wizard_hotkey = None
            else:
                self._global_wizard_hotkey = None

            # NEW: Register Library Manager hotkey (always active)
            try:
                self._global_library_hotkey = keyboard.add_hotkey(
                    library_key, self.app._on_library_manager_hotkey, suppress=False
                )
            except Exception as e:
                print(f"Failed to register library hotkey '{library_key}': {e}")
                self._global_library_hotkey = None

            # NEW Sprint 22: Register Vision Wizard hotkey (always active)
            try:
                self._global_vision_hotkey = keyboard.add_hotkey(
                    vision_key, self.app._on_vision_wizard_hotkey, suppress=False
                )
            except Exception as e:
                print(f"Failed to register vision hotkey '{vision_key}': {e}")
                self._global_vision_hotkey = None

            # NEW: Register Monster Editor hotkey (always active)
            try:
                self._global_monster_hotkey = keyboard.add_hotkey(
                    monster_key, self.app._on_monster_editor_hotkey, suppress=False
                )
            except Exception as e:
                print(f"Failed to register monster editor hotkey '{monster_key}': {e}")
                self._global_monster_hotkey = None

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
                # Update new status-driven UI
                try:
                    self.app.after(150, self.app._update_hotkey_diagnostics_ui)
                except Exception:
                    pass

        except Exception as e:
            print(f"Error registering global hotkeys: {e}")
            # Update UI to show error state
            try:
                self.app.after(150, self.app._update_hotkey_diagnostics_ui)
            except Exception:
                pass

    def unregister_all(self):
        """Unregister global hotkeys to clean up resources."""
        try:
            if keyboard is None:
                return

            # Unregister start hotkey
            if self._global_start_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_start_hotkey)
                except Exception as e:
                    print(f"Error unregistering start hotkey: {e}")
                finally:
                    self._global_start_hotkey = None

            # Unregister stop hotkey
            if self._global_stop_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_stop_hotkey)
                except Exception as e:
                    print(f"Error unregistering stop hotkey: {e}")
                finally:
                    self._global_stop_hotkey = None

            # NEW: Unregister wizard hotkey
            if self._global_wizard_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_wizard_hotkey)
                except Exception as e:
                    print(f"Error unregistering wizard hotkey: {e}")
                finally:
                    self._global_wizard_hotkey = None

            # NEW: Unregister library hotkey
            if self._global_library_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_library_hotkey)
                except Exception as e:
                    print(f"Error unregistering library hotkey: {e}")
                finally:
                    self._global_library_hotkey = None

            # NEW Sprint 22: Unregister vision hotkey
            if self._global_vision_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_vision_hotkey)
                except Exception as e:
                    print(f"Error unregistering vision hotkey: {e}")
                finally:
                    self._global_vision_hotkey = None

            # NEW: Unregister monster editor hotkey
            if self._global_monster_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_monster_hotkey)
                except Exception as e:
                    print(f"Error unregistering monster hotkey: {e}")
                finally:
                    self._global_monster_hotkey = None

        except Exception as e:
            print(f"Error in _unregister_global_hotkeys: {e}")
            try:
                self.app._hotkey_diag_var.set(str(e))
            except Exception:
                pass
