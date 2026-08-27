# P0 - Baseline i18n Inventory

Paste `00-global-rules.md` first, then this prompt.

```text
Read .jules/i18n-sprint-roadmap.md and inspect every *_TRANSLATIONS dictionary and every i18n_register_bulk call site in the repository. Produce a short inventory document at .jules/i18n-cleanup-baseline.md.

Scope:
- lib/i18n.py
- lib/i18n/__init__.py
- lib/i18n/translations.py
- lib/i18n/monster_editor_translations.py
- ui/windows/library_manager.py
- ui/windows/setup_wizard.py
- ui/windows/setup_wizard_vision.py
- ui/windows/quick_monster_editor.py
- app_gui.py
- existing tests under tests/ that reference i18n

Deliverable:
- A table of every *_TRANSLATIONS dict: namespace, source file, current registration mechanism (self-register vs manual vs fallback shim).
- A list of every local fallback re-definition of i18n_register_bulk (try/except ImportError shims) and whether it could silently swallow a real import failure.
- A suggested order for Sprint 1 sessions if any dictionary has hidden coupling (e.g. shared namespace with another module).
```
