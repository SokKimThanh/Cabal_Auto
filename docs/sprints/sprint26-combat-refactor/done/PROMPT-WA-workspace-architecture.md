# Workspace Redesign - Architecture Alignment & Implementation Guide

**Version**: 1.0  
**Date**: 2026-09-04  
**Status**: Architecture Recommendation  
**Purpose**: Align UI Design with Logic Design for cohesive implementation

---

## 1. Executive Summary

### Problem
The current workspace layout is disorganized, with skill controls, monster information, and performance metrics scattered across tabs. The skill preset system lacks database persistence and can't distinguish between default and custom configurations.

### Solution
Implement a **4-panel balanced layout** with a **class-based skill preset system** backed by SQLite, enabling:
- Organized workspace with clear information hierarchy
- Runtime flexibility to change skill combos during combat
- Persistent, class-specific skill presets (default + custom)
- Clear UI/UX indicators for preset state (default vs. custom)

### Key Design Decisions

| Decision | Rationale | Impact |
|----------|-----------|--------|
| **4-Panel Layout** | Balances information needs with visual simplicity | Improves UX; reduces tab switching |
| **2-Column, 2-Row Grid** | Column 1 (60%) for interaction, Column 2 (40%) for monitoring | SkillPanel occupies 65% of left column; MonsterTarget 35% |
| **Database Presets** | Enables versioning and persistence | Custom presets saved automatically; users can switch presets mid-hunt |
| **Dual Modes** (Default/Custom) | Distinction between factory presets and user customizations | Clear "undo" option (Reset to Default); users always know their state |
| **Service Layer** (SkillPresetService) | Encapsulates preset logic away from UI | Reusable by multiple UI components; easier testing |
| **AppStateController as State Hub** | Single source of truth for `skill_slots` | No synchronization bugs; all components read same state |

---

## 2. Visual-Logical Integration

### 2.1 How UI Panels Map to Data Model

```
┌──────────────────────────────────┬─────────────────────────────┐
│ COLUMN 1: Interaction (60%)      │ COLUMN 2: Monitoring (40%)  │
├──────────────────────────────────┼─────────────────────────────┤
│                                  │                             │
│ ROW 1 (35%)                      │ ROW 1 (50%)                │
│ ┌────────────────────────────┐   │ ┌─────────────────────────┐ │
│ │ Monster Target Panel       │   │ │ Target & Status Panel    │ │
│ ├────────────────────────────┤   │ ├─────────────────────────┤ │
│ │ Data Source:               │   │ │ Data Source:            │ │
│ │ - BotManager.current_target    │ │ - Vision Engine         │ │
│ │ - Display: Name, Level,Type    │ │ - Display: Health, Mana │ │
│ │ Freq: Real-time update    │   │ │ - Status effects        │ │
│ └────────────────────────────┘   │ └─────────────────────────┘ │
│                                  │                             │
├──────────────────────────────────┼─────────────────────────────┤
│                                  │                             │
│ ROW 2 (65%) ◄ PRIMARY            │ ROW 2 (50%)                │
│ ┌────────────────────────────┐   │ ┌─────────────────────────┐ │
│ │ Skill Panel (ACTIVE)       │   │ │ Skill Stats Panel       │ │
│ ├────────────────────────────┤   │ ├─────────────────────────┤ │
│ │ Data Source:               │   │ │ Data Source:            │ │
│ │ - AppStateController       │   │ │ - SkillRuntimeService   │ │
│ │   .skill_slots             │   │ │ - Display: DPS, Hit %   │ │
│ │ - Active Dropdowns         │   │ │ - Log: Last 5 skills    │ │
│ │ - Action: [⚙️][📋][🔄]   │   │ │ Freq: 100ms             │ │
│ │ Preset: {current_mode}     │   │ │                         │ │
│ └────────────────────────────┘   │ └─────────────────────────┘ │
│                                  │                             │
└──────────────────────────────────┴─────────────────────────────┘
```

### 2.2 Data Flow: From User Action to Preset Application

```
USER ACTION
│
├─ Selects skill from dropdown in SkillPanel
│  │
│  └─→ SkillPanel._on_skill_changed(skill_id)
│      │
│      ├─→ AppStateController.set_skill_slot(lane, position, skill_id)
│      │   │
│      │   ├─ Update skill_slots[lane][position] = skill_id
│      │   ├─ Compare: skill_slots != active_preset → Mark as CUSTOM
│      │   └─ Emit: on_skill_slots_changed() callback
│      │
│      ├─→ SkillPanel receives callback
│      │   ├─ Update display: Show new skill name
│      │   ├─ Mark: "Custom (Unsaved) ✏️"
│      │   └─ Enable: "Save Custom" button
│      │
│      ├─→ SkillStatsPanel receives callback
│      │   ├─ Fetch new skill properties (from SkillRepository)
│      │   └─ Recalculate: DPS, cooldown impact, etc.
│      │
│      └─→ BotManager receives callback
│          └─ Update hunt loop: Use new skill sequence

ALTERNATIVE: User clicks [🔄 Reset] button
│
├─ SkillPanel._on_reset_clicked()
│  │
│  └─→ AppStateController.apply_default_preset(class_name)
│      │
│      ├─ PresetStateManager.get_active_preset(class_name)
│      │   └─ Returns: default_preset_id from user_preset_state
│      │
│      ├─ SkillPresetRepository.get_preset_skills(default_preset_id)
│      │   └─ Returns: {attack_combo: [...], buff_lane: [...]}
│      │
│      ├─ Update: skill_slots = fetched preset
│      ├─ Update: preset_mode = 'default'
│      ├─ Update: user_preset_state.preset_mode = 'default'
│      └─ Emit: on_skill_slots_changed()
│
└─→ SkillPanel updates display: "Default Preset ⭐"
```

---

## 3. Component Integration Matrix

### 3.1 SkillPanel & Dropdown Logic

**SkillPanel - The Hub**:
- Displays current `skill_slots` (from AppStateController)
- Two dropdowns: Attack Combo & Buff Lane
- Shows preset indicator: ⭐ (default) or ✏️ (custom)
- Three action buttons: [⚙️ Build], [📋 Presets], [🔄 Reset]

**Dropdown Data Flow**:
```python
# When dropdown loads
dropd_items = SkillRepository.list_skills(
    class_requirement=current_class,
    type='attack'  # for attack combo
)
dropdown.populate(dropdown_items)

# When user selects
selected_skill = dropdown.get_selected()
AppStateController.set_skill_slot(
    lane='attack_combo',
    position=0,  # first skill
    skill_id=selected_skill.id
)
```

**Integration with Skill Build Tab**:
- [⚙️ Build] button: Opens Skill Build Tab (passes current class)
- Skill Build Tab: Allows editing preset definitions
- User saves changes in Skill Build Tab
- Callback: SkillPanel reloads dropdown items
- Result: SkillPanel dropdown shows updated skill list

### 3.2 Presets Dialog & Preset Selection

**Presets Dialog - Selection Interface**:
- Lists all presets for current class
- Shows ⭐ icon for default, ✏️ icon for custom
- Current active preset highlighted
- Buttons: [Apply], [Delete] (custom only), [Cancel]

**Data Flow**:
```python
# Load presets on dialog open
presets = SkillPresetService.list_presets_by_class(current_class)
# Display in dialog

# User clicks [Apply] on preset #2
SkillPresetService.apply_preset(preset_id=2, class_name=current_class)
  ├─ Fetch preset_skills from database
  ├─ Update AppStateController.skill_slots
  ├─ Update user_preset_state (active_preset_id=2)
  └─ Emit: on_skill_slots_changed()

# SkillPanel receives callback
├─ Update dropdown selections
├─ Update preset indicator
└─ Close dialog
```

### 3.3 Skill Build Tab & Preset Definition

**Skill Build Tab - Preset Editor**:
- Left panel: Skill library (searchable)
- Middle panel: Current preset preview
- Right panel: Skill details
- Controls: Drag-to-reorder, Add/Remove skills
- Save button: "Save as Default" or "Save as Custom"

**Integration with Database**:
```python
# On load
preset_id = state_manager.get_active_preset(current_class)
preset_skills = SkillPresetRepository.get_preset_skills(preset_id)
  ├─ attack_combo: [Skill1, Skill2, Skill3]
  └─ buff_lane: [Skill4]

# Display in Skill Build Tab
render_preset_with_skills(preset_skills)

# User reorders skills (drag Skill2 → position 0)
new_order = [Skill2, Skill1, Skill3]

# User clicks Save
SkillPresetService.update_custom_preset(
    preset_id=current_preset_id,
    skill_slots={'attack_combo': [2, 1, 3], 'buff_lane': [4]}
)
  ├─ Delete existing preset_skills
  ├─ Insert new preset_skills with new positions
  ├─ Mark mode='custom'
  └─ Emit: preset_updated()

# SkillPanel receives callback
└─ Reload dropdown items (new order)
```

---

## 4. State Management Rules

### 4.1 Golden Rules for Consistency

**Rule 1: AppStateController.skill_slots is Source of Truth**
```python
# At any point in time:
app_state.skill_slots == {
    'attack_combo': [skill_1, skill_2, skill_3, ...],
    'buff_lane': [skill_4, skill_5, ...]
}

# All UI components read from this
SkillPanel.display_skills(app_state.skill_slots)
SkillStatsPanel.calc_dps(app_state.skill_slots)
BotManager.execute_hunt(app_state.skill_slots)
```

**Rule 2: Database Presets Match skill_slots**
```python
# If preset_mode == 'default':
#   skill_slots == get_preset_skills(active_preset_id)

# If preset_mode == 'custom':
#   skill_slots == user_modified_copy_of_preset
#   (and should be saved to DB)

# Invariant: Never let them drift
assert (preset_mode == 'custom' and unsaved_changes) or \
       (skill_slots == db_preset.skills)
```

**Rule 3: Preset State Persists**
```python
# user_preset_state table ALWAYS reflects current state:
{
    class_name: 'Mage',
    active_preset_id: 1,
    preset_mode: 'default'  # or 'custom'
}

# On next app launch:
state = PresetStateManager.get_active_preset('Mage')
AppStateController.load_preset_for_class('Mage', state.active_preset_id)
```

**Rule 4: Custom Presets Auto-Persist**
```python
# When user modifies skill_slots:
if skill_slots != current_preset.skills:
    preset_mode = 'custom'
    _preset_changed_flag = True
    enable_save_button()

# User can:
# a) Click Save → Creates custom preset in DB
# b) Click Reset → Reverts to default preset
# c) Close app → Prompt "Save changes?"
```

### 4.2 State Diagram: Preset Mode Transitions

```
┌────────────────────────────────────────────────────────────┐
│         Preset Mode State Machine                         │
└────────────────────────────────────────────────────────────┘

START (App Launch)
  │
  ▼
Query user_preset_state
  ├─ Get: active_preset_id, preset_mode
  └─ If not found: Use default preset
  
  ▼
┌────────────────────────────┐
│  LOAD PRESET               │
│  skill_slots = fetch(db)   │
│  preset_mode = 'default'   │
└────────────┬───────────────┘
             │
             ▼
      ┌────────────────────┐
      │ DEFAULT MODE       │
      │ (Unmodified)       │
      │ ⭐ Indicator       │
      └────┬───────────────┘
           │
    [User modifies skill]
           │
           ▼
      ┌────────────────────┐
      │ CUSTOM MODE        │
      │ (Modified)         │
      │ ✏️ Indicator       │
      └────┬───────────────┘
           │
    ┌──────┴──────┬────────────┐
    │             │            │
[Click Save]      │      [Click Reset]
    │             │            │
    ▼             │            ▼
┌──────────────┐  │      ┌──────────────┐
│CUSTOM SAVED  │  │      │DEFAULT APPLIED
│Create preset │  │      │Revert changes
│in DB         │  │      │Delete unsaved
│Update state  │  │      │Update state
└──────────────┘  │      └──────────────┘
                  │
         [Close without saving]
                  │
                  ▼
          ┌──────────────┐
          │ PROMPT DIALOG│
          │"Save changes?"
          └──────────────┘
```

---

## 5. Integration Timeline & Dependencies

### 5.1 Phase-Based Implementation

#### Phase 1: Database Foundation (Week 1)
**Goal**: Enable persistent preset storage

**Tasks**:
1. Create SQLite schema (skills, skill_presets, preset_skills, user_preset_state)
2. Implement SkillRepository class
3. Implement SkillPresetRepository class
4. Seed initial skills and default presets
5. Create migration from legacy JSON

**Dependencies**: None (foundation)

**Deliverable**: 
- `/lib/db/repositories/skill_repository.py`
- `/lib/db/repositories/skill_preset_repository.py`
- `schema.sql` with all tables

---

#### Phase 2: Service & State Layer (Week 2)
**Goal**: Implement business logic for preset management

**Tasks**:
1. Implement SkillPresetService
2. Add callback/event system to AppStateController
3. Implement state machine logic (default/custom modes)
4. Add error handling and recovery

**Dependencies**: Phase 1 (Database)

**Deliverable**:
- `/lib/features/skills/skill_preset_service.py`
- Updated `AppStateController` with preset state

---

#### Phase 3: UI Layout Redesign (Week 3)
**Goal**: Implement 4-panel balanced layout

**Tasks**:
1. Refactor HuntTab frame structure (PanedWindow with weights)
2. Implement MonsterTargetPanel class
3. Implement SkillPanel class (without dropdown yet)
4. Implement TargetStatusPanel class
5. Implement SkillStatsPanel class

**Dependencies**: Phase 1 (Database provides skill data), Phase 2 (AppStateController state)

**Deliverable**:
- `/ui/panels/` directory with 4 panel classes
- Updated `hunt_tab.py` with new layout

---

#### Phase 4: Skill Selection & Dropdowns (Week 4)
**Goal**: Wire dropdowns to preset system

**Tasks**:
1. Add skill dropdown to SkillPanel
2. Implement dropdown callback (on_skill_selected)
3. Integrate with AppStateController (set_skill_slot)
4. Add preset mode indicator (⭐ / ✏️)
5. Add action buttons: [⚙️ Build], [📋 Presets], [🔄 Reset]

**Dependencies**: Phase 2, 3

**Deliverable**:
- Functional SkillPanel with dropdowns
- Preset indicator display
- Action buttons wired to callbacks

---

#### Phase 5: Preset Dialog & Selection (Week 5)
**Goal**: Allow users to switch and manage presets

**Tasks**:
1. Create PresetDialog component
2. Implement preset list display
3. Wire [Apply] button to SkillPresetService.apply_preset()
4. Wire [Delete] button (custom presets only)
5. Show current active preset

**Dependencies**: Phase 2, 4

**Deliverable**:
- PresetDialog component
- Full preset switching workflow

---

#### Phase 6: Skill Build Tab Redesign (Week 6)
**Goal**: Integrate skill preset editing with Skill Build Tab

**Tasks**:
1. Refactor Skill Build Tab layout
2. Add skill library picker
3. Implement drag-to-reorder
4. Wire Save button to SkillPresetService
5. Sync with SkillPanel dropdown

**Dependencies**: Phase 2, 4, 5

**Deliverable**:
- Redesigned Skill Build Tab
- Presets can be edited and saved

---

#### Phase 7: Integration Testing (Week 7)
**Goal**: Verify all components work together

**Tasks**:
1. Test preset loading on app startup
2. Test skill dropdown changes
3. Test default/custom mode switching
4. Test save/load custom presets
5. Test Reset button functionality
6. Test Skill Build Tab changes sync to SkillPanel
7. Performance testing (load time for large preset lists)

**Dependencies**: All phases

**Deliverable**:
- Test suite with 20+ integration tests
- Performance benchmarks

---

#### Phase 8: Polish & Documentation (Week 8)
**Goal**: Finalize UI/UX and documentation

**Tasks**:
1. Visual design refinement (colors, fonts, icons)
2. DPI scaling testing across 0.8x - 1.2x
3. User documentation
4. Migration guide for existing users
5. Keyboard shortcuts & accessibility

**Dependencies**: All phases

**Deliverable**:
- Polish UI design
- User guide
- Troubleshooting documentation

---

### 5.2 Dependency Graph

```
┌──────────────────────┐
│ Phase 1: Database    │ ◄── Foundation (no dependencies)
│ (Week 1)             │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Phase 2: Service     │ ◄── Depends on Phase 1
│ (Week 2)             │
└──────────┬───────────┘
           │
      ┌────┴────┐
      │          │
      ▼          ▼
 Phase 3    Phase 3.5
 (Layout)   (Skill Mgmt
 Week 3      Updates)
      │          │
      └────┬─────┘
           │
           ▼
┌──────────────────────┐
│ Phase 4: Dropdowns   │ ◄── Depends on Phase 2, 3
│ (Week 4)             │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Phase 5: Presets     │ ◄── Depends on Phase 2, 4
│ (Week 5)             │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Phase 6: Skill Build │ ◄── Depends on Phase 2, 4, 5
│ (Week 6)             │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Phase 7: Integration │ ◄── Depends on all
│ (Week 7)             │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Phase 8: Polish      │ ◄── Depends on Phase 7
│ (Week 8)             │
└──────────────────────┘
```

---

## 6. How New System Integrates with Existing UX4.2

### 6.1 No Breaking Changes

The workspace redesign **wraps and extends** the existing UX4.2 implementation without modifying core logic:

```
EXISTING (UX4.2)
├─ Skill routing (single-hop) → UNCHANGED
├─ Toast notifications → UNCHANGED
├─ Dropdown revert logic → UNCHANGED
├─ Key conflict validation → UNCHANGED
└─ JSON migration → Extended to DB migration

NEW (Workspace Redesign)
├─ 4-Panel Layout → New UI organization
├─ Class Presets → New database layer
├─ Preset State Management → New service layer
└─ Enhanced Dropdowns → Uses existing dropdown, adds preset support

Integration Point: AppStateController.skill_slots
- Existing code reads/writes skill_slots
- New preset system populates skill_slots
- Both work together: skill_slots is the contract
```

### 6.2 Example: Skill Routing Still Works

```python
# Existing UX4.2 code in hunt_tab.py:
def _on_cmb_selected(self, event):
    """Handle combo selection (UX4.2 - existing)"""
    new_combo = self.cmb.get()
    old_combo = self._cached_combo
    
    if new_combo != old_combo:
        # Single-hop routing logic (unchanged)
        if self._should_revert():
            self.cmb.set(old_combo)
        else:
            AppStateController.set_skill_slot(...)

# New workspace redesign - extends this:
class SkillPanel:
    """New panel-based UI"""
    
    def on_skill_dropdown_changed(self, event):
        """Same callback, new UI container"""
        # Calls same AppStateController methods
        AppStateController.set_skill_slot(...)
        
    # Plus: Added preset mode indicator
    def display_preset_mode(self):
        if app_state._preset_mode == 'default':
            self.mode_label.config(text="⭐ Default")
        else:
            self.mode_label.config(text="✏️ Custom")
```

---

## 7. Class Diagram: Key Components

```
┌─────────────────────────────────────────────────────────────┐
│                     AppStateController                       │
├─────────────────────────────────────────────────────────────┤
│ - skill_slots: dict                                         │
│ - _current_class: str                                       │
│ - _active_preset_id: int                                    │
│ - _preset_mode: str ('default' or 'custom')                │
│ - _preset_changed_flag: bool                                │
├─────────────────────────────────────────────────────────────┤
│ + load_preset_for_class(class_name)                         │
│ + apply_default_preset(class_name)                          │
│ + set_custom_mode()                                         │
│ + set_skill_slot(lane, position, skill_id)                 │
│ + get_available_presets(class_name): List[Preset]          │
│ + register_callback(event, handler)                         │
└──────────┬────────────────────────────────────────────────┬─┘
           │                                                  │
           │ uses                                             │ uses
           │                                                  │
           ▼                                                  ▼
┌──────────────────────────────────┐      ┌─────────────────────────┐
│  SkillPresetService              │      │ SkillRepository         │
├──────────────────────────────────┤      ├─────────────────────────┤
│ - preset_repo                    │      │ + get_skill(id)         │
│ - skill_repo                     │      │ + list_skills(filters)  │
│ - state_manager                  │      │ + search_skills(query)  │
├──────────────────────────────────┤      ├─────────────────────────┤
│ + apply_preset(id, class)        │      │ Returns: SkillInfo      │
│ + create_custom_preset(...)      │      └─────────────────────────┘
│ + update_custom_preset(...)      │
│ + delete_custom_preset(...)      │      ┌──────────────────────────────┐
│ + list_presets_by_class(class)   │      │ SkillPresetRepository        │
└──────────┬───────────────────────┘      ├──────────────────────────────┤
           │                              │ + create_preset(...)         │
           │ uses                         │ + get_preset_skills(id)      │
           │                              │ + set_preset_skills(id, ...) │
           ▼                              │ + delete_preset(id)          │
┌──────────────────────────────────┐      └──────────────────────────────┘
│ PresetStateManager               │
├──────────────────────────────────┤      ┌──────────────────────────────┐
│ + get_active_preset(class)       │      │ Database (SQLite)            │
│ + set_active_preset(class, id)   │      ├──────────────────────────────┤
│ + get_preset_mode(class)         │      │ skills table                 │
│ + reset_to_default(class)        │      │ skill_presets table          │
└──────────────────────────────────┘      │ preset_skills table          │
                                          │ user_preset_state table      │
                                          └──────────────────────────────┘
```

---

## 8. Error Scenarios & Recovery

### 8.1 Scenario: Missing Skill in Preset

```
Flow:
1. Load preset from DB
2. Find skill with skill_id=99 (doesn't exist in skills table)

Error Handling:
├─ Log warning: "Skill 99 missing from library"
├─ Check: Is skill_id=99 in current skill_slots?
│  ├─ Yes: Mark as "ORPHANED SKILL" in UI
│  ├─ Show warning: "Preset contains deleted skill"
│  └─ Option: "Remove from combo" or "Revert to default"
│
└─ No: Skip in UI (don't crash)
   └─ Fallback: Load default preset
   
Recovery Options:
a) User clicks "Remove" → Splice out missing skill
b) User clicks "Revert" → Apply default preset
c) Auto-recover: On app startup, detect and fix
```

### 8.2 Scenario: Corrupted Preset in Database

```
Flow:
1. Query: SELECT * FROM preset_skills WHERE preset_id=1
2. Result is malformed or incomplete

Error Handling:
├─ Validate: Check for missing positions (gap in sequence)
├─ Check: Duplicate positions (constraint violation)
├─ Verify: All skill_ids exist in skills table
│
└─ If validation fails:
   ├─ Log error with preset_id
   ├─ Apply default preset instead
   └─ Prompt user: "Your custom preset was corrupted. Reverted to default."
   
Recovery:
1. User can re-create the custom preset
2. Admin can restore from backup
```

### 8.3 Scenario: User Has Legacy JSON Config

```
Flow:
1. App startup
2. Check: Does hunt_cfg.json exist?

If Yes:
├─ Call: SkillPresetService.migrate_legacy_presets(legacy_cfg)
│
├─ For each class in legacy config:
│  ├─ Create default preset for class
│  ├─ Add skills from legacy array
│  ├─ Insert into database
│  └─ Update user_preset_state
│
├─ Backup: Rename hunt_cfg.json → hunt_cfg.json.backup
├─ Log: "Migrated X presets from legacy config"
└─ Continue: App loads normally

User Experience:
- App starts
- User's old skill order is preserved as default preset
- No manual reconfiguration needed
```

---

## 9. Testing Strategy

### 9.1 Unit Tests (Database & Service Layer)

```python
# test_skill_repository.py
def test_get_skill_by_id():
    repo = SkillRepository()
    skill = repo.get_skill(1)
    assert skill.name == 'Fireball'
    assert skill.type == 'attack'

# test_skill_preset_repository.py
def test_get_preset_skills():
    repo = SkillPresetRepository()
    skills = repo.get_preset_skills(1)
    assert skills['attack_combo'] == [Skill1, Skill2, Skill3]
    assert skills['buff_lane'] == [Skill4]

# test_skill_preset_service.py
def test_apply_preset():
    service = SkillPresetService(...)
    result = service.apply_preset(preset_id=1, class_name='Mage')
    assert result['success'] == True
    assert app_state.skill_slots == expected_slots

# test_state_transitions.py
def test_default_to_custom_transition():
    app_state.load_preset(preset_id=1)
    assert app_state._preset_mode == 'default'
    
    app_state.set_skill_slot('attack_combo', 0, skill_id=99)
    assert app_state._preset_mode == 'custom'
    assert app_state._preset_changed_flag == True
```

### 9.2 Integration Tests (UI-Logic)

```python
# test_skill_panel_integration.py
def test_skill_dropdown_updates_state():
    panel = SkillPanel(app_state, skill_service)
    
    # Simulate user selecting skill
    panel.attack_dropdown.set(skill_id=2)
    panel._on_skill_changed(mock_event)
    
    # Verify state updated
    assert app_state.skill_slots['attack_combo'][0] == 2
    assert app_state._preset_mode == 'custom'
    
    # Verify UI updated
    assert panel.mode_label.cget('text') == '✏️ Custom'

# test_preset_dialog_integration.py
def test_apply_preset_from_dialog():
    dialog = PresetDialog(app_state, preset_service)
    dialog.presets_listbox.select(1)  # Select custom preset
    dialog._on_apply_clicked()
    
    # Verify preset applied
    assert app_state._active_preset_id == 2
    assert app_state._preset_mode == 'default'

# test_reset_button.py
def test_reset_to_default():
    # Start in custom mode
    app_state.set_skill_slot('attack_combo', 0, skill_id=99)
    assert app_state._preset_mode == 'custom'
    
    # Click Reset
    panel._on_reset_clicked()
    
    # Verify reset
    assert app_state._preset_mode == 'default'
    assert app_state.skill_slots == default_preset_skills
```

### 9.3 UI Tests (Visual & Interaction)

```python
# test_ui_layout.py
def test_4_panel_layout():
    hunt_tab = HuntTab(app_gui)
    
    # Verify column 1 (60%) and column 2 (40%)
    col1_width = hunt_tab.col1.winfo_width()
    col2_width = hunt_tab.col2.winfo_width()
    total = col1_width + col2_width
    assert col1_width / total == pytest.approx(0.6, 0.05)
    
    # Verify row heights in column 1
    row1_height = hunt_tab.col1_row1.winfo_height()
    row2_height = hunt_tab.col1_row2.winfo_height()
    total_h = row1_height + row2_height
    assert row1_height / total_h == pytest.approx(0.35, 0.05)
    assert row2_height / total_h == pytest.approx(0.65, 0.05)

# test_dpi_scaling.py
@pytest.mark.parametrize('scale_factor', [0.8, 1.0, 1.2])
def test_dpi_scaling(scale_factor):
    panel = SkillPanel(app_state, skill_service, scale_factor)
    
    # Verify fonts scaled
    font_size = panel.title_font[1]
    assert font_size == int(11 * scale_factor)
    
    # Verify padding scaled
    expected_pad = int(10 * scale_factor)
    assert panel.winfo_padx() == expected_pad
```

---

## 10. User Journey Examples

### 10.1 New User: First Hunt

```
1. App launches
   └─ Auto-loads default preset for selected class (⭐ Default)

2. Hunt tab opens with 4-panel layout
   ├─ Left column shows: Monster Target + Skill Panel
   ├─ Right column shows: Status + Stats
   └─ User sees current skill combo in Skill Panel

3. User starts hunt
   ├─ Monster Target Panel updates with current target
   ├─ Skill Panel shows next skill countdown
   ├─ Status Panel shows target HP/mana
   └─ Stats Panel shows DPS and skill log

4. User wants to switch skills mid-hunt
   ├─ Clicks dropdown in Skill Panel
   ├─ Selects different skill
   └─ UI shows "Custom (Unsaved) ✏️"

5. User stops hunt
   ├─ Can click [📋 Presets] to load different preset
   ├─ Or click [🔄 Reset] to revert to default
   ├─ Or click [💾 Save Custom] to save changes
   └─ Settings persist for next hunt
```

### 10.2 Power User: Custom Preset Workflow

```
1. User opens Hunt tab
   └─ Loads last-used custom preset (✏️ Custom)

2. Wants to test new skill order
   ├─ Clicks [⚙️ Build] → Opens Skill Build Tab
   ├─ Reorders skills by dragging
   ├─ Clicks "Save as Custom" → Enters name "Boss v3"
   └─ Switches back to Hunt tab

3. Hunt tab now shows new skill order
   └─ [📋 Presets] dialog shows "Boss v3" as active

4. After hunt, user compares presets
   ├─ Clicks [📋 Presets]
   ├─ Compares "Boss v2" vs "Boss v3" (see stats)
   ├─ Chooses to activate "Boss v3"
   └─ Deletes "Boss v2" (no longer needed)

5. Next app launch
   └─ Automatically loads "Boss v3" (saved as active)
```

### 10.3 Error Recovery: Corrupted Preset

```
1. User opens Hunt tab

2. System detects preset issue
   ├─ Queries: SELECT * FROM preset_skills WHERE preset_id=5
   ├─ Validation fails: Missing skill in library
   ├─ Automatic fallback: Load default preset
   └─ Show notification: "Custom preset was corrupted. Using default."

3. User can manually fix
   ├─ Clicks [⚙️ Build] → Skill Build Tab
   ├─ Manually re-creates custom preset
   ├─ Clicks Save
   └─ Preset restored

OR

4. User reverts completely
   └─ Clicks [🔄 Reset] → Back to default
```

---

## 11. Implementation Checklist

### Architecture Foundation
- [ ] Review both design documents (UI + Logic)
- [ ] Create implementation task tickets
- [ ] Establish coding standards for new classes
- [ ] Set up code review process

### Database & Service Layer
- [ ] Design and validate SQL schema
- [ ] Create migration scripts (legacy JSON → DB)
- [ ] Implement SkillRepository
- [ ] Implement SkillPresetRepository
- [ ] Implement PresetStateManager
- [ ] Implement SkillPresetService
- [ ] Add comprehensive error handling

### Controller & State Management
- [ ] Update AppStateController with preset methods
- [ ] Implement callback/event system
- [ ] Add state validation and consistency checks
- [ ] Test state transitions

### UI Layout Redesign
- [ ] Refactor HuntTab frame structure (PanedWindow)
- [ ] Create 4 panel classes (MonsterTargetPanel, SkillPanel, etc.)
- [ ] Implement responsive layout with proper weights
- [ ] Add DPI scaling support

### Skill Panel & Dropdowns
- [ ] Implement skill selection dropdowns
- [ ] Add preset mode indicator (⭐ / ✏️)
- [ ] Implement action buttons: [⚙️], [📋], [🔄]
- [ ] Wire callbacks to AppStateController

### Presets Dialog & Management
- [ ] Create PresetDialog component
- [ ] List all presets (default + custom)
- [ ] Implement [Apply], [Delete], [Cancel] buttons
- [ ] Wire to SkillPresetService

### Skill Build Tab Integration
- [ ] Redesign Skill Build Tab
- [ ] Integrate with SkillPresetService
- [ ] Add skill library picker
- [ ] Implement save as custom preset

### Testing
- [ ] Write unit tests (repository layer)
- [ ] Write integration tests (service layer)
- [ ] Write UI tests (panel layer)
- [ ] Performance testing
- [ ] User acceptance testing

### Documentation & Polish
- [ ] User guide
- [ ] Troubleshooting guide
- [ ] Migration guide (legacy users)
- [ ] API documentation for service layer
- [ ] Code comments and docstrings

---

## 12. Quick Reference: Where Everything Lives

| Component | Location | Responsibility |
|-----------|----------|-----------------|
| Database Schema | `/lib/db/schema.sql` | Define tables & relationships |
| SkillRepository | `/lib/db/repositories/skill_repository.py` | Skill CRUD |
| SkillPresetRepository | `/lib/db/repositories/skill_preset_repository.py` | Preset CRUD |
| PresetStateManager | `/lib/db/repositories/preset_state_manager.py` | State tracking |
| SkillPresetService | `/lib/features/skills/skill_preset_service.py` | Business logic |
| AppStateController | `app_gui.py` or extracted to `/lib/controllers/app_state_controller.py` | State management |
| MonsterTargetPanel | `/ui/panels/monster_target_panel.py` | Monster display |
| SkillPanel | `/ui/panels/skill_panel.py` | Skill selection + actions |
| TargetStatusPanel | `/ui/panels/target_status_panel.py` | Target health/status |
| SkillStatsPanel | `/ui/panels/skill_stats_panel.py` | Performance metrics |
| PresetDialog | `/ui/dialogs/preset_dialog.py` | Preset selection |
| HuntTab | `/ui/tabs/hunt_tab.py` | Main layout container |

---

## 13. Success Criteria

### User Experience
- [ ] Hunt workspace is visually organized and intuitive
- [ ] Skill selection is quick and doesn't require tab switching
- [ ] Preset changes apply immediately
- [ ] Users understand preset state (default vs. custom)
- [ ] Users can quickly reset to default or switch presets

### Technical Excellence
- [ ] All 4 panels load within 100ms
- [ ] Database queries take < 10ms
- [ ] No memory leaks or connection leaks
- [ ] State consistency maintained (invariants never violated)
- [ ] Error handling covers all edge cases

### Integration
- [ ] 100% backward compatible with existing UX4.2
- [ ] No performance regression
- [ ] All existing tests pass
- [ ] New tests cover 80%+ of code
- [ ] Legacy JSON users auto-migrate seamlessly

---

## Conclusion

This architecture provides a **cohesive solution** that:
1. **Organizes** the hunt workspace into 4 balanced panels
2. **Persists** skill presets in a database with class-based organization
3. **Distinguishes** between factory defaults and user customizations
4. **Enables** runtime flexibility for mid-hunt skill changes
5. **Maintains** backward compatibility with existing features
6. **Scales** from new users (with defaults) to power users (with custom presets)

The separation of concerns (UI ↔ Service ↔ Repository ↔ Database) makes the system maintainable, testable, and extensible for future enhancements.

