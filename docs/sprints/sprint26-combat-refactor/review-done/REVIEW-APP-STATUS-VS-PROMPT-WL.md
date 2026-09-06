# Review: Current App Status vs. PROMPT-WL Requirements

**Date**: 2026-09-06  
**Status**: ⚠️ PARTIALLY IMPLEMENTED - Multiple Critical Gaps

---

## Executive Summary

The workspace redesign implementation (Sessions 24-29) has made significant progress on **backend infrastructure** but has **critical gaps in UI logic, state management, and data population**. The app starts without crashing (post-connection fix), but the skill preset system is largely non-functional from a user perspective.

| Area | Status | Issues |
|------|--------|--------|
| **Database Schema** | ✅ DONE | skill_presets, preset_skills, user_preset_state tables created |
| **Repository Layer** | ⚠️ PARTIAL | Connection leak fixed, but methods untested |
| **Service Layer** | ✅ DONE | SkillPresetService implemented correctly |
| **UI Layout** | ✅ DONE | 4-panel structure in HuntTab implemented |
| **SkillPanel Component** | ❌ BROKEN | Dropdowns created but unpopulated; buff_lane missing |
| **AppStateController** | ❌ MISSING | No preset state management methods |
| **Data Flow** | ❌ BROKEN | skill_slots not populated; no preset loading |
| **State Machine** | ❌ MISSING | No preset mode switching (default↔custom) |

---

## 1. Database Schema ✅ DONE

### Current Status
All 3 required tables created in `lib/db/schema.py`:

```sql
✅ skill_presets (preset_id, class_name, name, is_default, created_at, updated_at)
✅ preset_skills (id, preset_id, skill_id, lane, position)
✅ user_preset_state (class_name, active_preset_id, preset_mode, updated_at)
```

### Issues Found
- ⚠️ Using `class_name TEXT` instead of `class_id INTEGER FK` (PROMPT-WL specifies class_id FK to classes table)
- ⚠️ Should enforce unique constraints on (class_name, name, is_default) for skill_presets
- ⚠️ Missing indexes for performance (idx_presets_class, idx_preset_skills_preset, idx_preset_skills_skill)

### Fix Required
```python
# CURRENT (WRONG)
class_name TEXT NOT NULL

# SHOULD BE (CORRECT per PROMPT-WL)
class_id INTEGER NOT NULL FOREIGN KEY(class_id) REFERENCES classes(class_id)
```

---

## 2. Repository Layer ⚠️ PARTIAL

### Current Status
✅ Database connection leak fixed (is_local flag properly checked in finally blocks)

Files fixed:
- ✅ `lib/db/repositories/skill_preset_repository.py`
- ✅ `lib/db/repositories/preset_state_manager.py`
- ✅ `lib/db/repositories/skill_repository.py`

### Issues Found

#### 2.1 PresetStateManager - Queries Using Wrong FK
```python
# CURRENT (WRONG - using class_name)
cursor.execute("SELECT active_preset_id FROM user_preset_state WHERE class_name = ?", (class_name,))

# SHOULD BE (per PROMPT-WL - using class_id)
cursor.execute("SELECT active_preset_id FROM user_preset_state WHERE class_id = ?", (class_id,))
```

#### 2.2 SkillPresetRepository - Wrong Column Name
```python
# CURRENT (WRONG)
"SELECT * FROM skill_presets WHERE class_name = ?"

# SHOULD BE
"SELECT * FROM skill_presets WHERE class_id = ?"
```

#### 2.3 No Error Logging
- Repositories silently return empty results on errors (no logging/debugging)
- Should log exceptions for troubleshooting

#### 2.4 Untested End-to-End
- Test script shows repositories work at SQL level
- But no validation that data flows correctly through service layer
- No integration tests

### Status: 🔴 BLOCKING
Repositories use wrong column names (class_name vs class_id), will query wrong data.

---

## 3. Service Layer ✅ DONE

### Current Status
`lib/features/skills/skill_preset_service.py` implemented correctly:
- ✅ `apply_preset()` - Load preset and populate skills
- ✅ `create_custom_preset()` - Save user customization
- ✅ `update_custom_preset()` - Modify existing preset
- ✅ `delete_custom_preset()` - Remove custom preset
- ✅ `list_presets_by_class()` - Query all presets for class
- ✅ `migrate_legacy_presets()` - JSON→DB migration support

### Issues Found
None identified in service logic itself. Service layer correctly implements specification.

### Status: ✅ WORKING

---

## 4. UI Layout - Hunt Tab ✅ DONE

### Current Status
4-panel structure correctly implemented in `ui/tabs/hunt_tab.py`:

```
┌─────────────────────────┬─────────────────────────┐
│  col_interaction (60%)  │  col_monitoring (40%)   │
├─────────────────────────┼─────────────────────────┤
│  container_monster      │  container_target       │
│  target (35% height)    │  status (35% height)    │
├─────────────────────────┼─────────────────────────┤
│  container_skill_panel  │  container_skill_stats  │
│  (65% height)           │  (65% height)           │
└─────────────────────────┴─────────────────────────┘
```

### Issues Found
✅ No issues - layout structure is correct

### Status: ✅ WORKING

---

## 5. SkillPanel Component ❌ BROKEN

### Current Status
`ui/panels/skill_panel.py` created but has **critical functional gaps**:

```python
class SkillPanel:
    def __init__(self, parent, app_state):
        self.frame = tk.Frame(parent)
        self.app_state = app_state
        self.skill_service = SkillPresetService()
        self._build()
    
    def _build(self):
        # Header with preset indicator + buttons
        tk.Label(header_frame, text="⭐ Default")  # Preset indicator
        tk.Button(btn_frame, text="⚙️ Build")      # Placeholder - not functional
        tk.Button(btn_frame, text="📋 Presets")    # SHOULD open PresetDialog
        tk.Button(btn_frame, text="🔄 Reset")      # SHOULD apply default preset
        
        # Try to load skill values for combobox
        skills = self.skill_service.skill_repo.list_skills()
        skill_names = [s.get('name') for s in skills]
        
        # Create attack_combo dropdowns (UNPOPULATED)
        for i in range(4):
            combo = ttk.Combobox(...)
            combo.values = skill_names  # ❌ This only works if skills are loaded
        
        # ❌ BUFF_LANE SECTION IS MISSING
        # (Only attack_combo slots created, no buff_lane)
```

### Issues Found

#### 5.1 Combobox Values Not Populated ❌ BLOCKING
```python
# CURRENT: Loads all global skills
skills = self.skill_service.skill_repo.list_skills()  # No class filtering!
skill_names = [s.get('name') for s in skills]

# SHOULD BE (per PROMPT-WL):
class_name = self.app_state._current_class  # Get selected class
presets = self.skill_service.list_presets_by_class(class_name)  # Get class presets
# Extract skill_ids from active preset's preset_skills
# Then populate combobox with AVAILABLE SKILLS FOR THIS CLASS ONLY
```

#### 5.2 Buff Lane Missing ❌ BLOCKING
```python
# CURRENT:
for i in range(4):
    combo = ttk.Combobox(...)  # Only attack_combo

# SHOULD BE:
# Attack Combo section (0-3 slots)
for i in range(4):
    combo = ttk.Combobox(...)  # attack_combo[i]

# Buff Lane section (0-2 slots)
for i in range(2):
    combo = ttk.Combobox(...)  # buff_lane[i]
```

#### 5.3 No State Binding ❌ BLOCKING
- SkillPanel doesn't read from app_state.skill_slots
- SkillPanel doesn't update app_state.skill_slots on combo changes
- No event listeners for state changes

#### 5.4 PresetDialog Not Callable ❌ BLOCKING
```python
def on_presets(self):
    dialog = PresetDialog(self.frame, self.app_state)
    # ✅ Dialog created, but:
    # - No way to select/apply preset
    # - No way to save custom preset
    # - No return value handling
```

#### 5.5 Reset Button Placeholder ❌ BLOCKING
```python
def on_reset(self):
    pass  # NOT IMPLEMENTED

# SHOULD:
# Load default preset for current class
# Update app_state.skill_slots
# Refresh UI
```

### Status: 🔴 BLOCKING (Core feature broken)

---

## 6. PresetDialog Implementation ⚠️ PARTIAL

### Current Status
`ui/dialogs/preset_dialog.py` created with basic structure:

```python
class PresetDialog(tk.Toplevel):
    def __init__(self, parent, app_state):
        super().__init__(parent)
        self.app_state = app_state
        self._load_presets()  # ← Calls list_presets_by_class()
    
    def _load_presets(self):
        class_name = getattr(self.app_state, '_current_class', 'Unknown')
        self.presets = self.service.list_presets_by_class(class_name)  # Queries DB
        # ❌ But nothing done with results - no UI rendering
```

### Issues Found

#### 6.1 UI Not Rendered
```python
# CURRENT:
def _load_presets(self):
    self.presets = self.service.list_presets_by_class(class_name)
    # ❌ Returns list but doesn't create UI widgets

# SHOULD BE:
def _load_presets(self):
    presets = self.service.list_presets_by_class(class_name)
    for preset in presets:
        # Create: [⭐ Default-Mage] [Apply] [Delete*]
        # Create: [Custom-Mage1] [Apply] [Delete]
        # (with proper styling per spec)
```

#### 6.2 Button Actions Not Implemented
- No [Apply] button logic
- No [Delete] button logic  
- No [Cancel] button logic
- Dialog has no way to communicate back to SkillPanel

#### 6.3 No Integration with SkillPanel
```python
# CURRENT (SkillPanel.on_presets):
def on_presets(self):
    dialog = PresetDialog(self.frame, self.app_state)
    # Creates dialog but doesn't wait for result

# SHOULD BE:
def on_presets(self):
    dialog = PresetDialog(self.frame, self.app_state, callback=self.on_preset_selected)
    self.frame.wait_window(dialog.frame)

def on_preset_selected(self, preset_id):
    self.skill_service.apply_preset(preset_id, self.app_state._current_class)
    self.on_skill_slots_changed()  # Refresh UI
```

### Status: 🔴 BLOCKING (Dialog not functional)

---

## 7. AppStateController - Preset State Methods ❌ MISSING

### Current Status
`ui/controllers/app_state_controller.py` is initialized but **LACKS all preset-related methods**.

```python
class AppStateController:
    def __init__(self, root):
        app.skill_selected_index = None
        app.skill_slot_vars = []
        app.skill_slot_boxes = []
        app.skill_slot_count = 6
        # ❌ No preset state attributes
        # ❌ No skill_slots dict
        # ❌ No _current_class, _active_preset_id, _preset_mode
```

### Missing Methods (Per PROMPT-WL Section 3.2)

#### Required Preset State Methods
```python
# MISSING - Should load preset for class
def load_preset_for_class(self, class_id: int):
    pass

# MISSING - Should reset to default preset
def apply_default_preset(self, class_id: int):
    pass

# MISSING - Should mark as custom mode
def set_custom_mode(self):
    pass

# MISSING - Should save custom preset to DB
def save_custom_preset(self, preset_name: str):
    pass

# MISSING - Should get list of presets
def get_available_presets(self, class_id: int) -> List:
    pass

# MISSING - Preset state tracking
_current_class_id: int = 1
_active_preset_id: int = None
_preset_mode: str = "default"  # 'default' or 'custom'
```

#### Required Skill Slots Methods
```python
# MISSING - Skill slots structure (per PROMPT-WL 3.2a.1)
skill_slots: dict = {
    "attack_combo": [
        {
            "position": 0,
            "lane_type": "attack_combo",
            "skill_id": 1,
            "skill_name": "Fireball",
            "user_hotkey": "1",
            "assigned": False,
            "is_ready": True,
            "cooldown_remaining": 0.0,
            # ... more fields
        },
        # ... more slots
    ],
    "buff_lane": [
        # ... buff slots
    ]
}

# MISSING - Combo mode methods
def activate_combo_mode(self):
    pass

def deactivate_combo_mode(self):
    pass

def get_combo_mode_status(self) -> str:
    pass

def set_skill_hotkey(self, lane: str, position: int, hotkey: str):
    pass

def update_skill_cooldown(self, lane: str, position: int, remaining: float):
    pass
```

#### Required Event Callbacks
```python
# MISSING - Should notify UI of state changes
def register_callback(self, event: str, handler):
    pass

# Events that should be emitted:
# - on_skill_slots_changed
# - on_preset_changed
# - on_combo_mode_activated
# - on_combo_mode_deactivated
# - on_hotkey_changed
# - on_cooldown_updated
```

### Status: 🔴 BLOCKING (Core state management missing)

---

## 8. Data Flow - skill_slots Population ❌ BROKEN

### Current PROMPT-WL Spec (Section 3.2a.2)

Expected flow when user loads hunt tab:
```
1. App starts / User selects class
2. System calls: app_state.load_preset_for_class(class_id)
3. AppStateController queries: service.list_presets_by_class(class_id)
4. Gets default preset (is_default=TRUE)
5. Queries preset_skills for that preset
6. Joins with skills table to get full details
7. Populates: app_state.skill_slots with:
   - skill_id, skill_name, icon_x/y, user_hotkey (empty), is_ready, cooldown, etc.
8. SkillPanel reads: app_state.skill_slots
9. SkillPanel renders: combos with skill_names populated
10. User can click combo, select different skill, assign hotkey
```

### Current Implementation

❌ **Steps 1-7 are completely missing**

What actually happens:
```
1. HuntTab loads
2. SkillPanel.__init__() called
3. SkillPanel calls: skill_service.skill_repo.list_skills()
   - Returns ALL global skills (no class filtering)
   - Tries to populate combobox with all skill names
4. SkillPanel has NO link to app_state.skill_slots
5. Changes in combobox don't update app_state
6. Changing tabs/class doesn't reload skill_slots
```

### Status: 🔴 BLOCKING (Core data flow missing)

---

## 9. State Machine - Preset Switching ❌ MISSING

### PROMPT-WL Spec (Section 3.1)

Expected state transitions:
```
START
  ↓
[Load Default Preset]  ← Should happen automatically
  ↓
PRESET MODE: DEFAULT (Read-Only)
  ├─ User clicks "📋 Presets" → PresetDialog
  │   ├─ Select custom preset → apply_preset()
  │   └─ DELETE custom → delete_preset()
  │
  └─ User customizes skills → set_custom_mode()
       ↓
    PRESET MODE: CUSTOM (Allow edits)
       ├─ Click "Save" → save_custom_preset()
       └─ Click "Reset" → apply_default_preset()
```

### Current Implementation
❌ **No state machine implemented**

What's missing:
- No automatic preset loading on app start
- No mode switching (default ↔ custom)
- No logic to disable/enable UI based on mode
- Buttons (Save, Reset) are placeholders

### Status: 🔴 BLOCKING (Business logic missing)

---

## 10. Integration Testing ❌ NO TESTS

### Current Status
- ✅ `test_fix_db_connection.py` verifies repositories don't crash
- ❌ No end-to-end tests for preset workflow
- ❌ No tests for skill_slots population
- ❌ No tests for state transitions

### Required Tests (for Sessions 24-29 completion)
```python
# Missing test cases:
test_load_default_preset_for_class()
test_apply_custom_preset()
test_save_custom_preset()
test_delete_custom_preset()
test_skill_slots_populated_correctly()
test_preset_mode_transitions()
test_combobox_populated_with_preset_skills()
test_skill_hotkey_assignment()
test_cooldown_updates()
test_preset_dialog_apply_button()
test_preset_dialog_delete_button()
```

### Status: 🔴 NOT DONE

---

## Summary Table: What's Working vs What's Broken

| Component | Implemented | Functional | Status |
|-----------|-------------|-----------|--------|
| **Database Schema** | ✅ Yes | ⚠️ Wrong FK | 🟡 Needs fix |
| **Repositories** | ✅ Yes | ⚠️ Wrong queries | 🟡 Needs fix |
| **Service Layer** | ✅ Yes | ✅ Yes | ✅ WORKING |
| **UI Layout (4-panel)** | ✅ Yes | ✅ Yes | ✅ WORKING |
| **SkillPanel Widgets** | ✅ Yes | ❌ No | 🔴 BROKEN |
| **SkillPanel Buff Lane** | ❌ No | ❌ No | 🔴 MISSING |
| **SkillPanel State Binding** | ❌ No | ❌ No | 🔴 MISSING |
| **PresetDialog UI** | ⚠️ Partial | ❌ No | 🔴 BROKEN |
| **PresetDialog Actions** | ❌ No | ❌ No | 🔴 MISSING |
| **AppStateController Presets** | ❌ No | ❌ No | 🔴 MISSING |
| **skill_slots Population** | ❌ No | ❌ No | 🔴 MISSING |
| **State Machine** | ❌ No | ❌ No | 🔴 MISSING |
| **Preset Callbacks/Events** | ❌ No | ❌ No | 🔴 MISSING |
| **Integration Tests** | ❌ No | ❌ No | 🔴 MISSING |

---

## Critical Path to Functional MVP

### Phase 1: Fix Database (1 hour)
1. ✅ Already fixed: Connection leak
2. ❌ TODO: Change `class_name TEXT` → `class_id INTEGER FK`
3. ❌ TODO: Add unique constraints and indexes

### Phase 2: Fix Repositories (30 min)
1. ❌ TODO: Change all queries from `class_name` → `class_id`
2. ❌ TODO: Add logging for debugging
3. ✅ Already done: Connection handling

### Phase 3: Implement AppStateController (2 hours)
1. ❌ TODO: Add skill_slots dict structure
2. ❌ TODO: Add preset state attributes (_current_class_id, _active_preset_id, _preset_mode)
3. ❌ TODO: Implement load_preset_for_class()
4. ❌ TODO: Implement apply_default_preset()
5. ❌ TODO: Add event callback system

### Phase 4: Fix SkillPanel (2 hours)
1. ❌ TODO: Add buff_lane dropdowns
2. ❌ TODO: Bind combobox to app_state.skill_slots
3. ❌ TODO: Populate combobox from loaded preset
4. ❌ TODO: Handle combo selection changes (update app_state)
5. ❌ TODO: Implement Reset button logic

### Phase 5: Implement PresetDialog (1.5 hours)
1. ❌ TODO: Render preset list UI
2. ❌ TODO: Implement [Apply] button
3. ❌ TODO: Implement [Delete] button
4. ❌ TODO: Callback to update SkillPanel

### Phase 6: Integration Tests (2 hours)
1. ❌ TODO: Write end-to-end test suite

**Total Estimated Time**: ~9 hours of focused work

---

## Recommendations

1. **Immediate** (BLOCKING MERGE): Fix database schema and repositories to use class_id FK
2. **Immediate** (BLOCKING MERGE): Implement core AppStateController methods
3. **High Priority**: Fix SkillPanel data binding and buff_lane
4. **High Priority**: Implement PresetDialog actions
5. **Medium Priority**: Add comprehensive test coverage
6. **Follow-up**: Implement combo mode and hotkey assignment (Sessions 30+)

---

## Next Steps

1. Create story cards for Phase 1-6 work items
2. Prioritize by dependency (Schema → Repos → AppState → UI → Tests)
3. Re-assign to Jules with revised scope for immediate PRs
4. Plan Sessions 30-38 (advanced features) after MVP is functional
