from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app_gui import App

class SkillManagerController:
    """Manages the modal lifecycle and external integrations for the Skill Manager Window."""

    def __init__(self, root: "App"):
        self.root = root
        self._window = None

    def open_window(self) -> None:
        """Opens the library manager window focused on the skills tab."""
        # Use LibraryManagerController as the single source of truth for skill editing
        controller = getattr(self.root, "library_manager_controller", None)
        if not controller:
            print("[SkillManagerController] Cannot open window: library_manager_controller missing.")
            return

        # Open or focus the library manager window
        controller.open_library_manager()

        # Switch to the Skills tab
        lib_win = getattr(self.root, "library_manager_win", None)
        if lib_win and hasattr(lib_win, "notebook") and hasattr(lib_win, "skill_tab"):
            try:
                lib_win.notebook.select(lib_win.skill_tab)
            except Exception as e:
                print(f"[SkillManagerController] Failed to select skill tab: {e}")

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
