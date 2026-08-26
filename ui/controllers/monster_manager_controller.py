from typing import TYPE_CHECKING

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

        from ui.windows.monster_manager_win import MonsterManagerWin
        self.app.monster_manager_win = MonsterManagerWin(self.app)
