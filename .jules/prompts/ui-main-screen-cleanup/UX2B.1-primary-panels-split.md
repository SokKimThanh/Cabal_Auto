# UX2B.1 - Primary Panels Split

Paste `00-global-rules.md` before this prompt.

```text
Split only the Hunt workspace into Monster Rotation and Active Target & Status primary panels.

Timebox: 25-30 minutes. At minute 25, run validation; use remaining time only for direct repair or the rollback/abort rule.

Dependencies:
- UX2.2 has passed startup, control, and tab-switching validation.

Files in scope:
- ui/tabs/hunt_tab.py
- app_gui.py only for a necessary existing container integration
- focused UI import/startup tests only if practical

Tasks:
- Configure the internal HuntTab grid for two primary panels.
- Target `776 x 552 px` per panel at 1920x1080/100% DPI, using grid weight/minsize rather than absolute coordinates.
- Keep Monster Rotation independently scrollable.
- Keep skills widgets in their current temporary location; UX2B.2 owns the Quick Skill Strip.

Do not:
- Move or restyle skill widgets.
- Change Monster Rotation listbox bindings, StringVar, callbacks, persistence, managers, hunt logic, Sidebar, or Bottom Logs.

Acceptance criteria:
- Monster Rotation and Active Target & Status display together without overlap.
- Empty and long rotation states remain stable; long lists scroll without hiding status.
- The layout stays usable at 125%-150% DPI and at the documented narrower fallback.

Session boundary gate:
- Empty rotation: add action remains reachable.
- Long rotation: scroll remains within its panel.
- Missing/invalid bounds: existing warning remains visible in Vùng A/B.

Validation:
- Run the narrowest import/startup smoke test and UI import test if applicable.
- Manually verify the three boundary cases and responsive fallback.
- Report layout, ownership, visual, lifecycle, timebox, and recovery evidence.
```