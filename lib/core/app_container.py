from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class AppContainer:
    """Dependency Injection Container for the application."""
    scan_controller: Any = None
    monster_library_service: Any = None
    skill_service: Any = None
    db_skill_service: Any = None
    db_skill_type_service: Any = None
    db_class_service: Any = None
    db_scan_service: Any = None
    overlay_controller: Any = None
    skill_caster_service: Any = None
    window_controller: Any = None
    window_tracker_controller: Any = None
    hunt_runner: Any = None
    hunt_orchestrator: Any = None
    hunt_controller: Any = None
    monster_rotation_controller: Any = None
