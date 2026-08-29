# M25-0 - Form Data Contract Audit

Paste `00-global-rules.md` before this prompt.

```text
Read-only/documentation session, 20-25 minutes.

Inspect dialogs/monster_edit.py, ui/windows/monster_manager_win.py, database.py, lib/data/monsters.json, and focused monster-editor tests. Write a short audit artifact under docs/sprints/ that records:
- every MonsterDatabase.MONSTER_COLUMNS field and its current form/persistence coverage;
- every local metadata field and its source/persistence behavior;
- the current load -> dialog -> callback -> pending_changes -> refresh -> save path;
- any current data-loss risks, including paginated refresh replacing local state;
- the current reference source for monster_type and dungeons.

Do not change Python behavior. Do not infer a DB field from a similarly named local field.

Exit condition: the next session has an explicit field inventory and one confirmed owner for each load/save responsibility.
```