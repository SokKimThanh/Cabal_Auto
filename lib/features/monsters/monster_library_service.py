from typing import Dict, Any, List, Optional
from lib.features.monsters.monster_repo import (
    load_monster_library,
    save_monster_library,
)
from lib.features.monster_service import ensure_unique_monster_id


class MonsterLibraryService:
    def __init__(self):
        pass

    def load_monsters(self) -> List[Dict[str, Any]]:
        monsters = load_monster_library()
        if isinstance(monsters, list):
            return monsters
        elif isinstance(monsters, dict):
            # Normalization fallback for legacy array-in-dict or dict format
            # This is handled differently in different parts, but we'll return what we load
            # Legacy config migration may yield dicts, ensure they become lists or leave them alone if a higher layer normally normalizes it
            return [monsters] if monsters else []
        return []

    def save_monsters(self, monsters: List[Dict[str, Any]]) -> bool:
        return save_monster_library(monsters)
