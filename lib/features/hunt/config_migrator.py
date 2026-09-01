from typing import Any, Dict, List, Optional

from lib.features.hunt.config_validator import normalize_window_bounds_value

import logging

logger = logging.getLogger(__name__)

def migrate_hunt_config(data: Any) -> Dict[str, Any]:
    """Migrates and normalizes the hunt config dictionary in-place."""
    if not isinstance(data, dict):
        data = {}

    # Check for schema version
    schema_version = data.get("schema_version")
    if schema_version and isinstance(schema_version, int) and schema_version >= 2:
        return data

    if "ui_mode" not in data:
        data["ui_mode"] = "beginner"

    # Migrate monster rotation
    if "monster_rotation" not in data:
        data["monster_rotation"] = []

    # Check for legacy monster fields
    if isinstance(data.get("monsters"), list):
        old_list = data["monsters"]
        new_rotation = []
        priority = 1
        for m in old_list:
            if isinstance(m, dict):
                m_id = m.get("id", m.get("monster_id", 0))
                if isinstance(m_id, str) and m_id.isdigit():
                    m_id = int(m_id)
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
                    "monster_id": int(m_id) if str(m_id).isdigit() else 0,
                    "name": m.get("name", str(m_id)),
                    "priority": m.get("priority", priority),
                    "dungeon_id": m.get("dungeon_id", None)
                })
                priority += 1
            elif isinstance(m, (str, int)):
                new_rotation.append({
                    "monster_id": int(m) if str(m).isdigit() else 0,
                    "name": str(m),
                    "priority": priority,
                    "dungeon_id": None
                })
                priority += 1
        data["monster_rotation"] = sorted(new_rotation, key=lambda x: x.get("priority", 999))
        # Enforce consecutive priorities starting from 1 for neatness
        for i, entry in enumerate(data["monster_rotation"]):
            entry["priority"] = i + 1

    # Check for legacy skills field
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
                    "cast_time": float(k.get("cast_time", 0.0)),
                    "cooldown": float(k.get("cooldown", 0.0)),
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
                    "cast_time": float(k.get("cast_time", 0.0)),
                    "cooldown": float(k.get("cooldown", 0.0)),
                    "type": str(k.get("type", "attack"))
                }

    # Add new ones if they don't already exist in skill_slots
    existing_keys = {s.get("key") for s in skill_slots if isinstance(s, dict)}
    for sk in merged_skills.values():
        if sk["key"] not in existing_keys:
            skill_slots.append(sk)

    data["skill_slots"] = skill_slots

    data["schema_version"] = 2

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
