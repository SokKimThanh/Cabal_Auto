from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app_gui import App

class SkillManagerController:
    """Manages the modal lifecycle and external integrations for the Skill Manager Window."""

    def __init__(self, root: "App"):
        self.root = root
        self._window = None

    def open_window(self) -> None:
        """Opens or refocuses the skill manager window."""
        existing = getattr(self.root, "skill_manager_win", None) or self._window
        if existing is not None:
            try:
                if existing.winfo_exists():
                    existing.deiconify()
                    existing.lift()
                    existing.focus_force()
                    return
            except Exception:
                pass

        from ui.windows.skill_manager_win import SkillManagerWin

        self._window = SkillManagerWin(self.root)
        self.root.skill_manager_win = self._window

    def on_window_closed(self) -> None:
        """Callback to safely clean up references when the window closes."""
        self._window = None
        if getattr(self.root, "skill_manager_win", None) is not None:
             self.root.skill_manager_win = None

        # Trigger an update of skill data
        if hasattr(self.root, "skill_service"):
            self.root.skill_service.reload_skills()

        # Repopulate skill comboboxes
        if hasattr(self.root, "_refresh_skill_slots_options"):
            self.root._refresh_skill_slots_options()
