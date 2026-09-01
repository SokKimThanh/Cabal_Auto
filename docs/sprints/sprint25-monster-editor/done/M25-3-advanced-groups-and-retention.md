# M25-3 - Advanced Groups And Retention

Paste `00-global-rules.md` before this prompt.

```text
Implement only advanced disclosure/groups in MonsterEditDialog using existing metadata and controls.

Files in scope:
- dialogs/monster_edit.py
- focused tests for disclosure/data retention

Create clearly discoverable advanced groups for defense/damage modifiers, resistances, and optional metadata. Keep templates in their existing workflow. Hidden groups must remain loaded and emitted in the candidate record.

Do not:
- Change reference fetching, manager callback/persistence, DB schema, or template capture behavior.
- Treat grid_remove as data removal; widgets/state must survive repeated show/hide.

Validate: collapse/expand repeatedly, open/edit/save candidate without opening groups, all advanced values round trip, and long content scrolls without hiding Save/Cancel.
```