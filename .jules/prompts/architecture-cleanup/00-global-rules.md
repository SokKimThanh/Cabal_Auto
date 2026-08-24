# Global Rules For Architecture Cleanup Jules Sessions

Paste this block before a session prompt if Jules does not already have these rules in context.

```text
You are working in the Cabal_Auto repository. Follow .jules/architecture-sprint-roadmap.md as the source of truth.

Hard constraints:
- Keep the change small, reversible, and scoped to the files named in this prompt.
- Preserve current behavior and config compatibility.
- Do not move logic back into app_gui.py after extracting it.
- Do not accept a newly split module design just because it is split; use the new design only if it is simpler, clearer, easier to test, or less error-prone than the old code. If it is not, improve it inside this prompt's scope or explicitly report the follow-up needed.
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
- Identify the original/source code path and the new split module path that should now own the behavior.
- State one local hypothesis about the extraction.
- State the cheapest validation that can falsify it.
- Identify at least 3 boundary/edge cases relevant to this session.

Original-vs-module comparison checks:
- Compare the original behavior source with the module(s) that now own that behavior before changing code.
- Build a short checklist of moved responsibilities: callbacks, public App attributes, imports, compatibility fallbacks, config migrations, UI event bindings, cleanup paths, and helper methods relevant to this session.
- For each important original function/block touched by this session, state whether it is kept, moved, replaced, or intentionally removed.
- If a function became a thin wrapper, prove the real behavior exists in the new module and the call path still reaches it.
- If any original behavior cannot be found in the new modules, treat it as possibly lost code and either restore it or stop with a clear report.
- When comparing old and new code, prefer the simpler and less error-prone version. If the split version adds unnecessary layers, forwarding methods, or duplicated logic, simplify it within scope instead of keeping a worse design.

Boundary checks:
- Cover empty, missing, malformed, legacy, repeated-call, cleanup/dispose, and startup/shutdown boundaries when relevant.
- Add or run an automated test for the riskiest boundary case when practical.
- If a boundary case requires manual GUI confirmation, document the exact manual check in the final response.
- Treat compatibility behavior as a boundary: legacy config shapes, existing callbacks, existing public attributes, and repeated open/close flows must keep working unless the prompt explicitly says otherwise.

Code preservation checks:
- Before deleting or heavily rewriting a block, search for references and document why deletion is safe.
- Prefer extraction by moving existing logic into the new controller/service with minimal edits, then validate, then simplify only if still inside scope.
- Keep fallback paths until the replacement path is validated and all active callers are updated.
- Do not replace working code with a stub, pass-through, or placeholder unless the prompt explicitly asks for a temporary adapter and the missing behavior is tracked.
- Watch especially for lost UI handlers, hotkey callbacks, menu commands, Tk bindings, config migration code, close/destroy cleanup, and app-level attributes consumed by split tab/window modules.
- Review the diff before final response and call out any removed code intentionally.

Simplicity and maintainability checks:
- Prefer a small direct function or service method over a new class when no state/lifecycle ownership is needed.
- Avoid extra forwarding layers unless they preserve compatibility during the migration.
- If two modules now perform the same validation, migration, or lifecycle decision, centralize it in the owner named by the roadmap.
- The final code should be easier to locate, test, and reason about than the original code. If not, report why and propose the smallest follow-up cleanup.

Before final response:
- Summarize changed files.
- Include the original-vs-module comparison result: what moved, what stayed, what was replaced, and whether anything looked missing.
- List validation commands and results.
- List boundary/edge cases checked, including any that remain manual-only.
- List any code removed or replaced and why it was safe.
- Explain why the new version is simpler/safer than the old version, or list the improvement still required.
- Call out any residual risks or follow-up tasks.
```
