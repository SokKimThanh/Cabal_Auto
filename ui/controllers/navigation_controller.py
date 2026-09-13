from typing import Dict, Any, Callable

class NavigationController:
    """
    Manages application view transitions to avoid tight coupling in the main App God Class.
    """
    def __init__(self, container, on_view_changed: Callable[[str], None] = None):
        self.container = container
        self.views: Dict[str, Any] = {}
        self.current_view_key = None
        self._current_view = None
        self.on_view_changed = on_view_changed

    def register_views(self, app_instance):
        """
        Instantiate and register all the major application views.
        """
        from ui.views.hunt_workspace_frame import HuntWorkspaceFrame
        from ui.views.setup_content_frame import SetupContentFrame
        from ui.views.help_support_frame import HelpSupportFrame
        from ui.views.stats_content_frame import StatsContentFrame
        from ui.views.activity_logs_frame import ActivityLogsFrame
        from ui.views.monster_manager_frame import MonsterManagerFrame
        from ui.views.skill_manager_frame import SkillManagerFrame
        from ui.views.build_manager_frame import BuildManagerFrame
        from ui.views.class_manager_frame import ClassManagerFrame
        from ui.views.icon_manager_frame import IconManagerFrame
        from ui.views.scan_history_frame import ScanHistoryFrame

        # Initialize all views. Pass `app_instance` as it acts as the global state context for now.
        self.views["hunt"] = HuntWorkspaceFrame(self.container, app=app_instance)
        self.views["setup"] = SetupContentFrame(self.container, app=app_instance)
        self.views["help"] = HelpSupportFrame(self.container, app=app_instance)
        self.views["stats"] = StatsContentFrame(self.container, app=app_instance)
        self.views["logs"] = ActivityLogsFrame(self.container, app=app_instance)

        self.views["build_manager"] = BuildManagerFrame(self.container, app=app_instance)
        self.views["monster_manager"] = MonsterManagerFrame(self.container, app=app_instance)
        self.views["skill_manager"] = SkillManagerFrame(self.container, app=app_instance)
        self.views["class_manager"] = ClassManagerFrame(self.container, app=app_instance)

        self.views["icon_manager"] = IconManagerFrame(self.container, app=app_instance)
        self.views["scan_history"] = ScanHistoryFrame(self.container, app=app_instance)

    def navigate_to(self, view_key: str):
        """
        Switches the visible view in the container.
        """
        if view_key not in self.views:
            return

        # Hide current view
        if self._current_view:
            self._current_view.grid_remove()
            if hasattr(self._current_view, "on_view_hidden"):
                self._current_view.on_view_hidden()

        # Show new view
        target_view = self.views[view_key]
        target_view.grid(row=0, column=0, sticky="nsew")

        # Update container grid configuration
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        self._current_view = target_view
        self.current_view_key = view_key

        # Trigger lifecycle hook if it exists
        if hasattr(target_view, "on_view_shown"):
            target_view.on_view_shown()

        # Notify listener (e.g. App to update sidebar styling)
        if self.on_view_changed:
            self.on_view_changed(view_key)
