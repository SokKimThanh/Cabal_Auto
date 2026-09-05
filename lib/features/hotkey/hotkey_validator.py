def validate_hotkey_no_conflict(combo_key, skill_slots, existing_hotkeys):
    """
    Check if combo_key conflicts with:
    1. Any attack skill key
    2. Any buff skill key
    3. Any app-wide hotkey (pause, resume, emergency stop)
    """
    # Collect all assigned keys
    occupied_keys = set()
    for slot in skill_slots:
        if isinstance(slot, dict) and slot.get("key"):
            occupied_keys.add(slot["key"].lower())

    # Check against app hotkeys (global_hotkeys in config)
    for hotkey in existing_hotkeys.values():
        if isinstance(hotkey, str):
            occupied_keys.add(hotkey.lower())

    if combo_key.lower() in occupied_keys:
        return (
            False,
            f"Hotkey conflict: {combo_key} already used by skill or app hotkey",
        )
    return True, None
