from typing import Any, Dict, List
from lib.features.monsters.monster_repo import load_monster_library, save_monster_library


class MonsterLibraryService:
    def load_monsters(self) -> Any:
        """Load raw monster library data (list or dict) from disk."""
        return load_monster_library()

    def save_monsters(self, monsters: List[Dict[str, Any]]) -> bool:
        return save_monster_library(monsters)
