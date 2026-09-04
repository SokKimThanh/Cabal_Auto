import re

with open("lib/features/hunt/config_migrator.py", "r", encoding="utf-8") as f:
    content = f.read()

migrator_code = """def _migrate_skills(data: Dict[str, Any]) -> None:
    \"\"\"Migrate legacy 'skills' and 'attack_keys' into 'skill_slots' and 'buff_slots'.\"\"\"
    from lib.features.skills.skill_repo import load_skill_library
    skills_db = load_skill_library() or {}

    legacy_skills = data.pop("skills", {})
    legacy_attack_keys = data.pop("attack_keys", [])

    skill_slots = data.get("skill_slots", [])
    if not isinstance(skill_slots, list):
        skill_slots = []

    buff_slots = data.get("buff_slots", [])
    if not isinstance(buff_slots, list):
        buff_slots = []

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
                    "type": str(k.get("type", ""))
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
                    "type": str(k.get("type", ""))
                }

    # Add new ones if they don't already exist in skill_slots + buff_slots
    existing_keys = {s.get("key") for s in skill_slots + buff_slots if isinstance(s, dict)}
    for sk in merged_skills.values():
        if sk["key"] not in existing_keys:
            skill_slots.append(sk)

    # Also we should iterate all of them to categorize correctly
    all_slots = skill_slots + buff_slots

    attacks = []
    buffs = []

    # Sanitize canonical skill slots
    for s in all_slots:
        if not isinstance(s, dict):
            continue

        s_key = s.get("key")
        if not isinstance(s_key, str) or not s_key.strip():
            logger.warning(f"Skipping malformed skill entry (missing key): {s}")
            continue

        s_name = s.get("name", "")
        if not s_name:
            # Fallback to key or lookup
            s_name = s_key
            for db_key, db_skill in skills_db.items():
                if db_skill.get("key") == s_key:
                    s_name = db_skill.get("name", s_key)
                    break
            s["name"] = s_name

        s_type = s.get("type", "")
        # Resolve type via DB if missing or invalid
        if s_type not in ("attack", "buff"):
            # Lookup type in db
            resolved_type = "attack"
            found = False
            for db_key, db_skill in skills_db.items():
                if db_skill.get("name") == s_name or db_skill.get("key") == s_key:
                    resolved_type = db_skill.get("type", "attack")
                    found = True
                    break
            if not found:
                logger.warning(f"Skill '{s_name}' (key {s_key}) missing type or invalid '{s_type}'. Fallback to 'attack', cast_time 1.0, cd 1.0.")
                s["cast_time"] = _safe_float(s.get("cast_time", 1.0)) if s.get("cast_time") else 1.0
                s["cooldown"] = _safe_float(s.get("cooldown", 1.0)) if s.get("cooldown") else 1.0
            s_type = resolved_type

        s["type"] = s_type

        c_time = _safe_float(s.get("cast_time", 1.0))
        if c_time < 0: c_time = 0.0
        s["cast_time"] = c_time

        cooldown = _safe_float(s.get("cooldown", 1.0))
        if cooldown < 0: cooldown = 0.0
        s["cooldown"] = cooldown

        if s_type == "buff":
            buffs.append(s)
        else:
            attacks.append(s)

    data["skill_slots"] = attacks
    data["buff_slots"] = buffs
"""

content = re.sub(r'def _migrate_skills\(data: Dict\[str, Any\]\) -> None:\n(?:.*\n)*?        valid_skills\.append\(s\)\n\n    data\["skill_slots"\] = valid_skills', migrator_code.strip(), content)

with open("lib/features/hunt/config_migrator.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
