# -*- coding: utf-8 -*-
"""
Monster Data Validation Module.
Enforces validation rules across all 30 monster schema fields.
"""

from typing import Dict, Any, Tuple, Optional, List

# All 30 schema columns
SCHEMA_COLUMNS = [
    "id",
    "name",
    "level",
    "exp",
    "hp",
    "defense",
    "attackRate",
    "defenseRate",
    "hpRecharge",
    "accuracy",
    "penetration",
    "damageReduction",
    "evasion",
    "resistCritRate",
    "primaryAttackMin",
    "primaryAttackMax",
    "secondaryAttackMin",
    "secondaryAttackMax",
    "ignoreAccuracy",
    "ignoreDamageReduction",
    "ignorePenetration",
    "absoluteDamage",
    "resistSkillAmp",
    "resistCritDamage",
    "resistSuppress",
    "resistSilence",
    "resistDiffDamage",
    "hpProportionDamage",
    "serverBossType",
    "dungeonId",
]

INTEGER_FIELDS = [
    "level",
    "exp",
    "hp",
    "defense",
    "attackRate",
    "defenseRate",
    "hpRecharge",
    "accuracy",
    "penetration",
    "damageReduction",
    "evasion",
    "resistCritRate",
    "primaryAttackMin",
    "primaryAttackMax",
    "secondaryAttackMin",
    "secondaryAttackMax",
    "ignoreAccuracy",
    "ignoreDamageReduction",
    "ignorePenetration",
    "absoluteDamage",
    "resistSkillAmp",
    "resistCritDamage",
    "resistSuppress",
    "resistSilence",
    "resistDiffDamage",
    "hpProportionDamage",
]


def validate_monster_data(
    data: Dict[str, Any],
    is_new: bool = False,
    existing_monsters: Optional[List[Dict[str, Any]]] = None,
    valid_dungeons: Optional[List[str]] = None,
    valid_types: Optional[List[str]] = None,
) -> Tuple[bool, Dict[str, str], Dict[str, Any]]:
    """
    Validates a monster data dictionary against all 30 schema fields.

    Returns:
        (is_valid, errors_dict, cleaned_data)
    """
    errors: Dict[str, str] = {}
    cleaned: Dict[str, Any] = {}

    # 1. Validate ID (Required)
    m_id = str(data.get("id", "") or "").strip()
    if not m_id:
        errors["id"] = "ID không được để trống"
    else:
        cleaned["id"] = m_id
        if is_new and existing_monsters:
            for ex in existing_monsters:
                if str(ex.get("id", "")).strip() == m_id:
                    errors["id"] = f"ID '{m_id}' đã tồn tại"
                    break

    # 2. Validate Name (Required)
    name = str(data.get("name", "") or "").strip()
    if not name:
        errors["name"] = "Tên quái vật không được để trống"
    else:
        cleaned["name"] = name

    # 3. Validate Integer Fields (level & hp are required ≥ 0)
    for field in INTEGER_FIELDS:
        val = data.get(field)
        if val is None or str(val).strip() == "":
            if field in ("level", "hp"):
                errors[field] = f"{field.capitalize()} là trường bắt buộc"
            else:
                cleaned[field] = 0
            continue

        try:
            num = int(val)
            if field in ("level", "hp") and num < 0:
                errors[field] = f"{field.capitalize()} phải là số nguyên ≥ 0"
            elif num < 0:
                errors[field] = "Giá trị phải là số nguyên ≥ 0"
            else:
                cleaned[field] = num
        except (ValueError, TypeError):
            errors[field] = "Phải là số nguyên hợp lệ"

    # 4. Primary & Secondary Attack Range Validation
    p_min = cleaned.get("primaryAttackMin", 0)
    p_max = cleaned.get("primaryAttackMax", 0)
    if "primaryAttackMin" not in errors and "primaryAttackMax" not in errors:
        if p_min > p_max:
            errors["primaryAttackMin"] = "primaryAttackMin phải ≤ primaryAttackMax"

    s_min = cleaned.get("secondaryAttackMin", 0)
    s_max = cleaned.get("secondaryAttackMax", 0)
    if "secondaryAttackMin" not in errors and "secondaryAttackMax" not in errors:
        if s_min > s_max:
            errors["secondaryAttackMin"] = "secondaryAttackMin phải ≤ secondaryAttackMax"

    # 5. DungeonId FK (Required)
    d_id = data.get("dungeonId")
    if d_id is None or str(d_id).strip() in ("", "None", "null", "(None / Unassigned)", "All Locations", "All Dungeons"):
        errors["dungeonId"] = "Dungeon/Map là trường bắt buộc"
    else:
        d_str = str(d_id).strip()
        if " - " in d_str:
            d_str = d_str.split(" - ")[0].strip()
        if valid_dungeons is not None and d_str not in valid_dungeons:
            errors["dungeonId"] = f"Dungeon ID '{d_str}' không hợp lệ"
        else:
            cleaned["dungeonId"] = d_str

    # 6. ServerBossType FK (Required)
    b_type = data.get("serverBossType")
    if b_type is None or str(b_type).strip() in ("", "None", "null", "(None / Unassigned)", "All Monsters"):
        errors["serverBossType"] = "Monster Type là trường bắt buộc"
    else:
        b_str = str(b_type).strip()
        if " - " in b_str:
            b_str = b_str.split(" - ")[0].strip()
        if valid_types is not None and b_str not in valid_types:
            errors["serverBossType"] = f"Loại quái '{b_str}' không hợp lệ"
        else:
            cleaned["serverBossType"] = b_str

    # Copy over non-schema fields like 'templates', 'description', 'priority'
    for k, v in data.items():
        if k not in cleaned and k not in SCHEMA_COLUMNS:
            cleaned[k] = v

    is_valid = len(errors) == 0
    return is_valid, errors, cleaned
