# M25-2 - Primary Form Layout

Paste `00-global-rules.md` before this prompt.

```text
Implement only the initial visible MonsterEditDialog form using M25-1 field metadata.

Files in scope:
- dialogs/monster_edit.py
- focused UI tests for primary controls

Show: read-only ID, name, level, HP, primary/secondary attack min/max, attack rate, defense, defense rate, accuracy, dungeon placeholder, boss-type placeholder, and priority. Use compact two-column grid rows, UIStyle, i18n keys, and minsize/weight for DPI-safe layout.

Do not:
- Add the actual reference data loading, advanced groups, persistence changes, or template workflow changes.
- Remove existing template/settings tabs, callbacks, StringVars, or compatibility attributes.

Validate: edit record populates primary controls, new record defaults display, read-only ID behavior, min/max controls remain usable at DPI 100%-150%, and vi/en labels have no raw keys.
```