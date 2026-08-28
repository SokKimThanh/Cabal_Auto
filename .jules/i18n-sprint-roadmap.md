# i18n Unification Sprint Roadmap

## 1. Context and objective

On 2026-08-27, `app_gui.py` shipped with `GLOBAL_TRANSLATIONS` imported but never registered into the i18n registry, because a prior refactor (commit `c597c60`, "decompose app_gui God Class") reorganized the import block and silently dropped a bare module-level `i18n_register_bulk(...)` statement that sat next to the imports. The user-visible symptom: every `self._t(key)` call returned the raw key instead of an English/Vietnamese string.

The immediate bug was fixed by making `GLOBAL_TRANSLATIONS` self-register on import (see `lib/i18n/translations.py`) and adding a regression test (`tests/unit/test_i18n_global_registration.py`). But the underlying design is still fragile and will not scale:

- Translation data lives as plain Python dicts scattered across `lib/i18n/translations.py` and `lib/i18n/monster_editor_translations.py`.
- Several dictionaries (`LIBRARY_MANAGER_TRANSLATIONS`, `SETUP_WIZARD_TRANSLATIONS`, `MONSTER_EDITOR_TRANSLATIONS`, `VISION_WIZARD_TRANSLATIONS`) are still registered manually inside the consumer window module (`ui/windows/*.py`) instead of at the data source — the exact pattern that caused the original bug.
- There is a dead, shadowed duplicate module `lib/i18n.py` sitting next to the real package `lib/i18n/__init__.py`, which is confusing and risks someone editing the wrong file.
- Adding a brand-new screen today requires a developer to remember, unprompted, to call `register_bulk(namespace, MY_TRANSLATIONS)` somewhere convenient — there is no enforced, discoverable convention, and no test fails if they forget.
- The dict-based design does not scale cleanly to 3+ languages: every new language means editing every dict by hand across every file, with no tooling to detect missing keys per language, and no non-developer-friendly way to manage copy.

### Goal

Move from "scattered self-registering dicts" (Sprint 1, already partially applied) to a single, enforced, discoverable registration contract (Sprint 2), then to a database-backed translation store with a hydration layer (Sprint 3-4) that scales to any number of languages without code changes, while keeping full backward compatibility with the existing `t(key, ns=..., lang=...)` API so no call site outside the i18n layer itself needs to change.

### Non-goals

- Rewriting the whole UI string layer in one PR.
- Introducing a heavyweight i18n framework/dependency (e.g. gettext/babel) — the existing `t()`/namespace model is good enough and already used everywhere; we are hardening and extending it, not replacing its call-site API.
- Changing existing translated copy/wording.

## 2. Principles for every sprint

1. Keep each PR scoped to one responsibility boundary, same discipline as `architecture-sprint-roadmap.md`.
2. Never leave a translation dictionary that is imported somewhere without a way to prove (via test) that it is actually registered.
3. Any new registration mechanism must keep `lib.i18n.t()` / `lib.i18n.register_bulk()` / `lib.i18n.GLOBAL_NS` as the stable public API — consumer code (`app_gui.py`, `ui/windows/*.py`, dialogs) should not need to change how it calls `_t()`.
4. Prefer self-registration at the data source (module-level side effect on import) over "remember to call register_bulk from the consumer" — this is the exact class of bug that started this roadmap.
5. Add an automated integrity test after each sprint that would have caught the original 2026-08-27 regression, and expand it to cover the new mechanism.
6. Database migration must be additive and reversible: dict files remain as the seed/fallback source until the DB-backed path is proven, so the app never has a moment where translations are missing.

## 3. Current state summary (as of 2026-08-27)

### Files carrying i18n debt

- `lib/i18n.py` — dead, shadowed flat module (never imported; `lib/i18n/__init__.py` always wins). Confusing duplicate, not yet deleted.
- `lib/i18n/__init__.py` — the real registry (`register`, `register_bulk`, `t`, `get_lang`, `set_default_lang`, `GLOBAL_NS`).
- `lib/i18n/translations.py` — `GLOBAL_TRANSLATIONS` (self-registers, fixed 2026-08-27), plus `LIBRARY_MANAGER_TRANSLATIONS` and `SETUP_WIZARD_TRANSLATIONS` (still manually registered by their consumer window modules).
- `lib/i18n/monster_editor_translations.py` — `MONSTER_EDITOR_TRANSLATIONS`, registered manually from `ui/windows/quick_monster_editor.py`.
- `ui/windows/setup_wizard_vision.py` — `VISION_WIZARD_TRANSLATIONS`, registered manually in the same file.
- `ui/windows/library_manager.py`, `ui/windows/setup_wizard.py`, `ui/windows/quick_monster_editor.py` — each contains its own manual `i18n_register_bulk(...)` call plus, in some cases, a **local fallback shim redefinition of `i18n_register_bulk`** guarded by `try/except ImportError` (see `ui/windows/setup_wizard.py:53`, `ui/windows/setup_wizard_vision.py:68`, `ui/windows/quick_monster_editor.py:77`) — an additional footgun: if the real import silently fails, a no-op shim swallows registration with no visible error.
- `tests/unit/test_i18n_global_registration.py` — regression guard for `GLOBAL_TRANSLATIONS` only; does not cover the other namespaces.

### Observed anti-patterns to eliminate

- Registration responsibility living in the consumer instead of the data module.
- Silent `try/except: pass` around registration calls.
- Local per-file fallback re-definitions of `register_bulk` that can mask a real import failure.
- No single place that lists "all namespaces that must be registered" — impossible to audit completeness.
- No support for adding a language without touching every dict file by hand.

## 4. Sprint plan

## Sprint 1 — Stabilize and unify the existing dict-based registry

### Objective

Apply the same self-registration fix already done for `GLOBAL_TRANSLATIONS` to every remaining translation dictionary, and remove the dead duplicate module, so there is exactly one correct place to look for i18n data and one correct way to register it.

### Files in scope

- `lib/i18n.py` (delete)
- `lib/i18n/translations.py`
- `lib/i18n/monster_editor_translations.py`
- `ui/windows/library_manager.py`
- `ui/windows/setup_wizard.py`
- `ui/windows/setup_wizard_vision.py`
- `ui/windows/quick_monster_editor.py`
- `tests/unit/test_i18n_global_registration.py`

### Planned changes

- I1A: Make `LIBRARY_MANAGER_TRANSLATIONS`, `SETUP_WIZARD_TRANSLATIONS`, `MONSTER_EDITOR_TRANSLATIONS`, `VISION_WIZARD_TRANSLATIONS` self-register at the bottom of their own data module (same pattern as `GLOBAL_TRANSLATIONS`). Remove the now-redundant manual `i18n_register_bulk(...)` calls and the local fallback shim redefinitions from the consumer window modules, after proving via repository search that nothing else depends on the shim behavior.
- I1B: Delete `lib/i18n.py` (proven dead: `import lib.i18n` always resolves to the package). Generalize the regression test into an integrity test that iterates every `*_TRANSLATIONS` dict discoverable in `lib/i18n/` and asserts each key resolves to a non-key string in both `en` and `vi`.

### Acceptance criteria

- No translation dictionary depends on a consumer module remembering to register it.
- `lib/i18n.py` no longer exists; only the package remains.
- The integrity test fails if any future dict is added without self-registration.
- No behavior change in currently displayed strings.

### Validation checklist

- `py -m pytest tests/unit/test_i18n_global_registration.py -v`
- `py .\app_gui.py` starts with no i18n-related console warnings.
- Manually open Setup Wizard, Library Manager, Monster Editor, Vision Wizard and confirm translated (not raw-key) labels in both `en` and `vi`.

---

## Sprint 2 — Enforced, discoverable registration contract for new screens

### Objective

Make it impossible for a future screen to ship with untranslated raw keys without a test catching it, without relying on developer memory.

### Files in scope

- `lib/i18n/__init__.py`
- `lib/i18n/translations.py`
- new: `tests/unit/test_i18n_registry_integrity.py`
- new: `docs/guides/I18N_GUIDE.md`
- `CODING_RULES_QUICK_REFERENCE.md`

### Planned changes

- I2A: Add a lightweight registry audit helper in `lib/i18n/__init__.py`, e.g. `get_registered_namespaces()` / `iter_missing_keys(namespace, langs)`, and a test that walks every `*_TRANSLATIONS` constant defined under `lib/i18n/**` (via `pkgutil`/module introspection) and asserts it is present in the live registry after import. This generalizes Sprint 1's integrity test into a standing contract, not a one-off.
- I2B: Write `docs/guides/I18N_GUIDE.md`: the mandatory pattern for adding a new bilingual screen (data dict + self-register at the bottom of its own module; namespace naming convention; how the audit test will catch a mistake). Add a short pointer to it in `CODING_RULES_QUICK_REFERENCE.md`.

### Acceptance criteria

- The audit test is namespace-agnostic: it does not need editing when a new `*_TRANSLATIONS` dict is added, as long as the dict lives under `lib/i18n/` and follows the self-register convention.
- A developer (or Jules session) adding a new screen has a single documented pattern to follow, and CI would fail loudly if they skip registration.

### Validation checklist

- `py -m pytest tests/unit/test_i18n_registry_integrity.py -v`
- Add a throwaway test-only translations dict without self-registering it; confirm the audit test fails; remove the throwaway dict.

---

## Sprint 3 — Database-backed translation store (foundation)

### Objective

Introduce a persistent, structured store for `(namespace, key, lang) -> text` so translations can scale past 2 languages and be edited without touching Python source, while keeping the existing dict files working as the seed/fallback data source (no big-bang cutover).

### Files in scope

- new: `lib/db/services/translation_service.py` (200-300 line budget, per repo DB service convention)
- new: `scripts/migrate_translations_to_db.py`
- `database.py` (schema init hook)
- `lib/i18n/__init__.py`

### Planned changes

- I3A: Design the schema:
  ```sql
  CREATE TABLE IF NOT EXISTS translations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      namespace TEXT NOT NULL,
      key TEXT NOT NULL,
      lang TEXT NOT NULL,
      text TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      UNIQUE(namespace, key, lang)
  );
  ```
  Implement `TranslationService` (in `lib/db/services/`, following the existing repository connection/`finally: close()` convention) with `get_all(namespace=None)`, `upsert(namespace, key, lang, text)`, `bulk_upsert(namespace, translations)`, wrapped in an explicit transaction for multi-row bulk writes.
  Implement `scripts/migrate_translations_to_db.py`: a one-time, idempotent importer that reads every existing `*_TRANSLATIONS` dict (via the Sprint 2 audit helper) and upserts it into the `translations` table, safe to re-run.
- I3B: Add a hydration path in `lib/i18n/__init__.py`: on first use (or an explicit `load_from_db()` call during app startup), read all rows from `TranslationService.get_all()` and feed them through the existing `register()` function, so the in-memory registry becomes a cache populated from DB. If the DB is empty or unavailable, fall back to the dict-based self-registration already in place (Sprint 1) — the app must never show raw keys because of a DB hiccup.

### Acceptance criteria

- Existing behavior is unchanged: every screen still renders identically, whether translations came from dicts or DB.
- DB is additive: deleting the DB file does not break the app (dict fallback still works).
- Migration script is idempotent and safe to run multiple times.

### Validation checklist

- Run `scripts/migrate_translations_to_db.py`, then delete `monsters.db`'s translations table and confirm fallback to dicts still works.
- `py -m pytest tests/unit/test_i18n_registry_integrity.py -v` still passes with DB-hydrated data.

---

## Sprint 4 — Migrate consumers and add language-scale tooling

### Objective

Make the DB-backed store the single source of truth, remove now-redundant manual registration call sites, and prove the design scales to a 3rd language end-to-end.

### Files in scope

- `app_gui.py`
- `ui/windows/*.py` (all remaining manual `i18n_register_bulk` call sites)
- new: `scripts/i18n_report.py`

### Planned changes

- I4A: Remove remaining manual `i18n_register_bulk(...)` call sites in consumer modules now that hydration happens centrally at startup (guided by repository search per the "prove callers moved" rule); keep the dict files as the DB seed data (not deleted), so `scripts/migrate_translations_to_db.py` still has a source of truth to import from.
- I4B: Add `scripts/i18n_report.py`: a CLI that reports, per namespace, which keys are missing a translation for a given language (diffing DB rows against the superset of keys across all languages). Use this tool to add a 3rd language (e.g. `zh` or `ko`, whichever the team plans next) for a small representative namespace (e.g. `GLOBAL_NS`'s top 10 most-visible strings), end-to-end, as proof the architecture scales without code changes — only DB rows and a `set_default_lang()`/language-selector UI option are needed.

### Acceptance criteria

- No consumer module calls `register_bulk` directly anymore; all registration flows through the DB hydration path (dict files remain solely as seed data for migration).
- `scripts/i18n_report.py` correctly flags missing keys when a language is incomplete.
- Adding a 3rd language for the pilot namespace requires zero Python code changes — only data.

### Validation checklist

- `py -m pytest tests/unit/test_i18n_registry_integrity.py tests/unit/test_i18n_global_registration.py -v`
- Manually switch language to the pilot 3rd language and confirm the pilot namespace renders correctly; confirm other namespaces still fall back to `en`/`vi` without crashing.

---

## Sprint 5 — Final consolidation and guardrails

### Objective

Lock in the new architecture as the permanent design, matching the "Definition of done" discipline used in `architecture-sprint-roadmap.md`.

### Files in scope

- `.jules/i18n-sprint-roadmap.md` (status update)
- `docs/guides/I18N_GUIDE.md`
- repo memory (`/memories/repo/i18n-conventions.md`)
- full test suite

### Tasks

- Confirm no dead registration code paths remain (search for `register_bulk` usages; every call site should be either inside `lib/i18n/` internals or the migration script).
- Search UI/consumer modules for active or commented manual-registration references and local no-op registration fallback shims; remove stale code/comments only after proving they are obsolete.
- Update `docs/guides/I18N_GUIDE.md` to describe the DB-backed flow as current (Sprint 2's doc described the pre-DB interim state).
- Update repo memory with the final architecture summary and the location of the audit/report tools.
- Run the full targeted i18n test suite plus a full app smoke start.

### Acceptance criteria

- A new screen needing translations only needs: (1) add rows via `scripts/i18n_report.py`-compatible data or a future admin UI, (2) call `self._t(key, ns=my_namespace)` — no manual registration step, and the audit test would fail if the namespace's data path is wired incorrectly.
- Full test suite green; `py .\app_gui.py` starts clean.
- No stale manual-registration comment, local fallback shim, or dead consumer-side registration code remains in UI modules.

## 5. Test plan by sprint

### Required baseline check for every sprint

1. `py -m pytest tests/unit/test_i18n_global_registration.py -v`
2. `py .\app_gui.py` starts without i18n console warnings.
3. Manual spot check of at least 2 screens in both `en` and `vi`.

### Recommended targeted tests added along the way

- `tests/unit/test_i18n_registry_integrity.py` (Sprint 2) — namespace-agnostic completeness audit.
- DB fallback test (Sprint 3) — DB absent/empty still renders correct strings.
- Missing-key report test (Sprint 4) — `scripts/i18n_report.py` correctly flags gaps.

## 6. Suggested PR limits

- Sprint 1: two PRs (I1A self-registration migration, I1B dead-module removal + integrity test).
- Sprint 2: two PRs (I2A audit helper + test, I2B docs).
- Sprint 3: two PRs (I3A schema/service/migration script, I3B hydration wiring).
- Sprint 4: two PRs (I4A consumer cleanup, I4B report tool + pilot language).
- Sprint 5: one PR (final consolidation).

## 7. Definition of done for the i18n unification

- Exactly one i18n package exists (`lib/i18n/__init__.py`); no shadowed duplicate module.
- Every translation dictionary self-registers on import; no consumer module manually calls `register_bulk`.
- An automated, namespace-agnostic integrity test fails CI if any registered namespace has a raw-key leak in any supported language.
- A DB-backed store is the source of truth at runtime, hydrated at startup, with dict files retained only as migration seed data.
- Adding a new language requires zero Python code changes for existing namespaces.
- `docs/guides/I18N_GUIDE.md` documents the mandatory pattern for new screens.

## 8. Recommended next action

Start with Sprint 1 (I1A then I1B) — it is the direct, low-risk continuation of the fix already applied to `GLOBAL_TRANSLATIONS`, and it removes the exact anti-pattern (manual registration in the consumer) that caused the original regression, before any DB work begins.
