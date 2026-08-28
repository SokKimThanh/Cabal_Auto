# T1 - Build Stats Tab

Paste `00-global-rules.md` first, then this prompt.

```text
Implement Sprint 18 Phase 4 Task #4 (Create Stats Tab) from
docs/sprints/sprint18/SPRINT18_PHASE4_TAB_REORGANIZATION.md.

Context:
ui/tabs/stats_tab.py currently only contains `def _build_ui(self): pass` - a
never-implemented placeholder (marked "Status: Not started" in the design doc).
When Hunt tab was streamlined in Sprint 18, hunt statistics and performance
metrics were deliberately planned to move here, but that move never happened -
this data currently has nowhere to display in the app at all.

Goal:
Build the real Stats tab UI per the design doc's Task #4 sections:
- Section 1: Hunt Statistics (runtime duration, monsters hunted, average kill
  time, exp/hour estimate, skills cast count per skill)
- Section 2: Performance Metrics (template matching FPS, CPU usage %, memory
  usage MB, screenshot latency ms)
- Section 3: Rotation History (current monster, previous monsters, time spent
  on each, rotation efficiency) - only if multi-monster rotation is active
- Section 4: Controls (reset stats button, export stats to CSV button, refresh
  rate dropdown 1s/5s/10s)

Files in scope:
- ui/tabs/stats_tab.py
- app_gui.py (only to wire callbacks/read existing state such as
  hunt_orchestrator, hunt_runner, SkillStats - do not move hunt logic itself)
- lib/i18n/translations.py (new i18n keys for Stats tab labels, en + vi)
- a small focused test (e.g. tests/unit/ui or tests/test_ui_imports.py-style
  instantiate check)

Boundaries:
- Do not modify HuntTab, SetupTab, or hunt_orchestrator/hunt_runner internals
  beyond reading already-exposed state or adding a narrow callback hook if one
  is genuinely missing (state what you need and why before adding it).
- Where live data does not exist yet (e.g. no CPU/memory sampling utility
  exists in the repo), it is acceptable to show a "--" placeholder and note
  this as a follow-up rather than inventing a new metrics-collection subsystem
  in this session.
- Follow the periodic-update pattern shown in the design doc
  (`self.after(1000, self._update_stats_display)`), but guard against stacking
  multiple update loops if the tab is rebuilt (e.g. on language change).
- Reuse existing i18n helper (`self.app._t(key)` or `self._t`) rather than
  hardcoded bilingual if/else strings.

Acceptance criteria:
- Stats tab shows real hunt runtime/kill/skill-cast data once a hunt has been
  started and stopped at least once (verified via a scripted App() + simulated
  hunt state, not necessarily a live GUI session).
- Tab does not crash or show garbage when no hunt has ever run (sensible
  zero/placeholder defaults).
- Reset stats button clears the displayed values without crashing.
- No duplicate periodic update loops after repeated tab rebuilds/language switches.

Validation:
- Instantiate `App()` directly and assert the new StringVars/widgets exist and
  have sane default values.
- Run the narrowest existing UI smoke test (`py -m pytest tests/test_ui_imports.py -v`).
- Run `py .\app_gui.py` and manually confirm the Stats tab renders without
  exceptions; document any manual-only checks (e.g. actually running a hunt to
  see live numbers) in the final response.
```
