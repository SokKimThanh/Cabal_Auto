# Auto Cabal Origin – Project Context (Updated 2025-10-18)

This document summarizes the current project context from “docs/archive/v2/context/CONTEXT_MAIN.txt” (migrated from assets/documents) so developers have a concise, actionable reference linked to code modules and data schemas.

## 🎯 Goals
- Safe auto-hunting for Cabal VTC Origin on Windows.
- Robust GUI with correct window focus (PID/HWND) and global stop hotkey.
- Monster library with multi-template recognition and per-template thresholds/regions.
- Skills management with cooldowns and buff durations (duration_sec, pre_refresh_sec).
- Timing calculator integrated with skills to compute attack speed and apply to config.
- Progressive disclosure UI (Beginner/Intermediate/Advanced) and first‑time Setup Wizard.

## 🛠 Environment
- OS: Windows, PowerShell recommended as Admin for reliable hotkeys.
- Python: 3.14.0 (venv at E:\Cabal_Auto\venv).
- Key libs: pyautogui, opencv-python (4.12.0), numpy (2.3.4), pillow, keyboard.

## 📁 Key Files and Modules
- app_gui.py: Main GUI (Hunt tab core, mode toggle, progressive disclosure, wizard entry).
- auto_hunt.py: Non-GUI hunt loop; integrates template matcher and logging.
- lib/template_matcher.py: Unified locate_template (OpenCV preferred, PyAutoGUI fallback).
- lib/timing_calculator.py: Computes lost_timeout_sec and attack_min_duration_sec.
- lib/skill_runtime.py: Attack rotation and buff auto-casting runtime.
- lib/hunt_logger.py: Dual logging (human text + structured JSONL).
- setup_wizard.py: 5-step onboarding (Welcome → Window → Monster → Skills → Review).
- data/*.json: hunt_config.json, monsters.json, skills.json schemas.

## 🧩 Data Schemas

### monsters.json (multi-template, window bounds)
- Monster fields: id?, name, description?, window_bounds {left, top, width, height}
- templates[]: [{
  - name?, path (relative preferred, under assets/images/monsters/),
  - threshold (0..1, suggest 0.80–0.90),
  - region_strategy: "window" | "custom",
  - region?: [left, top, width, height],
  - grayscale?: bool
}]
- Backward compat: if legacy template_path exists elsewhere, use first templates[] as default.

### skills.json (attack/buff with durations)
- Fields: name, key, type: "attack"|"buff", cooldown, cast_time,
- duration_sec (buff uptime, 0 for attacks), pre_refresh_sec (buff recast lead time),
- hold_ms? (override press duration; null uses cast_time), image (relative path under assets/images/skills/).

### hunt_config.json (Hunt runtime)
- window_title, window_pid?, window_hwnd?, bring_to_front_each_cycle,
- target_key, attack_keys (derived from skill_slots; advanced override only),
- search_interval, attack_interval, target_cycle_delay,
- lost_timeout_sec, attack_min_duration_sec,
- window_bounds default region, optional region overrides per template.

## 🔎 Template Matching
- OpenCV preferred (TM_CCOEFF_NORMED) returns accurate confidence float.
- PyAutoGUI used as fallback; both unified by lib/template_matcher.locate_template().
- Per-template threshold and region_strategy respected; logging captures template name, box, threshold, confidence.

## ⏱ Timing Recommendations
- From lib/timing_calculator:
  - hits_to_kill = ceil(hp / damage_per_hit)
  - estimated_kill_time = hits_to_kill / attacks_per_second
  - lost_timeout_sec clamp 0.3–3.0 (with +50% safety),
  - attack_min_duration_sec clamp 1.0–30.0 (with +20% safety).
- Attack speed source:
  - Recommended: computed from selected attack skills’ average cooldown (app_gui helper), or
  - Manual presets: slow/normal/fast/very_fast/custom.
- “Apply to Hunt Config” writes results to hunt_config.json and updates GUI fields.

## 🧠 Skill Runtime
- Separate attack rotation and buff lane.
- Buff auto-recast when (duration_sec - elapsed) <= pre_refresh_sec and cooldown ready.
- Attack rotation round-robin while respecting cooldowns; uses skill-specific hold_ms when present.

## 🪟 Window Handling
- Enumerate windows via WinAPI; select by title filter and show PID/HWND.
- Prefer focus by HWND/PID; minimize GUI so key events go to game.
- Bring To Front option available; global hotkey (e.g., F9) to stop.

## 🧪 Tools and UX Enhancements
- Screenshot capture overlay to crop template regions; auto-save under assets/images/monsters/ with sanitized filenames.
- Test Recognition button to validate template live and show confidence/thumbnail.
- Tooltips, localized messages (EN/VI), thumbnail caching to reduce I/O.

## 📝 Logging
- lib/hunt_logger.py outputs:
  - hunt.log (rotating, human-readable),
  - logs/hunt_structured.jsonl (JSON Lines for analysis).
- Log match events, lost events, state changes, start/stop, and errors with timestamps.

## ✅ Acceptance Criteria (high level)
- Multi-template matching with thresholds/regions per monster works in GUI and CLI hunt.
- Timing calculator computes from real skills and can apply to config with one click.
- Buff fields visible only for buff skills; validation enforces duration/pre_refresh correctness.
- Setup Wizard completes 5 steps and saves to hunt_config.json.
- Logging captures confidence and template details during hunt.

## 🔗 Cross‑References
- Source context: docs/archive/v2/context/CONTEXT_MAIN.txt (updated 2025‑10‑19).
- Implementation details: docs/sprints/sprint16/* and sprint18/*.
- Modules: lib/template_matcher.py, lib/timing_calculator.py, lib/skill_runtime.py, lib/hunt_logger.py.

---
Last updated: 2025‑10‑18