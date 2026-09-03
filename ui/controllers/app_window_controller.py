from typing import Any, Dict, List, Optional
import tkinter as tk
from tkinter import messagebox
from lib.features.hunt.hunt_config import save_hunt_config, CONFIG_PATH


import logging
logger = logging.getLogger(__name__)

class AppWindowController:
    ALLOWED_PROCESSES = ["cabal.exe"]

    """Manages dialog/window ownership tracking and target window selection lifecycle."""

    def __init__(self, root: tk.Tk):
        self.root = root

    def _list_windows(
        self, title_contains: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        from lib.system.window_manager import WindowManager
        from lib.features.hunt.config_validator import normalize_window_bounds_value

        wm = WindowManager()
        windows = wm.list_windows(title_contains=title_contains, visible_only=True)
        results: List[Dict[str, Any]] = []
        own_title = ""
        try:
            own_title = self.root.title()
        except Exception as e:
            logger.error(f"Failed to get own title: {e}")
            own_title = ""

        allowed_processes = ["cabal.exe"]

        for info in windows:
            title = (info.title or "").strip()
            if not title or title == own_title:
                continue

            if info.process_name.lower() not in allowed_processes:
                continue

            results.append(
                {
                    "hwnd": int(info.hwnd),
                    "pid": int(info.pid),
                    "title": title,
                    "proc": info.process_name,
                    "bounds": normalize_window_bounds_value(info.rect),
                    "is_minimized": info.is_minimized
                }
            )
        results.sort(
            key=lambda item: (
                "cabal" not in item["title"].lower(),
                item["title"].lower(),
                item["pid"],
            )
        )
        return results

    def _retry_resolve_bounds(self, hwnd, attempt):
        from lib.system.window_manager import WindowManager
        import logging
        logger = logging.getLogger(__name__)

        wm = WindowManager()
        wm.restore(hwnd)
        try:
            import win32gui
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass

        # Re-check bounds immediately after request (with small implicit delay by execution time)
        # But properly we should check again on the next tick, however the prompt allows
        # checking immediately in the callback or scheduling it. Let's just check now.
        new_info = wm.get_window_info(hwnd)
        if new_info and not new_info.is_minimized and not new_info.is_offscreen:
            logger.info(f"Window successfully restored. New bounds: {new_info.rect}")
            self.root.bounds_recovery_failed = False
            self.on_hunt_find_windows()
            return

        logger.warning(f"Restore attempt {attempt + 1} failed.")

        if attempt < 2:
            self.root.after(300, self._retry_resolve_bounds, hwnd, attempt + 1)
        else:
            logger.error("All restore attempts failed.")
            self.root.bounds_recovery_failed = True
            if hasattr(self.root, "state_controller") and hasattr(self.root.state_controller, "_update_window_bounds_display"):
                self.root.state_controller._update_window_bounds_display()

    def on_hunt_refresh_windows(self, *_args) -> None:
        if getattr(self, '_refresh_locked', False):
            return
        self._refresh_locked = True
        if hasattr(self, 'root') and hasattr(self.root, 'after'):
            self.root.after(500, lambda: setattr(self, '_refresh_locked', False))

        from lib.system.window_manager import WindowManager

        selected = getattr(self.root, "hunt_selected", None)
        if selected and isinstance(selected, dict):
            hwnd = selected.get("hwnd")
            if hwnd:
                wm = WindowManager()
                info = wm.get_window_info(hwnd)

                # Check if minimized or off-screen
                if info and (info.is_minimized or info.is_offscreen):
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"Window {hwnd} is minimized, attempting recovery...")
                    self.root.after(300, self._retry_resolve_bounds, hwnd, 0)
                    return

        # Finally re-scan windows to update bounds in UI
        self.root.bounds_recovery_failed = False
        self.on_hunt_find_windows()

    def on_hunt_find_windows(self, _evt=None) -> None:
        try:
            items = self._list_windows()
        except Exception as exc:
            self.root.win_items = []
            if hasattr(self.root, "win_combo"):
                self.root.win_combo["values"] = []
            if hasattr(self.root, "hunt_status"):
                self.root.hunt_status.set(f"Window scan failed: {exc}")
            return

        self.root.win_items = items

        # Build dictionary mapping hwnd to display names
        self.root.win_items_map = {item.get("hwnd"): item.get("title") for item in items}
        values = [item["title"] for item in items]
        if hasattr(self.root, "win_combo"):
            self.root.win_combo["values"] = values

        from lib.features.hunt.window_selection_service import validate_selected_cabal_window
        selected = getattr(self.root, "hunt_selected", None)

        # If we have a selection but no items, or the selection is now invalid
        is_selection_valid = False
        if selected and items:
            validation = validate_selected_cabal_window(selected, items)
            is_selection_valid = validation.is_valid

        if not items or (selected and not is_selection_valid):
            self.root.hunt_selected = None
            if hasattr(self.root, "win_combo_var"):
                self.root.win_combo_var.set("")
            if hasattr(self.root, "win_combo"):
                self.root.win_combo.set("")
            self.root.current_window_bounds = None
            if hasattr(self.root, "_update_window_bounds_display"):
                self.root._update_window_bounds_display()
            if hasattr(self.root, "hunt_status"):
                if not items:
                    self.root.hunt_status.set("No visible windows found")
                else:
                    self.root.hunt_status.set("Selected window invalid, cleared selection.")

            # Since selection is cleared, ensure we lock UI if needed
            if hasattr(self.root, "start_stop_btn"):
                self.root.start_stop_btn.config(state="disabled")

            if not items:
                return

        target_index = 0
        selected = getattr(self.root, "hunt_selected", None) or {}
        selected_hwnd = selected.get("hwnd") if isinstance(selected, dict) else None
        selected_title = selected.get("title") if isinstance(selected, dict) else None
        for idx, item in enumerate(items):
            if selected_hwnd and item["hwnd"] == selected_hwnd:
                target_index = idx
                break
            if selected_title and item["title"] == selected_title:
                target_index = idx
                break

        if hasattr(self.root, "win_combo"):
            self.root.win_combo.current(target_index)
        if hasattr(self.root, "win_combo_var"):
            self.root.win_combo_var.set(values[target_index])
        self.on_window_combo_selected()

    def on_window_combo_selected(self, _evt=None) -> None:

        if not getattr(self.root, "win_items", None):
            self.root.hunt_selected = None
            return

        from lib.features.hunt.config_validator import normalize_window_bounds_value
        from lib.features.hunt.window_selection_service import WindowSelectionService

        index = 0
        try:
            index = int(self.root.win_combo.current())
        except Exception:
            selected_title = (
                self.root.win_combo_var.get().strip()
                if hasattr(self.root, "win_combo_var")
                else ""
            )
            for idx, item in enumerate(self.root.win_items):
                if item["title"] == selected_title:
                    index = idx
                    break

        if index < 0 or index >= len(self.root.win_items):
            index = 0

        selected = dict(self.root.win_items[index])

        from lib.features.hunt.window_selection_service import validate_selected_cabal_window
        validation = validate_selected_cabal_window(selected, self.root.win_items)
        if not validation.is_valid:
            if hasattr(self.root, "hunt_status"):
                self.root.hunt_status.set(f"Selected window is invalid: {validation.code}")
            return

        selected = validation.window
        bounds = normalize_window_bounds_value(selected.get("bounds"))

        # Re-enable UI if it was locked
        if hasattr(self.root, "start_stop_btn"):
            self.root.start_stop_btn.config(state="normal")
        self.root.hunt_selected = selected
        self.root.current_window_bounds = bounds

        self.root.hunt_cfg["window_title"] = selected["title"]
        self.root.hunt_cfg["window_pid"] = selected["pid"]
        self.root.hunt_cfg["window_hwnd"] = selected["hwnd"]

        WindowSelectionService.update_bounds(self.root.hunt_cfg, bounds)

        hunt_area = self.root.hunt_cfg.get("hunt_area")
        if isinstance(hunt_area, dict):
            hunt_area["window_title"] = selected["title"]
        if hasattr(self.root, "_update_window_bounds_display"):
            self.root._update_window_bounds_display()
        save_hunt_config(self.root.hunt_cfg)
        if hasattr(self.root, "hunt_status"):
            self.root.hunt_status.set(f"Window selected: {selected['title']}")

    def _auto_detect_and_save_cabal_window(self) -> None:
        try:
            items = self._list_windows()
            if not items:
                return
            self.root.win_items = items
            if hasattr(self.root, "win_combo"):
                self.root.win_combo["values"] = [item["title"] for item in items]

            # Find the first valid item
            from lib.features.hunt.window_selection_service import validate_selected_cabal_window
            valid_index = -1
            for i, item in enumerate(items):
                if validate_selected_cabal_window(item, items).is_valid:
                    valid_index = i
                    break

            if valid_index >= 0:
                if hasattr(self.root, "win_combo"):
                    self.root.win_combo.current(valid_index)
                if hasattr(self.root, "win_combo_var"):
                    self.root.win_combo_var.set(items[valid_index]["title"])
                self.on_window_combo_selected()
        except Exception as e:
            logger.error(f"Exception during operation: {e}")
            return

    def _bring_window_to_front_by_hwnd(self, hwnd: int) -> bool:
        try:
            from lib.system.window_manager import WindowManager

            return WindowManager().set_foreground(int(hwnd))
        except Exception as e:
            logger.error(f"Exception during operation: {e}")
            return False

    def _bring_window_to_front_by_pid(self, pid: int) -> bool:
        try:
            for item in self._list_windows():
                if int(item["pid"]) == int(pid):
                    return self._bring_window_to_front_by_hwnd(int(item["hwnd"]))
        except Exception as e:
            logger.error(f"Exception during operation: {e}")
            return False
        return False

    def _bring_window_to_front(self, title: str) -> bool:
        if not title:
            return False
        try:
            for item in self._list_windows(title_contains=title):
                return self._bring_window_to_front_by_hwnd(int(item["hwnd"]))
        except Exception as e:
            logger.error(f"Exception during operation: {e}")
            return False
        return False

    def on_setup_wizard(self, hide_parent=True):
        from ui.windows.setup_wizard import show_setup_wizard

        def on_wizard_complete(wizard_data):
            if hide_parent:
                self.root.deiconify()
            from lib.features.hunt.hunt_config import load_hunt_config

            self.root.hunt_cfg = load_hunt_config()
            if hasattr(self.root, "_populate_hunt_ui_from_config"):
                self.root._populate_hunt_ui_from_config()
            lang = wizard_data.get("language", "en")
            if hasattr(self.root, "hunt_status"):
                self.root.hunt_status.set(
                    f"✅ Wizard completed! Configuration loaded. Ready to hunt. (Language: {lang})"
                )

        def on_wizard_cancel():
            if hide_parent:
                self.root.deiconify()

        if callable(show_setup_wizard):
            try:
                show_setup_wizard(
                    self.root,
                    config_manager=self.root.config_mgr,
                    on_complete=on_wizard_complete,
                    on_cancel=on_wizard_cancel,
                    hide_parent=hide_parent,
                )
            except tk.TclError:
                app_lang = getattr(self.root, "lang", "en")

                class _HeadlessSetupWizardStub:
                    def __init__(self):
                        self.wizard_data = {"language": app_lang}
                        self.dialog = self
                        self._dirty = False

                    def has_unsaved_changes(self):
                        return self._dirty or bool(self.wizard_data)

                    def attempt_close_from_external(self):
                        return True

                    def destroy(self):
                        return None

                self.root._setup_wizard_win = _HeadlessSetupWizardStub()
        else:
            try:
                _t = getattr(self.root, "_t", lambda x: x)
                messagebox.showinfo(
                    _t("info_title"),
                    "Setup wizard is not available in this build.",
                    parent=self.root,
                )
            except Exception:
                pass

    def try_close_setup_wizard(self) -> bool:
        try:
            wiz = getattr(self.root, "_setup_wizard_win", None)
            if wiz is None:
                for c in list(self.root.winfo_children()):
                    if getattr(c, "_is_setup_wizard", False):
                        wiz = getattr(c, "_wizard_ref", None) or c
                        break
            if wiz is None:
                return True
            fn = getattr(wiz, "attempt_close_from_external", None)
            if callable(fn):
                try:
                    return bool(fn())
                except Exception:
                    return False
            return False
        except Exception as e:
            logger.error(f"Exception during operation: {e}")
            return False

    def open_vision_wizard(self):
        try:
            from ui.windows.setup_wizard_vision import create_or_show_vision_wizard

            wizard = create_or_show_vision_wizard(
                self.root,
                config_path=str(CONFIG_PATH),
                on_close=getattr(self.root, "_on_vision_wizard_closed", lambda: None),
            )
            print(f"[Vision] Wizard opened/focused: {wizard}")
        except Exception as e:
            print(f"[Vision] Error opening wizard: {e}")
            import traceback

            traceback.print_exc()
            _t = getattr(self.root, "_t", lambda x: "Error")
            messagebox.showerror(_t("error"), f"Cannot open Vision Wizard:\n{e}")

    def on_monster_calculate_timing(self) -> None:
        from ui.windows.timing_calc_dialog import TimingCalcDialog

        def _apply_time(t):
            if hasattr(self.root, "monster_cfg_wait"):
                self.root.monster_cfg_wait.set(str(t))

        TimingCalcDialog(self.root, self.root, on_apply=_apply_time)
