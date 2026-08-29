# Global Rules For UI Main Screen Cleanup Jules Sessions

Paste this block before a session prompt if Jules does not already have these rules in context.

```text
You are working in the Cabal_Auto repository. Follow the UX cleanup goals described in docs/UX_ANALYSIS_AND_INTERFACE_REDESIGN.md and the architecture cleanup rules in .jules/architecture-sprint-roadmap.md.
Read .jules/prompts/ui-main-screen-cleanup/UI_MANAGEMENT_AND_OWNERSHIP.md before editing. Its zone ownership, lifecycle, and Main Thread rules are mandatory.
Read .jules/prompts/ui-main-screen-cleanup/UI_ZONE_IMPLEMENTATION_PLAYBOOK.md before editing. Its widget mapping, zone-specific implementation steps, non-goals, and validation rules are mandatory.
Read .jules/prompts/ui-main-screen-cleanup/I18N_UI_INTEGRATION.md before editing. Its translation-key, language-rebuild, and bilingual validation rules are mandatory for every user-visible UI string.

Hard constraints:
- Keep the change small, reversible, and scoped to the files named in this prompt.
- Preserve current behavior and config compatibility.
- Do not perform broad rewrites, style-only refactors, or unrelated cleanup.
- Do not commit changes.
- Do not delete code unless the prompt explicitly asks for deletion and repository search proves the code is unused.
- Do not remove compatibility paths, callbacks, imports, or public attributes just because they look redundant; first prove all callers have moved.
- Do not overwrite or revert user changes outside this session's scope.
- Prefer moving code intact before simplifying it; behavior-preserving extraction comes before cleanup.
- Prefer controller/service boundaries over large helper files.
- Add or update focused tests when practical.
- Run the narrowest useful validation command before finishing.
- Treat the four-zone `1920x1080` baseline in docs/UX_ANALYSIS_AND_INTERFACE_REDESIGN.md as a design target, not an exact rendered-pixel assertion: Header `56 px`, Quick Action Bar `80 px`, Sidebar target `280 px`, Workspace target `1640 x 744 px`, and Bottom Logs target `1640 x 200 px`.
- Support Windows DPI scaling from 100% through 150% by using `grid`, `weight`, `minsize`, content measurement, and the documented responsive fallbacks. A small rendered-pixel difference caused by Tk scaling is acceptable when controls remain readable, reachable, non-overlapping, and in the specified priority order.
- Do not move a primary hunt action into the Sidebar or Bottom Logs. Do not move deep configuration into the Quick Action Bar.
- Only the Main Thread may call Tkinter widget methods. Background workers and services pass data through a UI scheduler (`after(0, ...)`) or `queue.Queue`.
- Do not let a zone directly update another zone's widgets. Use an explicit callback or an existing controller/service state contract.
- Do not add a hard-coded user-visible string. Use the existing i18n registry and `App._t`/zone `_t` helper; new main-screen copy requires both `en` and `vi` keys.

Execution & Rollback Protocol (Strict 30-Minute Budget):
- At minute 25: stop writing new features or expanding scope immediately. Run the automated smoke test and selected boundary checks.
- Minute 25-30 (Direct Repair Window): if validation fails, use a maximum of 5 minutes only for direct, targeted bug fixes that restore basic functionality.
- At minute 30 (Hard Abort Threshold): if the smoke test still fails or the UI exhibits severe breakage, revert all code changes made by the current session using a deliberate, reviewed patch. Never use `git checkout -- .`, `git reset`, or another broad discard command because it can remove unrelated user changes.
- After recovery, rerun the failing smoke/import check. In the final response, state whether the session `PASSED` or was `ABORTED/REVERTED`, the exact error that triggered rollback, the recovered files, the validation result, and the deferred next slice.

Before editing:
- Identify the current controlling code path for the main screen workflow.
- Identify the current widget source and target zone from the UI zone implementation playbook.
- State the exact UI edit to make, the callback/binding that must remain unchanged, and the zone-specific non-goal.
- State one local hypothesis about the UX extraction or layout change.
- State the cheapest validation that can falsify it.
- Identify at least 3 boundary/edge cases relevant to this session.

Boundary checks:
- Cover empty, missing, malformed, legacy, repeated-call, cleanup/dispose, and startup/shutdown boundaries when relevant.
- Add or run an automated test for the riskiest boundary case when practical.
- If a boundary case requires manual GUI confirmation, document the exact manual check in the final response.
- Treat compatibility behavior as a boundary: legacy config shapes, existing callbacks, existing public attributes, and repeated open/close flows must keep working unless the prompt explicitly says otherwise.

Session boundary gate (mandatory for every session):
- Before editing, select at least 3 concrete boundary cases affected by this session; one must cover target window, window bounds, or target region whenever the session touches the main hunt workflow.
- After editing, run or manually verify the selected cases. Do not mark the session complete only because the app starts.
- If the application fails the smoke test or exhibits severe layout breakage at the 25-minute mark, you MUST revert all UI changes made in the current session to return the app to a runnable state, and report the specific failure cause in the final response. Revert only the current session's reviewed UI diff; never discard unrelated user changes.
- For UI changes that touch window selection, status, layout, setup modes, capture, or Start Hunt, check the applicable states: valid bounds, no selected window, invalid/malformed bounds, minimized or unavailable window, and target region outside the game window.
- Preserve the existing normalized bounds flow: `normalize_window_bounds_value` and `WindowSelectionService.update_bounds` remain the source of truth. Do not introduce a duplicate UI-only bounds state.
- In the final response, report each selected case as passed, failed, or manual-only and include the recovery action the UI exposes.

Visual design gate (mandatory for every session that changes UI):
- Use semantic colors and button-state tokens from `lib/ui_style.py` (`UIStyle`); do not add hard-coded hex colors in app_gui.py, tabs, controllers, or dialogs.
- Green is for Start/confirm/ready, red is for Stop/destructive/blocking error, orange is for warnings needing action, blue is for neutral information or Refresh, and gray is for secondary/disabled context.
- Do not use color as the only status signal. Every ready, warning, error, or bounds state must include readable text and its recovery action.
- Keep visual hierarchy unambiguous: while idle, Start Hunt is the single dominant action; while running, Stop Hunt is the single dominant action.
- Check normal, hover, disabled, and keyboard-focus visibility for each touched control. Keep text contrast at WCAG AA ($4.5:1$ minimum for normal text).
- In the final response, report the tokens used, confirm no new hard-coded colors were introduced, and list the visual states manually checked.

i18n gate (mandatory for every session that changes user-visible UI):
- Identify the translation namespace and existing `_t` render path before adding/changing visible copy.
- For every new key, provide both `en` and `vi` translations; do not allow raw keys or string concatenation to reach the UI.
- Verify the changed zone at `vi`, then change to `en` and back to `vi`; confirm the UI rebuilds translated labels while runtime/config state remains intact.
- Confirm translated text does not clip, wrap primary controls, or break the documented DPI/responsive layout.
- In the final response, report added/reused keys, namespace, bilingual check result, and any manual-only result.

Code preservation checks:
- Before deleting or heavily rewriting a block, search for references and document why deletion is safe.
- Prefer extraction by moving existing logic into the new controller/service with minimal edits, then validate, then simplify only if still inside scope.
- Keep fallback paths until the replacement path is validated and all active callers are updated.
- Review the diff before final response and call out any removed code intentionally.

Before final response:
- Summarize changed files.
- List validation commands and results.
- List boundary/edge cases checked, including any that remain manual-only.
- Include a `Session boundary gate` section listing the selected cases and their results.
- Include a `Layout evidence` section: viewport checked, affected zone dimensions, and any responsive fallback manually checked.
- Include a `UI management evidence` section: zone owner, source of truth, Main Thread path, and lifecycle/cleanup case checked.
- Include a `Timebox and recovery` section: minute-25 validation result, whether a repair/recovery was required, and the exact deferred next slice.
- List any code removed or replaced and why it was safe.
- Call out any residual risks or follow-up tasks.
```
