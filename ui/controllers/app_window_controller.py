from typing import Any, Dict, List, Optional
import tkinter as tk
from tkinter import messagebox
from lib.features.hunt.hunt_config import save_hunt_config, CONFIG_PATH

import logging
import ctypes
from ctypes import wintypes

logger = logging.getLogger(__name__)

# Try to import psutil for process name detection
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class AppWindowController:
    ALLOWED_PROCESSES = ["cabal.exe", "cabalmain.exe"]

    """Manages dialog/window ownership tracking and target window selection lifecycle."""

    def __init__(self, root: tk.Tk):
        self.root = root

    def _enum_windows_winapi(self) -> List[Dict[str, Any]]:
        """Enumerate visible windows using WinAPI (from setup_wizard).
        
        This is more reliable than WindowManager for getting complete list.
        Uses direct Win32 API calls via ctypes.
        """
        try:
            user32 = ctypes.windll.user32
            EnumWindows = user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(
                ctypes.c_bool, wintypes.HWND, wintypes.LPARAM
            )
            IsWindowVisible = user32.IsWindowVisible
            GetWindowTextW = user32.GetWindowTextW
            GetWindowTextLengthW = user32.GetWindowTextLengthW
            GetWindowThreadProcessId = user32.GetWindowThreadProcessId

            results = []

            def callback(hwnd, lParam):
                try:
                    if not IsWindowVisible(hwnd):
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
                    if PSUTIL_AVAILABLE and psutil is not None:
                        try:
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
                logger.error(f"EnumWindows failed: {e}")
                pass

            logger.debug(f"WinAPI enumeration found {len(results)} total windows")
            return results
        except Exception as e:
            logger.error(f"_enum_windows_winapi failed: {e}")
            return []

    def _list_windows(
        self, title_contains: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List Cabal windows using WinAPI enumeration.
        
        Flow:
        1. Uses _enum_windows_winapi() for complete window list
        2. Filters to only Cabal process windows (cabal.exe, cabalmain.exe)
        3. Excludes app's own window (Cabal Auto Hunt)
        4. Gets bounds from each window via WindowManager
        5. Sorts by title
        
        Returns list of window dicts with: hwnd, pid, title, proc, bounds, is_minimized
        """
        from lib.features.hunt.config_validator import normalize_window_bounds_value
        from lib.system.window_manager import WindowManager

        # Get all visible windows via WinAPI
        all_windows = self._enum_windows_winapi()
        logger.debug(f"WinAPI returned {len(all_windows)} visible windows")

        results: List[Dict[str, Any]] = []
        own_title = ""
        try:
            own_title = self.root.title()
        except Exception as e:
            logger.error(f"Failed to get own title: {e}")
            own_title = ""

        logger.debug(f"Own window title: '{own_title}'")
        logger.debug(f"Allowed processes: {self.ALLOWED_PROCESSES}")

        # Filter to Cabal windows only
        for info in all_windows:
            title = (info.get("title") or "").strip()
            if not title or title == own_title:
                logger.debug(f"Skipping window: empty title or own app (title='{title}')")
                continue

            # Check if process name matches allowed processes
            proc_name = (info.get("proc") or "").lower()
            logger.debug(f"Checking window '{title}': proc='{proc_name}'")
            
            # Match if proc_name contains any allowed process name
            is_cabal = any(
                ap.lower() in proc_name 
                for ap in self.ALLOWED_PROCESSES
            ) if proc_name else False
            
            if not is_cabal:
                logger.debug(f"  → Not a Cabal window, skipping")
                continue

            logger.debug(f"  → Found Cabal window!")

            # Get window bounds
            wm = WindowManager()
            hwnd = info["hwnd"]
            win_info = wm.get_window_info(hwnd)
            
            if win_info is None:
                logger.debug(f"Could not get window info for HWND {hwnd}, using default bounds")
                bounds = {"left": 0, "top": 0, "width": 0, "height": 0}
                is_minimized = False
            else:
                bounds = normalize_window_bounds_value(win_info.rect)
                is_minimized = win_info.is_minimized
                logger.debug(f"  Bounds: {bounds}, is_minimized={is_minimized}")

            results.append(
                {
                    "hwnd": int(info["hwnd"]),
                    "pid": int(info["pid"]),
                    "title": title,
                    "proc": info.get("proc") or "",
                    "bounds": bounds,
                    "is_minimized": is_minimized,
                }
            )
            logger.debug(f"  Added: HWND={info['hwnd']}, Title='{title}', PID={info['pid']}")

        # Sort by title
        results.sort(
            key=lambda item: (
                "cabal" not in item["title"].lower(),
                item["title"].lower(),
                item["pid"],
            )
        )
        logger.debug(f"_list_windows returning {len(results)} Cabal windows after filtering")
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
            if hasattr(self.root, "state_controller") and hasattr(
                self.root.state_controller, "_update_window_bounds_display"
            ):
                self.root.state_controller._update_window_bounds_display()

    def on_hunt_refresh_windows(self, *_args) -> None:
        logger.debug("on_hunt_refresh_windows() called")
        if getattr(self, "_refresh_locked", False):
            logger.debug("  Refresh locked, returning early")
            return
        self._refresh_locked = True
        if hasattr(self, "root") and hasattr(self.root, "after"):
            self.root.after(500, lambda: setattr(self, "_refresh_locked", False))

        from lib.system.window_manager import WindowManager

        selected = getattr(self.root, "hunt_selected", None)
        if selected and isinstance(selected, dict):
            hwnd = selected.get("hwnd")
            if hwnd:
                wm = WindowManager()
                info = wm.get_window_info(hwnd)

                # Check if minimized or off-screen
                if info and (info.is_minimized or info.is_offscreen):
                    logger.info(f"Window {hwnd} is minimized, attempting recovery...")
                    # Schedule restoration and window refresh (don't return early!)
                    self.root.after(300, self._retry_resolve_bounds, hwnd, 0)
                    # Continue to scan windows anyway
                    self.root.bounds_recovery_failed = False
                    logger.debug("  Calling on_hunt_find_windows() after scheduling restore")
                    self.on_hunt_find_windows()
                    return

        # Scan windows to update bounds in UI
        self.root.bounds_recovery_failed = False
        logger.debug("  Calling on_hunt_find_windows()")
        self.on_hunt_find_windows()

    def on_hunt_find_windows(self, _evt=None) -> None:
        """List available windows and update combobox values.
        
        IMPORTANT: This only updates the list of available windows in the combobox.
        It does NOT auto-select, validate, or change the current selection.
        Selection validation only happens when hunt starts.
        """
        logger.debug("on_hunt_find_windows() called")
        try:
            items = self._list_windows()
            logger.debug(f"  _list_windows() returned {len(items)} items")
        except Exception as exc:
            logger.error(f"  _list_windows() failed: {exc}")
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
        logger.debug(f"  Setting combobox values: {values}")
        if hasattr(self.root, "win_combo"):
            self.root.win_combo["values"] = values
            logger.debug(f"  Combobox values set. Current: {self.root.win_combo['values']}")
        else:
            logger.warning("  win_combo not found on root!")

        # Update status to show how many windows found
        if hasattr(self.root, "hunt_status"):
            if items:
                self.root.hunt_status.set(f"Found {len(items)} window(s). Select and click Start.")
            else:
                self.root.hunt_status.set("No Cabal windows found. Launch game and try again.")

    def on_window_combo_selected(self, _evt=None) -> None:
        logger.debug("on_window_combo_selected() called")

        if not getattr(self.root, "win_items", None):
            logger.debug("  win_items is empty, setting hunt_selected = None")
            self.root.hunt_selected = None
            return

        from lib.features.hunt.config_validator import normalize_window_bounds_value
        from lib.features.hunt.window_selection_service import WindowSelectionService

        index = 0
        try:
            index = int(self.root.win_combo.current())
            logger.debug(f"  Combobox current index: {index}")
        except Exception as e:
            logger.debug(f"  Failed to get combobox index: {e}")
            selected_title = (
                self.root.win_combo_var.get().strip()
                if hasattr(self.root, "win_combo_var")
                else ""
            )
            logger.debug(f"  Trying to find by title: {selected_title}")
            for idx, item in enumerate(self.root.win_items):
                if item["title"] == selected_title:
                    index = idx
                    logger.debug(f"  Found at index {idx}")
                    break

        if index < 0 or index >= len(self.root.win_items):
            logger.debug(f"  Index {index} out of bounds, resetting to 0")
            index = 0

        selected = dict(self.root.win_items[index])
        logger.debug(f"  Selected window: {selected['title']} (hwnd={selected['hwnd']})")

        # RESTORE WINDOW FIRST if minimized (important for new selections)
        hwnd = selected.get("hwnd")
        if hwnd and selected.get("is_minimized"):
            logger.info(f"Selected window {hwnd} is minimized, restoring...")
            try:
                from lib.system.window_manager import WindowManager
                wm = WindowManager()
                wm.restore(hwnd)
                # Wait briefly for restoration
                import time
                time.sleep(0.2)
                # Get updated window info
                updated_info = wm.get_window_info(hwnd)
                if updated_info:
                    selected["is_minimized"] = updated_info.is_minimized
                    selected["bounds"] = normalize_window_bounds_value(updated_info.rect)
            except Exception as e:
                logger.warning(f"Failed to restore window: {e}")

        from lib.features.hunt.window_selection_service import (
            validate_selected_cabal_window,
        )

        validation = validate_selected_cabal_window(selected, self.root.win_items)
        if not validation.is_valid:
            logger.warning(f"  Window validation failed: {validation.code}")
            if hasattr(self.root, "hunt_status"):
                self.root.hunt_status.set(
                    f"Selected window is invalid: {validation.code}"
                )
            return

        selected = validation.window
        bounds = normalize_window_bounds_value(selected.get("bounds"))
        logger.debug(f"  Validation passed, setting hunt_selected")

        # Re-enable UI if it was locked
        if hasattr(self.root, "start_stop_btn"):
            self.root.start_stop_btn.config(state="normal")
        self.root.hunt_selected = selected
        self.root.current_window_bounds = bounds
        logger.debug(f"  hunt_selected set: {self.root.hunt_selected}")

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
        logger.debug(f"  on_window_combo_selected() completed successfully")

    def _auto_detect_and_save_cabal_window(self) -> None:
        try:
            items = self._list_windows()
            if not items:
                return
            self.root.win_items = items
            if hasattr(self.root, "win_combo"):
                self.root.win_combo["values"] = [item["title"] for item in items]

            # Find the first valid item
            from lib.features.hunt.window_selection_service import (
                validate_selected_cabal_window,
            )

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
