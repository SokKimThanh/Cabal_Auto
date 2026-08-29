# M25-4 - Reference Options And Defaults

Paste `00-global-rules.md` before this prompt.

```text
Implement only dungeon and monster-type reference options plus new-record defaults.

Files in scope:
- dialogs/monster_edit.py
- database.py only if an existing read-only reference API is demonstrably missing
- focused tests for reference/nullable behavior

Use existing get_monster_type_list() and get_dungeon_list() where available. Comboboxes display labels but candidate data persists reference IDs/values. Include an explicit empty option mapping to None.

Do not:
- Seed/alter DB tables, change filter semantics, modify manager pending/persistence, or turn missing reference data into a blocking error.

Validate: populated reference list, empty DB/reference fallback, label-to-ID mapping, None never serializes as "None", edit load preserves unmatched historical reference IDs, and new defaults do not overwrite user-entered values.
```