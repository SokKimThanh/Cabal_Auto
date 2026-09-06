# Pre-Push Verification Checklist - Sprint 26 Skill Preset System

**Date**: 2026-09-06  
**Purpose**: Validate all critical paths before merging Sessions 24-29  
**Target Completion**: All ✅ PASS before push

---

## Phase 1: State Machine & Data Flow ⚙️

### 1.1 App Startup → Preset Loading

- [ ] **Test Case**: Launch app, navigate to Hunt Tab
  - **Expected**: AppStateController.load_preset_for_class() auto-invoked
  - **Check**: SkillPanel displays preset indicator (e.g., "⭐ Default - Mage")
  - **Validation**: Log output shows "Loading default preset for class_id=X"
  - **PROMPT-WL Ref**: Section 3.2a.2, Step 2-4

- [ ] **Verify**: skill_slots dict populated with correct structure
  - **Fields Present**: position, lane_type, skill_id, skill_name, user_hotkey, is_ready, cooldown_remaining, cooldown_max
  - **attack_combo**: Contains N slots (as defined in build tab, typically 3-4)
  - **buff_lane**: Contains M slots (as defined in build tab, typically 1-2)
  - **Check File**: `ui/controllers/app_state_controller.py` - skill_slots initialization
  - **PROMPT-WL Ref**: Section 3.2a.1 - detailed skill_slots structure

- [ ] **Validate**: Comboboxes populated from loaded preset
  - **Attack Combo Dropdowns**: Show skill names from attack_combo lane
  - **Buff Lane Dropdowns**: Show skill names from buff_lane
  - **Expected**: All combos have values, no empties
  - **Validation Script**:
    ```python
    # After UI renders, check combobox state
    assert len(skill_panel.widgets['combo_dropdowns']) == 4  # attack_combo
    assert len(skill_panel.widgets['buff_dropdowns']) == 2   # buff_lane
    for combo in skill_panel.widgets['combo_dropdowns']:
        assert len(combo['values']) > 0, "Combo should have skill options"
    ```

---

### 1.2 State Machine: Default Mode → Custom Mode

**PROMPT-WL Spec**: Section 3.1 - Preset State Machine

- [ ] **Starting State**: 
  - preset_mode = "default"
  - UI shows "⭐ Default - Mage" indicator
  - Validation: `assert app_state._preset_mode == "default"`

- [ ] **User Customization Trigger** (e.g., user changes combo skill selection):
  - **Check**: Does SkillPanel.on_skill_changed() call app_state.set_custom_mode()?
  - **Expected Result**:
    - preset_mode → "custom"
    - UI indicator changes to "✏️ Custom"
    - "Save" and "Reset" buttons become active
  - **Validation**:
    ```python
    # Simulate user changing skill
    skill_panel.widgets['combo_dropdowns'][0].set('Lightning')
    assert app_state._preset_mode == "custom"
    assert app_state._active_preset_id == app_state._custom_preset_id  # New custom ID
    ```

- [ ] **Save Custom Preset**:
  - **Trigger**: User clicks "Save" button → prompt for preset name → click OK
  - **Expected Flow**:
    1. Dialog prompts: "Enter preset name: [_________]"
    2. User types: "Boss Fight - Mage"
    3. Click [Save]
    4. SkillPresetService.create_custom_preset() called
    5. New row inserted in skill_presets (is_default=FALSE)
    6. preset_skills rows created for each slot
    7. user_preset_state.active_preset_id updated
    8. UI shows "✏️ Custom - Boss Fight - Mage"
  - **Validation**:
    ```python
    # Query DB after save
    preset_rows = cursor.execute(
        "SELECT * FROM skill_presets WHERE class_id = ? AND is_default = FALSE"
    ).fetchall()
    assert len(preset_rows) > 0, "Custom preset should exist in DB"
    assert preset_rows[0]['name'] == "Boss Fight - Mage"
    ```

- [ ] **Reset to Default Preset**:
  - **Trigger**: User clicks "🔄 Reset" button while in custom mode
  - **Expected Flow**:
    1. Dialog confirms: "Reset to default preset?"
    2. Click [Yes]
    3. AppStateController.apply_default_preset() called
    4. skill_slots reloaded from default preset
    5. UI updates to show default skills + "⭐ Default - Mage"
    6. preset_mode → "default"
  - **Validation**:
    ```python
    assert app_state._preset_mode == "default"
    assert app_state._active_preset_id == default_preset_id
    # Verify skill_slots restored
    assert app_state.skill_slots['attack_combo'] == original_skills
    ```

---

## Phase 2: PresetDialog Workflow 📋

**PROMPT-WL Spec**: Section 3.2a.2 - PresetDialog flow

### 2.1 Open PresetDialog

- [ ] **Trigger**: User clicks "📋 Presets" button
  - **Expected**: Modal dialog opens showing list of presets for current class
  - **Validation**:
    ```python
    # Check dialog exists and is visible
    assert hasattr(skill_panel, '_preset_dialog')
    assert skill_panel._preset_dialog.winfo_exists()
    ```

### 2.2 Preset List Rendering

- [ ] **Dialog Content**:
  - **Default Presets** (labeled with ⭐):
    - "[⭐ Default - Mage]" with [Apply] [Delete*] buttons
    - Default presets have Delete button DISABLED (*grayed out)
  - **Custom Presets**:
    - "[Custom - Boss]" with [Apply] [Delete] buttons
    - Custom presets have Delete button ENABLED
  - **Validation**:
    ```python
    # Inspect dialog treeview/listbox
    presets = dialog.get_preset_list()
    default_count = len([p for p in presets if p['is_default']])
    custom_count = len([p for p in presets if not p['is_default']])
    assert default_count >= 1, "Should have at least 1 default preset"
    ```

### 2.3 Apply Preset Action

- [ ] **Trigger**: User selects preset row → clicks [Apply]
  - **Flow**:
    1. SkillPresetService.apply_preset(preset_id, class_id) called
    2. preset_skills loaded for that preset
    3. skill_slots populated with new skills
    4. user_preset_state.active_preset_id updated
    5. Dialog closes
    6. SkillPanel refreshes with new skills
  - **Validation**:
    ```python
    # After apply
    assert app_state._active_preset_id == selected_preset_id
    assert skill_panel.widgets['preset_indicator'].cget('text').startswith('⭐' or '✏️')
    # Combos should show new skills
    for i, combo in enumerate(skill_panel.widgets['combo_dropdowns']):
        assert combo.get() != ''
    ```

### 2.4 Delete Preset Action

- [ ] **Trigger**: User selects custom preset → clicks [Delete]
  - **Flow**:
    1. Confirmation: "Delete preset 'Custom - Boss'?"
    2. Click [Yes]
    3. SkillPresetService.delete_custom_preset(preset_id) called
    4. Preset row deleted from skill_presets
    5. preset_skills rows deleted
    6. If was active, revert to default preset
    7. Dialog updates to show new list
  - **Validation**:
    ```python
    # Verify DB
    preset_row = cursor.execute(
        "SELECT * FROM skill_presets WHERE preset_id = ?"
    ).fetchone()
    assert preset_row is None, "Preset should be deleted from DB"
    ```

- [ ] **Cannot Delete Default Preset**:
  - Default preset's [Delete] button should be DISABLED (grayed out)
  - Clicking should show tooltip: "Cannot delete default preset"
  - **Validation**: `assert dialog.get_delete_button_state('default') == 'disabled'`

---

## Phase 3: SkillPanel Binding & State Updates 🎨

**PROMPT-WL Spec**: Section 3.2a.2 - SkillPanel interaction

### 3.1 Skill Slot Combobox Binding

- [ ] **Attack Combo Comboboxes**:
  - [ ] 4 comboboxes displayed (or as configured)
  - [ ] Each labeled "Slot 0", "Slot 1", etc.
  - [ ] Populated with available skills for class
  - [ ] Current selection shows loaded preset skill
  - [ ] Test: Change combo value → app_state.skill_slots updated
    ```python
    old_skill_id = app_state.skill_slots['attack_combo'][0]['skill_id']
    skill_panel.widgets['combo_dropdowns'][0].set('Lightning')
    new_skill_id = app_state.skill_slots['attack_combo'][0]['skill_id']
    assert old_skill_id != new_skill_id, "skill_slots should update on combo change"
    assert app_state._preset_mode == "custom", "Should enter custom mode"
    ```

- [ ] **Buff Lane Comboboxes**:
  - [ ] 2 comboboxes displayed (or as configured)
  - [ ] Each labeled "Buff Slot 0", "Buff Slot 1"
  - [ ] Populated with buff skills only (if available)
  - [ ] Behavior same as attack_combo

### 3.2 Mode Indicator Updates

- [ ] **Default Mode Display**:
  - Text shows: "⭐ Default - [PresetName]"
  - Color/styling: neutral (not highlighted)
  - Buttons: [Build] [Presets] [Reset]

- [ ] **Custom Mode Display**:
  - Text shows: "✏️ Custom - [PresetName]"
  - Color/styling: highlighted (warning/yellow)
  - Buttons: [Build] [Presets] [Save] [Reset]
  - "Save" button enabled, "Reset" button enabled

### 3.3 Hotkey Assignment (if implemented)

- [ ] **User Assigns Hotkey**:
  - Next to each skill combo: [Hotkey: 1 ▼] or [Assign? □]
  - User clicks dropdown → selects key (1, 2, 3, q, w, e, a, s, d)
  - app_state.set_skill_hotkey(lane, position, hotkey) called
  - skill_slots[lane][position].user_hotkey updated
  - **Validation**:
    ```python
    skill_panel.set_hotkey(lane='attack_combo', position=0, hotkey='1')
    assert app_state.skill_slots['attack_combo'][0]['user_hotkey'] == '1'
    ```

---

## Phase 4: Combo Mode Execution 🎮

**PROMPT-WL Spec**: Section 3.2 - Combo Mode State & Execution

### 4.1 Combo Mode Activation

- [ ] **UI Element Present**:
  - Button displayed: "[▶️ START COMBO MODE]"
  - Visible and clickable

- [ ] **Trigger Combo Mode**:
  - Click [▶️ START COMBO MODE]
  - **Expected Flow**:
    1. AppStateController.activate_combo_mode() called
    2. _combo_mode_active = True
    3. _combo_sequence_index = 0
    4. _combo_current_lane = "attack_combo"
    5. UI updates: button changes to "[⏹️ STOP COMBO MODE]"
    6. Skill selection dropdowns DISABLED (grayed out)
    7. Status shows: "🟢 COMBO MODE: ACTIVE"
  - **Validation**:
    ```python
    assert app_state._combo_mode_active == True
    assert skill_panel.get_combo_status() == "🟢 COMBO MODE: ACTIVE"
    for combo in skill_panel.widgets['combo_dropdowns']:
        assert combo['state'] == 'disabled', "Combos should be locked"
    ```

### 4.2 Skill Sequence Execution (Auto-Press)

- [ ] **During Hunt**: Skills execute automatically in sequence
  - Sequence: attack_combo[0] → cooldown → attack_combo[1] → cooldown → ...
  - After last attack slot: buff_lane[0] → cooldown → buff_lane[1] → cooldown → repeat
  - **Validation**: Check logs show skill presses
    ```
    [HuntRunner] Executing skill: Fireball (hotkey=1) - position=0, lane=attack_combo
    [HuntRunner] Skill ready in 1.2s (cooldown)
    [HuntRunner] Executing skill: Blizzard (hotkey=2) - position=1, lane=attack_combo
    ...
    ```

### 4.3 Cooldown Tracking

- [ ] **Cooldown Update During Execution**:
  - AppStateController.update_skill_cooldown(lane, position, remaining) called by BotManager
  - skill_slots[lane][position].cooldown_remaining updated
  - skill_slots[lane][position].is_ready recalculated (remaining == 0)
  - **Validation**:
    ```python
    app_state.update_skill_cooldown('attack_combo', 0, 0.8)
    assert app_state.skill_slots['attack_combo'][0]['cooldown_remaining'] == 0.8
    assert app_state.skill_slots['attack_combo'][0]['is_ready'] == False
    ```

### 4.4 Combo Mode Deactivation

- [ ] **Trigger**: User clicks [⏹️ STOP COMBO MODE] or hunt ends
  - **Expected Flow**:
    1. AppStateController.deactivate_combo_mode() called
    2. _combo_mode_active = False
    3. BotManager stops pressing hotkeys
    4. UI updates: button changes to "[▶️ START COMBO MODE]"
    5. Skill selection dropdowns RE-ENABLED
    6. Status shows: "🔴 COMBO MODE: INACTIVE"
  - **Validation**:
    ```python
    assert app_state._combo_mode_active == False
    assert skill_panel.get_combo_status() == "🔴 COMBO MODE: INACTIVE"
    for combo in skill_panel.widgets['combo_dropdowns']:
        assert combo['state'] == 'normal', "Combos should be unlocked"
    ```

---

## Phase 5: Database Integrity 🗄️

### 5.1 Schema Verification

- [ ] **Table Structure Correct**:
  ```sql
  -- Verify schema matches PROMPT-WL
  .schema skill_presets
  -- Should show: preset_id, class_id (FK), name, is_default, created_at, updated_at
  
  .schema preset_skills
  -- Should show: id, preset_id (FK), skill_id (FK), lane, position
  
  .schema user_preset_state
  -- Should show: class_id (PK), active_preset_id (FK), preset_mode, updated_at
  ```

- [ ] **Foreign Keys Active**:
  - `PRAGMA foreign_keys;` should return `1` (enabled)
  - Attempting to delete class with presets should fail (FK constraint)
  - **Validation**:
    ```python
    from database import get_db
    conn, is_local = get_db()
    result = conn.execute("PRAGMA foreign_keys;").fetchone()
    assert result[0] == 1, "Foreign keys should be enabled"
    if is_local:
        conn.close()
    ```

### 5.2 Data Migration from Old Schema

- [ ] **If Old Schema Exists**:
  - Old preset data from JSON migrated to new tables
  - Migration script creates skill_presets rows with migrated data
  - preset_skills created with correct skill_ids and ordering
  - **Validation**: Query presets for each class, verify count matches
    ```python
    legacy_presets_count = len(legacy_json['presets'])
    db_presets_count = cursor.execute(
        "SELECT COUNT(*) FROM skill_presets WHERE is_default = TRUE"
    ).fetchone()[0]
    assert db_presets_count >= legacy_presets_count
    ```

### 5.3 Query Validation

- [ ] **Repository Queries Return Correct Data**:
  - SkillPresetRepository.get_presets_by_class(class_id=1) returns ≥1 preset
  - PresetStateManager.get_active_preset(class_id=1) returns valid preset_id
  - SkillRepository.list_skills() returns skills for class
  - **Validation Script**:
    ```python
    from lib.db.repositories import SkillPresetRepository, PresetStateManager
    repo = SkillPresetRepository()
    
    presets = repo.get_presets_by_class(1)
    assert len(presets) > 0, "Should have presets"
    assert 'name' in presets[0]
    assert 'class_id' in presets[0]
    
    # Verify class_id in result matches query
    for preset in presets:
        assert preset['class_id'] == 1
    ```

---

## Phase 6: Error Handling & Edge Cases 🛡️

### 6.1 No Default Preset Exists

- [ ] **Scenario**: User selects class with NO default preset
  - **Expected**: App shows error: "No default preset for this class"
  - **Handler**: create_default_preset() or show config UI
  - **Check**: No crash, graceful fallback

### 6.2 Rapid Preset Switching

- [ ] **Scenario**: User opens PresetDialog, clicks [Apply] multiple times rapidly
  - **Expected**: Only last preset applied (race condition handled)
  - **Check**: No duplicate loads, skill_slots consistent

### 6.3 Preset Deleted During Hunt

- [ ] **Scenario**: User deletes custom preset via PresetDialog while hunt is running
  - **Expected**: Hunt continues with active preset (delete doesn't affect running state)
  - **Check**: skill_slots unchanged, no crash

### 6.4 Class Switching During Combo Mode

- [ ] **Scenario**: User switches class while combo mode active
  - **Expected**: 
    1. Combo mode deactivated automatically
    2. skill_slots reloaded for new class
    3. New preset applied
  - **Check**: No orphaned threads, clean state transition

### 6.5 Empty Skill List

- [ ] **Scenario**: Class has no available skills
  - **Expected**: UI shows empty dropdowns with tooltip "No skills available for this class"
  - **Check**: No crash, UI remains responsive

### 6.6 Concurrent DB Access

- [ ] **Scenario**: Multiple operations on DB (e.g., save preset + hunt running)
  - **Expected**: No "database locked" errors
  - **Check**: Connection pooling handles concurrency
  - **Validation**:
    ```python
    # Simulate concurrent access
    import threading
    def save_preset():
        service.create_custom_preset(...)
    def read_preset():
        service.list_presets_by_class(1)
    
    threads = [threading.Thread(target=save_preset) for _ in range(5)]
    threads += [threading.Thread(target=read_preset) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # Should complete without errors
    ```

---

## Phase 7: Test Coverage Validation ✅

### 7.1 Unit Tests (AppStateController methods)

- [ ] `test_load_preset_for_class_default()` 
  - Verify skill_slots populated correctly
  - preset_mode = "default"

- [ ] `test_set_custom_mode()`
  - Verify preset_mode switches
  - UI indicator updates

- [ ] `test_save_custom_preset()`
  - Verify preset inserted in DB
  - active_preset_id updated

- [ ] `test_apply_default_preset()`
  - Verify skill_slots reset
  - preset_mode = "default"

- [ ] `test_activate_deactivate_combo_mode()`
  - Verify state flags toggle
  - UI elements update

- [ ] `test_update_skill_cooldown()`
  - Verify cooldown tracked
  - is_ready flag updates

### 7.2 Integration Tests (UI + Service + DB)

- [ ] `test_end_to_end_default_preset_workflow()`
  - Launch → Load preset → Display skills → Close

- [ ] `test_end_to_end_custom_preset_workflow()`
  - Load preset → Edit skills → Save custom → Apply → Verify DB

- [ ] `test_preset_dialog_apply_workflow()`
  - Open dialog → Select custom preset → Click Apply → Verify UI updates

- [ ] `test_combo_mode_activation_with_hotkeys()`
  - Activate combo mode → Verify sequence execution → Deactivate

### 7.3 Run All Tests

- [ ] **Command**: `pytest tests/ -v --tb=short -m "db or ui"`
  - All tests pass ✅
  - No warnings or deprecations
  - Coverage ≥80% for modified files

---

## Phase 8: Code Review Checklist 👀

### 8.1 AppStateController

- [ ] skill_slots structure matches PROMPT-WL 3.2a.1 (all required fields)
- [ ] Event callbacks properly registered (register_callback mechanism works)
- [ ] No hardcoded values (magic numbers, strings)
- [ ] Logging present for debugging
- [ ] Error handling for DB operations
- [ ] Type hints present for all methods
- [ ] Comments explain complex logic

### 8.2 SkillPanel

- [ ] Combos dynamically bound to app_state.skill_slots
- [ ] Buff lane section implemented (not stub)
- [ ] State indicator (⭐ vs ✏️) updates correctly
- [ ] Buttons (Build, Presets, Save, Reset) all functional
- [ ] No direct DB queries (use service layer only)
- [ ] Graceful error handling (empty preset list, no skills)

### 8.3 PresetDialog

- [ ] Renders full preset list (default + custom)
- [ ] Default preset [Delete] button disabled
- [ ] Custom preset [Delete] button enabled
- [ ] [Apply] button logic correct
- [ ] [Delete] button logic correct
- [ ] Dialog closes after action
- [ ] Callbacks fire correctly to update SkillPanel

### 8.4 Database & Repositories

- [ ] All queries use class_id (not class_name)
- [ ] Connection closing respects is_local flag
- [ ] No hardcoded table/column names (constants used)
- [ ] Error logging present
- [ ] Transaction handling for multi-table operations
- [ ] Indexes present for performance (class_id, preset_id, skill_id)

### 8.5 Code Style & Testing

- [ ] Code formatted with `black`
- [ ] Linting passes: `flake8 --max-line-length=100`
- [ ] No TODO/FIXME comments left behind
- [ ] Test files follow naming: `test_*.py`
- [ ] Tests use pytest markers: `@pytest.mark.db`, `@pytest.mark.ui`
- [ ] No hardcoded paths (use constants)

---

## Final Pre-Push Validation

### Checklist Summary
- [ ] **Phase 1** (State Machine): ✅ All tests pass
- [ ] **Phase 2** (PresetDialog): ✅ All workflows verified
- [ ] **Phase 3** (SkillPanel): ✅ Binding works, buff_lane present
- [ ] **Phase 4** (Combo Mode): ✅ Activation/deactivation works
- [ ] **Phase 5** (Database): ✅ Schema correct, queries validated
- [ ] **Phase 6** (Edge Cases): ✅ No crashes, graceful handling
- [ ] **Phase 7** (Tests): ✅ 80%+ coverage, all passing
- [ ] **Phase 8** (Code Review): ✅ Style, comments, error handling OK

### Git Pre-Push Verification
```bash
# Run tests
pytest tests/ -v --tb=short

# Check style
black --check .
flake8 --max-line-length=100 lib/ ui/ tests/

# Verify app starts without errors
python app_gui.py

# Manual QA (5 minutes)
# 1. Select class → verify preset loads
# 2. Change skill → verify custom mode
# 3. Open PresetDialog → apply preset
# 4. Save custom → verify in DB
# 5. Start combo mode → verify execution
```

---

## Sign-Off

**Ready to Push**: ______ (Date/Time)

**By**: ________________________ (Reviewer)

**Notes**: 
```
[Document any findings, deviations, or follow-up work needed]
```

---

## Post-Merge Follow-Up (Sessions 30+)

- [ ] Monitor for preset loading issues in real usage
- [ ] Gather user feedback on UI/UX
- [ ] Performance testing under load
- [ ] Internationalization (i18n) for preset names
- [ ] Advanced features:
  - Preset import/export (JSON/CSV)
  - Preset templates (public/community)
  - Skill rotation patterns (alternate combos per trigger)
  - Macro recording (complex sequences)
