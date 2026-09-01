# Session Prompt CB4: Synchronize Skill & Monster Config Schema

Timebox: 25-30 minutes.

Objective:
Resolve data mismatch between `config_migrator.py`, `hunt_config.json`, `app_gui.py`, and `HuntOrchestrator`. Standardize on `skill_slots` and unified `monster_rotation`.

Target Files:
- Modify: `lib/features/hunt/config_migrator.py`
- Modify: `lib/features/hunt/hunt_config.py`
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `app_gui.py`

## Implementation Details

1. Standardize schema fields:
   - Use `skill_slots: List[Dict[str, Any]]` as canonical source for active attack keys, cast times, and cooldowns. Each entry: `{"id": str, "key": str, "cast_time": float, "cooldown": float, "type": "attack"|"buff", ...}` (extend as needed by CB3B's dual-lane fields, e.g. `duration_sec` for buffs).
   - Use `monster_rotation: List[Dict[str, Any]]` as the canonical unified structure for the hunt's target/monster priority list. Each entry: `{"monster_id": int, "name": str, "priority": int, "dungeon_id": Optional[str]}`, ordered by ascending `priority` (lower number = higher priority). This replaces any prior ad-hoc or per-feature monster-list representations scattered across `hunt_config.json` — confirm and enumerate exactly which legacy fields/keys currently hold this data (e.g. an old `target_list` or `monster_ids` array) before writing the migration mapping in step 2, since this schema was previously undefined and needs a concrete source-to-target field mapping.
   - Add a top-level `schema_version: int` field to `hunt_config.json` (start at `2` for this migration; treat absence of the field as `schema_version == 1` / legacy). This lets `config_migrator.py` and any loader determine whether migration is needed without re-inspecting field shapes, and makes the migration idempotent (see step 2).
   - Remove legacy fallback lookups for `attack_keys` and raw `skills` dict **only after** confirming migration runs unconditionally on load (see step 2) — do not remove the fallback and the auto-migration-on-load behavior in the same step without verifying order; a config that somehow bypasses migration and hits code with no fallback will crash.
2. In `config_migrator.py`:
   - Ensure migration safely translates older `skills: {}` or `attack_keys: []` into standardized `skill_slots`, and older monster-list fields into `monster_rotation`.
   - Conflict precedence: if a legacy config contains both `skills: {}` and `attack_keys: []` with overlapping/conflicting entries for the same key, `skills: {}` takes precedence (it carries richer per-skill metadata like cast_time/cooldown); `attack_keys` entries are only used to fill in keys not already present via `skills`.
   - Idempotency: if `schema_version >= 2` is already present, `migrate()` must be a no-op (return the config unchanged) rather than re-processing already-migrated data.
   - Backup before overwrite: before writing the migrated config back to disk, copy the existing `hunt_config.json` to `hunt_config.json.bak` (overwriting any previous `.bak`). If the write of the migrated file fails partway, the original config must still be recoverable from the backup.
   - Ensure migration runs automatically as the first step of `hunt_config.py`'s load path (i.e. `load_hunt_config()` always calls the migrator before any other field is read), so no other code path can observe a pre-migration config shape.
   - Malformed/partial legacy entries: if an individual `skills`/`attack_keys` entry is missing a required field (e.g. no `key` or no `cast_time`), skip that single entry with a logged warning rather than raising or aborting the whole migration.
3. In `app_gui.py`:
   - Ensure `on_hunt_start()` exports `skill_slots` in exact format expected by `HuntOrchestrator.prepare_skill_runtime` (per the schema in step 1), and likewise exports `monster_rotation` in the format `HuntOrchestrator` expects for target prioritization.

## Validation

- Run: `python tests/test_migration.py`
- Test loading legacy `hunt_config.json` and verify clean export without data loss.
- (Added) Idempotency test: run the migrator twice on the same legacy config; assert the second run is a no-op and produces byte-identical output to the first run's result.
- (Added) Backup test: run migration, assert `hunt_config.json.bak` exists and matches the pre-migration content.
- (Added) Conflict precedence test: construct a legacy config with both `skills` and `attack_keys` defining different `cast_time`/`key` for the same skill; assert the `skills`-derived value wins.
- (Added) Malformed entry test: construct a legacy config with one skill entry missing `cast_time`; assert migration completes, that entry is skipped with a logged warning, and all other entries migrate correctly.
- (Added) `monster_rotation` migration test: construct a legacy config using the old monster-list field(s) identified in step 1; assert it migrates into the new `monster_rotation` schema with correct `priority` ordering.

## Session Boundary Gate

- Verify no unhandled `KeyError` when loading empty or partially filled configuration files.
- Confirm migration is idempotent and runs unconditionally before any other config read.
- Confirm a `.bak` backup is written before any overwrite of the config file.
- Confirm `monster_rotation`'s schema and its legacy-field source mapping were concretely defined (not left as a placeholder) before implementation.
- Report PASSED/REVERTED at minute 25.