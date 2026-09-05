import logging
from typing import Any, Dict, List, Optional
from lib.features.hunt.config_validator import normalize_window_bounds_value

logger = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 3


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

    legacy_candidates = []

    # Check for legacy monster fields
    if "monsters" in data and isinstance(data["monsters"], list):
        legacy_candidates.extend(data["monsters"])
        data.pop("monsters", None)

    if "monster_list" in data and isinstance(data["monster_list"], list):
        legacy_candidates.extend(data["monster_list"])
        data.pop("monster_list", None)

    # If canonical rotation is empty, backfill from legacy candidates
    if not data["monster_rotation"] and legacy_candidates:
        data["monster_rotation"] = legacy_candidates

    # Process monster_rotation, normalizing format and deduplicating
    new_rotation = []
    priority = 1
    for m in data["monster_rotation"]:
        if isinstance(m, dict):
            m_id = m.get("monster_id", m.get("id", 0))
            new_rotation.append(
                {
                    "monster_id": _safe_int(m_id),
                    "name": str(m.get("name", m_id)),
                    "priority": _safe_int(m.get("priority", priority), priority),
                    "dungeon_id": m.get("dungeon_id", None),
                }
            )
            priority += 1
        elif isinstance(m, (str, int)):
            new_rotation.append(
                {
                    "monster_id": _safe_int(m),
                    "name": str(m),
                    "priority": priority,
                    "dungeon_id": None,
                }
            )
            priority += 1

    data["monster_rotation"] = sorted(
        new_rotation, key=lambda x: x.get("priority", 999)
    )

    # Deduplicate on (monster_id, dungeon_id)
    seen = set()
    deduped = []
    for entry in data["monster_rotation"]:
        key = (entry.get("monster_id"), entry.get("dungeon_id"))
        if key not in seen:
            seen.add(key)
            deduped.append(entry)
    data["monster_rotation"] = deduped

    # Enforce consecutive priorities starting from 1 for neatness
    valid_deduped = []
    for entry in data["monster_rotation"]:
        m_id = entry.get("monster_id", 0)
        if not isinstance(m_id, int) or m_id <= 0:
            logger.warning(f"Skipping malformed monster entry (invalid id): {entry}")
            continue

        m_name = entry.get("name", "")
        if isinstance(m_name, str):
            m_name = m_name.strip()
        else:
            m_name = str(m_name)

        if not m_name:
            m_name = str(m_id)

        entry["monster_id"] = m_id
        entry["name"] = m_name

        # dungeon_id
        d_id = entry.get("dungeon_id", None)
        if isinstance(d_id, str):
            d_id = d_id.strip()
            if not d_id:
                d_id = None
        entry["dungeon_id"] = d_id

        valid_deduped.append(entry)

    data["monster_rotation"] = valid_deduped

    for i, entry in enumerate(data["monster_rotation"]):
        entry["priority"] = i + 1


def _migrate_buff_slots(data: Dict[str, Any]) -> None:
    """
    Extract buff-type skills from legacy skill_slots into separate buff_slots

    Precedence:
    1. Use explicit "type" field if present
    2. If missing, lookup in skill catalog by name/id
    3. If still unresolved, default to attack lane + log warning
    """
    skill_slots = data.get("skill_slots", [])
    if not isinstance(skill_slots, list):
        skill_slots = []

    buff_slots = data.get("buff_slots", [])
    if not isinstance(buff_slots, list):
        buff_slots = []

    remaining_attack_slots = []

    from lib.features.skills.skill_repo import load_skill_library

    skill_db = load_skill_library()

    for slot in skill_slots:
        if not isinstance(slot, dict):
            continue

        skill_type = slot.get("type")

        # Step 1: Has explicit type?
        if skill_type in ("buff", "attack"):
            if skill_type == "buff":
                slot.setdefault("duration_sec", 300)  # Default duration
                if slot not in buff_slots:
                    buff_slots.append(slot)
            else:
                if slot not in remaining_attack_slots:
                    remaining_attack_slots.append(slot)
        else:
            # Step 2: Lookup in skill catalog
            skill_name = slot.get("name", "")
            catalog_type = None

            skill_entries = (
                skill_db.values()
                if isinstance(skill_db, dict)
                else skill_db
                if isinstance(skill_db, list)
                else []
            )
            for skill_entry in skill_entries:
                if isinstance(skill_entry, dict) and skill_entry.get("name") == skill_name:
                    catalog_type = skill_entry.get("type")
                    break

            if catalog_type == "buff":
                slot["type"] = "buff"
                slot.setdefault("duration_sec", 300)
                if slot not in buff_slots:
                    buff_slots.append(slot)
            elif catalog_type == "attack":
                slot["type"] = "attack"
                if slot not in remaining_attack_slots:
                    remaining_attack_slots.append(slot)
            else:
                # Step 3: Unresolved -> default to attack + log
                logger.warning(
                    f"Unclassified skill '{skill_name}' -> defaulted to attack lane"
                )
                slot["type"] = "attack"
                if slot not in remaining_attack_slots:
                    remaining_attack_slots.append(slot)

    data["skill_slots"] = remaining_attack_slots
    data["buff_slots"] = buff_slots


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
                    logger.warning(
                        f"Skipping malformed attack_key entry (missing cast_time): {k}"
                    )
                    continue
                k_id = k.get("id", k["key"])
                merged_skills[k["key"]] = {
                    "id": str(k_id),
                    "key": str(k["key"]),
                    "cast_time": _safe_float(k.get("cast_time")),
                    "cooldown": _safe_float(k.get("cooldown")),
                    "type": str(k.get("type", "attack")),
                }

    # Process legacy skills (higher precedence)
    if isinstance(legacy_skills, dict):
        for slot_id, k in legacy_skills.items():
            if isinstance(k, dict) and "key" in k:
                if "cast_time" not in k:
                    logger.warning(
                        f"Skipping malformed skill entry (missing cast_time): {k}"
                    )
                    continue
                k_key = k["key"]
                merged_skills[k_key] = {
                    "id": str(slot_id),
                    "key": str(k_key),
                    "cast_time": _safe_float(k.get("cast_time")),
                    "cooldown": _safe_float(k.get("cooldown")),
                    "type": str(k.get("type", "attack")),
                }

    # Add new ones if they don't already exist in skill_slots
    existing_keys = {s.get("key") for s in skill_slots if isinstance(s, dict)}
    for sk in merged_skills.values():
        if sk["key"] not in existing_keys:
            skill_slots.append(sk)

    # Sanitize canonical skill slots
    valid_skills = []
    for s in skill_slots:
        s_key = s.get("key")
        if not isinstance(s_key, str) or not s_key.strip():
            logger.warning(f"Skipping malformed skill entry (missing key): {s}")
            continue

        s_type = s.get("type")
        if s_type not in ("attack", "buff"):
            if s_type is not None:
                logger.warning(
                    f"Invalid skill type '{s_type}' for key {s_key}, defaulting to 'attack'"
                )
                s["type"] = "attack"

        c_time = _safe_float(s.get("cast_time", 0.0))
        if c_time < 0:
            c_time = 0.0
        s["cast_time"] = c_time

        cooldown = _safe_float(s.get("cooldown", 0.0))
        if cooldown < 0:
            cooldown = 0.0
        s["cooldown"] = cooldown

        valid_skills.append(s)

    data["skill_slots"] = valid_skills


def _sanitize_v3(data: Dict[str, Any]) -> None:
    """Run lightweight current-schema sanitizer for target_policy and skill acknowledgment metadata."""
    # target_policy
    valid_policies = {"configured_only", "all_resolved", "any_target"}
    if "target_policy" not in data or data["target_policy"] not in valid_policies:
        data["target_policy"] = "configured_only"

    # skill acknowledgment metadata
    valid_strategies = {"combo", "hotbar_cooldown", "none"}
    if "ack_strategy" not in data or data["ack_strategy"] not in valid_strategies:
        data["ack_strategy"] = "none"

    if "hotbar_roi" not in data:
        data["hotbar_roi"] = None
    elif data["hotbar_roi"] is not None:
        if not isinstance(data["hotbar_roi"], list) or len(data["hotbar_roi"]) != 4:
            data["hotbar_roi"] = None
        else:
            try:
                data["hotbar_roi"] = [int(x) for x in data["hotbar_roi"]]
            except (ValueError, TypeError):
                data["hotbar_roi"] = None

    if "ack_timeout_ms" not in data:
        data["ack_timeout_ms"] = 500
    else:
        try:
            data["ack_timeout_ms"] = int(data["ack_timeout_ms"])
        except (ValueError, TypeError):
            data["ack_timeout_ms"] = 500


def migrate_hunt_config(data: Any) -> Dict[str, Any]:
    """Migrates and normalizes the hunt config dictionary in-place."""
    if not isinstance(data, dict):
        data = {}

    # Check for schema version
    schema_version = _safe_int(data.get("schema_version", 1), 1)

    if schema_version < CURRENT_SCHEMA_VERSION:
        if "ui_mode" not in data:
            data["ui_mode"] = "beginner"

        _migrate_monster_rotation(data)
        _migrate_skills(data)

        data["schema_version"] = CURRENT_SCHEMA_VERSION

    _migrate_buff_slots(data)

    _sanitize_v3(data)

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
