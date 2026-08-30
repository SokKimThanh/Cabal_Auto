# Session Prompt CB4: Synchronize Skill & Monster Config Schema

Timebox: 25-30 minutes.

Objective:
Resolve data mismatch between `config_migrator.py`, `hunt_config.json`, `app_gui.py`, and `HuntOrchestrator`. Standardize on `skill_slots` and unified `monster_rotation`.

Target Files:
- Modify: `lib/features/hunt/config_migrator.py`
- Modify: `lib/features/hunt/hunt_config.py`
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `app_gui.py`

Implementation Details:
1. Standardize schema fields:
   - Use `skill_slots: List[Dict[str, Any]]` as canonical source for active attack keys, cast times, and cooldowns.
   - Remove legacy fallback lookups for `attack_keys` and raw `skills` dict.
2. In `config_migrator.py`:
   - Ensure migration safely translates older `skills: {}` or `attack_keys: []` into standardized `skill_slots`.
3. In `app_gui.py`:
   - Ensure `on_hunt_start()` exports `skill_slots` in exact format expected by `HuntOrchestrator.prepare_skill_runtime`.

Validation:
- Run: `python tests/test_migration.py`
- Test loading legacy `hunt_config.json` and verify clean export without data loss.

Session Boundary Gate:
- Verify no unhandled `KeyError` when loading empty or partially filled configuration files.
- Report PASSED/REVERTED at minute 25.