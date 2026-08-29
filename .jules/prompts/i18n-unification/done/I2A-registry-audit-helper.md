# I2A - Add A Namespace-Agnostic Registry Audit Helper

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 2 audit helper from .jules/i18n-sprint-roadmap.md.

Goal:
Add a small audit API to lib/i18n/__init__.py (e.g. get_registered_namespaces() and iter_missing_keys(namespace, langs)) and a standing test (tests/unit/test_i18n_registry_integrity.py) that discovers every *_TRANSLATIONS constant under lib/i18n/ via module introspection and asserts it is present in the live registry after import, without needing to be edited when a new dictionary is added later.

Files in scope:
- lib/i18n/__init__.py
- lib/i18n/translations.py
- tests/unit/test_i18n_registry_integrity.py (new or extend from I1B)

Boundaries:
- Keep the audit helper read-only; it must not mutate the registry.
- The test must be able to detect a newly added, non-self-registering dictionary without any test code change - prove this by temporarily adding a throwaway *_TRANSLATIONS dict without self-registration, confirming the test fails, then removing the throwaway dict before finishing.

Acceptance criteria:
- The audit test passes for all current namespaces and would fail for a hypothetical unregistered one.
- No behavior change to any currently displayed string.

Validation:
- Run `py -m pytest tests/unit/test_i18n_registry_integrity.py -v`.
- Perform the throwaway-dict failure proof described above and include the result in the final response.
```
