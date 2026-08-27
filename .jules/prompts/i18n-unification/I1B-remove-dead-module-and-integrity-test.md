# I1B - Remove Dead i18n Module And Generalize The Integrity Test

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 1 dead-module cleanup and integrity-test generalization from .jules/i18n-sprint-roadmap.md.

Goal:
Delete the shadowed dead module lib/i18n.py (proven dead: `import lib.i18n` always resolves to the package lib/i18n/__init__.py because Python prefers packages over same-named modules in the same directory), and generalize tests/unit/test_i18n_global_registration.py into a namespace-agnostic integrity test that walks every *_TRANSLATIONS dict under lib/i18n/ and asserts each key resolves to a non-key string in both en and vi.

Files in scope:
- lib/i18n.py (delete)
- tests/unit/test_i18n_global_registration.py (or add a new tests/unit/test_i18n_registry_integrity.py)

Boundaries:
- Before deleting lib/i18n.py, run a repository-wide search for any reference to it (not lib/i18n/ or lib.i18n as a package import) to confirm it is truly unused.
- Do not change lib/i18n/__init__.py's public API.
- This session should run after I1A so the integrity test covers all four newly self-registering namespaces plus GLOBAL_TRANSLATIONS.

Acceptance criteria:
- lib/i18n.py no longer exists.
- The integrity test iterates every *_TRANSLATIONS constant discoverable under lib/i18n/ and fails if any key falls back to the raw key string in en or vi.
- `import lib.i18n` still resolves correctly to the package with no behavior change.

Validation:
- Run `py -m pytest tests/unit/ -k i18n -v`.
- Run `py .\app_gui.py` and confirm clean startup with no import errors.
```
