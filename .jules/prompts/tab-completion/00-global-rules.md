# Global Rules For Tab Completion Jules Sessions

Paste this block before a session prompt if Jules does not already have these rules in context.

```text
You are working in the Cabal_Auto repository. Follow docs/sprints/sprint18/SPRINT18_PHASE4_TAB_REORGANIZATION.md (Task #4 / Task #5) as the design source of truth, and .jules/tab-completion-jules-prompts.md for session sequencing.

Hard constraints:
- Keep the change scoped to the one tab named in this prompt's session file; do not build both Stats and Help tabs in the same session.
- ui/tabs/stats_tab.py and ui/tabs/help_tab.py currently contain only `def _build_ui(self): pass` - this is unimplemented, planned work (Sprint 18 Phase 4, marked "Not started" in the design doc), not a regression to revert.
- Do not remove or rename the StatsTab/HelpTab classes or their constructor signature (`__init__(self, parent, app)`); app_gui.py already instantiates and adds them to the notebook.
- New StringVars/widgets should live on the tab instance (`self.*`), matching the pattern already used in ui/tabs/hunt_tab.py and ui/tabs/setup_tab.py - do not put new state directly on `App` unless the data must be read from outside the tab (e.g. hunt_runner needs to update a stats var).
- Add i18n keys to lib/i18n/translations.py (GLOBAL_TRANSLATIONS, both en and vi) for any new label text; do not hardcode bilingual if/else strings when a translation key would work, following the existing pattern in hunt_tab.py/setup_tab.py.
- Do not delete code unless explicitly asked and proven unused via repository search.
- Do not commit changes.
- Prefer moving/adapting the exact structure already sketched in the design doc's "Implementation" code samples over inventing a new layout.
- Add or update focused tests when practical (a simple instantiate-and-check-attributes test is enough; full GUI interaction tests are not required).
- Run the narrowest useful validation command before finishing.

Before editing:
- Re-read the relevant Task section (#4 for Stats, #5 for Help) in the design doc in full.
- State one local hypothesis about which existing app/controller data sources you'll wire the tab to (e.g. hunt_orchestrator state, SkillStats, hunt_cfg).
- State the cheapest validation that can falsify it.
- Identify at least 3 boundary/edge cases relevant to this session (e.g. hunt never started yet, stats reset mid-session, language switch while tab is open).

Boundary checks:
- Cover: app just started (no hunt run yet - stats must show sensible defaults, not crash), language switch (self._t() must still resolve), and repeated tab switches (no duplicate periodic `self.after()` update loops stacking up).
- If a boundary case requires manual GUI confirmation, document the exact manual check in the final response.

Before final response:
- Summarize changed files.
- List validation commands and results.
- List boundary/edge cases checked, including any that remain manual-only.
- Call out any residual risks or follow-up tasks (e.g. "Export stats to CSV" button from Task #4 deferred).
```
