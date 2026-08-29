# Global Rules For i18n Unification Jules Sessions

Paste this block before a session prompt if Jules does not already have these rules in context.

```text
You are working in the Cabal_Auto repository. Follow .jules/i18n-sprint-roadmap.md as the source of truth.
Read docs/I18N_DATABASE_COMPATIBILITY_CONTRACT.md before changing translation schema, hydration, language availability, or DB integration.

Hard constraints:
- Keep the change small, reversible, and scoped to the files named in this prompt.
- Preserve current behavior: every displayed string must keep rendering identically in en and vi.
- Do not reintroduce manual `i18n_register_bulk(...)` calls inside consumer/UI modules once a data module self-registers.
- Do not perform broad rewrites, style-only refactors, or unrelated cleanup.
- Do not commit changes.
- Do not delete code unless the prompt explicitly asks for deletion and repository search proves the code is unused (e.g. `lib/i18n.py` is proven dead because `import lib.i18n` always resolves to the package `lib/i18n/__init__.py`).
- Do not remove compatibility paths, callbacks, imports, or public attributes just because they look redundant; first prove all callers have moved.
- Do not overwrite or revert user changes outside this session's scope.
- Prefer moving code intact before simplifying it; behavior-preserving extraction comes before cleanup.
- Any new registration mechanism must keep `lib.i18n.t()`, `lib.i18n.register_bulk()`, and `lib.i18n.GLOBAL_NS` as the stable public API used by all consumer code.
- Keep `translations` independent from gameplay catalogue tables: no FK to classes, skills, monsters, dungeons, mappings, synergies, scans, or builds. Do not use numeric gameplay IDs as translation identity.
- Do not expose a partial pilot language in the global selector unless all reachable UI keys are covered or a tested fallback chain prevents raw keys.
- Add or update focused tests when practical; every sprint must be validated by an automated test that would have caught the original 2026-08-27 regression (translations imported but never registered, silently falling back to raw keys).
- Run the narrowest useful validation command before finishing.

Execution & Rollback Protocol (Strict 30-Minute Budget):
- Every implementation session has a maximum 30-minute budget. At minute 25, stop writing new features or expanding scope and run the automated smoke test plus selected boundary checks.
- Minute 25-30 (Direct Repair Window): if validation fails, use a maximum of 5 minutes only for direct, targeted bug fixes that restore basic functionality.
- At minute 30 (Hard Abort Threshold): if the smoke test still fails, the i18n registry returns unexpected raw keys, or DB migration/hydration leaves the app unable to start, revert only code changes made by the current session using a deliberate, reviewed patch. Never use `git checkout -- .`, `git reset`, or another broad discard command because it can remove unrelated user changes.
- After recovery, rerun the failing validation. In the final response, state whether the session `PASSED` or was `ABORTED/REVERTED`, the exact error that triggered rollback, recovered files, validation result, and deferred next slice.

Before editing:
- Identify the current controlling code path for the namespace/dictionary in scope.
- State one local hypothesis about the change.
- State the cheapest validation that can falsify it.
- Identify at least 3 boundary/edge cases relevant to this session (e.g. missing DB, empty dict, duplicate key across namespaces, language not yet populated).

Boundary checks:
- Cover empty, missing, malformed, legacy dict shape, repeated-import, and startup boundaries when relevant.
- Add or run an automated test for the riskiest boundary case when practical.
- If a boundary case requires manual GUI confirmation (e.g. visually checking a screen in vi/en), document the exact manual check in the final response.
- Treat "does _t() ever return a raw key when it shouldn't" as the primary boundary to guard against in every session of this roadmap.

Code preservation checks:
- Before deleting or heavily rewriting a block, search for references and document why deletion is safe.
- Prefer extraction/self-registration by moving existing dict data into a self-registering module with minimal edits, then validate, then simplify only if still inside scope.
- Keep fallback paths (e.g. dict-based seed data during the DB migration sprints) until the replacement path is validated and all active callers are updated.
- Review the diff before final response and call out any removed code intentionally.

Before final response:
- Summarize changed files.
- List validation commands and results.
- List boundary/edge cases checked, including any that remain manual-only.
- Include a `Timebox and recovery` section: minute-25 validation result, whether repair/recovery was required, and the deferred next slice.
- List any code removed or replaced and why it was safe.
- Call out any residual risks or follow-up tasks.
```
