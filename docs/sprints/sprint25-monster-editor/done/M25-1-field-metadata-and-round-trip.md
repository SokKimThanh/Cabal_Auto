# M25-1 - Field Metadata And Round Trip

Paste `00-global-rules.md` before this prompt.

```text
Implement only one field metadata definition and pure form data round-trip behavior in MonsterEditDialog.

Files in scope:
- dialogs/monster_edit.py
- focused tests for dialog data collection only

Tasks:
- Define field metadata for every MonsterDatabase.MONSTER_COLUMNS field: key, group, widget type, default, nullable flag, validation category, and translation key.
- Define local metadata separately: priority, damage_per_hit, description, templates.
- Create pure/default/load/collect helpers driven by metadata. A new candidate gets UUID, level=1, priority=1, numeric DB defaults, nullable references=None, templates=[].
- When editing, merge form changes with a deep copy of the existing record so unknown existing keys survive.

Do not:
- Redesign visible layout, add advanced groups/reference comboboxes, change manager callback/persistence, or modify database schema.

Acceptance:
- Collecting an unchanged existing record preserves all DB columns, local metadata, and unknown keys.
- New candidate has all canonical DB keys plus local metadata.
- No field is silently converted from None to "None".

Validate: new defaults, complete existing-record round trip, unknown-key retention, and nullable reference values.
```