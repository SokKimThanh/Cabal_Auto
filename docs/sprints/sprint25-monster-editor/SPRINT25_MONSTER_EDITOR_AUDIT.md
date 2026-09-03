# M25-0: Form Data Contract Audit

## 1. MonsterDatabase.MONSTER_COLUMNS Fields & Coverage
- **`id`**: Loaded, passed to dialog, preserved, passed back, persisted correctly.
- **`name`**: Loaded, edited in form, saved correctly.
- **`level`, `hp`**: Loaded, edited in form, saved correctly.
- **`exp`**: Loaded (if exists), but missing from form. Preserved by dialog due to deep copy of `self.monster_data`.
- **`defense`, `attackRate`, `defenseRate`, `hpRecharge`, `accuracy`, `penetration`, `damageReduction`, `evasion`, `resistCritRate`, `primaryAttackMin`, `primaryAttackMax`, `secondaryAttackMin`, `secondaryAttackMax`, `ignoreAccuracy`, `ignoreDamageReduction`, `ignorePenetration`, `absoluteDamage`, `resistSkillAmp`, `resistCritDamage`, `resistSuppress`, `resistSilence`, `resistDiffDamage`, `hpProportionDamage`**: Not presented in the current `MonsterEditDialog`. Preserved because the dialog initializes its state with `json.loads(json.dumps(monster))` and mutates known keys before calling the callback.
- **`serverBossType`**: Loaded via DB. Missing from form. Preserved by dictionary copy. DB requires it as string or None.
- **`dungeonId`**: Loaded via DB. Missing from form. Preserved by dictionary copy. DB requires it as string or None.

## 2. Local Metadata Fields
- **`priority`, `damage_per_hit`, `description`, `templates`**: Not part of `MONSTER_COLUMNS` but used locally.
  - Source: Legacy JSON fallback or loaded into the dictionary object.
  - `MonsterEditDialog` natively supports these fields, but when `insert_or_update_monster` is called on the DB layer, it iterates: `data = {k: v for k, v in monster.items() if k in columns}`.
  - **Risk**: Local metadata fields are NOT saved to the SQLite database during `insert_or_update_monster`. If JSON fallback is not running concurrently, they might be lost on DB-only loads.

## 3. Data Flow Path
- **Load**: `MonsterManagerWin` -> `_refresh_monster_table` -> calls `self.db.get_filtered_monsters()`.
- **Dialog**: `_on_edit_monster_selected` -> `_open_edit_dialog` -> instantiates `MonsterEditDialog(monster=dict)`.
- **Callback**: `on_dialog_save(updated_data)` -> appends to `self.pending_changes` dict and mutates `self.monsters`.
- **Pending Changes**: A dict mapping `id -> data`. Survives filter/pagination updates.
- **Refresh**: `_refresh_monster_table` -> reloads paginated data from DB, applies `pending_changes` on top before updating treeview.
- **Save**: `_save_monsters` -> iterates over `pending_changes.values()`, pushes to DB (`self.db.insert_or_update_monster`). Clear `pending_changes`.

## 4. Risks & Observations
- **Data-loss risk**: `MonsterDatabase.insert_or_update_monster` discards non-schema fields (metadata like `priority`, `templates`).
- **Paginated refresh replacement**: `self.monsters` is replaced completely by `self.filtered_monsters` from the paginated query, although `pending_changes` correctly patches the currently visible items.
- **DB saving risk**: Unedited DB fields are preserved in `self.monster_data`, so `insert_or_update_monster` will correctly write them back without wiping them, assuming the initial DB read fetched them.

## 5. Reference Sources
- **`monster_type`**: `database.py -> MonsterDatabase.get_monster_type_list()` (via `monster_type` table).
- **`dungeons`**: `database.py -> MonsterDatabase.get_dungeon_list()` (via `dungeons` table).

## 6. Next Session Handoff
- The next session must implement the new fields (exp, defenses, types, etc.) in the UI form using `UIStyle` tokens and preserve existing fields.
- Form owner: `MonsterEditDialog`
- Persistence owner: `MonsterManagerWin` / `MonsterDatabase`. Need to ensure metadata isn't dropped, or figure out how local metadata will be stored if the DB schema doesn't hold it.
