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

    def _retry_resolve_bounds(self, hwnd, attempt):
        from lib.features.hunt.window_detection_service import WindowDetectionService
        import logging

        logger = logging.getLogger(__name__)

        service = WindowDetectionService()
        success = service.restore_window_if_minimized(hwnd)

        if success:
            logger.info("Window successfully restored.")
            self.root.bounds_recovery_failed = False
            self.on_hunt_find_windows()
            return

        logger.warning(f"Restore attempt {attempt + 1} failed.")

        if attempt < 2:
            self.root.after(300, self._retry_resolve_bounds, hwnd, attempt + 1)
        else:
            logger.error("All restore attempts failed.")
            self.root.bounds_recovery_failed = True
            if hasattr(self.root, "state_controller") and hasattr(
                self.root.state_controller, "_update_window_bounds_display"
            ):
                self.root.state_controller._update_window_bounds_display()

    def on_hunt_refresh_windows(self, *_args) -> None:
        if getattr(self, "_refresh_locked", False):
            return
        self._refresh_locked = True
        if hasattr(self, "root") and hasattr(self.root, "after"):
            self.root.after(500, lambda: setattr(self, "_refresh_locked", False))

        from lib.features.hunt.window_detection_service import WindowDetectionService

        selected = getattr(self.root, "hunt_selected", None)
        if selected and isinstance(selected, dict):
            hwnd = selected.get("hwnd")
            if hwnd:
                service = WindowDetectionService()
                bounds = service.get_window_bounds(hwnd)

                # Check if minimized or off-screen
                if not bounds:
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
            from lib.features.hunt.window_detection_service import WindowDetectionService
            service = WindowDetectionService()
            items = service.find_all_cabal_windows()

            # Remove our own window from the list
            own_title = ""
            try:
                own_title = self.root.title()
            except Exception as e:
                logger.error(f"Failed to get own title: {e}")
                own_title = ""
            items = [item for item in items if item["title"] != own_title]

        except Exception as exc:
            self.root.win_items = []
            if hasattr(self.root, "win_combo"):
                self.root.win_combo["values"] = []
            if hasattr(self.root, "hunt_status"):
                self.root.hunt_status.set(f"Window scan failed: {exc}")
            return

        self.root.win_items = items

        # Build dictionary mapping hwnd to display names
        self.root.win_items_map = {
            item.get("hwnd"): item.get("title") for item in items
        }
        values = [item["title"] for item in items]
        if hasattr(self.root, "win_combo"):
            self.root.win_combo["values"] = values

        from lib.features.hunt.window_selection_service import (
            validate_selected_cabal_window,
        )

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
                    self.root.hunt_status.set(
                        "Selected window invalid, cleared selection."
                    )

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

        from lib.features.hunt.window_selection_service import (
            validate_selected_cabal_window,
        )

        validation = validate_selected_cabal_window(selected, self.root.win_items)
        if not validation.is_valid:
            if hasattr(self.root, "hunt_status"):
                self.root.hunt_status.set(
                    f"Selected window is invalid: {validation.code}"
                )
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
            from lib.features.hunt.window_detection_service import WindowDetectionService
            service = WindowDetectionService()
            best_window = service.find_best_cabal_window()

            if not best_window:
                return

            self.on_hunt_find_windows()

            if hasattr(self.root, "win_items") and self.root.win_items:
                items = self.root.win_items
                valid_index = -1
                for i, item in enumerate(items):
                    if item["hwnd"] == best_window["hwnd"]:
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
            from lib.features.hunt.window_detection_service import WindowDetectionService
            service = WindowDetectionService()
            for item in service.find_all_cabal_windows():
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
            from lib.features.hunt.window_detection_service import WindowDetectionService
            service = WindowDetectionService()
            for item in service.find_all_cabal_windows(filter_text=title):
                return self._bring_window_to_front_by_hwnd(int(item["hwnd"]))
        except Exception as e:
            logger.error(f"Exception during operation: {e}")
            return False
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
