# Session Prompt CB3B: Redesign Skill Configuration & Dual-Lane Combo UI

Timebox: 25-30 minutes.

Objective:
Refactor Skill Configuration panel in `app_gui.py` and `ui/tabs/hunt_tab.py` into a dual-lane layout separating Attack/Combo Rotation from automated Buffs.

Target Files:
- Modify: `ui/tabs/hunt_tab.py` (or `app_gui.py` skill section)
- Modify: `lib/features/skills/skill_runtime_service.py`
- Modify: `lib/features/hunt/hunt_config.py`
- Reference: `lib/ui_style.py`

## Implementation Details

1. Dual-Lane Layout Construction:
   - Lane A (Combo Chain): horizontal scroll/grid container displaying skill cards sequentially for Attack skills (`type == 'attack'`). Default visible width shows 4-6 cards before scrolling kicks in — this is a display-sizing target, not a hard cap; the lane must scroll to accommodate any number of configured attack skills without truncating or dropping entries.
   - Each Card displays: Skill Name dropdown, Key entry, compact labels for `Cast: X.Xs` and `CD: X.Xs` read from database.
   - Lane B (Buff Lane): 2-3 rows for Buff skills (`type == 'buff'`), with Key entry and Auto-Refresh interval (`duration_sec`).
   - Scope note: this session covers the UI panel and config schema (storing `duration_sec` per buff slot). Whether `skill_runtime_service.py` actively schedules buff refresh using this value, or only persists it for a future session to consume, must be confirmed before coding — if runtime scheduling is in scope, add it explicitly as its own implementation step with its own test; otherwise document this session as "config + UI only, runtime consumption is out of scope."
2. Combo Mode Controls:
   - Add Checkbutton `Enable Auto Combo` and Entry/Combobox for `Combo Start Key` (default: `Alt+3`).
   - Specify the hotkey capture mechanism explicitly: state whether this is a global OS-level hook (e.g. via a `keyboard`/`pynput`-style library, active even when the app is unfocused) or an in-window binding (only active while the app has focus). This materially changes both implementation and the conflict risk with other applications' shortcuts — pick one and note it in code comments.
   - Validate that `Combo Start Key` does not conflict with:
     - Any key currently assigned to an attack skill (Lane A),
     - Any key currently assigned to a buff skill (Lane B),
     - Any other existing global hotkey already registered by the app (e.g. pause/resume, emergency stop), if the app has any.
   - On conflict, block save and show which existing binding it collides with (not just a generic "conflict" message).
3. Config Separation & Migration:
   - Save clean lists to config: `hunt_cfg["skill_slots"]` (attacks only) and `hunt_cfg["buff_slots"]` (buffs only).
   - In `load_hunt_config()`, automatically sort legacy combined slots into their respective lanes using this precedence:
     1. If the legacy entry has a `type` field (`'attack'` or `'buff'`), use it directly.
     2. If `type` is missing, look up the skill by name/id in the skill database and use its catalog-defined type.
     3. If still unresolved (skill not found in catalog either), default it into Lane A (attack) and flag it in logs as "unclassified — defaulted to attack lane" so the user can manually correct it, rather than silently dropping the entry or raising an exception.

## Validation

- Launch GUI at Windows DPI 100%, 125%, 150%: confirm horizontal skill cards do not overlap or wrap destructively. Define pass/fail concretely: after render at each DPI level, assert no two card bounding boxes (via widget `winfo_x/y/width/height`) intersect, and no card's right edge exceeds the lane container's visible width in a way that clips content instead of triggering scroll.
- Switch language between `vi` and `en`: confirm all lane headers and badges translate correctly (pull strings from the existing locale/i18n source, not hard-coded literals in the widget code).
- (Added) Legacy config migration round-trip test: load a mock legacy config containing (a) entries with explicit `type`, (b) entries missing `type` but present in the skill catalog, and (c) an entry missing `type` and absent from the catalog → assert each lands in the correct lane per the precedence rules above, and the catalog-absent case is logged as unclassified rather than raising.
- (Added) Save → reload round-trip: after migrating and saving, reload `hunt_cfg` and assert `skill_slots` contains only attack-type entries and `buff_slots` contains only buff-type entries (no cross-contamination).
- (Added) Hotkey conflict test: attempt to set `Combo Start Key` to a key already bound to an existing attack skill → assert save is blocked and the specific conflicting binding is reported.

## Session Boundary Gate

- Use UIStyle tokens (zero hard-coded hex colors).
- Ensure existing hotkeys and key-bindings remain functional.
- Confirm the hotkey capture mechanism (global hook vs in-window binding) is explicitly documented in code.
- Confirm buff-runtime scope (config-only vs active scheduling) was decided and documented before implementation, not left ambiguous.
- Report PASSED/REVERTED at minute 25.