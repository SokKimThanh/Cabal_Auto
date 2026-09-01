import logging
from typing import Any, Dict, List, Optional
from lib.features.hunt.config_validator import normalize_window_bounds_value

logger = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 2

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def _migrate_monster_rotation(data: Dict[str, Any]) -> None:
    """Migrate legacy 'monsters' array and normalize 'monster_rotation'."""
    if "monster_rotation" not in data or not isinstance(data["monster_rotation"], list):
        data["monster_rotation"] = []

    # Check for legacy monster fields
    if isinstance(data.get("monsters"), list):
        old_list = data["monsters"]
        new_rotation = []
        priority = 1
        for m in old_list:
            if isinstance(m, dict):
                m_id = m.get("id", m.get("monster_id", 0))
                m_id = _safe_int(m_id)
                new_rotation.append({
                    "monster_id": m_id,
                    "name": m.get("name", str(m_id)),
                    "priority": priority,
                    "dungeon_id": m.get("dungeon_id", None)
                })
                priority += 1
            elif isinstance(m, str):
                new_rotation.append({
                    "monster_id": 0,
                    "name": m,
                    "priority": priority,
                    "dungeon_id": None
                })
                priority += 1

        # Merge old monsters to monster_rotation
        for r in new_rotation:
            data["monster_rotation"].append(r)

        # Clear out old embedded monsters
        data.pop("monsters", None)

    # Process older monster_rotation if it is list of strings or list of ids
    if data.get("monster_rotation") and isinstance(data["monster_rotation"], list):
        new_rotation = []
        priority = 1
        for m in data["monster_rotation"]:
            if isinstance(m, dict):
                m_id = m.get("monster_id", m.get("id", 0))
                new_rotation.append({
                    "monster_id": _safe_int(m_id),
                    "name": m.get("name", str(m_id)),
                    "priority": _safe_int(m.get("priority", priority), priority),
                    "dungeon_id": m.get("dungeon_id", None)
                })
                priority += 1
            elif isinstance(m, (str, int)):
                new_rotation.append({
                    "monster_id": _safe_int(m),
                    "name": str(m),
                    "priority": priority,
                    "dungeon_id": None
                })
                priority += 1
        data["monster_rotation"] = sorted(new_rotation, key=lambda x: x.get("priority", 999))
        # Enforce consecutive priorities starting from 1 for neatness
        for i, entry in enumerate(data["monster_rotation"]):
            entry["priority"] = i + 1

def _migrate_skills(data: Dict[str, Any]) -> None:
    """Migrate legacy 'skills' and 'attack_keys' into 'skill_slots'."""
    legacy_skills = data.pop("skills", {})
    legacy_attack_keys = data.pop("attack_keys", [])

    skill_slots = data.get("skill_slots", [])
    if not isinstance(skill_slots, list):
        skill_slots = []

    merged_skills = {}

    # Process legacy attack keys first (lower precedence)
    if isinstance(legacy_attack_keys, list):
        for k in legacy_attack_keys:
            if isinstance(k, dict) and "key" in k:
                if "cast_time" not in k:
                    logger.warning(f"Skipping malformed attack_key entry (missing cast_time): {k}")
                    continue
                k_id = k.get("id", k["key"])
                merged_skills[k["key"]] = {
                    "id": str(k_id),
                    "key": str(k["key"]),
                    "cast_time": _safe_float(k.get("cast_time")),
                    "cooldown": _safe_float(k.get("cooldown")),
                    "type": str(k.get("type", "attack"))
                }

    # Process legacy skills (higher precedence)
    if isinstance(legacy_skills, dict):
        for slot_id, k in legacy_skills.items():
            if isinstance(k, dict) and "key" in k:
                if "cast_time" not in k:
                    logger.warning(f"Skipping malformed skill entry (missing cast_time): {k}")
                    continue
                k_key = k["key"]
                merged_skills[k_key] = {
                    "id": str(slot_id),
                    "key": str(k_key),
                    "cast_time": _safe_float(k.get("cast_time")),
                    "cooldown": _safe_float(k.get("cooldown")),
                    "type": str(k.get("type", "attack"))
                }

    # Add new ones if they don't already exist in skill_slots
    existing_keys = {s.get("key") for s in skill_slots if isinstance(s, dict)}
    for sk in merged_skills.values():
        if sk["key"] not in existing_keys:
            skill_slots.append(sk)

    data["skill_slots"] = skill_slots

def migrate_hunt_config(data: Any) -> Dict[str, Any]:
    """Migrates and normalizes the hunt config dictionary in-place."""
    if not isinstance(data, dict):
        data = {}

    # Check for schema version
    schema_version = data.get("schema_version")
    if schema_version and isinstance(schema_version, int) and schema_version >= CURRENT_SCHEMA_VERSION:
        return data

    if "ui_mode" not in data:
        data["ui_mode"] = "beginner"

    _migrate_monster_rotation(data)
    _migrate_skills(data)

    data["schema_version"] = CURRENT_SCHEMA_VERSION

    # Ensure global hotkeys exist
    if not isinstance(data.get("global_hotkeys"), dict):
        data["global_hotkeys"] = {
            "enabled": True,
            "start_key": "ctrl+shift+r",
            "stop_key": "ctrl+shift+e",
        }
    else:
        if "enabled" not in data["global_hotkeys"]:
            data["global_hotkeys"]["enabled"] = True

    # Normalize window_bounds
    hunt_area = data.get("hunt_area")
    if not isinstance(hunt_area, dict):
        data["hunt_area"] = {"window_bounds": None}
    else:
        bounds = hunt_area.get("window_bounds")
        data["hunt_area"]["window_bounds"] = normalize_window_bounds_value(bounds)

    return data
