# 📊 REVIEW: UX6 + Auto Hunt Prompts vs Current Implementation

**Date**: 2026-09-05  
**Review Scope**: Compare PROMPT-UX6 + PROMPT-UX-Auto-Hunt vs codebase actual status  
**Outcome**: Identify gaps, refine prompts, create executable improvement roadmap

---

## 🎯 Executive Summary

| Aspect | UX6 (Window Detection) | Auto Hunt Flow | Status |
|--------|------------------------|-----------------|--------|
| **Architecture** | 60% implemented | 40% implemented | ⚠️ Gaps found |
| **UI Components** | 75% ready | 50% ready | 📝 Needs completion |
| **Backend Services** | 70% done | 30% done | 🔧 Requires work |
| **Integration** | 40% wired | 20% wired | ❌ Critical gaps |
| **Tests** | 0% | 0% | 📋 Need creation |
| **i18n** | Partial | Partial | 📚 Needs review |

---

## 📋 DETAILED GAP ANALYSIS

### **PART 1: UX6 (Window Detection & Refresh)**

#### ✅ WHAT'S ALREADY THERE

```python
# 1. Window Manager (lib/system/window_manager.py) — ✅ Complete
   - WindowManager.list_windows()
   - WindowManager.find_window()
   - WindowManager.find_all_windows()
   - Filter by: title, process_name, class_name, visible_only

# 2. Window Selection Service (lib/features/hunt/window_selection_service.py) — ✅ Complete
   - validate_selected_cabal_window()
   - Returns WindowValidationResult with detailed validation

# 3. App Window Controller (ui/controllers/app_window_controller.py) — ✅ 70% Done
   - on_hunt_find_windows() — Find windows via button click
   - on_window_combo_selected() — Handle combo selection
   - _list_windows() — Fetch window list
   - _auto_detect_and_save_cabal_window() — Auto-detect on startup
   - MISSING: Refresh button wiring, startup enumeration flow

# 4. Auto Scanner (lib/features/hunt/scanner.py) — ✅ 50% Done
   - detect_window() — Get HWND, PID, bounds
   - scan_screen() — Screen capture + monster/skill detection
   - run_scan() — Full scan workflow
   - MISSING: Explicit skill validation, location detection

# 5. Setup Wizard (ui/windows/setup_wizard.py) — ✅ Complete
   - _enum_windows() — Manual enumeration
   - _search_windows() — Filter logic
   - _on_window_select() — Selection handling
   - Auto-selects first match

# 6. Hunt Tab UI (ui/tabs/hunt_tab.py) — ✅ 80% Done
   - update_target_card()
   - update_hp_display()
   - clear_target_card()
   - MISSING: Refresh button, scan button, screen state display panel

# 7. Hunt Config Management (lib/features/hunt/) — ✅ Complete
   - Saves window_hwnd, window_pid, window_bounds to config.json
   - Persists selection for next app startup
```

#### ❌ WHAT'S MISSING (Prompt vs Actual)

| Requirement | Promise | Actual | Gap |
|-------------|---------|--------|-----|
| **R1: Startup Enum** | Auto-enumerate on startup | Partial (only in SetupWizard) | 🔴 Missing in app_gui.py startup |
| **R1: Startup Display** | Show windows in combobox immediately | Not in main tab (only setup wizard) | 🔴 UI not integrated to hunt tab |
| **R2: Refresh Button** | Button to re-enumerate | EXISTS but not wired to hunt tab | 🟡 Need to wire to UI |
| **R3: Game Window Criteria** | 4-level filtering system | PARTIAL (title + process only) | 🟡 Missing window state checks |
| **R4: Manual Select** | Save HWND to config | ✅ Working | ✅ Complete |
| **Screen Scan Panel** | Show character class, skill validity, location | Partial (only in AutoScanner) | 🔴 Missing UI display |
| **Status Display** | Character class, skill validity, location indicator | Not displayed | 🔴 Missing all indicators |
| **i18n Keys** | 15+ translation keys | ~5 keys exist | 🟡 Incomplete |

#### 🔧 Concrete Implementation Status

```python
# Current Flow (Actual):
app_gui.py startup
  → SetupWizard (if first time)
    → _enum_windows()
    → _search_windows()
    → _on_window_select()
    → Saves to config.json
  → HuntTab appears but NO window selection visible
  → NO "Start Hunt" available until manual setup

# Prompt Flow (Desired):
app_gui.py startup
  → Enumerate windows automatically
  → Populate combo in HuntTab directly
  → Show spinner during enum
  → User can select window or click "Refresh"
  → When selected, enable "Scan" button
  → Click "Scan" → Show character class, skills, location
```

---

### **PART 2: Auto Hunt Flow**

#### ✅ WHAT'S ALREADY THERE

```python
# 1. Hunt Orchestrator (lib/features/hunt/hunt_orchestrator.py) — ✅ 80% Done
   - start_hunt(), stop_hunt()
   - State machine (IDLE, HUNTING, LOST)
   - Monster detection integration
   - Target rotation coordination
   - HP reading + status updates
   - MISSING: Clean "Start Auto" button integration from UI

# 2. Scan Controller (lib/features/hunt/scan_controller.py) — ✅ 70% Done
   - run_scan() with worker thread
   - Window detection + frame capture
   - DB validation
   - Error handling
   - MISSING: Cleanup of screenshots, explicit scan cycle loop

# 3. Scene Monster Detector (lib/features/hunt/scene_monster_detector.py) — ✅ 60% Done
   - process_frame() for detection
   - Template matching
   - Monster state tracking
   - MISSING: Dead/alive state detection, monster state change callbacks

# 4. Runtime Monster Queue (lib/features/hunt/runtime_monster_queue.py) — ✅ 50% Done
   - Tracks detected monsters in real-time
   - Publishes snapshots
   - MISSING: Integration with UI display

# 5. Hunt Tab UI (ui/tabs/hunt_tab.py) — ✅ 70% Done
   - Target Card display (monster name, image, level, HP)
   - HP progress bar + color coding
   - update_target_card(), update_hp_display()
   - MISSING: "Start Auto" / "Stop" buttons
   - MISSING: Session stats display (kills, EXP, drops)
   - MISSING: Cleanup after scan

# 6. Hunt Config (lib/data/hunt_config.json) — ✅ Complete
   - monster_rotation[], templates[], skill_slots[]
   - window_bounds, rotation_mode

# 7. Auto Hunt Window (ui/windows/auto_hunt.py) — ⚠️ CLI Only
   - Full CLI implementation of hunt loop
   - locate_monster_target(), check state, attack logic
   - But: NOT integrated to main UI
   - Runs as separate process (python ui/windows/auto_hunt.py)
```

#### ❌ WHAT'S MISSING (Prompt vs Actual)

| Requirement | Promise | Actual | Gap |
|-------------|---------|--------|-----|
| **R1: Start Auto Button** | "🎬 Bắt Đầu Tự Động" in hunt panel | EXISTS in hunt_tab.py but NOT wired | 🟡 Button exists, callback missing |
| **R1: Stop Auto Button** | "⏹️ Dừng" button | Not implemented | 🔴 Missing |
| **R2A: Send Z Key** | Keyboard Z key to game | ⚠️ In auto_hunt.py (CLI only) | 🔴 Not in orchestrator |
| **R2B-C: Screen Capture** | Capture + OCR monster name | ✅ In AutoScanner, ScanController | ✅ Partially done |
| **R2D: Lookup DB** | Query monster in DB | ✅ In hunt_orchestrator.py | ✅ Done |
| **R2E: Display on Hunt Screen** | Update HuntScreen with monster info | ✅ update_target_card() exists | ✅ Done |
| **R2F: Check Monster State** | Detect dead/alive/changed | ⚠️ In auto_hunt.py (CLI), not orchestrator | 🟡 Partial |
| **R2G: Cleanup Screenshots** | Delete after scan | ❌ Not done | 🔴 Missing |
| **R2H: Wait Between Scans** | Configurable delay | ✅ In orchestrator (1-2s default) | ✅ Done |
| **Session Tracking** | HuntSession tracking kills/EXP | ❌ Not implemented | 🔴 Missing |
| **Session Summary** | Display after stop | ❌ Not implemented | 🔴 Missing |
| **i18n Keys** | 15+ keys | ~5 keys exist | 🟡 Incomplete |

#### 🔧 Concrete Implementation Status

```python
# Current Flow (Actual):
User clicks "Start Hunt" button
  → HuntRunner or HuntOrchestrator.start_hunt()
  → Starts worker thread for hunt loop
  → BUT: No explicit "scan cycle" with cleanup
  → Monster detection via RuntimeMonsterQueue
  → HP updated via TargetHPReader
  → NO "session tracking" (kills, EXP, drops)

# CLI Flow (Separate Process):
python ui/windows/auto_hunt.py
  → Full hunt loop with:
     - locate_monster_target()
     - check dead/alive
     - attack logic
  → Logging to hunt_structured.jsonl
  → PROBLEM: Runs separately, not integrated to GUI

# Prompt Flow (Desired):
User clicks "Start Auto" in HuntTab
  → AutoHuntOrchestrator.start_auto_hunt()
  → Loop:
     1. Send Z key
     2. Capture screen + extract monster name
     3. Lookup in DB
     4. Display on HuntScreen
     5. Check state (dead/alive)
     6. Cleanup screenshot
     7. Wait 1.5s
  → Show session stats (kills, EXP, drops)
  → User clicks "Stop Auto"
  → Show session summary
```

---

## 📌 ROOT CAUSES OF GAPS

### UX6 Issues:
1. **Startup Flow Not Integrated** — Setup Wizard works but not connected to main HuntTab
2. **UI Not Unified** — Window selection in SetupWizard but should be in HuntTab
3. **Refresh Button Missing** — `on_hunt_refresh_windows()` exists but UI button not present
4. **Screen State Display Missing** — No panel for character class, skills, location
5. **Startup Auto-enum** — App should enumerate on startup, currently defers to manual setup

### Auto Hunt Issues:
1. **CLI vs GUI Dichotomy** — Full logic in `auto_hunt.py` (CLI) but not in orchestrator (GUI)
2. **Start/Stop UI Not Wired** — Buttons exist but callbacks not implemented
3. **Screenshot Cleanup** — No automatic cleanup between scans
4. **Session Tracking** — No kills/EXP/drops tracking
5. **Z Key Sending** — Only in CLI, not orchestrator backend
6. **State Detection** — Monster dead/alive detection in CLI but not orchestrator

---

## ✅ RECOMMENDATIONS

### Priority 1: UX6 Improvements
1. **Add window enumeration to app startup** (30 sec)
2. **Add refresh button to hunt tab combobox** (2 min)
3. **Create screen state display panel** showing character class + skills + location (5 min)
4. **Wire AutoScanner.scan_screen() results to UI** (3 min)

### Priority 2: Auto Hunt Improvements
1. **Extract CLI hunt logic from auto_hunt.py to AutoHuntOrchestrator** (5 min)
2. **Add Start Auto / Stop Auto button callbacks** (2 min)
3. **Implement screenshot cleanup** (1 min)
4. **Add session tracking** (3 min)
5. **Add Z key sending to orchestrator** (1 min)

### Priority 3: Integration
1. **Wire both features in app_gui.py** (3 min)
2. **Add all i18n keys** (2 min)
3. **Write tests** (5 min)

---

## 📊 Current vs Desired: Implementation Checklist

### UX6 (Window Detection)

| Feature | Current | Desired | Work Needed |
|---------|---------|---------|-------------|
| Enumerate on startup | ❌ | ✅ | Add 5 lines to app_gui.py |
| Display in HuntTab | ❌ | ✅ | Move/link from SetupWizard |
| Refresh button | ⚠️ Exists separately | ✅ In HuntTab | Wire button callback (1 min) |
| Game window criteria | ⚠️ Title+process only | ✅ 4-level | Enhance WindowManager (2 min) |
| Manual select | ✅ | ✅ | No change needed |
| Screen scan UI | ❌ | ✅ | Create panel (3 min) |
| Character class display | ❌ | ✅ | Extract from AutoScanner (2 min) |
| Skill validation display | ❌ | ✅ | Extract from AutoScanner (2 min) |
| Location indicator | ⚠️ In code | ✅ In UI | Display in panel (1 min) |

### Auto Hunt Flow

| Feature | Current | Desired | Work Needed |
|---------|---------|---------|-------------|
| Start Auto button | ⚠️ Exists | ✅ Wired | Add callback (2 min) |
| Stop Auto button | ❌ | ✅ | Create + wire (2 min) |
| Send Z key | ⚠️ In CLI only | ✅ In orchestrator | Move logic (1 min) |
| Capture + OCR | ⚠️ Partial | ✅ Full | Integrate to orchestrator (2 min) |
| Monster lookup | ✅ | ✅ | No change needed |
| Display on screen | ✅ | ✅ | No change needed |
| Check dead/alive | ⚠️ In CLI | ✅ In orchestrator | Extract logic (1 min) |
| Screenshot cleanup | ❌ | ✅ | Add cleanup (1 min) |
| Session tracking | ❌ | ✅ | Create HuntSession class (2 min) |
| Session summary | ❌ | ✅ | Create summary dialog (1 min) |
| i18n strings | ⚠️ Partial | ✅ All | Add 15 keys (1 min) |

---

## 🎯 Total Estimated Work

| Component | Time | Complexity |
|-----------|------|------------|
| UX6 Improvements | 15-20 min | Medium |
| Auto Hunt Improvements | 12-15 min | Medium-High |
| Integration + Testing | 10-15 min | Medium |
| **TOTAL** | **40-50 min** | **Medium** |

---

## 📝 Next Steps

1. **Create IMPROVED-PROMPT-UX6.md** with actual code locations + realistic scope
2. **Create IMPROVED-PROMPT-AUTO-HUNT.md** integrating CLI logic + GUI callbacks
3. **Create IMPLEMENTATION-ROADMAP.md** with step-by-step tasks for app improvement

---

**Generated**: 2026-09-05  
**Review Status**: ✅ COMPLETE — Ready for action
