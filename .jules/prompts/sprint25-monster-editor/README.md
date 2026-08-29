# Sprint 25 Monster Editor Prompt Pack

This pack implements [SPRINT25_MONSTER_EDITOR_FULL_FIELDS_REDESIGN.md](../../../docs/sprints/SPRINT25_MONSTER_EDITOR_FULL_FIELDS_REDESIGN.md) as small, sequential Jules sessions. Do not run the original Sprint 25 document as a single implementation session.

## Architecture boundary

- `dialogs/monster_edit.py::MonsterEditDialog` owns the visible Add/Edit form, form metadata, field load/collect/validate behavior, and template UI.
- `ui/windows/monster_manager_win.py::MonsterManagerWin` owns `pending_changes`, filters, pagination, DB/JSON persistence, and manager table refresh.
- `database.py::MonsterDatabase` owns canonical monster columns and reference reads for `dungeons` and `monster_type`.
- `lib/data/monsters.json` owns local user metadata such as priority, damage per hit, description, templates, and hunt/window state. Do not treat it as a canonical monster-catalogue replacement.

## Required execution order

1. `M25-0-form-data-contract-audit.md`
2. `M25-1-field-metadata-and-round-trip.md`
3. `M25-2-primary-form-layout.md`
4. `M25-3-advanced-groups-and-retention.md`
5. `M25-4-reference-options-and-defaults.md`
6. `M25-5-pending-changes-pagination.md`
7. `M25-6-persistence-validation-i18n-tests.md`

## Post-implementation hardening

After M25-6 passes, run the M25-X regression wave only if the Sprint 25 result needs additional proof at boundaries that are prone to silent data loss:

1. `M25-X.1-reference-and-null-guard.md`
2. `M25-X.2-hidden-field-and-unknown-key-retention.md`
3. `M25-X.3-pending-pagination-boundary.md`

`M25-X-technical-hardening-index.md` is an epic index, not a runnable session. The three hardening prompts remain separately timeboxed at `20-25 minutes`.

Each session must pass its focused validation before the next begins. `M25-5` and `M25-6` must not begin until the dialog emits a complete candidate record from M25-1 through M25-4.

M25-X runs after M25-6, in order. M25-X.1 owns reference/null mapping; M25-X.2 owns hidden/unknown-field retention; M25-X.3 owns pending/pagination persistence boundaries. Do not combine them.