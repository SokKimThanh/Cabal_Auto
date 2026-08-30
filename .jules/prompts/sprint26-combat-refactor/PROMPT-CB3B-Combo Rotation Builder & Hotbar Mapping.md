# Session Prompt CB3B: Redesign Skill Configuration & Dual-Lane Combo UI

Timebox: 25-30 minutes.

Objective:
Refactor Skill Configuration panel in `app_gui.py` and `ui/tabs/hunt_tab.py` into a dual-lane layout separating Attack/Combo Rotation from automated Buffs.

Target Files:
- Modify: `ui/tabs/hunt_tab.py` (or `app_gui.py` skill section)
- Modify: `lib/features/skills/skill_runtime_service.py`
- Modify: `lib/features/hunt/hunt_config.py`
- Reference: `lib/ui_style.py`

Implementation Details:
1. Dual-Lane Layout Construction:
   - Lane A (Combo Chain): Horizontal scroll/grid container displaying 4-6 skill cards sequentially for Attack skills (`type == 'attack'`).
   - Each Card displays: Skill Name dropdown, Key entry, compact labels for `Cast: X.Xs` and `CD: X.Xs` read from database.
   - Lane B (Buff Lane): 2-3 rows for Buff skills (`type == 'buff'`), with Key entry and Auto-Refresh interval (`duration_sec`).
2. Combo Mode Controls:
   - Add Checkbutton `Enable Auto Combo` and Entry/Combobox for `Combo Start Key` (default: `Alt+3`).
   - Validate that Combo Start Key does not conflict with active attack keys.
3. Config Separation & Migration:
   - Save clean lists to config: `hunt_cfg["skill_slots"]` (attacks only) and `hunt_cfg["buff_slots"]` (buffs only).
   - In `load_hunt_config()`, automatically sort legacy combined slots into their respective lanes.

Validation:
- Launch GUI at Windows DPI 100%, 125%, 150%: confirm horizontal skill cards do not overlap or wrap destructively.
- Switch language between `vi` and `en`: confirm all lane headers and badges translate correctly.

Session Boundary Gate:
- Use UIStyle tokens (zero hard-coded hex colors).
- Ensure existing hotkeys and key-bindings remain functional.
- Report PASSED/REVERTED at minute 25.