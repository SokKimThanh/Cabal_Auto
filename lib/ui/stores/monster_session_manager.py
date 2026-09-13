from typing import List, Dict, Any, Optional
from database import get_monster_by_id_api, find_monster_by_name_api

class MonsterSessionManager:
    """Manages monster rotation session state and metadata caching."""

    def __init__(self):
        self._rotation: List[Dict[str, Any]] = []
        self._metadata_cache: Dict[str, Any] = {}

    def get_rotation(self) -> List[Dict[str, Any]]:
        """Returns the current monster rotation list."""
        return self._rotation

    def set_rotation(self, rotation: List[Dict[str, Any]]) -> None:
        """Sets the monster rotation list."""
        self._rotation = rotation

    def add_monster(self, monster: Dict[str, Any]) -> None:
        """Adds a monster to the rotation."""
        self._rotation.append(monster)

    def clear_rotation(self) -> None:
        """Clears the rotation list."""
        self._rotation = []

    def remove_monster_at(self, index: int) -> None:
        """Removes a monster at a specific index."""
        if 0 <= index < len(self._rotation):
            del self._rotation[index]

    def get_metadata(self, monster_id: Optional[int], name: Optional[str], dungeon_id: Optional[int] = None) -> Any:
        """Gets metadata for a monster, caching the result."""
        cache_key = f"{monster_id}_{name}_{dungeon_id}"

        if cache_key in self._metadata_cache:
            return self._metadata_cache[cache_key]

        # Try by ID
        db_record = get_monster_by_id_api(str(monster_id)) if monster_id else None

        # Try by Name fallback
        if not db_record and name:
            db_record = find_monster_by_name_api(name, dungeon_id)

        self._metadata_cache[cache_key] = db_record
        return db_record

    def clear_cache(self) -> None:
        """Clears the metadata cache."""
        self._metadata_cache.clear()
