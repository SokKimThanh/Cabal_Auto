from typing import Any, Dict, Optional
import tkinter as tk
from lib.features.hunt.hunt_config import save_hunt_config

class LibraryManagerController:
    """Manages library manager window lifecycle and callback dispatch."""

    def __init__(self, app: Any):
        self.app = app

    def open_library_manager(self) -> None:
        existing = getattr(self.app, "library_manager_win", None)
        if existing is not None:
            try:
                if existing.winfo_exists():
                    existing.deiconify()
                    existing.lift()
                    existing.focus_force()
                    return
            except Exception:
                self.app.library_manager_win = None

        from ui.windows.library_manager import LibraryManagerWindow
        from lib.features.monsters.monster_repo import save_monster_library
        from lib.features.skills.skill_repo import save_skill_library

        def on_close_callback(changes: Dict[str, Any]) -> None:
            try:
                hunt_cfg = changes.get("hunt_cfg")
                if isinstance(hunt_cfg, dict):
                    self.app.hunt_cfg.update(hunt_cfg)
                    save_hunt_config(self.app.hunt_cfg)
                monsters = changes.get("monsters")
                if monsters is not None:
                    if hasattr(self.app, "_normalize_library_items"):
                        self.app.monsters = self.app._normalize_library_items(monsters)
                    else:
                        self.app.monsters = monsters
                    save_monster_library(self.app.monsters)
                    if hasattr(self.app, "_refresh_monster_select_options"):
                        self.app._refresh_monster_select_options()
                    if hasattr(self.app, "_refresh_monster_rotation_list"):
                        self.app._refresh_monster_rotation_list()
                skills = changes.get("skills")
                if skills is not None:
                    if hasattr(self.app, "_normalize_library_items"):
                        self.app.skills = self.app._normalize_library_items(skills)
                    else:
                        self.app.skills = skills
                    save_skill_library(self.app.skills)
                    if hasattr(self.app, "_refresh_skill_slots_options"):
                        self.app._refresh_skill_slots_options()
            finally:
                self.app.library_manager_win = None

        try:
            self.app.library_manager_win = LibraryManagerWindow(
                parent=self.app,
                hunt_cfg=self.app.hunt_cfg,
                monsters=self.app.monsters,
                skills=self.app.skills,
                lang=getattr(self.app, "lang", "vi"),
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

            self.app.library_manager_win = _HeadlessLibraryManagerStub()

    def try_close_library_manager(self) -> bool:
        win = getattr(self.app, "library_manager_win", None)
        if win is None:
            return True
        try:
            if not win.winfo_exists():
                self.app.library_manager_win = None
                return True
            if hasattr(win, "_on_window_close"):
                win._on_window_close()
            else:
                win.destroy()
            if win.winfo_exists():
                return False
        except Exception:
            return False
        self.app.library_manager_win = None
        return True
