# I1A - Self-Register Remaining Translation Dictionaries

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 1 self-registration migration from .jules/i18n-sprint-roadmap.md.

Goal:
Apply the same self-registration pattern already used for GLOBAL_TRANSLATIONS (see lib/i18n/translations.py) to LIBRARY_MANAGER_TRANSLATIONS, SETUP_WIZARD_TRANSLATIONS, MONSTER_EDITOR_TRANSLATIONS, and VISION_WIZARD_TRANSLATIONS, so each dictionary registers itself at import time instead of relying on its consumer window module to remember.

Files in scope:
- lib/i18n/translations.py
- lib/i18n/monster_editor_translations.py
- ui/windows/library_manager.py
- ui/windows/setup_wizard.py
- ui/windows/setup_wizard_vision.py
- ui/windows/quick_monster_editor.py

Boundaries:
- Do not change any translated copy/wording.
- Do not remove a manual i18n_register_bulk call site until the corresponding data module self-registers and you have proven (repository search) no other code path depends on the manual call's side effect or timing.
- Local fallback shim redefinitions of i18n_register_bulk (try/except ImportError) may only be removed once the self-registering import path is confirmed to work without them; do not remove them blindly.
- Preserve the existing namespace strings (e.g. "library_manager", "setup_wizard", "monster_editor", "vision_wizard") exactly.

Acceptance criteria:
- Each of the four dictionaries self-registers on import via the same pattern as GLOBAL_TRANSLATIONS.
- No consumer window module calls i18n_register_bulk manually for these four namespaces anymore.
- All four screens still render translated (non-key) strings in en and vi.

Validation:
- Run `py -m pytest tests/unit/test_i18n_global_registration.py -v`.
- Manually open Library Manager, Setup Wizard, Monster Editor, and Vision Wizard in both languages and confirm no raw keys are visible.
```
