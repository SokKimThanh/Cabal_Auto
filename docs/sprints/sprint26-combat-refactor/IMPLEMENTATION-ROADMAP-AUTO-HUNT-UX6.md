# 🚀 IMPLEMENTATION ROADMAP: Auto Hunt Features

**Goal**: Implement App-Focused UX6 + Auto Hunt Flow improvements  
**Total Time**: ~50-60 minutes (realistic)  
**Complexity**: Medium  
**Risk**: Low (all backend exists, just UI wiring)

---

## 📋 Phase 1: UX6 Window Detection (12 min)

**Goal**: Add window selection UI to main HuntTab + show screen state

### Subtask 1.1: Add Window Combo + Refresh Button (3 min)
- **File**: `ui/tabs/hunt_tab.py`
- **Action**: 
  1. Add window frame with combobox
  2. Add refresh button
  3. Wire to `AppWindowController.on_hunt_find_windows()`
- **Verification**: Combobox shows game windows on startup

### Subtask 1.2: Call Enumerate on App Startup (1 min)
- **File**: `app_gui.py`
- **Action**:
  1. Add `self.after(500, self.window_controller.on_hunt_find_windows)`
- **Verification**: Windows populate on app start

### Subtask 1.3: Add Scan Button (1 min)
- **File**: `ui/tabs/hunt_tab.py`
- **Action**:
  1. Add "🔍 Quét Màn Hình" button
  2. Wire to `on_scan_screen()` callback
  3. Disable until window selected

### Subtask 1.4: Create Screen State Display Panel (5 min)
- **File**: `ui/tabs/hunt_tab.py`
- **Action**:
  1. Create LabelFrame for screen state
  2. Add labels for: character class, skills, location, monsters
  3. Implement `on_scan_screen()` to call `AutoScanner.run_scan()`
  4. Display results in labels
- **Verification**: 
  - Click scan → character class displayed
  - Click scan → skill count displayed
  - Click scan → location shown
  - Click scan → monster count shown

### Subtask 1.5: Add i18n Keys (1 min)
- **File**: `lib/i18n/translations.json`
- **Action**: Add 12 keys for UX6 labels
- **Verification**: All labels translated

### Subtask 1.6: Test UX6 End-to-End (1 min)
- App startup → windows in combo
- Click refresh → re-enumerates
- Select window → stored to config
- Click scan → screen state displayed

**Expected Output**: 
- Window combo in HuntTab
- Scan button functional
- Character class, skills, location, monsters displayed on scan

---

## 📋 Phase 2: Auto Hunt Flow (25 min)

**Goal**: Create AutoHuntOrchestrator + wire Start/Stop buttons

### Subtask 2.1: Create AutoHuntOrchestrator Class (8 min)
- **File**: `lib/features/hunt/auto_hunt_orchestrator.py` (NEW)
- **Action**:
  1. Copy code from IMPROVED-PROMPT-AUTO-HUNT-FLOW.md
  2. Implement 9 methods: `_send_z_key()`, `_capture_and_extract()`, etc.
  3. Implement `start_hunt()` and `stop_hunt()`
  4. Add session tracking (HuntSessionStats dataclass)
- **Verification**: 
  - Import succeeds
  - No syntax errors
  - All methods callable

### Subtask 2.2: Add Start/Stop Buttons to HuntTab (3 min)
- **File**: `ui/tabs/hunt_tab.py`
- **Action**:
  1. Add button frame with 2 buttons
  2. Implement `on_start_auto()` → disable start, enable stop
  3. Implement `on_stop_auto()` → reverse buttons, show summary
  4. Add status label showing "⏳ Đang quét..." during hunt
- **Verification**: 
  - Buttons visible
  - Start button enables, stop button disabled initially
  - Click start → stop button enables

### Subtask 2.3: Wire Orchestrator to App (3 min)
- **File**: `app_gui.py`
- **Action**:
  1. Import `AutoHuntOrchestrator`
  2. Initialize in `App.__init__()`
  3. Pass all required params (vision_engine, monster_repo, etc.)
  4. Pass callbacks (schedule_ui_task, update_target_hp, etc.)
- **Verification**: Orchestrator initializes without error

### Subtask 2.4: Wire Buttons to Orchestrator (3 min)
- **File**: `ui/tabs/hunt_tab.py`
- **Action**:
  1. Connect `on_start_auto()` to `self.app.auto_hunt_orchestrator.start_hunt()`
  2. Connect `on_stop_auto()` to `self.app.auto_hunt_orchestrator.stop_hunt()`
  3. Show summary dialog after stop
- **Verification**: 
  - Click start → orchestrator.start_hunt() called
  - Click stop → orchestrator.stop_hunt() called
  - Summary shows kills, time, drops

### Subtask 2.5: Test Z-Key Sending (2 min)
- **File**: (Already in AutoHuntOrchestrator)
- **Action**:
  1. Add debug logging to `_send_z_key()`
  2. Run hunt cycle once
  3. Check logs for "Z key sent"
- **Verification**: Logs show Z key sent

### Subtask 2.6: Test Screenshot Cleanup (2 min)
- **File**: (Already in AutoHuntOrchestrator)
- **Action**:
  1. Check `tmp/hunt_screenshots` folder
  2. Run hunt for 2 cycles
  3. Verify no leftover screenshots
- **Verification**: Folder stays empty

### Subtask 2.7: Test Session Tracking (2 min)
- **File**: (Already in AutoHuntOrchestrator)
- **Action**:
  1. Run hunt
  2. Kill some monsters
  3. Stop hunt
  4. Verify summary shows correct count
- **Verification**: Summary shows monsters_killed, duration, drops

### Subtask 2.8: Add i18n Keys (1 min)
- **File**: `lib/i18n/translations.json`
- **Action**: Add 8 keys for Auto Hunt labels
- **Verification**: All labels translated

**Expected Output**:
- AutoHuntOrchestrator class created
- Start/Stop buttons wired
- Hunt loop runs when start clicked
- Summary shown when stop clicked
- Session stats tracked

---

## 📋 Phase 3: Integration & Testing (15 min)

### Subtask 3.1: Integrate HuntTab Updates (3 min)
- **File**: `app_gui.py`
- **Action**:
  1. Ensure HuntTab.update_target_card() called by orchestrator
  2. Ensure HuntTab.update_hp_display() called by orchestrator
  3. Test monster appears when hunt running
- **Verification**: Target card updates in real-time during hunt

### Subtask 3.2: End-to-End Test UX6 → Start Hunt (5 min)
- **Action**:
  1. Start app
  2. Windows auto-enumerate
  3. Select window
  4. Click scan → screen state shows
  5. Click start auto → hunt begins
  6. Monster appears on target card
  7. HP updates as hunt progresses
  8. Click stop → summary shows
- **Verification**: Full workflow works

### Subtask 3.3: Test Edge Cases (3 min)
- [ ] No window selected → start button disabled or shows error
- [ ] No monsters found → hunt waits and continues
- [ ] Monster dies mid-hunt → session count increments
- [ ] Stop clicked mid-scan → hunt stops cleanly
- [ ] App closed during hunt → thread cleanup OK

### Subtask 3.4: Create Unit Tests (2 min)
- **File**: `tests/test_auto_hunt_orchestrator.py`
- **Action**:
  1. Test `_send_z_key()` with mocked pyautogui
  2. Test `_capture_and_extract()` with mock frame
  3. Test `_check_if_dead()` with mock monster data
  4. Test start/stop state transitions
- **Verification**: Tests pass

### Subtask 3.5: Performance Check (2 min)
- **Action**:
  1. Run hunt for 30 seconds
  2. Check CPU usage (should be <20%)
  3. Check memory (should be <100MB growth)
  4. Check for thread leaks (should clean up on stop)
- **Verification**: No performance degradation

**Expected Output**:
- Full integration working
- Edge cases handled
- Tests passing
- Performance acceptable

---

## 🎯 Task Priority & Execution Order

### CRITICAL (Do First - 5 min)
1. Create AutoHuntOrchestrator class (Subtask 2.1)
   - This is the foundation for auto hunt
   - All other tasks depend on it

### HIGH (Do Next - 20 min)
2. Add window combo to HuntTab (Subtask 1.1)
3. Add scan button + screen state panel (Subtask 1.4)
4. Wire orchestrator to app (Subtask 2.3)
5. Add start/stop buttons (Subtask 2.2)
6. Wire buttons to orchestrator (Subtask 2.4)

### MEDIUM (Do After - 15 min)
7. Add all i18n keys (Subtask 1.5 + 2.8)
8. Integrate HuntTab updates (Subtask 3.1)
9. End-to-end test (Subtask 3.2)
10. Create unit tests (Subtask 3.4)

### LOW (Do Last - 5 min)
11. Test edge cases (Subtask 3.3)
12. Performance check (Subtask 3.5)

---

## 🔧 Execution Checklist

### Before Starting
- [ ] All prompts reviewed (IMPROVED-PROMPT-UX6.md + IMPROVED-PROMPT-AUTO-HUNT-FLOW.md)
- [ ] Code snippets copied and ready
- [ ] Test cases planned

### Phase 1 Execution (UX6 - 12 min)
- [ ] 1.1: Window combo added to HuntTab
- [ ] 1.2: Enumeration called on startup
- [ ] 1.3: Scan button created and wired
- [ ] 1.4: Screen state panel displays results
- [ ] 1.5: i18n keys added
- [ ] 1.6: UX6 end-to-end test passed

### Phase 2 Execution (Auto Hunt - 25 min)
- [ ] 2.1: AutoHuntOrchestrator class created
- [ ] 2.2: Start/Stop buttons added to HuntTab
- [ ] 2.3: Orchestrator initialized in app
- [ ] 2.4: Buttons wired to orchestrator
- [ ] 2.5: Z-key sending tested
- [ ] 2.6: Screenshot cleanup working
- [ ] 2.7: Session tracking working
- [ ] 2.8: i18n keys added

### Phase 3 Execution (Integration - 15 min)
- [ ] 3.1: HuntTab updates wired
- [ ] 3.2: End-to-end test passed
- [ ] 3.3: Edge cases tested
- [ ] 3.4: Unit tests created
- [ ] 3.5: Performance acceptable

### After Completion
- [ ] All tests passing
- [ ] No regressions
- [ ] Code review done
- [ ] Documentation updated

---

## 📊 Time Breakdown

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | UX6 Window Detection | 12 min | 📋 Planned |
| 2 | Auto Hunt Flow | 25 min | 📋 Planned |
| 3 | Integration & Test | 15 min | 📋 Planned |
| **TOTAL** | | **52 min** | 🚀 Ready |

---

## 🎁 Deliverables

After completing this roadmap:

1. ✅ **UX6 Features**
   - Window selection in main HuntTab
   - Refresh button
   - Scan button with screen state display
   - Character class, skills, location indicators

2. ✅ **Auto Hunt Flow Features**
   - Start Auto button wired and working
   - Stop Auto button with summary
   - Automatic Z-key sending
   - Screenshot cleanup
   - Session tracking (kills, EXP, drops)
   - Monster display updates in real-time
   - Session summary dialog

3. ✅ **Code Quality**
   - Proper threading (background + UI callbacks)
   - Error handling
   - i18n support (Vietnamese labels)
   - Unit tests
   - Performance validated

4. ✅ **Documentation**
   - Implementation guide (this file)
   - Feature status updates
   - Edge case handling documented

---

## ⚠️ Known Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Z-key not sending to game window | Medium | High | Test with actual game; add logging |
| Monster detection fails | Low | High | Fallback to manual targeting; error display |
| Thread deadlock on stop | Low | High | Use Event instead of flag; join with timeout |
| Memory leak from screenshots | Low | Medium | Explicit cleanup in cycle; verify folder empty |
| UI thread stalls | Low | High | All work in background thread; use callbacks |

---

## 🎯 Next Steps After Roadmap

1. **Follow Execution Checklist** above in order
2. **Test Each Subtask** before moving to next
3. **Update This Roadmap** as tasks complete
4. **Report Blocking Issues** immediately
5. **Create PR** when all tasks done

---

**Roadmap Created**: 2026-09-05  
**Status**: ✅ READY FOR EXECUTION  
**Estimated Duration**: 50-60 minutes  
**Complexity Level**: MEDIUM  
**Ready to Start**: YES

