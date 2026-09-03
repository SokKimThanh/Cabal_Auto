# M25-0 Form Data Contract Audit

## MonsterDatabase.MONSTER_COLUMNS Coverage
- `id`: System field, managed via UUID generation for new records or preserved for existing ones. Persisted correctly.
- `name`: Handled by `name_entry` in `dialogs/monster_edit.py`. Persisted properly. Validated for uniqueness.
- `level`: Handled by `level_spinbox`. Persisted.
- `exp`: Form field mapped in `DB_COLUMNS`. Persisted.
- `hp`: Handled by `hp_entry`. Persisted.
- `defense`: Form field mapped. Persisted.
- `attackRate`, `defenseRate`, `hpRecharge`, `accuracy`, `penetration`, `damageReduction`, `evasion`, `resistCritRate`, `primaryAttackMin`, `primaryAttackMax`, `secondaryAttackMin`, `secondaryAttackMax`, `ignoreAccuracy`, `ignoreDamageReduction`, `ignorePenetration`, `absoluteDamage`, `resistSkillAmp`, `resistCritDamage`, `resistSuppress`, `resistSilence`, `resistDiffDamage`, `hpProportionDamage`: Mapped via `DB_COLUMNS` and dynamically generated entry fields. Persisted.
- `serverBossType`: Handled via combobox in reference tab. Persisted (handled as nullable/empty string).
- `dungeonId`: Handled via combobox in reference tab. Persisted (handled as nullable/empty string).

All DB columns are fully mapped to dynamic widget creation via `DB_COLUMNS` metadata in `MonsterEditDialog` and persisted via `MonsterDatabase.insert_or_update_monster`.

## Local Metadata Fields Coverage
- `priority`: Mapped in `LOCAL_METADATA` as spinbox.
- `damage_per_hit`: Mapped in `LOCAL_METADATA` as entry.
- `description`: Mapped in `LOCAL_METADATA` as text widget.
- `templates`: Custom widget handling image templates.

These are preserved locally in JSON format (via `DataSyncManager` or fallback JSON save) but *not* saved to the SQLite DB `monsters` table directly as columns. The fallback syncs DB properties into the JSON alongside local keys.

## Load -> Dialog -> Callback -> Pending Changes -> Refresh -> Save Path
1. `_open_edit_dialog` creates/re-uses `MonsterEditDialog`.
2. Dialog extracts fields on save, checks for duplicates, and calls `on_save_callback`.
3. The callback stores the returned dictionary into `self.pending_changes[m_id] = updated_data` and conditionally appends/updates `self.monsters`.
4. Then `_refresh_monster_table()` is called, which fetches a fresh page from `self.db.get_filtered_monsters(...)`.
5. The `_refresh_monster_table` loops over `self.filtered_monsters` and overwrites elements with `self.pending_changes.get(...)`.
6. Clicking "Save" flushes `self.pending_changes` to the DB via `db.insert_or_update_monster()` (and/or JSON via sync fallback), then calls `pending_changes.clear()`.

## Data-Loss Risks
- Duplicate name check (`check_duplicate_name`) currently checks against `self.monsters` (the *currently visible page* of results). If a duplicate exists on page 2, and the user edits/creates on page 1, the duplicate name check will incorrectly allow it. (Risk identified in task instructions).
- When a new monster is created and `_refresh_monster_table` is called, the new monster might not belong to the current page. The new monster is added to `self.monsters`, but then `_refresh_monster_table` pulls data from DB and overwrites `self.monsters = self.filtered_monsters`. If the new item isn't on the DB page, it disappears from the UI, even though it's still in `pending_changes`! It will be saved when "Save" is clicked, but user feedback is lost. (Risk identified in task instructions).

## Reference Source
- `monster_type`: Uses `MonsterDatabase.get_monster_types()` (alias `get_monster_type_list()`).
- `dungeons`: Uses `MonsterDatabase.get_dungeons()` (alias `get_dungeon_list()`).
