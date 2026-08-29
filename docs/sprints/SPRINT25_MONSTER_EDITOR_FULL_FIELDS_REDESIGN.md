# Sprint 25 - Monster Editor Full-Field Form Redesign

**Status:** PLANNED  
**Scope:** `MonsterManagerWin` / `MonsterEditDialog`  
**Priority:** High  
**Related:** PR #108, Sprint 19 Task #2.5, Sprint 19 Task #2.6

**Execution Pack:** [.jules/prompts/sprint25-monster-editor/README.md](../../.jules/prompts/sprint25-monster-editor/README.md). Sprint 25 must run as the seven micro-sessions defined there; do not implement T1-T7 in a single session.

**Post-implementation hardening:** After M25-6 passes, run the M25-X regression wave for reference/null mapping, hidden advanced fields/unknown-key retention, and pending-pagination persistence. The three M25-X prompts are intentionally separate 20-25 minute sessions and must not be combined.

## 1. Problem Statement

PR #108 moves the monster manager window into `MonsterManagerWin`, but the Add/Edit dialog still exposes only a small subset of the database model:

- `name`
- `level`
- `priority`
- `hp`
- `damage_per_hit`
- `description`
- templates

The database model contains substantially more monster attributes, including combat, defense, resistance, boss type, and dungeon fields. Users cannot create or fully maintain a monster record from the UI. The existing hard-coded defaults also do not represent the complete database schema.

The previous Sprint 19 redesign documents describe grouping and reducing visual overload, but that design was not carried into the current `MonsterEditDialog`. This sprint completes that missing implementation.

## 2. Goals

1. Expose every supported monster database column in Add/Edit without forcing all fields into the initial viewport.
2. Group related fields so important values are immediately available and less-used values are discoverable under Advanced sections.
3. Provide safe defaults and automatic values to reduce repetitive data entry.
4. Preserve unknown or existing database values during edit.
5. Keep unsaved changes intact through refresh, filtering, pagination, and dialog reopen.
6. Add executable tests for the new form and persistence behavior.

## 3. Non-Goals

- Changing the database schema or renaming existing columns.
- Removing fields from the database because they are rarely used.
- Replacing the existing template editor workflow.
- Redesigning unrelated Hunt, Stats, or Help screens.

## 4. Database Field Inventory

The form must map to `MonsterDatabase.MONSTER_COLUMNS` in `database.py`.

### Identity and classification

- `id` - generated automatically for new records; read-only during edit
- `name` - required
- `level` - required numeric field
- `exp` - optional numeric field
- `serverBossType` - selectable reference value, nullable
- `dungeonId` - selectable dungeon reference, nullable

### Primary combat stats

- `hp`
- `primaryAttackMin`
- `primaryAttackMax`
- `secondaryAttackMin`
- `secondaryAttackMax`
- `attackRate`
- `hpRecharge`

### Defense and accuracy

- `defense`
- `defenseRate`
- `accuracy`
- `penetration`
- `damageReduction`
- `evasion`
- `ignoreAccuracy`
- `ignoreDamageReduction`
- `ignorePenetration`
- `absoluteDamage`

### Resistance stats

- `resistCritRate`
- `resistSkillAmp`
- `resistCritDamage`
- `resistSuppress`
- `resistSilence`
- `resistDiffDamage`
- `hpProportionDamage`

### Local UI metadata

These values are not database columns but remain part of the editor model where already supported:

- `priority`
- `damage_per_hit`
- `description`
- `templates`

The implementation must clearly separate database fields from local editor metadata and must not silently discard either category.

## 5. Proposed UI

### Initial view

The first tab should show the fields most users need:

- Name
- Level
- HP
- Primary attack min/max
- Secondary attack min/max
- Attack rate
- Defense
- Defense rate
- Accuracy
- Dungeon
- Boss type
- Priority

Use compact two-column rows where appropriate. Keep labels, values, and validation messages readable at the existing dialog size or a responsive larger size.

### Collapsible advanced groups

Place less frequently edited values in collapsible groups or an Advanced tab:

1. **Defense and Damage Modifiers**
   - penetration, damage reduction, evasion
   - ignore accuracy, ignore damage reduction, ignore penetration
   - absolute damage
2. **Resistances**
   - all `resist*` fields
   - hp proportion damage
3. **Metadata and Defaults**
   - exp, description, and other optional values
4. **Templates**
   - retain the existing template management UI

Collapsed groups must still load and save their values. Hidden is a presentation state, never a data-loss state.

### Display conventions

- Use `Spinbox` or validated numeric entries for integer fields.
- Use `Combobox` for `serverBossType` and `dungeonId`.
- Show nullable reference values with an explicit empty option.
- Show the generated ID as read-only in edit mode and a generated preview/status for new records.
- Use consistent units and labels; do not expose raw camelCase names to users.
- Preserve the existing bilingual i18n convention.

## 6. Automatic Defaults and Autofill

### New monster defaults

Define defaults in one field metadata table rather than scattering literals through widget construction. At minimum:

- Generate `id` with UUID.
- Set numeric fields to schema-safe zero/default values.
- Set `level` to `1`.
- Set `priority` to `1`.
- Set optional string/reference fields to `None` or empty display value.
- Set `templates` to an empty list.

### Contextual autofill

- Populate `serverBossType` from `monster_type` reference data.
- Populate `dungeonId` from the `dungeons` reference table.
- When editing, load every existing value into its corresponding field.
- When a user enters primary attack min/max or HP, do not overwrite explicit user values in other fields.
- Optional convenience presets may fill a documented group, but applying a preset must be explicit and reversible.

## 7. Data and Persistence Rules

1. Build a complete candidate monster from all form fields before invoking the callback.
2. Preserve existing values for fields not changed by the user.
3. Store new and edited records in `pending_changes` before any table refresh.
4. A refresh must merge pending records without replacing them with stale DB rows.
5. Save to DB/JSON only after validation succeeds.
6. Clear `pending_changes` only after every persistence operation succeeds.
7. On partial failure, retain unsaved records and show an actionable error.
8. Do not replace the complete monster collection with the current paginated page when saving or editing.

## 8. Validation

- `name` must be non-empty.
- Integer fields must accept only valid integers according to the existing schema policy.
- Reject invalid negative values where the field semantics require non-negative values.
- Attack min values must not exceed their matching max values.
- Nullable `serverBossType` and `dungeonId` must remain `None`, not become the string `"None"`.
- Duplicate-name behavior must check the complete data set, not only the current page.
- Validation errors stay in the dialog and must not mark the record as saved.

## 9. Implementation Tasks

### T1 - Establish field metadata

Create one metadata definition containing database key, display label, group, type, default, nullable flag, and validation rule. Use it to build/load/save the form.

### T2 - Redesign `MonsterEditDialog`

Implement grouped layout, advanced visibility behavior, read-only ID handling, reference comboboxes, and complete form population.

### T3 - Add autofill and defaults

Load reference options from the existing database APIs and apply safe defaults only when creating a new monster.

### T4 - Harden manager callback

Ensure `MonsterManagerWin` receives a complete record, merges it into pending/local state, and keeps it visible or clearly reports that it is pending when pagination/filtering excludes it.

### T5 - Harden persistence

Persist all supported fields, preserve pending changes on failure, and verify DB/JSON fallback behavior.

### T6 - Update translations and documentation

Add bilingual labels, group titles, validation messages, and a short user-facing note describing the Add/Edit groups.

### T7 - Add tests

Add focused tests for:

- New monster defaults and generated ID.
- Every DB column loading into the correct control.
- Every DB column being emitted on save.
- Collapsed advanced groups retaining values.
- Reference dropdown options and nullable values.
- Invalid numeric and min/max input.
- Duplicate names across different pagination pages.
- Refresh after dialog save preserving pending changes.
- Successful DB/JSON persistence and failed-save retention.

## 10. Acceptance Criteria

- A user can create a monster without manually entering fields that have safe defaults.
- A user can edit all fields in `MonsterDatabase.MONSTER_COLUMNS` without editing JSON or opening another tool.
- Important fields are visible immediately; less important fields are grouped and collapsed by default.
- Existing records round-trip through open, edit, save, and reload without dropped values.
- New records remain pending until the manager Save action succeeds.
- Filtering, pagination, and refresh do not erase unsaved changes.
- Duplicate-name validation considers the full data set.
- Focused tests pass on Windows and Linux CI; Tk tests use a real display or the repository's supported headless strategy.
- No unconditional module-level skips hide the new behavior.

## 11. Verification Plan

```powershell
py -m pytest tests/unit/ui/test_monster_edit_dialog_flow.py -q
py -m pytest tests/unit/ui/test_monster_editor_data.py tests/unit/ui/test_monster_editor_save.py -q
py -m pytest tests/unit/ui/test_monster_editor_info_tab.py tests/unit/ui/test_monster_editor_tabs.py -q
py -m compileall -q dialogs ui database.py
```

On Linux CI:

```bash
xvfb-run -a pytest tests/unit/ui -q
```

Manual smoke flow:

1. Open Monster Manager.
2. Click Add Monster.
3. Confirm defaults and reference dropdowns are populated.
4. Fill primary stats and save the dialog.
5. Filter or change page before manager Save.
6. Confirm the pending monster and its values remain intact.
7. Save in the manager, close, reopen, and verify every populated field.

## 12. Definition of Done

- [ ] Field metadata and grouping implemented.
- [ ] Full Add/Edit form implemented.
- [ ] Defaults and reference autofill implemented.
- [ ] Pending-change and pagination behavior verified.
- [ ] DB and JSON persistence verified.
- [ ] i18n labels and validation messages added.
- [ ] Focused Windows/Linux tests pass.
- [ ] Manual smoke flow completed.
- [ ] Documentation updated with final screenshots or layout notes.
