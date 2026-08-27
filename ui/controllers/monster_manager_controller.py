from typing import TYPE_CHECKING, Optional, Callable, Dict, Any
import tkinter as tk

if TYPE_CHECKING:
    from app_gui import App


class MonsterManagerController:
    """Controls the lifecycle and state of the Monster Manager window."""

    def __init__(self, app: "App"):
        self.app = app

    def open_window(self):
        """Open or focus the monster manager window."""
        existing = getattr(self.app, "monster_manager_win", None)
        if existing is not None:
            try:
                if existing.winfo_exists():
                    existing.deiconify()
                    existing.lift()
                    existing.focus_force()
                    return
            except Exception:
                self.app.monster_manager_win = None

        # NOTE: MonsterManagerWin is an empty placeholder shell left over from the
        # controller extraction; QuickMonsterEditor is still the real, fully
        # featured monster manager UI, so open that until the UI migration lands.
        from ui.windows.quick_monster_editor import QuickMonsterEditor

        editor = QuickMonsterEditor(self.app)
        self.app.monster_manager_win = editor

        def _clear_ref(win=editor):
            if getattr(self.app, "monster_manager_win", None) is win:
                self.app.monster_manager_win = None
            win.destroy()

        editor.protocol("WM_DELETE_WINDOW", _clear_ref)

