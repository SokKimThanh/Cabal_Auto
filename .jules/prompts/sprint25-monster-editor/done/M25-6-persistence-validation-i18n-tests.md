# M25-6 - Persistence, Validation, i18n And Tests

Paste `00-global-rules.md` before this prompt.

```text
Complete Sprint 25 only after M25-1 through M25-5 have passed.

Files in scope:
- dialogs/monster_edit.py
- ui/windows/monster_manager_win.py
- focused monster-editor tests
- lib/i18n/monster_editor_translations.py only for required en/vi keys
- docs/sprints/SPRINT25_MONSTER_EDITOR_FULL_FIELDS_REDESIGN.md status/checklist only

Tasks:
- Validate required name, integer fields, non-negative semantic values, primary/secondary min<=max, nullable reference mapping, and duplicate name across complete data.
- Persist all supported DB fields while preserving local metadata through the existing DB/JSON fallback contract.
- Clear pending_changes only after every required persistence operation succeeds; retain it with actionable error on partial failure.
- Add only needed bilingual labels/group titles/validation copy.
- Add focused tests for full DB-field emission, persistence success/failure retention, nullable references, min/max validation, and language labels.

Do not:
- Alter database schema, drop unknown keys, replace user library data with canonical catalogue rows, or add unrelated UI redesign.

Validation:
- Run the focused Sprint 25 pytest paths from the sprint document.
- Run py -m compileall -q dialogs ui database.py.
- Manually add/edit a record, change filter/page before manager save, verify pending retention, save/reopen, and check vi/en labels.
```