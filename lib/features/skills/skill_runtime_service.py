from typing import List, Dict, Optional, Any
from lib.features.skills.skill_repo import load_skill_library, save_skill_library
from lib.features.skills.runtime import SkillRuntime

class SkillRuntimeService:
    """Service facade for skill repository operations and runtime management."""

    def __init__(self):
        self._skills: List[Dict] = []
        self._runtime: Optional[SkillRuntime] = None
        self.reload_skills()

    @staticmethod
    def _normalize_library_items(items: Any) -> List[Dict[str, Any]]:
        """Convert a dictionary-based library into a normalized list."""
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
        if isinstance(items, dict):
            normalized: List[Dict[str, Any]] = []
            for key, value in items.items():
                if not isinstance(value, dict):
                    continue
                item = dict(value)
                item.setdefault("id", key)
                item.setdefault("name", str(item.get("name") or key))
                normalized.append(item)
            return normalized
        return []

    def reload_skills(self) -> None:
        """Load skills from disk and update the internal cache."""
        try:
            raw_data = load_skill_library()
            # Removed the `if not isinstance(raw_data, dict): raw_data = {}` check
            # to allow legacy list configurations to pass through to _normalize_library_items
            self._skills = self._normalize_library_items(raw_data)
        except Exception:
            self._skills = []

        try:
            self._runtime = SkillRuntime(self._skills)
        except Exception:
            self._runtime = None

    def get_all_skills(self) -> List[Dict]:
        """Return a safe copy of all active skills."""
        return [s.copy() for s in self._skills]

    def save_skills(self, skills_dict: Dict) -> bool:
        """Save skills back to disk and reload the cache."""
        success = save_skill_library(skills_dict)
        if success:
            self.reload_skills()
        return success

    def get_runtime(self) -> Optional[SkillRuntime]:
        """Get the skill runtime manager."""
        return self._runtime
