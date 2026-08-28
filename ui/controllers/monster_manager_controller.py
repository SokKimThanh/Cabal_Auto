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

        # Open the full MonsterManagerWin UI.
        from ui.windows.monster_manager_win import MonsterManagerWin

        editor = MonsterManagerWin(self.app)
        self.app.monster_manager_win = editor

        # S4D Hotfix: We must NOT override the window's own WM_DELETE_WINDOW protocol
        # unless we explicitly call its _on_cancel() method first to trigger unsaved changes confirmation.
        def _clear_ref(win=editor):
            if hasattr(win, "_on_cancel"):
                win._on_cancel()

            # The window will destroy itself if _on_cancel proceeds. We just clean up the reference.
            # We don't forcefully call destroy() here because the user might have clicked "No" in the prompt.
            if not win.winfo_exists():
                if getattr(self.app, "monster_manager_win", None) is win:
                    self.app.monster_manager_win = None

        editor.protocol("WM_DELETE_WINDOW", _clear_ref)

