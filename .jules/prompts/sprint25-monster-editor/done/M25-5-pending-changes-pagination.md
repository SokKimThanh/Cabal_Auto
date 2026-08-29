# M25-5 - Pending Changes And Pagination

Paste `00-global-rules.md` before this prompt.

```text
Harden only the MonsterEditDialog save callback, pending_changes merge, refresh/filter/page behavior in MonsterManagerWin.

Files in scope:
- ui/windows/monster_manager_win.py
- focused tests for pending changes, refresh, filter, and pagination

Tasks:
- Accept complete candidate records from MonsterEditDialog and store them in pending_changes before table refresh.
- Merge pending records into any DB page without replacing the complete local/pending dataset with a paginated result.
- Keep a newly added or edited pending record visible when possible; otherwise show a clear pending status without dropping it.
- Duplicate-name validation checks the complete data source, not only current visible page.

Do not:
- Change dialog widgets/metadata, DB schema, JSON format, or persistence implementation.

Validate: add/edit then refresh, filter, page change, duplicate name on a different page, and repeated dialog open/close. Pending data survives until M25-6 persistence confirms success.
```