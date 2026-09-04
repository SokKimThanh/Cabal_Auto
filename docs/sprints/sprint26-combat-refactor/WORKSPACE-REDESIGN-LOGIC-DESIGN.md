# Hunt Workspace Redesign - Logic Design Document

**Version**: 1.0  
**Date**: 2026-09-04  
**Status**: Logic Specification  
**Target**: Class-Based Skill Presets, State Management, Data Flow

---

## 1. Overview & Architecture Vision

### 1.1 Core Problem Statement

**Current State**:
- Skill combos are stored as JSON arrays (hunt_cfg.json)
- No database persistence for class-specific presets
- No distinction between default presets and user customizations
- Skill data scattered across JSON files

**Design Goals**:
1. **Database-Driven Presets**: Store class-based skill combos in SQLite
2. **Preset Versioning**: Track default vs. custom presets per class
3. **State Clarity**: Clear indication of which preset is active (default/custom)
4. **Skill Library CRUD**: Full database operations for skill data
5. **Runtime Flexibility**: Allow combat-time customization without losing state

### 1.2 System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Hunt Workspace                         │
│  (UI Layer - WORKSPACE-REDESIGN-UI-DESIGN.md)          │
└────────────┬────────────────────────────────────────────┘
             │
             ▼ (Data Binding)
┌─────────────────────────────────────────────────────────┐
│         AppStateController                              │
│  - skill_slots management                               │
│  - preset state tracking                                │
│  - preset switching logic                               │
└────────────┬────────────────────────────────────────────┘
             │
             ▼ (Service Layer)
┌─────────────────────────────────────────────────────────┐
│       SkillPresetService                                │
│  - Load presets from DB                                 │
│  - Save custom presets                                  │
│  - Apply/reset presets                                  │
│  - Migrate legacy JSON to DB                            │
└────────────┬────────────────────────────────────────────┘
             │
             ▼ (Repository Layer)
┌─────────────────────────────────────────────────────────┐
│      SkillRepository                                    │
│  - Skill CRUD operations                                │
│  - Skill library queries                                │
│  - Performance metadata                                 │
│                                                         │
│      SkillPresetRepository                              │
│  - Preset CRUD operations                               │
│  - Class-based preset queries                           │
│  - Default vs custom distinction                        │
└────────────┬────────────────────────────────────────────┘
             │
             ▼ (Data Layer)
┌─────────────────────────────────────────────────────────┐
│            SQLite Database                              │
│  - skills table (skill library)                         │
│  - skill_presets table (class presets)                  │
│  - preset_skills table (skill order in preset)          │
│  - user_custom_presets table (customizations)           │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Database Schema

### 2.1 Existing Tables (from lib/db/schema.py)

#### Table: `classes` (Nhân vật)
```sql
CREATE TABLE classes (
    class_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- e.g., 'Mage', 'Warrior', 'Rogue'
    description TEXT,
    icon_path TEXT,
    str_base INTEGER DEFAULT 0,           -- Base STR attribute
    int_base INTEGER DEFAULT 0,           -- Base INT attribute
    dex_base INTEGER DEFAULT 0            -- Base DEX attribute
);
```

#### Table: `skills` (Kỹ năng)
```sql
CREATE TABLE skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    alias TEXT,
    icon_x INTEGER DEFAULT 0,             -- Icon position X
    icon_y INTEGER DEFAULT 0,             -- Icon position Y
    icon_w INTEGER DEFAULT 0,             -- Icon width
    icon_h INTEGER DEFAULT 0,             -- Icon height
    type TEXT,                            -- 'attack', 'buff', 'utility'
    class_id INTEGER,                     -- Which class owns this skill
    FOREIGN KEY(class_id) REFERENCES classes(class_id) ON DELETE RESTRICT
);
```

#### Table: `class_skill_assignments` ⭐ **Class-Skill Relationship**
```sql
CREATE TABLE class_skill_assignments (
    class_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    category TEXT NOT NULL,               -- e.g., 'primary', 'secondary', 'support'
    source_ref TEXT NOT NULL,             -- Reference to manifest/source
    is_recommended INTEGER DEFAULT 0,     -- 0=optional, 1=recommended
    PRIMARY KEY(class_id, skill_id),
    FOREIGN KEY(class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    FOREIGN KEY(skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);
```
**Purpose**: Defines which skills are valid for each class (many-to-many)

#### Table: `synergies` (Combo skill effects)
```sql
CREATE TABLE synergies (
    synergy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    name TEXT NOT NULL,                   -- e.g., 'Elemental Burst'
    activation_sequence TEXT,             -- e.g., 'Fireball→Blizzard→Lightning'
    recommendation TEXT,n    FOREIGN KEY(class_id) REFERENCES classes(class_id) ON DELETE RESTRICT
);
```

---

### 2.2 New Tables (for Workspace Redesign - Presets)

#### Table: `skill_presets` (Default & Custom Presets)
```sql
CREATE TABLE skill_presets (
    preset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,            -- Link to class, not class_name TEXT
    name TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,     -- TRUE = built-in, FALSE = user custom
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(class_id, name, is_default),
    FOREIGN KEY(class_id) REFERENCES classes(class_id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_presets_class ON skill_presets(class_id);
CREATE INDEX idx_presets_default ON skill_presets(is_default);
```

**Example Data**:
```
| preset_id | class_id | name            | is_default | description                  |
|-----------|----------|-----------------|------------|------------------------------|
| 1         | 1        | Default - Mage  | TRUE       | Built-in default combo       |
| 2         | 1        | Custom - Mage1  | FALSE      | My personal variant          |
| 3         | 1        | Custom - Mage2  | FALSE      | Boss farming variant         |
| 4         | 2        | Default-Warrior | TRUE       | Built-in default combo       |
```

#### Table: `preset_skills` (Skill Order in Preset)
```sql
CREATE TABLE preset_skills (
    preset_skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    preset_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    lane_type TEXT NOT NULL,              -- 'attack_combo' or 'buff_lane'
    position INTEGER NOT NULL,                      -- 0, 1, 2, ... (position in lane)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(preset_id) REFERENCES skill_presets(preset_id) ON DELETE CASCADE,
    FOREIGN KEY(skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
    UNIQUE(preset_id, lane_type, position)
);

-- Indexes
CREATE INDEX idx_preset_skills_preset ON preset_skills(preset_id);
CREATE INDEX idx_preset_skills_skill ON preset_skills(skill_id);
```

**Example Data**:
```
| preset_skill_id | preset_id | skill_id | lane_type     | position |
|-----------------|-----------|----------|---------------|----------|
| 1               | 1         | 1        | attack_combo  | 0        |
| 2               | 1         | 2        | attack_combo  | 1        |
| 3               | 1         | 3        | attack_combo  | 2        |
| 4               | 1         | 4        | buff_lane     | 0        |
| 5               | 2         | 2        | attack_combo  | 0        | (custom)
| 6               | 2         | 1        | attack_combo  | 1        | (custom)
```

#### Table: `user_preset_state` (Current Active Preset Tracking)
```sql
CREATE TABLE user_preset_state (
    state_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL UNIQUE,       -- Link to class (FK, not class_name TEXT)
    active_preset_id INTEGER,               -- Currently active preset for this class
    preset_mode TEXT DEFAULT 'default',     -- 'default' or 'custom'
    last_applied TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    FOREIGN KEY(active_preset_id) REFERENCES skill_presets(preset_id) ON DELETE SET NULL
);

-- Example
-- | state_id | class_id | active_preset_id | preset_mode |
-- |----------|----------|------------------|-------------|
-- | 1        | 1        | 1                | default     | (Mage)
-- | 2        | 2        | 4                | default     | (Warrior)
```

### 2.3 Integrated Relationships Diagram

```
┌──────────────────────┐
│    classes           │  (Nhân vật)
├──────────────────────┤
│ class_id (PK)        │
│ name (Mage, Warrior) │
│ description          │
└────┬──────────────┬──┘
     │              │
     │              │ 1:N (Has many)
     │              ▼
     │    ┌──────────────────────┐
     │    │  skills              │  (Kỹ năng)
     │    ├──────────────────────┤
     │    │ skill_id (PK)        │
     │    │ name, type           │
     │    │ icon_*, class_id (FK)│
     │    └──────┬───────────────┘
     │           │
     │           │ M:N relationship
     │           ▼
     │ ┌──────────────────────────────────┐
     │ │ class_skill_assignments          │ (Xác định skill hợp lệ per class)
     │ ├──────────────────────────────────┤
     │ │ (class_id, skill_id) PK          │
     │ │ category, source_ref             │
     │ │ is_recommended                   │
     │ └──────────────────────────────────┘
     │
     │ 1:N (Has many presets)
     ▼
┌──────────────────────┐
│  skill_presets       │  (Preset definitions per class)
├──────────────────────┤
│ preset_id (PK)       │
│ class_id (FK) ◄──────┼── Reference to classes table
│ name                 │
│ is_default (BOOL)    │
└────────┬─────────────┘
         │ 1:N (Has many preset_skills)
         ▼
┌──────────────────────────────┐
│  preset_skills               │  (Skill order in preset)
├──────────────────────────────┤
│ preset_skill_id (PK)         │
│ preset_id (FK)    ───────────┼── Reference to skill_presets
│ skill_id (FK)     ───────────┼── Reference to skills (must exist)
│ lane_type, position          │
└──────────────────────────────┘

Additional: State Tracking
┌──────────────────────┐
│ user_preset_state    │  (Current active preset per class)
├──────────────────────┤
│ state_id (PK)        │
│ class_id (FK) ◄──────┼── Reference to classes
│ active_preset_id (FK)┼── Reference to skill_presets
│ preset_mode          │   ('default' or 'custom')
└──────────────────────┘
```

---

## 3. State Management Model

### 3.1 Preset State Machine

```
┌─────────────────────────────────────────────────────────────┐
│              Preset State Machine                           │
└─────────────────────────────────────────────────────────────┘

START
  │
  ▼
┌──────────────────────────────────────┐
│  Load Default Preset (on app start)  │
│  - Query default preset for class    │
│  - Load skill order from preset_skills
│  - Populate skill_slots array        │
│  - Mark as preset_mode='default'     │
└──────────────────┬───────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  PRESET MODE: DEFAULT
         │  (Read-Only Display)│
         └──┬──────────────┬───┘
            │              │
    [User Customizes]      │
    or [Manual Combo      │
     Selection]           │
            │              │
            ▼              ▼
      ┌──────────────────────────────────┐
      │ PRESET MODE: CUSTOM              │
      │ (Allow UI Edits)                 │
      │ - skill_slots array modified     │
      │ - Display "Custom" indicator     │
      │ - Enable Save to DB              │
      └───┬──────────────────────────┬───┘
          │                          │
[Save Custom to DB] or [Apply Default]
          │                          │
          ▼                          ▼
   ┌──────────────────┐    ┌──────────────────┐
   │ CUSTOM SAVED     │    │ DEFAULT APPLIED  │
   │ Mode: 'custom'   │    │ Mode: 'default'  │
   │ Persist in DB    │    │ Reset to default │
   └──────────────────┘    └──────────────────┘
          │                          │
          └──────────┬───────────────┘
                     │
                     ▼
              ┌────────────────┐
              │  Ready for Hunt│
              └────────────────┘
```

### 3.2 AppStateController - Preset & Combo Mode Management

```python
class AppStateController:
    """
    Centralized state management for app-wide data including presets and combo mode.
    """
    
    # Preset state tracking - uses class_id FK instead of class_name
    _current_class_id: int = 1  # FK to classes table
    _active_preset_id: int = None
    _preset_mode: str = "default"  # 'default' or 'custom'
    
    # Skill state
    skill_slots: dict = {
        "attack_combo": [],
        "buff_lane": []
    }
    
    # COMBO MODE STATE (NEW)
    # ════════════════════════════════════════════════════════════
    # Controls whether skills are executed manually (user presses hotkey)
    # or automatically (machine presses hotkey sequence)
    
    _combo_mode_active: bool = False  # 🔴 INACTIVE vs 🟢 ACTIVE
    
    _combo_sequence_index: int = 0  # Current skill index in auto-sequence
    # (If in attack_combo: 0,1,2,...; if in buff_lane: 0,1,...)
    
    _combo_current_lane: str = "attack_combo"  # Which lane being executed
    
    # ════════════════════════════════════════════════════════════
    
    def load_preset_for_class(self, class_id: int):
        """
        Load the active preset for a specific class.
        - Queries user_preset_state to find active preset
        - Loads preset_skills in order (via skill_id)
        - Validates skills exist via class_skill_assignments
        - Populates skill_slots
        - Notifies UI of changes
        - RESETS combo mode to inactive
        
        Args:
            class_id: Integer FK to classes table
        """
        pass
    
    def apply_default_preset(self, class_id: int):
        """
        Reset to default preset for class.
        - Query for is_default=TRUE preset for class_id
        - Load skill_slots from preset_skills
        - Update user_preset_state (preset_mode='default')
        - Notify UI
        - RESETS combo mode to inactive
        
        Args:
            class_id: Integer FK to classes table
        """
        pass
    
    def set_custom_mode(self):
        """
        Switch to custom preset mode.
        - Update user_preset_state (preset_mode='custom')
        - Mark current skill_slots as modified
        - Enable Save button in UI
        """
        pass
    
    def save_custom_preset(self, preset_name: str):
        """
        Save current skill_slots as custom preset.
        - Create/update custom preset in skill_presets table
        - Populate preset_skills with current skill order
        - Update user_preset_state (active_preset_id, preset_mode='custom')
        - Notify UI of save completion
        """
        pass
    
    def get_available_presets(self, class_id: int) -> List[Preset]:
        """
        Get all presets (default + custom) for a class.
        
        Args:
            class_id: Integer FK to classes table
        
        Returns: [
            Preset(id=1, name='Default - Mage', is_default=True, ...),
            Preset(id=2, name='Custom - Mage1', is_default=False, ...),
            Preset(id=3, name='Custom - Mage2', is_default=False, ...),
        ]
        """
        pass
    
    # ════════════════════════════════════════════════════════════
    # COMBO MODE METHODS (NEW - Skill Execution Modes)
    # ════════════════════════════════════════════════════════════
    
    def activate_combo_mode(self):
        """
        Activate combo mode (🟢 ACTIVE).
        - Set _combo_mode_active = True
        - Reset sequence index to 0
        - Start with attack_combo lane
        - Lock skill selections (UI disables dropdowns)
        - Enable hotkey automation (BotManager starts pressing hotkeys)
        - Emit: on_combo_mode_activated()
        
        Called by: User clicks [▶️ START COMBO MODE] button
        """
        pass
    
    def deactivate_combo_mode(self):
        """
        Deactivate combo mode (🔴 INACTIVE).
        - Set _combo_mode_active = False
        - Stop hotkey automation (BotManager stops pressing hotkeys)
        - Unlock skill selections (UI enables dropdowns)
        - Emit: on_combo_mode_deactivated()
        
        Called by: User clicks [⏹️ STOP COMBO MODE] button
        """
        pass
    
    def get_combo_mode_status(self) -> str:
        """
        Get current combo mode status for display.
        
        Returns:
        - "🔴 COMBO MODE: INACTIVE" (NOT combo mode, user manual control)
        - "🟢 COMBO MODE: ACTIVE" (Auto-executing skill sequence)
        """
        return "🟢 COMBO MODE: ACTIVE" if self._combo_mode_active else "🔴 COMBO MODE: INACTIVE"
    
    def set_skill_hotkey(self, lane: str, position: int, hotkey: str):
        """
        Assign or update hotkey for a skill slot.
        - lane: "attack_combo" or "buff_lane"
        - position: 0-based index within lane
        - hotkey: "1", "2", "3", "q", "w", "e", "a", "s", "d", "None"
        
        Updates: skill_slots[lane][position].user_hotkey
        Emits: on_hotkey_changed()
        """
        pass
    
    def update_skill_cooldown(self, lane: str, position: int, remaining: float):
        """
        Update cooldown timer for a skill (called during hunt).
        
        Updates: skill_slots[lane][position].cooldown_remaining, is_ready
        Emits: on_cooldown_updated()
        
        Called by: BotManager/HuntRunner during skill execution
        """
        pass
```

---

## 3.2a Skill Slots Architecture - Build Tab ↔ Hunt Tab Relationship

### 3.2a.1 Detailed Skill Slots Structure (Chi Tiết Cấu Trúc Ô Kỹ Năng)

**Key Concept**: `skill_slots` is NOT just a simple list of skill IDs. It's a detailed data structure containing all information needed by Hunt Tab to display and execute skills.

```python
# Detailed Skill Slots Structure (Loaded from Preset)
skill_slots: dict = {
    "attack_combo": [
        {
            # Slot metadata
            "position": 0,                          # Slot index (0-based)
            "lane_type": "attack_combo",           # Which lane this belongs to
            
            # Skill identity
            "skill_id": 1,                         # FK to skills table
            "skill_name": "Fireball",              # Display name
            "skill_type": "attack",                # Type: attack|buff|utility
            "skill_alias": "FB",                   # Short name for hotkey display
            
            # Visual information (from skills table)
            "icon_x": 10,                          # Icon sprite X coordinate
            "icon_y": 20,                          # Icon sprite Y coordinate
            "icon_w": 20,                          # Icon width
            "icon_h": 20,                          # Icon height
            
            # Runtime state (Hunt Tab Use)
            "user_hotkey": "1",                    # Phím user chọn để đánh (tự do)
                                                   # Có thể là: "1", "2", "3", "q", "w", "e", "a", "s", "d"
                                                   # NONE = user chưa assign phím
            "assigned": False,                     # Phím đã assign chưa?
            
            # Execution state (Updated during hunt)
            "is_ready": True,                      # Skill sẵn sàng đánh?
            "cooldown_remaining": 0.0,             # Cooldown còn lại (giây)
            "cooldown_max": 1.2,                   # Max cooldown (để show progress bar)
            "last_executed": 0.0,                  # Timestamp lần cuối đánh
            
            # Context information
            "preset_name": "Default - Mage",       # Preset this came from (for display)
            "from_build_tab": True,                # Whether from Build Tab definition
        },
        {
            "position": 1,
            "lane_type": "attack_combo",
            "skill_id": 2,
            "skill_name": "Blizzard",
            "skill_type": "attack",
            "skill_alias": "BZ",
            "icon_x": 30,
            "icon_y": 20,
            "icon_w": 20,
            "icon_h": 20,
            "user_hotkey": "2",
            "assigned": True,
            "is_ready": False,
            "cooldown_remaining": 0.8,
            "cooldown_max": 1.5,
            "last_executed": 0.4,
            "preset_name": "Default - Mage",
            "from_build_tab": True,
        },
        # ... more attack_combo slots
    ],
    
    "buff_lane": [
        {
            "position": 0,
            "lane_type": "buff_lane",
            "skill_id": 5,
            "skill_name": "Mana Shield",
            "skill_type": "buff",
            "skill_alias": "MS",
            "icon_x": 50,
            "icon_y": 20,
            "icon_w": 20,
            "icon_h": 20,
            "user_hotkey": "3",
            "assigned": True,
            "is_ready": True,
            "cooldown_remaining": 0.0,
            "cooldown_max": 2.0,
            "last_executed": 5.2,
            "preset_name": "Default - Mage",
            "from_build_tab": True,
        },
        # ... more buff_lane slots
    ]
}

# IMPORTANT:
# - Number of attack_combo slots = user defined in Skill Build Tab
# - Number of buff_lane slots = user defined in Skill Build Tab
# - user_hotkey = phím user chọn để đánh skill này (assignment happens in Hunt Tab)
# - is_ready, cooldown_remaining = runtime state (updates during hunt)
# - preset_name = shows which preset was loaded
```

### 3.2a.2 Build Tab → Hunt Tab Data Flow

```
┌────────────────────────────────────────────────────────────┐
│               TWO-SCREEN WORKFLOW                          │
└────────────────────────────────────────────────────────────┘

PHASE 1: BUILD TAB (Skill Build Tab)
═════════════════════════════════════════════════════════════
Purpose: Define how many skill slots, which skills, which order

┌──────────────────────────────────────────────────────────┐
│ Skill Build Tab Screen                                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ 1. SELECT CLASS                                          │
│    Choose: [Mage ▼] or [Warrior ▼] or [Rogue ▼]       │
│                                                          │
│ 2. DEFINE SKILL SLOTS (Edit how many & which skills)   │
│    Attack Combo Slots: [Skill Picker]                   │
│    ├─ Slot 0: [Fireball ▼] [X]                         │
│    ├─ Slot 1: [Blizzard ▼] [X]                         │
│    ├─ Slot 2: [Lightning ▼] [X]                        │
│    └─ [+ Add Slot]                                      │
│                                                          │
│    Buff Lane Slots: [Skill Picker]                      │
│    ├─ Slot 0: [Mana Shield ▼] [X]                      │
│    ├─ Slot 1: [Regenerate ▼] [X]                       │
│    └─ [+ Add Slot]                                      │
│                                                          │
│ 3. SAVE AS PRESET                                       │
│    Preset Name: [Default - Mage ▼]                     │
│    [Save] [Save as Custom]                              │
│                                                          │
│    Result: Store in Database                            │
│    - skill_presets row (preset_id, class_id, name)     │
│    - preset_skills rows (skill_id, position per slot)  │
│                                                          │
└───────────────────────┬────────────────────────────────┘
                        │ Save Preset
                        │ (skill_presets + preset_skills)
                        ▼
                ┌─────────────────────────┐
                │  Database Storage       │
                │ - skill_presets         │
                │ - preset_skills         │
                └─────────────────────────┘
                        │ Load when needed
                        ▼

PHASE 2: HUNT TAB (Hunt Tab - Skill Panel)
═════════════════════════════════════════════════════════════
Purpose: USE the preset definition, assign hotkeys, execute

┌──────────────────────────────────────────────────────────┐
│ Hunt Tab - Skill Panel                                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ 1. LOAD PRESET                                           │
│    [System loads "Default - Mage" preset from DB]       │
│    skill_slots populated with:                          │
│    - Number of slots = defined in Build Tab             │
│    - Skills = ordered as defined in Build Tab           │
│    - Hotkeys = EMPTY (user needs to assign)             │
│                                                          │
│ 2. DISPLAY SKILL SLOTS (From preset definition)         │
│    ┌──────────────────────────────────┐                 │
│    │ Attack Combo Slots:              │                 │
│    │ [🔥 Fireball] [❄️ Blizzard]    │  Slot 0, 1, 2    │
│    │ [⚡ Lightning]                  │  (From Build Tab) │
│    │                                  │                 │
│    │ Buff Lane Slots:                 │                 │
│    │ [🛡️ Mana Shield] [💚 Regen]    │  Slot 0, 1       │
│    │ (From Build Tab)                 │                 │
│    └──────────────────────────────────┘                 │
│                                                          │
│ 3. USER ASSIGNS HOTKEYS (Optional per slot)             │
│    Attack Combo:                                        │
│    Fireball   → [Hotkey: 1 ▼] or [Assign Key: ? □]   │
│    Blizzard   → [Hotkey: 2 ▼] or [Assign Key: ? □]   │
│    Lightning  → [Hotkey: 3 ▼] or [Assign Key: ? □]   │
│                                                          │
│    Buff Lane:                                           │
│    Mana Shield → [Hotkey: 3 ▼] or [Assign Key: ? □]   │
│    Regen       → [Hotkey: 4 ▼] or [Assign Key: ? □]   │
│                                                          │
│    Note: If NOT assigned, shows "[None]" or "?"        │
│                                                          │
│ 4. DISPLAY MODE & STATUS                                │
│    Current Preset: "Default - Mage" (preset_name)      │
│    Combo Status: 🔴 INACTIVE (not yet started)         │
│                                                          │
│    [⚙️ Build] [📋 Presets] [🔄 Reset]                 │
│    [▶️ START COMBO MODE]  ◄── Explicit activation     │
│                                                          │
└───────────────────────┬────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼ (NOT Combo Mode)              ▼ (IN Combo Mode)
────────────────────────────────────────────────────────────

NOT IN COMBO MODE:                  IN COMBO MODE:
═════════════════════════════════   ═══════════════════════════
User bấp phím tương ứng             Máy tự bấm sequence:
- Bấm "1" → Execute Fireball        - Bấm "1" → Fireball
- Bấm "2" → Execute Blizzard        - Auto wait 1.2s
- Bấm "3" → Execute Mana Shield     - Bấm "2" → Blizzard
                                    - Auto wait 1.5s
Hotkeys = User control              - Bấm "3" → Mana Shield
                                    - Loop back to "1"

Hotkeys = Machine control
(Auto-execute sequence)
```

### 3.2a.3 Skill Slot Lifecycle

```
1. DEFINITION PHASE (Skill Build Tab)
   └─ User defines: How many slots? Which skills?
      Result: Preset stored in DB (skill_presets + preset_skills)

2. LOAD PHASE (Hunt Tab startup)
   └─ System loads preset from DB
   └─ Populate skill_slots array
      Result: skill_slots has all slot definitions but NO hotkeys yet

3. ASSIGNMENT PHASE (Hunt Tab)
   └─ User optionally assigns hotkeys per slot
      Result: skill_slots.user_hotkey = "1", "2", "3", etc.

4. EXECUTION PHASE (Hunt Tab during hunt)
   ├─ NOT Combo Mode:
   │  └─ User presses hotkey → Execute skill
   │     skill_slots[slot].is_ready updates based on cooldown
   │
   └─ Combo Mode:
      └─ System auto-executes sequence
         skill_slots[slot].is_ready, cooldown_remaining updated
         Every slot loops according to cooldowns

5. RESET/SWITCH PHASE
   └─ User clicks [📋 Presets] or [🔄 Reset]
      Result: skill_slots reloaded from different preset
      Hotkey assignments cleared (need re-assign)
```

---

## 4. Service Layer Architecture

### 4.1 SkillPresetService

**Purpose**: High-level operations for preset management

```python
class SkillPresetService:
    """
    Service layer for skill preset operations.
    Coordinates between UI (AppStateController) and data layer (Repositories).
    """
    
    def __init__(self, skill_repo: SkillRepository, 
                 preset_repo: SkillPresetRepository,
                 state_manager: PresetStateManager):
        self.skill_repo = skill_repo
        self.preset_repo = preset_repo
        self.state_manager = state_manager
    
    # PRESET OPERATIONS
    
    def apply_preset(self, preset_id: int, class_id: int) -> Dict:
        """
        Apply a preset (default or custom) to active skill_slots.
        
        Args:
            preset_id: Integer PK of preset to apply
            class_id: Integer FK of class (for validation)
        
        Flow:
        1. Query preset_skills for this preset_id
        2. Join with skills to get full data
        3. Validate all skills valid for class_id (via class_skill_assignments)
        4. Update AppStateController.skill_slots
        5. Update user_preset_state (active_preset_id, preset_mode)
        6. Emit UI callback (skill_slots_changed)
        
        Return: { 'success': True, 'preset_name': '...', 'skill_count': 3 }
        """
        pass
    
    def create_custom_preset(self, preset_name: str, class_id: int,
                            skill_slots: Dict) -> int:
        """
        Create a new custom preset from current skill_slots.
        
        Args:
            preset_name: User-provided name
            class_id: Integer FK of class
            skill_slots: { 'attack_combo': [...], 'buff_lane': [...] }
        
        Flow:
        1. Validate skill_slots structure
        2. Validate all skill_ids valid for class_id (class_skill_assignments)
        3. Create skill_presets row (is_default=FALSE, class_id=...)
        4. For each skill in skill_slots:
            - Insert into preset_skills table
            - Maintain position order
        5. Update user_preset_state (active_preset_id, preset_mode='custom')
        6. Return new preset_id
        
        Return: preset_id (integer)
        """
        pass
    
    def update_custom_preset(self, preset_id: int, 
                            skill_slots: Dict) -> bool:
        """
        Update an existing custom preset with new skill order.
        
        Flow:
        1. Verify preset_id is custom (is_default=FALSE)
        2. Delete existing preset_skills for this preset
        3. Insert new preset_skills rows
        4. Emit UI callback
        
        Return: True if successful, False otherwise
        """
        pass
    
    def delete_custom_preset(self, preset_id: int) -> bool:
        """
        Delete a custom preset (only allows custom presets).
        
        Flow:
        1. Verify preset exists and is custom
        2. If currently active, revert to default
        3. Delete preset_skills entries
        4. Delete preset row
        
        Return: True if successful, False otherwise
        """
        pass
    
    def list_presets_by_class(self, class_id: int) -> List[PresetInfo]:
        """
        Get all presets for a class (default + custom).
        
        Args:
            class_id: Integer FK to classes table
        
        Return: [
            PresetInfo(id=1, name='Default - Mage', is_default=True, 
                      skill_count=3, last_used='2026-09-04'),
            PresetInfo(id=2, name='Custom - Boss', is_default=False,
                      skill_count=3, last_used='2026-09-02'),
            ...
        ]
        """
        pass
    
    def get_current_preset_info(self, class_id: int) -> PresetInfo:
        """
        Get info about currently active preset for class.
        
        Args:
            class_id: Integer FK to classes table
        
        Return: PresetInfo with current preset details
        """
        pass
    
    # SKILL OPERATIONS
    
    def list_all_skills(self, class_id: int = None) -> List[SkillInfo]:
        """
        Get all skills available.
        If class_id provided, filter by valid skills for that class.
        Uses class_skill_assignments for validation.
        
        Args:
            class_id: Optional FK to classes table for filtering
        
        Return: List of SkillInfo objects with metadata
        """
        pass
    
    def get_skill_details(self, skill_id: int) -> SkillInfo:
        """Get full details of a specific skill"""
        pass
    
    # MIGRATION
    
    def migrate_legacy_presets(self, legacy_hunt_cfg: Dict, class_mapping: Dict) -> bool:
        """
        Migrate presets from legacy JSON format to database.
        
        Args:
            legacy_hunt_cfg: Dict from hunt_cfg.json: { 'Mage': [...skills...], ... }
            class_mapping: Dict mapping class names to class_ids: { 'Mage': 1, 'Warrior': 2, ... }
        
        Called once on app startup if legacy data detected.
        For each class in legacy_hunt_cfg:
            1. Get class_id from class_mapping
            2. Create default preset for class_id
            3. Add skills as preset_skills
            4. Initialize user_preset_state
        """
        pass
```

### 4.2 SkillRepository (Data Access Layer)

```python
class SkillRepository:
    """
    Repository for skill CRUD operations.
    Direct database access for skill_library.
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.db = db_connection
    
    # CREATE
    def create_skill(self, skill_data: Dict) -> int:
        """Insert new skill, return skill_id"""
        pass
    
    # READ
    def get_skill(self, skill_id: int) -> SkillInfo:
        """Fetch skill by ID"""
        pass
    
    def list_skills(self, filters: Dict = None) -> List[SkillInfo]:
        """
        Fetch multiple skills with optional filters.
        Filters can include:
        - type: 'attack', 'buff', 'utility'
        - class_id: integer FK for filtering by valid assignments
        - is_recommended: 0/1 (from class_skill_assignments)
        """
        pass
    
    def search_skills(self, query: str) -> List[SkillInfo]:
        """Full-text search by skill name/description"""
        pass
    
    # UPDATE
    def update_skill(self, skill_id: int, updates: Dict) -> bool:
        """Modify existing skill"""
        pass
    
    # DELETE
    def delete_skill(self, skill_id: int) -> bool:
        """Remove skill (cascade delete from preset_skills)"""
        pass
    
    # BATCH
    def seed_default_skills(self, skills_data: List[Dict]) -> bool:
        """Bulk insert skills (on initial DB setup)"""
        pass
```

### 4.3 SkillPresetRepository

```python
class SkillPresetRepository:
    """
    Repository for skill preset CRUD operations.
    Manages preset definitions and skill ordering.
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.db = db_connection
    
    # SKILL_PRESETS TABLE
    
    def create_preset(self, class_id: int, preset_name: str,
                     is_default: bool = False) -> int:
        """Create preset record for class_id, return preset_id"""
        pass
    
    def get_preset(self, preset_id: int) -> PresetInfo:
        """Fetch preset metadata"""
        pass
    
    def list_presets_by_class(self, class_id: int) -> List[PresetInfo]:
        """Get all presets for a class (uses class_id FK)"""
        pass
    
    def update_preset(self, preset_id: int, updates: Dict) -> bool:
        """Update preset metadata"""
        pass
    
    def delete_preset(self, preset_id: int) -> bool:
        """Delete preset and associated preset_skills"""
        pass
    
    # PRESET_SKILLS TABLE
    
    def add_skill_to_preset(self, preset_id: int, skill_id: int,
                           lane_type: str, position: int) -> bool:
        """Add skill to preset at specific position"""
        pass
    
    def get_preset_skills(self, preset_id: int) -> PresetSkillsData:
        """
        Fetch all skills in preset, organized by lane.
        
        Return: {
            'attack_combo': [SkillInfo(...), SkillInfo(...), ...],
            'buff_lane': [SkillInfo(...), ...]
        }
        """
        pass
    
    def reorder_preset_skills(self, preset_id: int, 
                             lane_type: str,
                             new_order: List[int]) -> bool:
        """Update position of skills in lane"""
        pass
    
    def remove_skill_from_preset(self, preset_id: int, 
                                skill_id: int) -> bool:
        """Remove skill from preset"""
        pass
    
    # BULK OPERATIONS
    
    def set_preset_skills(self, preset_id: int, skills_by_lane: Dict) -> bool:
        """
        Replace all skills in preset.
        Deletes existing preset_skills, inserts new ones.
        """
        pass
    
    def seed_default_presets(self, presets_data: List[Dict]) -> bool:
        """Bulk insert default presets (on initial DB setup)"""
        pass
```

### 4.4 PresetStateManager

```python
class PresetStateManager:
    """
    Manages user_preset_state table.
    Tracks current active preset per class.
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.db = db_connection
    
    def get_active_preset(self, class_id: int) -> int:
        """Get currently active preset_id for class (FK)"""
        pass
    
    def set_active_preset(self, class_id: int, preset_id: int,
                         preset_mode: str = 'default') -> bool:
        """
        Update active preset and mode.
        Args:
            class_id: Integer FK to classes table
            preset_id: Integer PK to apply
            preset_mode: 'default' or 'custom'
        """
        pass
    
    def get_preset_mode(self, class_id: int) -> str:
        """Get current mode for class: 'default' or 'custom'"""
        pass
    
    def reset_to_default(self, class_id: int) -> bool:
        """Switch class back to default mode and preset"""
        pass
```

---

## 5. Data Flow Sequences

### 5.1 User Opens Hunt Tab (App Startup)

```
1. AppGUI.__init__()
   └─ Initialize AppStateController

2. HuntTab loads
   └─ Call AppStateController.load_preset_for_class(class_id=1)  # class_id from classes table
   
3. AppStateController.load_preset_for_class(class_id)
   ├─ Query user_preset_state WHERE class_id=1 (FK)
   ├─ Get active_preset_id (e.g., 1 for default)
   ├─ Call SkillPresetService.apply_preset(preset_id=1, class_id=1)
   └─ Return skill_slots
   
4. SkillPresetService.apply_preset()
   ├─ Query preset_skills WHERE preset_id=1
   ├─ Organize by lane_type and position
   ├─ Validate skills against class_skill_assignments for class_id=1
   ├─ Update AppStateController.skill_slots
   └─ Emit callback: on_skill_slots_changed()
   
5. SkillPanel receives callback
   ├─ Display attack_combo in combobox
   ├─ Display buff_lane in combobox
   └─ Mark as "Default Preset"
   
6. SkillStatsPanel receives callback
   └─ Calculate stats for new combo
   
7. Hunt ready to start
```

### 5.2 User Clicks "Reset to Default" Button

```
1. User clicks [🔄 Reset] in SkillPanel

2. SkillPanel._on_reset_clicked()
   └─ Call AppStateController.apply_default_preset(class_id=1)

3. AppStateController.apply_default_preset(class_id)
   ├─ Query skill_presets WHERE class_id=1 (FK) AND is_default=TRUE
   ├─ Get preset_id (e.g., 1)
   ├─ Call SkillPresetService.apply_preset(preset_id=1, class_id=1)
   └─ Emit callback
   
4. SkillPresetService.apply_preset()
   ├─ Query preset_skills WHERE preset_id=1
   ├─ Validate skills via class_skill_assignments for class_id=1
   ├─ Populate skill_slots
   ├─ Update user_preset_state (class_id=1, preset_mode='default')
   └─ Emit callback: on_skill_slots_changed()
   
5. SkillPanel updates display
   ├─ Show new skill combo
   ├─ Mark as "Default Preset ⭐"
   └─ Disable "Save Custom" until user changes skills
```

### 5.3 User Changes Skill Combo During Combat

```
1. User selects different skill from dropdown
   └─ SkillPanel._on_skill_selected()

2. SkillPanel notifies AppStateController
   └─ AppStateController.set_skill_slot(
        lane='attack_combo', position=0, skill_id=2)

3. AppStateController updates skill_slots
   └─ Checks if this differs from current preset
   
4. If different from current preset:
   ├─ Update preset_mode to 'custom'
   ├─ Set _preset_changed_flag = True
   ├─ Enable "Save Custom" button
   └─ Mark display as "Custom (Unsaved) ✏️"
   
5. Emit callbacks:
   ├─ on_skill_slots_changed() → SkillPanel refreshes display
   ├─ on_preset_mode_changed('custom') → Shows save prompt
   └─ on_stats_update() → Recalculate stats
   
6. User continues hunting with modified combo
   └─ Changes persist in memory (skill_slots)
   
7. User can:
   ├─ Click "Save Custom" → Create/update custom preset in DB
   ├─ Click "Reset" → Revert to default preset
   └─ Close app → Ask "Save changes?" dialog
```

### 5.4 User Saves Custom Preset

```
1. User clicks [📋 Presets] → Select "Save as Custom"
   └─ Opens SaveCustomPresetDialog

2. User enters preset name (e.g., "Boss Farming v2")
   └─ Clicks OK

3. Dialog calls SkillPresetService.create_custom_preset()
   ├─ Validate skill_slots
   ├─ Validate skills via class_skill_assignments for class_id
   ├─ Create skill_presets row (is_default=FALSE, class_id=FK)
   ├─ For each skill, insert preset_skills rows
   ├─ Update user_preset_state:
   │  ├─ class_id = FK
   │  ├─ active_preset_id = new_preset_id
   │  └─ preset_mode = 'custom'
   └─ Return new_preset_id
   
4. AppStateController receives callback
   ├─ Update internal state
   ├─ _preset_changed_flag = False
   └─ Emit on_preset_saved()
   
5. SkillPanel displays
   ├─ "Custom Preset: Boss Farming v2 ✏️"
   ├─ Disable "Save Custom" button (already saved)
   └─ Show "Load Different" button
   
6. Next time user opens app for same class:
   └─ Load this custom preset automatically (as active_preset_id in user_preset_state)
```

### 5.5 User Loads Different Preset from Dialog

```
1. User clicks [📋 Presets] → Shows all presets

Dialog displays (for class_id=1):
├─ ⭐ Default - Mage (is_default=TRUE, preset_id=1)
├─ ✏️ Custom - Boss Farming v1 (is_default=FALSE, preset_id=2)
├─ ✏️ Custom - Boss Farming v2 (is_default=FALSE, preset_id=3)
└─ ✏️ Custom - PvP Variant (is_default=FALSE, preset_id=4)

2. User selects "Custom - Boss Farming v1" (preset_id=2)
   └─ Click OK

3. Dialog calls SkillPresetService.apply_preset(preset_id=2, class_id=1)
   ├─ Query preset_skills WHERE preset_id=2
   ├─ Validate skills via class_skill_assignments for class_id=1
   ├─ Rebuild skill_slots from preset
   ├─ Update user_preset_state (class_id=1, active_preset_id=2, preset_mode='custom')
   └─ Emit callbacks
   
4. SkillPanel updates display
   ├─ Show skills from new preset
   ├─ Mark as "Custom: Boss Farming v1 ✏️"
   └─ Disable "Save Custom" (unmodified)
   
5. If user modifies skills:
   └─ Repeat 5.3 sequence (mark as custom/unsaved)
```

### 5.6 Hotkey Assignment & Skill Selection in Hunt Tab (Không Combo Mode)

```
SCENARIO: User assigns hotkeys to skills for manual execution

Prerequisite:
- skill_slots loaded from preset (e.g., "Default - Mage")
- Combo mode is 🔴 INACTIVE
- User can modify skill selections and assign hotkeys

FLOW:
─────────────────────────────────────────────────────────────

1. Hunt Tab displays Skill Panel with skill slots
   
   Attack Combo Slots (from preset):
   ├─ Slot 0: [Fireball] ← Hotkey: [1 ▼] or [Assign: □]
   ├─ Slot 1: [Blizzard] ← Hotkey: [2 ▼] or [Assign: □]
   └─ Slot 2: [Lightning] ← Hotkey: [3 ▼] or [Assign: □]
   
   Buff Lane Slots (from preset):
   ├─ Slot 0: [Mana Shield] ← Hotkey: [3 ▼] or [Assign: □]
   └─ Slot 1: [Regenerate] ← Hotkey: [4 ▼] or [Assign: □]
   
   Status: 🔴 COMBO MODE: INACTIVE
   User can modify skills manually

2. User chooses hotkeys (optional):
   
   Option A: Simple Assignment
   ├─ Click dropdown: [1 ▼] → Select "1", "2", "3", "q", "w", etc.
   └─ Result: skill_slots[0].user_hotkey = "1"
   
   Option B: No Assignment
   └─ Leave as "None" or "[  ]"
   └─ This skill cannot be executed manually (only in combo mode)

3. User can change skill selection:
   
   User clicks dropdown [Fireball ▼]
   └─ Choose different skill: [Blizzard] or [Lightning]
   └─ Result: skill_slots[0].skill_id changes
   └─ Mark preset as "Custom (Unsaved) ✏️"
   └─ Enable [Save Custom] button

4. During hunting (NOT Combo Mode):
   
   User presses hotkey (e.g., "1")
   └─ Skill Panel receives hotkey event
   └─ Find skill_slot WHERE user_hotkey="1"
   └─ Execute: skill_slots[0].skill_id (Fireball)
   └─ Update: skill_slots[0].is_ready=False, cooldown_remaining=1.2
   └─ BotManager calls game automation to execute skill
   
   Repeat for each hotkey press:
   User presses "2" → Execute Blizzard
   User presses "3" → Execute Mana Shield
   User presses "q" → Execute next assigned skill
   
   Parallel: Cooldown timer updates skill_slots[i].cooldown_remaining
   └─ UI shows countdown: "Blizzard (0.8s)"
   └─ When cooldown_remaining reaches 0, is_ready=True
   └─ UI shows: "Blizzard (Ready)"

5. Result:
   - User has full control over which hotkey does what
   - Can press any hotkey anytime (if skill is ready)
   - Skill selection can be changed mid-hunt
   - Changes persist in skill_slots (but not saved to preset unless user clicks Save)
```

### 5.7 Combo Mode Activation & Execution

```
SCENARIO: User activates combo mode for automatic skill sequence execution

Prerequisite:
- skill_slots loaded from preset
- User wants automated skill execution sequence
- At least some skills have hotkeys assigned

FLOW:
─────────────────────────────────────────────────────────────

1. Hunt Tab displays Skill Panel
   
   Current state:
   🔴 COMBO MODE: INACTIVE
   Attack Combo: [Fireball - key:1] [Blizzard - key:2] [Lightning - key:3]
   Buff Lane: [Mana Shield - key:3]
   
   [⚙️ Build] [📋 Presets] [🔄 Reset]
   [▶️ START COMBO MODE]  ← User clicks this

2. User clicks [▶️ START COMBO MODE] button

3. System activates Combo Mode:
   └─ Set AppStateController._combo_mode_active = True
   └─ Lock skill selections (disable dropdowns)
   └─ Enable hotkey interceptor for combo sequence
   └─ Emit callback: on_combo_mode_activated()

4. SkillPanel updates display:
   
   Visual change:
   🟢 COMBO MODE: ACTIVE  ← Status changed
   
   Current Skills (from preset):
   ├─ Executing: [Fireball]
   ├─ Next: [Blizzard] (0.8s)
   └─ Sequence: Fireball → Blizzard → Lightning → (repeat)
   
   Status: [EXECUTING] ← Shows it's running
   Hotkey Reminder: Alt+3 Ready
   
   [⏹️ STOP COMBO MODE]  ← Button changes to stop
   [Presets: SWITCH] [Reset]  ← Limited actions available

5. Combo Mode Execution Loop:
   
   Start of cycle:
   ├─ Read skill_slots array in order
   ├─ skill_slots[0] (Fireball, hotkey="1")
   ├─ Press hotkey "1" → Execute Fireball
   ├─ Update: skill_slots[0].cooldown_remaining = 1.2
   ├─ Update: skill_slots[0].is_ready = False
   └─ Record: skill_slots[0].last_executed = current_time
   
   Waiting for cooldown:
   ├─ Timer counts down: 1.2s → 1.1s → ... → 0.0s
   ├─ UI shows: "Blizzard (0.8s)" countdown
   ├─ When cooldown expires: skill_slots[0].is_ready = True
   
   Next skill in sequence:
   ├─ Move to skill_slots[1] (Blizzard, hotkey="2")
   ├─ Check: is_ready? YES
   ├─ Press hotkey "2" → Execute Blizzard
   ├─ Update: skill_slots[1].cooldown_remaining = 1.5
   ├─ Update: skill_slots[1].is_ready = False
   
   Continue cycle:
   ├─ Move to skill_slots[2] (Lightning, hotkey="3")
   ├─ Wait for cooldown...
   ├─ Execute Lightning
   
   Loop back:
   ├─ skill_slots[0] cooldown may have expired by now
   └─ Restart cycle from beginning
   
   Parallel: Buff lane skills (if cooldowns permit)
   └─ Intersperse buff skills among attack combo

6. User interaction during Combo Mode:
   
   Option A: Let machine run (hands off)
   └─ System auto-presses hotkeys in sequence
   └─ User watches monitor
   
   Option B: User presses hotkey manually
   ├─ System detects: User pressed "1"
   ├─ Execute skill (override auto sequence)
   ├─ Resume auto sequence after cooldown
   
   Option C: Stop Combo Mode
   └─ User clicks [⏹️ STOP COMBO MODE]
   └─ System stops hotkey automation
   └─ Return to 🔴 INACTIVE state
   └─ User can manually control skills again

7. Combo Mode deactivation:
   
   When user clicks [⏹️ STOP COMBO MODE]:
   ├─ Set AppStateController._combo_mode_active = False
   ├─ Clear hotkey automation
   ├─ Unlock skill selections
   ├─ Emit callback: on_combo_mode_deactivated()
   
   SkillPanel updates:
   └─ Display returns to 🔴 INACTIVE
   └─ Show current skill_slots with is_ready status
   └─ Enable skill selection dropdowns
   └─ Button returns to [▶️ START COMBO MODE]

8. Data persistence:
   
   During Combo Mode:
   └─ skill_slots runtime state updated (cooldowns, execution timestamps)
   └─ Changes NOT persisted to database (transient)
   
   After Stop or Crash:
   └─ skill_slots state reset to preset definition
   └─ No changes saved to database unless user manually saves

SUMMARY:
─────────────────────────────────────────────────────────────
NOT Combo Mode:  User presses hotkey → One skill executes
Combo Mode:      System auto-presses hotkeys → Skill sequence executes
Switching:       User clicks START/STOP button (explicit, clear indication)
Display:         🔴 (inactive) vs 🟢 (active) status indicator
```

---

## 6. UI-Logic Integration Strategy

### 6.1 Recommended UI-Logic Alignment

**Key Principle**: The Skill Build Tab is the "source of truth" for preset definitions.

```
┌─────────────────────────────────────┐
│  Skill Build Tab                    │  ← Source of Truth
│  (Skill Build Panel)                │    for preset definitions
│  ├─ Class selector                  │
│  ├─ Default/Custom tabs             │
│  ├─ Skill picker                    │
│  ├─ Reorder controls                │
│  └─ Save button                     │
└────────────┬────────────────────────┘
             │ reads/writes presets
             ▼
    ┌─────────────────────────┐
    │  SkillPresetRepository  │  ← Database persistence
    │  (skill_presets table)  │
    └────────────┬────────────┘
                 │
     ┌───────────┴────────────┐
     │                        │
     ▼                        ▼
┌──────────────────┐   ┌──────────────────┐
│ SkillPanel       │   │ Presets Dialog   │
│ (Hunt Tab)       │   │ (UI Component)   │
│ ├─ Dropdown      │   ├─ List presets    │
│ ├─ Current combo │   ├─ Load button     │
│ └─ Save button   │   └─ Delete button   │
└──────────────────┘   └──────────────────┘
```

### 6.2 UI-Logic Contract

#### SkillPanel ↔ AppStateController

```python
# UI (SkillPanel) sends to Logic
class SkillPanel:
    def on_skill_dropdown_changed(self, skill_id):
        self.app_state.set_skill_slot(
            lane='attack_combo',
            position=0,
            skill_id=skill_id,
            class_id=self.current_class_id  # Pass class_id for validation
        )
    
    def on_reset_clicked(self):
        self.app_state.apply_default_preset(
            class_id=self.current_class_id
        )
    
    def on_save_custom_clicked(self, name):
        self.skill_service.create_custom_preset(
            preset_name=name,
            class_id=self.current_class_id,  # FK to classes table
            skill_slots=self.app_state.skill_slots
        )

# Logic (AppStateController) notifies UI
class AppStateController:
    def on_skill_slots_changed_callback(self, new_slots):
        """Called when skill_slots change"""
        # SkillPanel receives this callback and updates display
        self.callbacks['skill_slots_changed'](new_slots)
    
    def on_preset_mode_changed_callback(self, mode):
        """Called when preset_mode changes (default/custom)"""
        # SkillPanel updates "Default" / "Custom ✏️" label
        self.callbacks['preset_mode_changed'](mode)
```

#### PresetDialog ↔ SkillPresetService

```python
# UI (PresetDialog) sends to Logic
class PresetDialog:
    def on_preset_selected(self, preset_id, class_id):
        """Apply selected preset (class_id used for validation)"""
        self.preset_service.apply_preset(
            preset_id=preset_id,
            class_id=class_id  # FK to classes table
        )
    
    def on_delete_preset(self, preset_id, class_id):
        """Delete custom preset"""
        self.preset_service.delete_custom_preset(
            preset_id=preset_id,
            class_id=class_id
        )
    
    def refresh_preset_list(self, class_id):
        """Reload all presets for class (uses class_id FK)"""
        presets = self.preset_service.list_presets_by_class(
            class_id=class_id
        )
        self.display_presets(presets)

# Logic (SkillPresetService) notifies UI
class SkillPresetService:
    def apply_preset(self, preset_id, class_id):
        # ...apply logic...
        self.ui_callback('preset_applied', preset_id, class_id)
        # PresetDialog receives and updates display
```

### 6.3 State Consistency Guarantees

**Guarantee 1**: At any point, `AppStateController.skill_slots` reflects the currently active preset or current modifications.

```python
# Invariant: skill_slots == current_preset + user_modifications
assert app_state.skill_slots == preset_repo.get_preset_skills(
    app_state._active_preset_id
) or app_state._preset_changed_flag == True
```

**Guarantee 2**: `user_preset_state` table accurately reflects current preset and mode for class_id.

```python
# Invariant: user_preset_state matches AppStateController state
# Query: user_preset_state WHERE class_id = ?
current_mode = state_manager.get_preset_mode(class_id=1)
assert current_mode == app_state._preset_mode
```

**Guarantee 3**: All custom presets are persisted in database immediately.

```python
# Invariant: Custom preset in memory == Custom preset in DB
# Both linked by class_id FK
custom_preset_id = app_state._active_preset_id
db_preset = preset_repo.get_preset_skills(custom_preset_id)
assert app_state.skill_slots == db_preset.to_dict()
```

**Guarantee 4**: All skills in a preset are valid for its class (via class_skill_assignments).

```python
# Invariant: Skills in preset must be assigned to its class
# Query: preset_skills WHERE preset_id = ?
#        JOIN class_skill_assignments WHERE class_id matches preset's class_id
for skill in preset.skills:
    assert skill_id in class_skill_assignments[class_id]
```

---

## 7. Skill Library CRUD Operations

### 7.1 Read Operations (Used by Hunt Workspace)

**List Skills for Class** (via class_id FK):
```python
def load_skills_for_class(class_id: int) -> List[SkillInfo]:
    """
    Load all valid skills for a class (via class_skill_assignments).
    Used by: SkillPanel dropdown, Skill Build Tab picker
    
    Args:
        class_id: Integer FK to classes table
    """
    sql = """
    SELECT s.skill_id, s.name, s.type, s.icon_x, s.icon_y
    FROM skills s
    JOIN class_skill_assignments csa ON s.skill_id = csa.skill_id
    WHERE csa.class_id = ?
    ORDER BY csa.is_recommended DESC, s.type, s.name
    """
    # Returns: [SkillInfo, SkillInfo, ...]
```

**Get Skill Details**:
```python
def get_skill_info(skill_id: int) -> SkillInfo:
    """
    Fetch full skill details.
    Used by: Skill Stats Panel, Skill Build Tab
    """
    sql = """
    SELECT * FROM skills WHERE skill_id = ?
    """
    # Returns: SkillInfo(id, name, type, icon_*, ...)
```

### 7.2 Create Operations (Admin/Initial Setup)

**Create New Skill** (Admin tool):
```python
def create_skill(skill_data: Dict) -> int:
    """
    Insert new skill into library.
    
    skill_data = {
        'name': 'New Skill',
        'type': 'attack',
        'cast_time': 1.2,
        'cooldown': 0.5,
        'damage_base': 150,
        'class_requirement': 'Mage'
    }
    
    Returns: skill_id
    """
    sql = """
    INSERT INTO skills 
    (name, type, cast_time, cooldown, damage_base, class_requirement)
    VALUES (?, ?, ?, ?, ?, ?)
    """
```

### 7.3 Update Operations

**Modify Skill Properties** (Admin tool):
```python
def update_skill(skill_id: int, updates: Dict) -> bool:
    """
    Modify skill definition.
    
    updates = {
        'cast_time': 1.5,
        'cooldown': 0.8,
        'damage_base': 180
    }
    
    Note: Changes affect all active presets using this skill
    """
    sql = """
    UPDATE skills 
    SET cast_time=?, cooldown=?, damage_base=?, updated_at=CURRENT_TIMESTAMP
    WHERE skill_id = ?
    """
    # Trigger: Notify all preset users of skill property change
```

### 7.4 Delete Operations

**Remove Skill** (Admin tool):
```python
def delete_skill(skill_id: int) -> bool:
    """
    Remove skill from library.
    
    On delete: Cascade removes skill from all presets.
    Note: Should warn if skill is in active presets.
    """
    sql = """
    DELETE FROM preset_skills WHERE skill_id = ?;
    DELETE FROM skills WHERE skill_id = ?;
    """
```

### 7.5 Skill Library Integration with Skill Management Screen

**Screen Flow**:
```
Skill Management Tab
├─ Search skill library (skills table)
├─ Display: name, type, damage, cooldown, class, icon
├─ Actions:
│  ├─ View details (full SkillInfo)
│  ├─ Add to preset (in Skill Build Tab)
│  └─ Adjust properties (admin only)
└─ Used by Skill Build Tab for skill picker
```

**Data Binding**:
```python
class SkillManagementTab:
    def load_skill_library(self, class_name: str = None):
        """Load skills for display"""
        skills = self.skill_repo.list_skills(
            filters={'class_requirement': class_name}
        )
        # Display in table/list widget
    
    def on_skill_selected(self, skill_id: int):
        """Show full details"""
        skill_info = self.skill_repo.get_skill(skill_id)
        # Display SkillInfo in detail panel
    
    def use_in_preset(self, skill_id: int):
        """Add skill to current preset in Skill Build Tab"""
        # Trigger: Switch to Skill Build Tab + skill picker
```

---

## 8. Database Initialization & Migration

### 8.1 Initial Setup (First App Launch)

```python
def initialize_database():
    """
    Called once on app startup if database doesn't exist.
    Uses class_id (FK) throughout, not class_name (TEXT).
    """
    # 1. Create tables (lib/db/schema.py: setup_skills_schema)
    from lib.db.schema import setup_skills_schema
    setup_skills_schema(self.db_connection)
    
    # 2. Seed classes (classes table)
    seed_classes(CLASSES_DATA)  # class_id auto-incremented
    
    # 3. Seed skills (skills table with class_id FK)
    seed_skills(SKILLS_DATA)
    
    # 4. Seed class-skill assignments (class_skill_assignments table)
    seed_class_skill_assignments(ASSIGNMENTS_DATA)
    
    # 5. Seed default presets (skill_presets with class_id FK)
    seed_default_presets(DEFAULT_PRESETS_DATA)
    
    # 6. Create user_preset_state for each class (uses class_id FK)
    for class_id in range(1, NUM_CLASSES + 1):
        default_preset = get_default_preset(class_id)  # Query: is_default=TRUE
        state_manager.set_active_preset(
            class_id=class_id,           # FK to classes table
            preset_id=default_preset.id,
            preset_mode='default'
        )
```

### 8.2 Migrating from Legacy JSON

```python
def migrate_legacy_config():
    """
    Migrate from hunt_cfg.json to database.
    Called if legacy JSON detected on app startup.
    Uses class_id (FK) instead of class_name (TEXT).
    """
    legacy_cfg = load_json('hunt_cfg.json')
    
    # Build mapping: class_name -> class_id (from classes table)
    class_name_to_id = {}
    for row in self.db.execute('SELECT class_id, name FROM classes'):
        class_name_to_id[row['name']] = row['class_id']
    
    for class_name, skill_order in legacy_cfg.items():
        if class_name not in class_name_to_id:
            logger.warning(f"Class '{class_name}' not found in database, skipping")
            continue
        
        class_id = class_name_to_id[class_name]
        
        # 1. Create default preset for this class (uses class_id FK)
        preset_id = preset_repo.create_preset(
            class_id=class_id,                      # FK, not class_name
            preset_name=f'Default - {class_name}',
            is_default=True
        )
        
        # 2. Add skills to preset (from legacy order)
        for idx, skill_name in enumerate(skill_order):
            skill = skill_repo.get_skill_by_name(skill_name)
            if not skill:
                logger.warning(f"Skill '{skill_name}' not found, skipping")
                continue
            
            preset_repo.add_skill_to_preset(
                preset_id, skill.skill_id,
                lane_type='attack_combo',  # assume all attack
                position=idx
            )
        
        # 3. Set as active for class (uses class_id FK)
        state_manager.set_active_preset(
            class_id=class_id,              # FK to classes table
            preset_id=preset_id,
            preset_mode='default'
        )
    
    # 4. Backup legacy file
    backup_json('hunt_cfg.json.backup')
    logger.info("Legacy JSON migration complete")
```

---

## 9. Error Handling & Recovery

### 9.1 Scenario: Corrupted Preset

```python
def load_preset_safely(preset_id: int, class_id: int) -> PresetSkillsData:
    """
    Load preset with validation and recovery.
    Uses class_id for fallback to default preset.
    """
    try:
        preset = preset_repo.get_preset(preset_id)
        if not preset:
            raise PresetNotFoundError(f"Preset {preset_id} not found")
        
        skills = preset_repo.get_preset_skills(preset_id)
        
        # Validate all skills exist and are assigned to this class
        for skill in skills['attack_combo'] + skills['buff_lane']:
            if not skill_repo.get_skill(skill.skill_id):
                logger.warning(f"Skill {skill.skill_id} missing from library")
                # Fallback: skip missing skill or use placeholder
            
            # Validate skill is assigned to class_id
            if not self._is_skill_valid_for_class(skill.skill_id, class_id):
                logger.warning(f"Skill {skill.skill_id} not valid for class {class_id}")
                # Fallback: skip invalid skill
        
        return skills
    
    except Exception as e:
        logger.error(f"Error loading preset {preset_id}: {e}")
        # Fallback: load default preset for class_id
        return self._load_default_preset_for_class(class_id)
    
def _is_skill_valid_for_class(self, skill_id: int, class_id: int) -> bool:
    """
    Check if skill is assigned to class via class_skill_assignments.
    """
    sql = """
    SELECT 1 FROM class_skill_assignments
    WHERE skill_id=? AND class_id=?
    """
    return self.db.execute(sql, (skill_id, class_id)).fetchone() is not None
    
def _load_default_preset_for_class(self, class_id: int) -> PresetSkillsData:
    """
    Fallback: load default preset (is_default=TRUE) for class_id.
    """
    default_preset = self.db.execute("""
        SELECT preset_id FROM skill_presets
        WHERE class_id=? AND is_default=TRUE
        LIMIT 1
    """, (class_id,)).fetchone()
    
    if default_preset:
        return self.get_preset_skills(default_preset[0])
    else:
        logger.error(f"No default preset for class {class_id}")
        return {'attack_combo': [], 'buff_lane': []}
```

### 9.2 Scenario: Skill Changes Affecting Active Presets

```python
def on_skill_property_changed(skill_id: int, class_id: int = None):
    """
    Called when a skill's properties change (e.g., icon coordinates).
    Notify all presets using this skill.
    
    Args:
        skill_id: Skill that changed
        class_id: Optional FK to classes, for targeted notifications
    """
    # Query: Find all presets using this skill
    # If class_id provided, filter to that class
    if class_id:
        affected_presets = self.db.execute("""
            SELECT DISTINCT sp.preset_id, sp.name
            FROM skill_presets sp
            JOIN preset_skills ps ON sp.preset_id = ps.preset_id
            WHERE ps.skill_id = ? AND sp.class_id = ?
        """, (skill_id, class_id)).fetchall()
    else:
        affected_presets = self.db.execute("""
            SELECT DISTINCT sp.preset_id, sp.name
            FROM skill_presets sp
            JOIN preset_skills ps ON sp.preset_id = ps.preset_id
            WHERE ps.skill_id = ?
        """, (skill_id,)).fetchall()
    
    for preset_id, preset_name in affected_presets:
        # Check if this is the active preset
        active_preset = state_manager.get_active_preset(class_id)
        if preset_id == active_preset:
            # Active preset affected
            logger.warning(f"Skill change may affect active preset: {preset_name}")
            # Trigger UI notification: "Your active preset may be outdated"
            ui_callback('skill_changed_warning', skill_id, preset_name, class_id)
```

---

## 10. Implementation Roadmap

### Phase 1: Database Setup (Week 1)
- [ ] Design and validate schema
- [ ] Create database initialization script
- [ ] Implement SkillRepository class
- [ ] Implement SkillPresetRepository class
- [ ] Implement PresetStateManager class

### Phase 2: Service Layer (Week 2)
- [ ] Implement SkillPresetService
- [ ] Add callback/event system for state changes
- [ ] Implement preset apply/save/delete operations
- [ ] Add error handling and recovery

### Phase 3: Controller Integration (Week 3)
- [ ] Update AppStateController for preset management
- [ ] Integrate with SkillPresetService
- [ ] Add callback handlers for UI updates
- [ ] Implement state synchronization

### Phase 4: UI Integration (Week 4)
- [ ] Update SkillPanel with preset mode display
- [ ] Create PresetDialog component
- [ ] Add "Reset to Default" button
- [ ] Add "Save Custom" button
- [ ] Implement preset selection dropdown

### Phase 5: Data Migration (Week 5)
- [ ] Implement legacy JSON → Database migration
- [ ] Create backup/rollback mechanism
- [ ] Test with real user data
- [ ] Document migration process

### Phase 6: Testing & Validation (Week 6)
- [ ] Unit tests for repository layer
- [ ] Integration tests for service layer
- [ ] UI tests for preset operations
- [ ] Performance testing (preset load time)
- [ ] User acceptance testing

---

## 11. Architecture Recommendations: UI-Logic Alignment

### 11.1 Recommended Approach

```
┌─────────────────────────────────────────────────────────┐
│   Hunt Workspace Redesign Architecture                 │
│                                                         │
│   UI Layer (WORKSPACE-REDESIGN-UI-DESIGN.md)           │
│   ├─ SkillPanel (Column 1, Row 2)                      │
│   │  ├─ Displays current skill_slots                   │
│   │  ├─ Dropdowns for runtime changes                  │
│   │  └─ Actions: [⚙️ Build] [📋 Presets] [🔄 Reset]  │
│   │                                                    │
│   ├─ Skill Build Tab (Separate Tab)                    │
│   │  ├─ Source of truth for preset definitions         │
│   │  ├─ Skill picker                                   │
│   │  ├─ Reorder controls                               │
│   │  └─ Save as default/custom                         │
│   │                                                    │
│   └─ Presets Dialog                                    │
│      ├─ Lists all presets (default + custom)           │
│      ├─ Apply / Delete buttons                         │
│      └─ Shows current active preset                    │
│                                                         │
├─────────────────────────────────────────────────────────┤
│   Service Layer (Logic Design)                          │
│   ├─ SkillPresetService                                │
│   │  ├─ apply_preset()                                 │
│   │  ├─ create_custom_preset()                         │
│   │  ├─ save_custom_preset()                           │
│   │  └─ delete_custom_preset()                         │
│   │                                                    │
│   └─ AppStateController                                │
│      ├─ skill_slots (current state)                    │
│      ├─ preset_mode ('default' or 'custom')            │
│      ├─ Callbacks for UI updates                       │
│      └─ State persistence                              │
│                                                         │
├─────────────────────────────────────────────────────────┤
│   Repository Layer                                      │
│   ├─ SkillRepository (CRUD for skills)                 │
│   ├─ SkillPresetRepository (CRUD for presets)          │
│   └─ PresetStateManager (active preset tracking)       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│   Data Layer                                            │
│   └─ SQLite Database                                    │
│      ├─ skills table                                   │
│      ├─ skill_presets table                            │
│      ├─ preset_skills table                            │
│      └─ user_preset_state table                        │
└─────────────────────────────────────────────────────────┘

Key Design Principles:
1. Separation of Concerns: UI ↔ Service ↔ Repository ↔ Database
2. Single Responsibility: Each class handles one domain
3. Data Flow: Unidirectional upward (UI → Service → Repo → DB)
4. Callbacks: Downward notifications (DB ← Repo ← Service → UI)
5. State Consistency: AppStateController is source of truth
```

### 11.2 Why This Architecture Works

| Principle | Benefit |
|-----------|---------|
| Separation of UI & Logic | UI can be redesigned without changing business logic |
| Database Persistence | Presets survive app restart |
| Service Layer | Reusable logic for multiple UI components |
| Repository Pattern | Easy to switch between JSON and SQLite without changing service layer |
| State Management | Single source of truth (AppStateController) prevents inconsistency |
| Callback Pattern | Loose coupling between layers, easier testing |

### 11.3 Integration with Existing UX4.2 Features

```
┌─────────────────────────────────────────────────────┐
│   New Workspace Redesign                           │
│   (4-Panel Layout + Preset System)                 │
│                                                    │
│   ↑ Uses ↓                                         │
│                                                    │
├─────────────────────────────────────────────────────┤
│   Existing UX4.2 Features                         │
│   ├─ Skill routing (single-hop)                   │
│   ├─ Toast notifications (latest-only)            │
│   ├─ Dropdown revert logic                        │
│   ├─ Key conflict validation                      │
│   └─ JSON config migration                        │
│                                                    │
│   No changes to these features!                   │
│   (New system wraps/extends, doesn't replace)     │
└─────────────────────────────────────────────────────┘

Integration Point: AppStateController.skill_slots
- Existing UX4.2 code reads/writes to skill_slots
- New preset system populates skill_slots
- Both systems work together seamlessly
```

---

## 11. Three-Screen UI & Data Specification

### 11.1 Overview: Three Screens for Three Workflows

```
┌────────────────────────────────────────────────────────────────────────┐
│                     HUNT WORKSPACE SCREENS                            │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│ SCREEN 1: COMBO PANEL (Skill Panel - Hunt Tab)                       │
│ Purpose: Display & use skills during hunt                            │
│ Workflow: Select skill → Assign hotkey → Execute (manual/combo mode) │
│ User: Huntmaster (during hunting session)                            │
│                                                                        │
│ ↕ (Preset Switching)                                                 │
│ [📋 Presets] Dialog opens                                            │
│                                                                        │
│ ↕ (Configure Preset)                                                 │
│ [⚙️ Build] Button navigates to                                       │
│                                                                        │
│ SCREEN 2: SKILL BUILD TAB (Skill Preset Builder)                     │
│ Purpose: Create/edit skill presets per class                         │
│ Workflow: Select class → Choose skills → Define slots → Save preset  │
│ User: Huntmaster (during preparation)                                │
│                                                                        │
│ ↕ (Add/Edit Skills)                                                  │
│ [🔍 Skill Library] opens                                             │
│                                                                        │
│ SCREEN 3: CRUD SKILL TAB (Skill Management/Library)                  │
│ Purpose: Manage individual skill definitions                         │
│ Workflow: View skills → Search → Create/Update/Delete → View changes│
│ User: Admin or advanced users (infrequent, setup/maintenance)        │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 11.2 SCREEN 1: Combo Panel (Skill Panel in Hunt Tab)

**Purpose**: Display active skill preset and control skill execution (manual vs combo mode)

**Location**: Hunt Tab → Skill Panel (Right panel, top section)

**Database Tables Used**: 
- `skill_presets` (read current preset info)
- `preset_skills` (read skill slots)
- `skills` (read skill properties: icon, name)
- `user_preset_state` (read active preset for class)

**UI Components**:

```
┌──────────────────────────────────────────────────────────────┐
│                 Skill Panel (Hunt Tab)                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ [Preset: "Default - Mage" ⭐] [📋 Presets] [⚙️ Build]       │
│                                                              │
│ Status: 🔴 COMBO MODE: INACTIVE   [▶️ START COMBO MODE]    │
│         (Click to toggle)          or [⏹️ STOP]            │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Attack Combo Slots:                                     │ │
│ │                                                         │ │
│ │ [🔥 Fireball] ← Hotkey: [1 ▼] or [Assign: □]          │ │
│ │              ← Status: 🟢 Ready (cooldown: 0.0s)       │ │
│ │                                                         │ │
│ │ [❄️ Blizzard] ← Hotkey: [2 ▼] or [Assign: □]          │ │
│ │              ← Status: 🔴 Cooling (0.8s remaining)     │ │
│ │                                                         │ │
│ │ [⚡ Lightning] ← Hotkey: [3 ▼] or [Assign: □]          │ │
│ │               ← Status: 🟢 Ready (cooldown: 0.0s)      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Buff Lane Slots:                                        │ │
│ │                                                         │ │
│ │ [🛡️ Mana Shield] ← Hotkey: [4 ▼] or [Assign: □]       │ │
│ │                  ← Status: 🟢 Ready (cooldown: 0.0s)    │ │
│ │                                                         │ │
│ │ [💚 Regenerate] ← Hotkey: [5 ▼] or [Assign: □]        │ │
│ │                 ← Status: 🟢 Ready (cooldown: 0.0s)     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ [🔄 Reset] [Change Skill] [ℹ️ Info]                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Data Display**:

For each skill slot displayed:
```python
{
    "position": 0,
    "lane_type": "attack_combo",
    
    # Display Properties (from DB)
    "skill_name": "Fireball",           # From skills.name
    "skill_icon": 🔥,                   # From skills.icon
    
    # Hotkey Assignment (runtime state)
    "user_hotkey": "1",                 # From AppStateController
    
    # Cooldown Status (runtime)
    "is_ready": True,                   # ✓ Ready or ✗ Cooling
    "cooldown_remaining": 0.0,          # "0.0s" or "0.8s"
    "cooldown_max": 1.2                 # Progress bar max
}
```

**Data Binding Flow**:

1. **On Tab Load**: 
   - Read `user_preset_state WHERE class_id = current_class`
   - Get `active_preset_id`
   - Load `preset_skills WHERE preset_id = active_preset_id`
   - Display each slot with skill info from `skills` table
   - Show preset name from `skill_presets.name`

2. **On Hotkey Assignment**:
   - User clicks [Assign: □] next to skill
   - Prompt for hotkey input
   - Store in `AppStateController.skill_slots[lane][position].user_hotkey`
   - Update UI display

3. **On Preset Change (📋 Presets)**:
   - Load list of all presets from `skill_presets WHERE class_id = current_class`
   - Display with markers: ⭐ (default), ✏️ (custom), ✅ (active)
   - On selection: Load new preset, update display

4. **On Combo Mode Toggle**:
   - User clicks [▶️ START] or [⏹️ STOP]
   - Set `AppStateController._combo_mode_active = True/False`
   - Update status indicator: 🟢 or 🔴
   - Lock/unlock dropdowns

5. **On Cooldown Update (Runtime)**:
   - During hunt execution, `cooldown_remaining` updates continuously
   - UI shows countdown: "Blizzard (0.8s)" → "Blizzard (Ready)"
   - When `is_ready=True`, change color to 🟢

**Related Actions**:
- `[📋 Presets]` → Opens Presets Dialog (load other presets)
- `[⚙️ Build]` → Switches to Build Skills Tab (edit this preset)
- `[🔄 Reset]` → Calls `AppStateController.apply_default_preset(class_id)`
- `[▶️ START]` / `[⏹️ STOP]` → Toggles `_combo_mode_active`

---

### 11.3 SCREEN 2: Skill Build Tab (Skill Preset Builder)

**Purpose**: Create and edit skill presets for each class

**Location**: Separate tab in notebook (alongside Hunt, Setup, Stats tabs)

**Database Tables Used**: 
- `classes` (select class)
- `skill_presets` (create/update preset)
- `preset_skills` (store skill order & lane assignment)
- `class_skill_assignments` (validate skills for class)
- `skills` (skill info for picker)

**UI Components**:

```
┌──────────────────────────────────────────────────────────────┐
│           Skill Build Tab (Preset Configuration)             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ CLASS SELECTION:                                             │
│ [Class: Mage ▼] [Warrior ▼] [Rogue ▼]                      │
│                                                              │
│ PRESET SELECTION:                                            │
│ [Preset Mode: Default ▼] [Custom ▼]                        │
│ Current Preset: "Default - Mage" (Read-Only)               │
│ or [Enter Custom Name: ____________]                        │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │         SKILL SLOTS CONFIGURATION                        │ │
│ │                                                          │ │
│ │ ATTACK COMBO (Max 3-5 slots per class):                 │ │
│ │ ═════════════════════════════════════════════════════════ │
│ │                                                          │ │
│ │ Slot 0: [Skill Picker ▼] [X] [↑] [↓]                   │ │
│ │         ├─ Current: Fireball                            │ │
│ │         ├─ Type: Attack                                 │ │
│ │         ├─ Cooldown: 1.2s                               │ │
│ │         └─ Lane: Attack Combo                           │ │
│ │                                                          │ │
│ │ Slot 1: [Skill Picker ▼] [X] [↑] [↓]                   │ │
│ │         ├─ Current: Blizzard                            │ │
│ │         ├─ Type: Attack                                 │ │
│ │         ├─ Cooldown: 1.5s                               │ │
│ │         └─ Lane: Attack Combo                           │ │
│ │                                                          │ │
│ │ [+ Add Skill Slot]                                      │ │
│ │                                                          │ │
│ │ BUFF LANE (Max 1-3 slots per class):                    │ │
│ │ ═════════════════════════════════════════════════════════ │
│ │                                                          │ │
│ │ Slot 0: [Skill Picker ▼] [X] [↑] [↓]                   │ │
│ │         ├─ Current: Mana Shield                         │ │
│ │         ├─ Type: Buff/Defense                           │ │
│ │         ├─ Cooldown: 2.0s                               │ │
│ │         └─ Lane: Buff Lane                              │ │
│ │                                                          │ │
│ │ [+ Add Skill Slot]                                      │ │
│ │                                                          │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ ACTIONS:                                                     │
│ [🔍 Skill Library] [Preview Stats] [Reset] [Save]           │
│                                                              │
│ Status: ✅ Preset ready to save                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Data Display & Structure**:

For each skill slot in Skill Build Tab:
```python
{
    # Slot Identity
    "position": 0,
    "lane_type": "attack_combo",  # or "buff_lane"
    
    # Skill Selection (from skills table)
    "skill_id": 1,                # FK to skills table
    "skill_name": "Fireball",
    "skill_type": "attack",
    
    # Skill Properties (from skills table)
    "cooldown": 1.2,
    "cast_time": 0.5,
    "damage_base": 150,
    "icon_x": 10,
    "icon_y": 20,
    
    # Preset State (being configured)
    "is_assigned": True,          # Slot has a skill selected
    "can_reorder": True,          # Can move up/down
}
```

**Database Operations**:

1. **Load Current Preset**:
   ```python
   # On tab load or class change
   SELECT sp.preset_id, sp.name, sp.is_default, sp.class_id
   FROM skill_presets sp
   WHERE sp.class_id = ? (current class)
   AND sp.is_default = TRUE  # Load default first
   
   # Then load skills for this preset
   SELECT ps.skill_id, ps.position, ps.lane_type, 
          s.name, s.cooldown, s.damage_base, s.icon_x, s.icon_y
   FROM preset_skills ps
   JOIN skills s ON ps.skill_id = s.skill_id
   WHERE ps.preset_id = ?
   ORDER BY ps.lane_type, ps.position
   ```

2. **Get Available Skills for Picker**:
   ```python
   SELECT s.skill_id, s.name, s.type, s.cooldown, s.damage_base
   FROM skills s
   JOIN class_skill_assignments csa ON s.skill_id = csa.skill_id
   WHERE csa.class_id = ?
   ORDER BY csa.is_recommended DESC, s.type, s.name
   ```

3. **Save Preset**:
   ```python
   # Create or update skill_presets row
   INSERT OR REPLACE INTO skill_presets 
   (preset_id, class_id, name, is_default, created_at, updated_at)
   VALUES (?, ?, ?, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
   
   # Clear old preset_skills
   DELETE FROM preset_skills WHERE preset_id = ?
   
   # Insert new preset_skills rows
   INSERT INTO preset_skills 
   (preset_id, skill_id, position, lane_type)
   VALUES (?, ?, ?, ?)  # Repeat for each slot
   
   # Update user_preset_state
   UPDATE user_preset_state 
   SET active_preset_id = ?, preset_mode = 'custom'
   WHERE class_id = ?
   ```

**Workflow**:

```
1. USER OPENS BUILD TAB
   ├─ Select class: [Mage ▼]
   ├─ System loads default preset for Mage
   ├─ Display all slots from preset_skills
   └─ Show skill names, types, cooldowns

2. USER CONFIGURES PRESET
   ├─ Click [Skill Picker ▼] for slot
   ├─ Dialog shows available skills
   ├─ User selects skill (only from class_skill_assignments)
   ├─ Display updates with new skill info
   ├─ User can reorder with [↑] [↓] buttons
   ├─ User can remove with [X] button
   └─ User can add slots with [+ Add Skill Slot]

3. USER SAVES PRESET
   ├─ Click [Save] button
   ├─ System validates:
   │  ├─ All skills valid for class (via class_skill_assignments)
   │  ├─ At least 1 skill in attack_combo
   │  └─ No duplicate skills in same lane
   ├─ Insert/update skill_presets row
   ├─ Clear preset_skills and insert new rows
   ├─ Update user_preset_state to point to new preset
   └─ Show confirmation: "✅ Preset saved successfully"

4. USER SWITCHES BACK TO HUNT TAB
   ├─ Skill Panel auto-loads new preset
   ├─ Display shows: "Preset: [Custom Name] ✏️"
   ├─ All slots reflect new configuration
   └─ Ready for hunting
```

**Validation Rules**:

```python
# Constraints for Skill Build Tab
1. Class must be selected
2. Attack Combo lane must have at least 1 skill
3. All skills must be valid for class (check class_skill_assignments)
4. No duplicate skills in same lane
5. Max slots per lane (e.g., 3-5 for attack, 1-3 for buff)
6. Preset name required when saving custom
```

---

### 11.4 SCREEN 3: CRUD Skill Tab (Skill Management/Library)

**Purpose**: Manage individual skill definitions (Create, Read, Update, Delete operations)

**Location**: Separate tab in notebook (or part of Setup tab)

**Database Tables Used**: 
- `skills` (CRUD operations)
- `classes` (skill class requirements)
- `class_skill_assignments` (assign skills to classes)

**UI Components**:

```
┌──────────────────────────────────────────────────────────────┐
│        CRUD Skill Tab (Skill Library Management)             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ SEARCH & FILTER:                                             │
│ [🔍 Search: __________] [Type: All ▼] [Class: All ▼]        │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Skill Library (Treeview/Table):                         │ │
│ │ ──────────────────────────────────────────────────────── │ │
│ │ ID │ Name       │ Type      │ Cooldown │ Damage │ Class  │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ 1  │ Fireball   │ Attack    │ 1.2s    │ 150    │ Mage   │ │
│ │ 2  │ Blizzard   │ Attack    │ 1.5s    │ 120    │ Mage   │ │
│ │ 3  │ Lightning  │ Attack    │ 1.0s    │ 200    │ Mage   │ │
│ │ 4  │ Mana Shield│ Defense   │ 2.0s    │ 0      │ Mage   │ │
│ │ 5  │ Slash      │ Attack    │ 0.8s    │ 100    │ Warrior│ │
│ │ 6  │ Whirlwind  │ Attack    │ 1.5s    │ 180    │ Warrior│ │
│ │ 7  │ Block      │ Defense   │ 1.0s    │ 0      │ Warrior│ │
│ │ 8  │ Backstab   │ Attack    │ 1.2s    │ 250    │ Rogue  │ │
│ │    │            │           │         │        │        │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ SKILL DETAILS (Click to select):                             │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Name:        [Fireball                    ]             │ │
│ │ Type:        [Attack ▼]                    │            │ │
│ │ Cooldown:    [1.2 seconds]                 │            │ │
│ │ Cast Time:   [0.5 seconds]                 │            │ │
│ │ Damage Base: [150                          ]            │ │
│ │ Class Req.:  [Mage ▼]                      │            │ │
│ │ Description: [Throws a fireball at target  ]            │ │
│ │              [for magical attack damage.   ]            │ │
│ │                                                          │ │
│ │ Icon Position: X=[10] Y=[20]                            │ │
│ │ Last Updated: 2026-09-04 10:30:00                       │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ ACTIONS:                                                     │
│ [➕ New] [✏️ Edit] [🗑️ Delete] [📋 Copy] [ℹ️ Info]           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Data Display & Structure**:

Skill Library Table columns:
```python
{
    "skill_id": 1,                      # From skills.skill_id
    "name": "Fireball",                 # From skills.name
    "type": "attack",                   # From skills.type (attack/buff/utility)
    "cooldown": 1.2,                    # From skills.cooldown
    "cast_time": 0.5,                   # From skills.cast_time
    "damage_base": 150,                 # From skills.damage_base
    "class_requirement": "Mage",        # From skills.class_requirement
    "icon_x": 10,                       # From skills.icon_x
    "icon_y": 20,                       # From skills.icon_y
    "description": "Throws a fireball...",  # From skills.description
    "created_at": "2026-01-01 ...",     # From skills.created_at
    "updated_at": "2026-09-04 ..."      # From skills.updated_at
}
```

**Database Operations**:

1. **Read All Skills** (Display table):
   ```python
   SELECT s.skill_id, s.name, s.type, s.cooldown, s.damage_base, 
          s.class_requirement, s.created_at, s.updated_at
   FROM skills s
   ORDER BY s.class_requirement, s.type, s.name
   ```

2. **Search Skills** (Filter):
   ```python
   SELECT ... FROM skills s
   WHERE (s.name LIKE ? OR s.description LIKE ?)
   AND (s.type = ? OR ? = 'all')
   AND (s.class_requirement = ? OR ? = 'all')
   ORDER BY s.class_requirement, s.type, s.name
   ```

3. **Get Skill Details** (Click row):
   ```python
   SELECT * FROM skills WHERE skill_id = ?
   ```

4. **Create New Skill**:
   ```python
   INSERT INTO skills 
   (name, type, cooldown, cast_time, damage_base, class_requirement, 
    icon_x, icon_y, description, created_at, updated_at)
   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
   
   RETURNING skill_id
   ```

5. **Update Skill**:
   ```python
   UPDATE skills
   SET name=?, type=?, cooldown=?, cast_time=?, damage_base=?, 
       class_requirement=?, icon_x=?, icon_y=?, description=?, 
       updated_at=CURRENT_TIMESTAMP
   WHERE skill_id = ?
   ```

6. **Delete Skill**:
   ```python
   -- Check if skill is in use by presets
   SELECT COUNT(*) FROM preset_skills WHERE skill_id = ?
   
   IF count > 0:
       Show warning: "This skill is used by X presets. Delete anyway?"
   
   -- If confirmed, delete skill
   DELETE FROM class_skill_assignments WHERE skill_id = ?
   DELETE FROM preset_skills WHERE skill_id = ?
   DELETE FROM skills WHERE skill_id = ?
   ```

7. **Assign Skill to Class** (class_skill_assignments):
   ```python
   INSERT INTO class_skill_assignments 
   (class_id, skill_id, is_recommended)
   VALUES (?, ?, TRUE)
   ```

**Workflow**:

```
1. USER OPENS CRUD SKILL TAB
   ├─ Load all skills from skills table
   ├─ Display in tree view with columns
   └─ Enable search/filter boxes

2. USER SEARCHES FOR SKILL
   ├─ Type in search box or select filters
   ├─ Query skills with WHERE clause
   └─ Update table display with results

3. USER CREATES NEW SKILL
   ├─ Click [➕ New] button
   ├─ Open "New Skill" dialog
   ├─ User enters: name, type, cooldown, damage, class requirement
   ├─ System validates data
   ├─ Insert into skills table
   ├─ Get returned skill_id
   ├─ Add to class_skill_assignments
   └─ Refresh table (show new skill)

4. USER EDITS SKILL
   ├─ Click on skill row to select
   ├─ Click [✏️ Edit] button
   ├─ Open "Edit Skill" dialog (pre-filled with current data)
   ├─ User modifies properties
   ├─ System validates data
   ├─ Update skills table
   ├─ Show warning if skill is in active presets
   │  "This skill is used by X presets. Changes will affect them."
   └─ Refresh table with updated values

5. USER DELETES SKILL
   ├─ Click on skill row to select
   ├─ Click [🗑️ Delete] button
   ├─ Show confirmation dialog:
   │  "Delete 'Fireball'? (Used in X presets)"
   ├─ If confirmed:
   │  ├─ Delete from class_skill_assignments
   │  ├─ Delete from preset_skills (removes from all presets!)
   │  └─ Delete from skills
   ├─ Show warning if any presets became invalid
   └─ Refresh table (skill removed)

6. USER WANTS TO USE SKILL IN PRESET
   ├─ Click on skill row
   ├─ Click [📋 Copy] or "Use in Preset"
   ├─ Switch to Build Skills Tab
   ├─ Skill auto-selected in picker
   └─ User adds to preset slot
```

**Validation Rules**:

```python
# When Creating/Updating Skills
1. Name: Required, unique, max 50 chars
2. Type: Must be one of [attack, buff, utility]
3. Cooldown: Must be >= 0, decimal (0.5 to 10.0 seconds)
4. Cast Time: Must be >= 0, decimal (0.1 to 5.0 seconds)
5. Damage Base: Must be >= 0 integer
6. Class Requirement: Must exist in classes table
7. Icon Position: Valid X,Y coordinates (0-2000)
8. Description: Optional, max 500 chars

# When Deleting Skills
- Warn if skill is in any preset
- Warn if skill is in active preset for current class
- Allow force-delete (removes from all presets)
```

---

### 11.5 Three-Screen Integration Summary

**Data Flow Between Screens**:

```
┌─────────────────────────────────────────────────────────────────┐
│          COMPLETE DATA FLOW ACROSS 3 SCREENS                   │
└─────────────────────────────────────────────────────────────────┘

SCREEN 3 (CRUD Skill Tab)
│
│ User creates new skill: "Meteor Storm"
│ └─ INSERT into skills table (skill_id=100)
│    └─ INSERT into class_skill_assignments (class_id=1, skill_id=100)
│       └─ Emit: Skill Library Updated
│
│ ▼ (Available for use)
│
SCREEN 2 (Build Skills Tab)
│
│ User opens Build Tab → Skill Picker
│ └─ Query skills from class_skill_assignments
│    └─ Display includes new "Meteor Storm" skill
│       └─ User selects it for slot
│          └─ Save preset → INSERT into preset_skills
│             └─ INSERT into user_preset_state (new preset active)
│                └─ Emit: Preset Updated
│
│ ▼ (Preset loaded)
│
SCREEN 1 (Combo Panel)
│
│ User opens Hunt Tab
│ └─ Skill Panel loads active preset
│    └─ Query user_preset_state → get active_preset_id
│       └─ Query preset_skills → load all slots
│          └─ Display: "Meteor Storm" in attack slot 2
│             └─ User assigns hotkey: "3"
│                └─ User clicks [▶️ START]
│                   └─ Combo mode active: Machine presses "1" → "2" → "3" (Meteor Storm)
│
│ ▼ (Changes from hunting)
│
SCREEN 3 (CRUD Skill Tab)
│
│ Admin notices cooldown is too short
│ └─ Edit "Meteor Storm" skill
│    └─ Change cooldown: 1.0s → 2.5s
│       └─ UPDATE skills table
│          └─ Emit: Skill Modified Warning
│             ├─ Affects preset: "Default - Mage"
│             ├─ Affects preset: "Boss Farming v1"
│             └─ Affects combo panel: If in active preset

```

**Synchronized State Across Screens**:

| Property | Screen 1 | Screen 2 | Screen 3 | Source |
|----------|----------|----------|----------|--------|
| Class ID | Read active | Read selected | Context menu | AppStateController |
| Skill List | Dropdown | Picker | Table | skills table |
| Preset Name | Display | Edit | N/A | skill_presets |
| Skill Slots | Display/Use | Define | N/A | preset_skills |
| Skill Properties | Show cooldown | Show when selected | Edit values | skills table |
| Combo Mode | Control | N/A | N/A | AppStateController |

**Error Handling Across Screens**:

```
If skill in Screen 3 is modified/deleted
  └─ Update all affected presets in Screen 2
     └─ Warn in Combo Panel (Screen 1) if affects active preset
        └─ Option: Reload preset or revert changes

If preset in Screen 2 is deleted
  └─ Check if it's active in Screen 1
     └─ If active: Switch to default preset
        └─ Notify user with message

If hotkey assignment in Screen 1 conflicts
  └─ Warn user: "Hotkey 'Q' already assigned to Skill X"
     └─ Allow override or choose different hotkey
```

---

## 12. Summary & Quick Reference

### 12.1 Key Entities

| Entity | Purpose | Storage |
|--------|---------|---------|
| Skill | Attack/Buff ability definition | `skills` table |
| Preset | Group of skills for a class | `skill_presets` table |
| PresetSkill | Skill in specific position in preset | `preset_skills` table |
| PresetState | Currently active preset per class | `user_preset_state` table |
| AppStateController | In-memory UI state | Python object |

### 12.2 Key Operations

| Operation | Trigger | Result |
|-----------|---------|--------|
| Apply Preset | User opens Hunt, selects preset | Load preset_skills into skill_slots |
| Save Custom | User modifies and clicks Save | Create custom preset in DB |
| Reset Default | User clicks Reset button | Revert to default preset |
| Change Preset | User selects from dropdown | Switch active preset |

### 12.3 Data Consistency Checks

```python
# At any point, these should be true:
assert app_state.skill_slots == loaded_preset.skills
assert state_manager.active_preset == app_state._active_preset_id
assert app_state._preset_mode in ['default', 'custom']
```

---

## Appendix B: Related Documents

- **WORKSPACE-REDESIGN-UI-DESIGN.md** - 4-panel layout, components, styling
- **UX4.2-AUTO-FIX-PROMPT.md** - Technical implementation for existing features
- **UX4.2-CORRECTED-GUIDELINE.md** - Original UX4.2 specification

---

## Appendix C: Sample SQL Queries

### Get Current Skill Slots for Hunt

```sql
-- Get active preset for current class
SELECT ps.name, ps.preset_id, ups.preset_mode
FROM user_preset_state ups
JOIN skill_presets ps ON ups.active_preset_id = ps.preset_id
WHERE ups.class_name = 'Mage';

-- Get skills in active preset, ordered by lane
SELECT ps.lane_type, ps.position, s.name, s.cast_time, s.cooldown
FROM preset_skills ps
JOIN skills s ON ps.skill_id = s.skill_id
WHERE ps.preset_id = 1
ORDER BY ps.lane_type, ps.position;
```

### Find All Presets for a Class

```sql
SELECT preset_id, name, is_default,
       COUNT(ps.skill_id) as skill_count
FROM skill_presets
LEFT JOIN preset_skills ps USING(preset_id)
WHERE class_name = 'Mage'
GROUP BY preset_id
ORDER BY is_default DESC, name;
```

### Check for Skill Changes Affecting Presets

```sql
-- Find all presets using a specific skill
SELECT DISTINCT sp.preset_id, sp.name
FROM skill_presets sp
JOIN preset_skills ps ON sp.preset_id = ps.preset_id
WHERE ps.skill_id = 1;

-- Check if any active presets are affected
SELECT DISTINCT sp.name
FROM user_preset_state ups
JOIN skill_presets sp ON ups.active_preset_id = sp.preset_id
WHERE sp.preset_id IN (
    SELECT DISTINCT preset_id
    FROM preset_skills
    WHERE skill_id = 1
);
```

