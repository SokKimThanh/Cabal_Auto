from typing import Any, Optional


class HotkeyController:
    """Controller for global hotkey management."""

    def __init__(self, parent: Any):
        self.parent = parent
        self.hotkey_mgr = getattr(parent, "hotkey_mgr", None)

    def register_all(self) -> None:
        if self.hotkey_mgr:
            self.hotkey_mgr.register_all()

    def unregister_all(self) -> None:
        if self.hotkey_mgr:
            self.hotkey_mgr.unregister_all()

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
            if hasattr(self.parent, "window_controller"):
                if hasattr(self.parent, "after"):
                    self.parent.after(
                        0,
                        lambda: self.parent.window_controller.on_setup_wizard(
                            hide_parent=False
                        ),
                    )
                else:
                    self.parent.window_controller.on_setup_wizard(hide_parent=False)
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
                try:
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
                except Exception:
                    # fall through to open a fresh manager if this reference is stale
                    try:
                        existing.destroy()
                    except Exception:
                        pass

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
