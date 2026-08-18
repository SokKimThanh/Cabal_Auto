"""
Monster Service - Business logic and validation utilities for monster data.

Provides functions for duplicate name checking, unique name generation with indexed suffixes,
and ID validation.
"""

from typing import Any, Dict, List, Optional
import re
import uuid


def check_duplicate_name(
    monsters: List[Dict[str, Any]],
    name: str,
    current_id: Optional[str] = None
) -> bool:
    """
    Check if a monster name already exists in the monsters list.

    Args:
        monsters: List of monster dictionaries.
        name: Monster name to check.
        current_id: ID of monster currently being edited (ignored during check).

    Returns:
        bool: True if a duplicate name exists for a different monster ID, False otherwise.
    """
    if not name:
        return False

    target_name = name.strip().lower()
    for monster in monsters:
        m_id = str(monster.get('id', ''))
        m_name = str(monster.get('name', '')).strip().lower()

        if current_id and m_id == str(current_id):
            continue

        if m_name == target_name:
            return True

    return False


def generate_unique_name(
    monsters: List[Dict[str, Any]],
    name: str,
    current_id: Optional[str] = None
) -> str:
    """
    Generate a unique monster name by appending an index suffix (e.g. "Quái Mới (1)").

    Args:
        monsters: List of monster dictionaries.
        name: Base monster name.
        current_id: ID of monster currently being edited.

    Returns:
        str: Unique monster name.
    """
    base_name = name.strip() if name else "Quái Mới"

    # Remove existing trailing index suffix if present (e.g. "Quái Mới (2)" -> "Quái Mới")
    match = re.search(r"^(.*?)\s*\(\d+\)$", base_name)
    if match:
        root_name = match.group(1).strip()
    else:
        root_name = base_name

    candidate = base_name
    index = 1

    while check_duplicate_name(monsters, candidate, current_id):
        candidate = f"{root_name} ({index})"
        index += 1

    return candidate


def ensure_unique_monster_id(
    monster_data: Dict[str, Any],
    existing_monsters: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Ensure monster_data has a valid unique ID.

    Args:
        monster_data: Monster dictionary.
        existing_monsters: Optional list of existing monsters to verify uniqueness.

    Returns:
        str: Unique monster ID.
    """
    existing_ids = set()
    if existing_monsters:
        for m in existing_monsters:
            if m.get('id'):
                existing_ids.add(str(m['id']))

    m_id = str(monster_data.get('id', '')).strip()
    if not m_id or m_id in existing_ids:
        m_id = str(uuid.uuid4())
        monster_data['id'] = m_id

    return m_id
