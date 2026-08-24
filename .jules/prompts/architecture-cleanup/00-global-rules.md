# Global Rules For Architecture Cleanup Jules Sessions

Paste this block before a session prompt if Jules does not already have these rules in context.

```text
You are working in the Cabal_Auto repository. Follow .jules/architecture-sprint-roadmap.md as the source of truth.

Hard constraints:
- Keep the change small, reversible, and scoped to the files named in this prompt.
- Preserve current behavior and config compatibility.
- Do not move logic back into app_gui.py after extracting it.
- Do not perform broad rewrites, style-only refactors, or unrelated cleanup.
- Do not commit changes.
- Do not delete code unless the prompt explicitly asks for deletion and repository search proves the code is unused.
- Do not remove compatibility paths, callbacks, imports, or public attributes just because they look redundant; first prove all callers have moved.
- Do not overwrite or revert user changes outside this session's scope.
- Prefer moving code intact before simplifying it; behavior-preserving extraction comes before cleanup.
- Prefer controller/service boundaries over large helper files.
- Add or update focused tests when practical.
- Run the narrowest useful validation command before finishing.

Before editing:
- Identify the current controlling code path.
- State one local hypothesis about the extraction.
- State the cheapest validation that can falsify it.
- Identify at least 3 boundary/edge cases relevant to this session.

Boundary checks:
- Cover empty, missing, malformed, legacy, repeated-call, cleanup/dispose, and startup/shutdown boundaries when relevant.
- Add or run an automated test for the riskiest boundary case when practical.
- If a boundary case requires manual GUI confirmation, document the exact manual check in the final response.
- Treat compatibility behavior as a boundary: legacy config shapes, existing callbacks, existing public attributes, and repeated open/close flows must keep working unless the prompt explicitly says otherwise.

Code preservation checks:
- Before deleting or heavily rewriting a block, search for references and document why deletion is safe.
- Prefer extraction by moving existing logic into the new controller/service with minimal edits, then validate, then simplify only if still inside scope.
- Keep fallback paths until the replacement path is validated and all active callers are updated.
- Review the diff before final response and call out any removed code intentionally.

Before final response:
- Summarize changed files.
- List validation commands and results.
- List boundary/edge cases checked, including any that remain manual-only.
- List any code removed or replaced and why it was safe.
- Call out any residual risks or follow-up tasks.
```
