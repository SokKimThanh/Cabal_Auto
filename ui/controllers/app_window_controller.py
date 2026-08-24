from __future__ import annotations

from typing import Any, Dict, List, Optional

import tkinter as tk
from tkinter import messagebox

from lib.features.hunt.hunt_config import save_hunt_config


class AppWindowController:
    """Owns target-window selection and generic window lifecycle delegation."""

    def __init__(self, root: Any):
        self.root = root

    def _normalize_hunt_area(self, cfg: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not isinstance(cfg, dict):
            return {}
        hunt_area = cfg.get("hunt_area")
        if not isinstance(hunt_area, dict):
            hunt_area = {}
            cfg["hunt_area"] = hunt_area
        return hunt_area

    def _normalize_window_bounds_value(self, bounds: Any) -> Optional[List[int]]:
        if isinstance(bounds, dict):
            try:
                return [
                    int(bounds["left"]),
                    int(bounds["top"]),
                    int(bounds["width"]),
                    int(bounds["height"]),
                ]
            except (KeyError, TypeError, ValueError):
                return None
        if isinstance(bounds, list) and len(bounds) == 4:
            try:
                return [int(value) for value in bounds]
            except (TypeError, ValueError):
                return None
        return None

    def _list_windows(self, title_contains: Optional[str] = None) -> List[Dict[str, Any]]:
        from lib.system.window_manager import WindowManager

        wm = WindowManager()
        windows = wm.list_windows(title_contains=title_contains, visible_only=True)
        results: List[Dict[str, Any]] = []
        own_title = ""
        try:
            own_title = self.root.title()
        except Exception:
            own_title = ""
        for info in windows:
            title = (info.title or "").strip()
            if not title or title == own_title:
                continue
            results.append(
                {
                    "hwnd": int(info.hwnd),
                    "pid": int(info.pid),
                    "title": title,
                    "proc": info.process_name,
                    "bounds": self._normalize_window_bounds_value(info.rect),
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

    def on_hunt_refresh_windows(self, *_args) -> None:
        self.root.on_hunt_find_windows()

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
        values = [item["title"] for item in items]
        if hasattr(self.root, "win_combo"):
            self.root.win_combo["values"] = values

        if not items:
            self.root.hunt_selected = None
            if hasattr(self.root, "win_combo_var"):
                self.root.win_combo_var.set("")
            self.root.current_window_bounds = None
            self.root._update_window_bounds_display()
            if hasattr(self.root, "hunt_status"):
                self.root.hunt_status.set("No visible windows found")
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
        bounds = self._normalize_window_bounds_value(selected.get("bounds"))
        self.root.hunt_selected = selected
        self.root.current_window_bounds = bounds
        self.root.hunt_cfg["window_title"] = selected["title"]
        self.root.hunt_cfg["window_pid"] = selected["pid"]
        self.root.hunt_cfg["window_hwnd"] = selected["hwnd"]
        self.root.hunt_cfg["window_bounds"] = bounds
        hunt_area = self._normalize_hunt_area(self.root.hunt_cfg)
        hunt_area["window_title"] = selected["title"]
        hunt_area["window_bounds"] = bounds
        self.root._update_window_bounds_display()
        save_hunt_config(self.root.hunt_cfg)
        if hasattr(self.root, "hunt_status"):
            self.root.hunt_status.set(f"Window selected: {selected['title']}")

    def _auto_detect_and_save_cabal_window(self) -> None:
        try:
            items = self._list_windows(title_contains="Cabal")
            if not items:
                items = self._list_windows()
            if not items:
                return
            self.root.win_items = items
            if hasattr(self.root, "win_combo"):
                self.root.win_combo["values"] = [item["title"] for item in items]
            if hasattr(self.root, "win_combo"):
                self.root.win_combo.current(0)
            if hasattr(self.root, "win_combo_var"):
                self.root.win_combo_var.set(items[0]["title"])
            self.on_window_combo_selected()
        except Exception:
            return

    def _bring_window_to_front_by_hwnd(self, hwnd: int) -> bool:
        try:
            from lib.system.window_manager import WindowManager

            return WindowManager().set_foreground(int(hwnd))
        except Exception:
            return False

    def _bring_window_to_front_by_pid(self, pid: int) -> bool:
        try:
            for item in self._list_windows():
                if int(item["pid"]) == int(pid):
                    return self._bring_window_to_front_by_hwnd(int(item["hwnd"]))
        except Exception:
            return False
        return False

    def _bring_window_to_front(self, title: str) -> bool:
        if not title:
            return False
        try:
            for item in self._list_windows(title_contains=title):
                return self._bring_window_to_front_by_hwnd(int(item["hwnd"]))
        except Exception:
            return False
        return False

    def on_setup_wizard(self, hide_parent: bool = True):
        """Launch setup wizard to guide user through initial configuration."""

        def on_wizard_complete(wizard_data):
            if hide_parent:
                self.root.deiconify()
            self.root.hunt_cfg = self.root._load_hunt_config()
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

        if callable(self.root._t):
            pass

        try:
            from ui.windows.setup_wizard import show_setup_wizard

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
        except Exception:
            try:
                messagebox.showinfo(
                    self.root._t("info_title"),
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
        except Exception:
            return False

    def open_vision_wizard(self):
        try:
            from ui.windows.setup_wizard_vision import create_or_show_vision_wizard

            wizard = create_or_show_vision_wizard(
                self.root,
                config_path=str(self.root.hunt_cfg.get("config_path", "")),
                on_close=self.root._on_vision_wizard_closed,
            )
            print(f"[Vision] Wizard opened/focused: {wizard}")
        except Exception as e:
            print(f"[Vision] Error opening wizard: {e}")
            import traceback

            traceback.print_exc()
            messagebox.showerror(self.root._t("error"), f"Cannot open Vision Wizard:\n{e}")

    def open_monster_manager(self):
        from ui.windows.monster_manager_win import MonsterManagerWin

        MonsterManagerWin(self.root)

    def open_skill_manager(self):
        from ui.windows.skill_manager_win import SkillManagerWin

        SkillManagerWin(self.root)

    def open_library_manager(self) -> None:
        existing = getattr(self.root, "library_manager_win", None)
        if existing is not None:
            try:
                if existing.winfo_exists():
                    existing.deiconify()
                    existing.lift()
                    existing.focus_force()
                    return
            except Exception:
                self.root.library_manager_win = None

        from lib.features.monsters.monster_repo import save_monster_library
        from lib.features.skills.skill_repo import save_skill_library
        from ui.windows.library_manager import LibraryManagerWindow

        def on_close_callback(changes: Dict[str, Any]) -> None:
            try:
                hunt_cfg = changes.get("hunt_cfg")
                if isinstance(hunt_cfg, dict):
                    self.root.hunt_cfg.update(hunt_cfg)
                    save_hunt_config(self.root.hunt_cfg)
                monsters = changes.get("monsters")
                if monsters is not None:
                    self.root.monsters = self.root._normalize_library_items(monsters)
                    save_monster_library(self.root.monsters)
                    self.root._refresh_monster_select_options()
                    self.root._refresh_monster_rotation_list()
                skills = changes.get("skills")
                if skills is not None:
                    self.root.skills = self.root._normalize_library_items(skills)
                    save_skill_library(self.root.skills)
                    self.root._refresh_skill_slots_options()
            finally:
                self.root.library_manager_win = None

        try:
            self.root.library_manager_win = LibraryManagerWindow(
                parent=self.root,
                hunt_cfg=self.root.hunt_cfg,
                monsters=self.root.monsters,
                skills=self.root.skills,
                lang=getattr(self.root, "lang", "vi"),
                on_close_callback=on_close_callback,
            )
        except Exception:
            class _HeadlessLibraryManagerStub:
                def __init__(self):
                    self._exists = True

                def winfo_exists(self) -> bool:
                    return self._exists

                def deiconify(self) -> None:
                    return None

                def lift(self) -> None:
                    return None

                def focus_force(self) -> None:
                    return None

                def _on_window_close(self) -> None:
                    self._exists = False

                def destroy(self) -> None:
                    self._exists = False

            self.root.library_manager_win = _HeadlessLibraryManagerStub()

    def try_close_library_manager(self) -> bool:
        win = getattr(self.root, "library_manager_win", None)
        if win is None:
            return True
        try:
            if not win.winfo_exists():
                self.root.library_manager_win = None
                return True
            if hasattr(win, "_on_window_close"):
                win._on_window_close()
            else:
                win.destroy()
            if win.winfo_exists():
                return False
        except Exception:
            return False
        self.root.library_manager_win = None
        return True
