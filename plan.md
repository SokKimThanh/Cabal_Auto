1. **Update `lib/db/schema.py`**:
   - Redefine `skill_presets` to include `preset_id`, `class_id`, `name`, `is_default`, `description`, `created_at`, `updated_at`. Ensure `UNIQUE(class_id, name, is_default)`. Create index `idx_presets_class` on `class_id` and `idx_presets_default` on `is_default`.
   - Redefine `preset_skills` to include `preset_skill_id`, `preset_id`, `skill_id`, `lane_type`, `position`, `created_at`. Add `UNIQUE(preset_id, lane_type, position)`. Create indexes.
   - Redefine `user_preset_state` to include `state_id`, `class_id` (UNIQUE), `active_preset_id`, `preset_mode`, `last_applied`, `created_at`, `updated_at`.
   - Ensure foreign keys correctly point to `classes(class_id)`, `skills(skill_id)`, `skill_presets(preset_id)` and use `ON DELETE CASCADE` or `SET NULL` as specified.
   - Double check schema for syntax correctness.

2. **Update `lib/db/repositories/skill_preset_repository.py`**:
   - Change `create_preset` parameter from `class_name` to `class_id: int`. Update SQL accordingly.
   - Change `get_presets_by_class` parameter from `class_name` to `class_id: int`. Update SQL accordingly.
   - Update SQL in `get_preset_skills` to select `lane_type` instead of `lane`, sort by `lane_type, position`. Use `lane_type` when creating the returned structure.
   - Update `set_preset_skills` to insert `lane_type` instead of `lane`.

3. **Update `lib/db/repositories/preset_state_manager.py`**:
   - Change `get_active_preset` parameter from `class_name` to `class_id: int`. Update SQL to query by `class_id`.
   - Change `set_active_preset` parameters from `class_name` to `class_id: int`. Update SQL to insert/update by `class_id`.
   - Change `get_preset_mode` parameter from `class_name` to `class_id: int`. Update SQL.
   - Change `reset_to_default` parameter from `class_name` to `class_id: int`. Update inner calls to `get_presets_by_class` and `set_active_preset`.

4. **Update `lib/features/skills/skill_preset_service.py`**:
   - Update methods `apply_preset`, `create_custom_preset`, `list_presets_by_class` to take `class_id: int` instead of `class_name`. Update internal repository calls.
   - Update `migrate_legacy_presets` to take both `class_id: int` and `class_name: str` (for logging). Update internal calls.

5. **Run Pre-Commit Checks**: Call `pre_commit_instructions` tool for guidance and follow it.
