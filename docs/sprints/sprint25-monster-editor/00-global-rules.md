# Global Rules For Sprint 25 Monster Editor Sessions

Paste this block before each Sprint 25 prompt.

```text
Follow docs/sprints/SPRINT25_MONSTER_EDITOR_FULL_FIELDS_REDESIGN.md and .jules/prompts/sprint25-monster-editor/README.md.

Timebox and recovery:
- Maximum 30 minutes. At minute 25 stop new feature work and run the focused validation.
- Use minutes 25-30 only for direct repair of the session's change.
- At minute 30, if validation still fails or the dialog/manager cannot start, revert only the current session's reviewed diff using a deliberate patch, rerun validation, and report ABORTED/REVERTED. Never use git reset, git checkout --, or a broad discard command.

Data and ownership:
- MonsterEditDialog owns form widgets. MonsterManagerWin owns pending_changes, filter/pagination and persistence. Do not move those responsibilities across modules without a dedicated session.
- MonsterDatabase.MONSTER_COLUMNS are canonical DB fields. Preserve local metadata (priority, damage_per_hit, description, templates) as a separate model; do not silently drop either category.
- Preserve serverBossType and dungeonId as string or None. Never persist the display string "None".
- Build a complete candidate record before the callback. Preserve unknown existing keys unless the session explicitly proves they are obsolete.
- Do not replace the complete dataset with the current paginated page. Pending changes survive refresh/filter/page transitions and are cleared only after full persistence succeeds.
- DB operations spanning records/tables use explicit transactions. Local SQLite connections close in finally blocks.

UI and i18n:
- Only the Main Thread calls Tkinter methods. No background worker/service calls widgets directly.
- Use UIStyle tokens; do not add hard-coded colors. Use existing i18n namespace monster_editor and provide both en/vi keys for new visible copy.
- Dialog layout must use grid/weight/minsize and remain usable at Windows DPI 100%-150%; dimensions are targets, not absolute pixel assertions.

Before final response:
- Report PASSED or ABORTED/REVERTED, validation results, form/persistence boundary cases, i18n checks, and deferred next session.
```