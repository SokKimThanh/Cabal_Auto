# Hunt Workspace Redesign - UI Design Document

**Version**: 1.0  
**Date**: 2026-09-04  
**Status**: Design Specification  
**Target**: Hunt Tab Layout Restructuring with 4-Panel Balanced System

---

## 1. Overview & Goals

### Current State
The hunt workspace currently displays information across multiple tabs and panels without a cohesive spatial organization. Skill information, monster targets, and performance metrics are scattered across different UI areas.

### Design Goals
1. **Balanced 4-Panel Layout**: Organize content into 4 equally-weighted areas with strategic emphasis
2. **Visual Hierarchy**: Skill Panel and Monster Target Panel occupy larger space (60% combined)
3. **Information Accessibility**: Related data grouped by functional domain
4. **DPI Awareness**: Support multiple display scales (scale_factor 0.8-1.2)
5. **Inter-Panel Linking**: Clear visual connections between combo selection → skill stats

---

## 2. Layout Architecture

### 2.1 Overall Structure: 2-Column, 2-Row Grid

```
┌─────────────────────────────────────────────────────────────┐
│                      Hunt Workspace                         │
├────────────────────────┬────────────────────────────────────┤
│                        │                                    │
│   COLUMN 1             │          COLUMN 2                 │
│   (60% width)          │          (40% width)              │
│                        │                                    │
├──────────────┐         ├──────────────┐                    │
│              │         │              │                    │
│  ROW 1       │ 35%     │   ROW 1      │ 50%                │
│              │ height  │              │ height             │
│   MONSTER    │         │   TARGET &   │                    │
│   TARGET     │         │   STATUS     │                    │
│   PANEL      │         │   PANEL      │                    │
│              │         │              │                    │
├──────────────┤         ├──────────────┤                    │
│              │         │              │                    │
│  ROW 2       │ 65%     │   ROW 2      │ 50%                │
│              │ height  │              │ height             │
│   SKILL      │         │   SKILL      │                    │
│   PANEL      │         │   STATS      │                    │
│              │         │   PANEL      │                    │
│              │         │              │                    │
└──────────────┘         └──────────────┘                    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 2.2 Dimension Specifications

| Component | Width | Height | Scale Factor Impact |
|-----------|-------|--------|---------------------|
| Column 1 | 60% of workspace width | Full height | Direct: width *= scale_factor |
| Column 2 | 40% of workspace width | Full height | Direct: width *= scale_factor |
| Row 1 | Column width | 35-40% | Inverse: height /= scale_factor |
| Row 2 | Column width | 60-65% | Inverse: height /= scale_factor |
| Padding | 8-10 px per panel | 8-10 px per panel | Scale: padding *= scale_factor |

### 2.3 Panel Sizing Ratios

#### Column 1 (Skill-Centric)
- **Total Vertical Space**: 100%
- **Monster Target Panel**: 35% (Primary reference - identifies combo target)
- **Skill Panel**: 65% (Primary interaction - skill selection & status)
- **Rationale**: Skill manipulation requires frequent interaction; monster display supports context

#### Column 2 (Status-Centric)
- **Total Vertical Space**: 100%
- **Target & Status Panel**: 50% (Health, conditions, special markers)
- **Skill Stats Panel**: 50% (Performance metrics, damage output)
- **Rationale**: Even split maintains visual balance; both panels update in real-time

#### Overall Emphasis
```
Emphasis Distribution:
├─ Skill Panel (65%): PRIMARY INTERACTION
├─ Monster Target (35%): CONTEXT & TARGET ID
├─ Status Panel (50%): REAL-TIME MONITORING
└─ Stats Panel (50%): ANALYTICS & FEEDBACK
```

---

## 3. Panel Specifications

### 3.1 Column 1, Row 1: Monster Target Panel (35% height)

**Purpose**: Quick identification and status of current combat target

**Components**:
```
┌─────────────────────────────────────┐
│ 🎯 Current Target                  │  Header with icon
├─────────────────────────────────────┤
│                                     │
│  [Monster Image/Icon - 32x32]      │  
│  Monster Name: Goblin Lord          │  Display name
│  Level: 45                          │  Level info
│  Type: Humanoid / Caster            │  Classification
│                                     │
├─────────────────────────────────────┤
│ ⚡ Quick Stats:                     │  Mini stat bar
│ HP: ████████░░ (340/400)            │  Health bar
│ Conditions: [Stun][Bleed]           │  Status effects
│                                     │
└─────────────────────────────────────┘
```

**Layout Code Structure** (Tkinter):
```python
# Monster Target Panel - Column 1, Row 1
monster_target_frame = ttk.LabelFrame(
    col1_row1_container,
    text="🎯 Current Target",
    padding=(10, 8)
)
monster_target_frame.pack(fill=tk.BOTH, expand=True)

# Components inside:
# - monster_icon: tk.Label (32x32 image)
# - monster_name: tk.Label (bold text)
# - monster_level: tk.Label
# - monster_type: tk.Label
# - health_bar: ttk.Progressbar
# - conditions_frame: tk.Frame (with status badges)
```

**Data Binding**:
- Source: `HuntOrchestrator.current_target` (from `BotManager`)
- Update Trigger: `on_target_changed()` callback
- Refresh Rate: Real-time (when target switches or health changes)
- DPI Scaling: Icon size *= scale_factor, font size *= scale_factor

---

### 3.2 Column 1, Row 2: Skill Panel (65% height)

**Purpose**: Primary interface for skill selection, ordering, and status monitoring

**Components**:
```
┌──────────────────────────────────────────┐
│ ⚔️ Active Skills                        │  Header
├──────────────────────────────────────────┤
│                                          │
│  [Combo Slots - Configurable]           │  
│  ┌─────────────────────────────────────┐ │
│  │ Slot 1: [Fireball] [Speed: 1.2s]   │ │  Combo slot display
│  │ Slot 2: [Blizzard] [Speed: 1.5s]   │ │
│  │ Slot 3: [Lightning] [Speed: 1.0s]  │ │
│  └─────────────────────────────────────┘ │
│                                          │
│  [Manual Skill Selection]                │
│  Attack Combo: [Skill Dropdown ▼]       │  Dropdown for combo change
│  Buff Lane: [Buff Dropdown ▼]           │  During combat customization
│                                          │
│  [Skill Controls]                        │
│  ┌─────────────────────────────────────┐ │
│  │ ⏱️ Next Skill: Fireball (0.3s)      │ │  Countdown timer
│  │ Status: Ready                        │ │  Skill ready state
│  │ Cooldown: None                       │ │  CD tracking
│  └─────────────────────────────────────┘ │
│                                          │
│  [Quick Actions]                         │
│  [⚙️ Build] [📋 Presets] [🔄 Reset]    │  Action buttons
│                                          │
└──────────────────────────────────────────┘
```

**Layout Code Structure**:
```python
# Skill Panel - Column 1, Row 2
skill_frame = ttk.LabelFrame(
    col1_row2_container,
    text="⚔️ Active Skills",
    padding=(10, 8)
)
skill_frame.pack(fill=tk.BOTH, expand=True)

# Sub-sections:
# 1. combo_slots_frame (read-only display of active combo)
#    - skill_slots: [List[SkillSlotDisplay]]
# 2. skill_selection_frame
#    - attack_combo_dropdown: ttk.Combobox
#    - buff_lane_dropdown: ttk.Combobox
# 3. controls_frame
#    - next_skill_label: tk.Label (countdown)
#    - status_label: tk.Label
#    - cooldown_label: tk.Label
# 4. actions_frame
#    - build_button: ttk.Button (→ Skill Build Tab)
#    - presets_button: ttk.Button (→ Presets Dialog)
#    - reset_button: ttk.Button (→ Reset to Default)
```

**Data Binding**:
- Source: `AppStateController.skill_slots` (attack & buff arrays)
- Update Trigger: `on_skill_changed()`, `on_cooldown_update()`
- Refresh Rate: 100ms (skill selection), 50ms (countdown timer)
- DPI Scaling: Font size *= scale_factor, icon size *= scale_factor, padding *= scale_factor

**Interaction Model**:
- **Dropdown Selection**: Shows list of available skill combos (from Skill Build tab)
- **Real-Time Change**: During combat, user can switch skill combos without stopping hunt
- **Preset Application**: "Reset" button applies default preset for current class
- **Visual Feedback**: Highlight changes when combo switches, show timer countdown

---

### 3.3 Column 2, Row 1: Target & Status Panel (50% height)

**Purpose**: Real-time monitoring of combat status and target conditions

**Components**:
```
┌──────────────────────────┐
│ 📊 Target Status         │  Header
├──────────────────────────┤
│                          │
│ Health Bar:              │
│ ████████████░░░ 85%     │  Animated bar
│ (1020 / 1200 HP)         │  Numeric display
│                          │
│ Mana/Resource:           │
│ ██████░░░░░░ 45%        │  Resource bar
│ (90 / 200 MP)            │
│                          │
│ Status Effects:          │
│ [🔥 Burn] [❄️ Freeze]  │  Effect badges
│ [🗡️ Bleed] [⚡ Stun]   │  Color-coded
│                          │
│ Defensive State:         │
│ Armor: +15%              │  Defense info
│ Resistance: Fire +30%    │
│                          │
└──────────────────────────┘
```

**Layout Code Structure**:
```python
# Target & Status Panel - Column 2, Row 1
status_frame = ttk.LabelFrame(
    col2_row1_container,
    text="📊 Target Status",
    padding=(8, 6)
)
status_frame.pack(fill=tk.BOTH, expand=True)

# Components:
# - health_bar: ttk.Progressbar
# - health_label: tk.Label (numeric)
# - resource_bar: ttk.Progressbar
# - resource_label: tk.Label
# - status_effects_frame: tk.Frame
#   - effect_badges: [List[tk.Label]]
# - defensive_frame: tk.Frame
#   - armor_label: tk.Label
#   - resistance_labels: tk.Label (list)
```

**Data Binding**:
- Source: `BotManager.current_target` (from vision engine & game state)
- Update Trigger: Real-time game state polling
- Refresh Rate: 50ms (health/status changes detected by vision)
- DPI Scaling: Bar thickness *= scale_factor, font size *= scale_factor

---

### 3.4 Column 2, Row 2: Skill Stats Panel (50% height)

**Purpose**: Performance analytics and skill effectiveness metrics

**Components**:
```
┌──────────────────────────────┐
│ 📈 Skill Performance         │  Header
├──────────────────────────────┤
│                              │
│ Damage Output:               │
│ Total: 4,250 DMG / min       │  Per-minute stat
│ Active Skill: 1,200 DMG/hit  │  Current skill
│ Buff Effect: +25% Damage     │  Active buffs
│                              │
│ Hit Rate:                    │
│ Last 10 Skills: 9/10 (90%)   │  Recent accuracy
│ Critical Rate: 25% (Avg)     │  Crit tracking
│                              │
│ Resource Efficiency:         │
│ Mana/DMG: 0.85 (efficient)  │  Resource cost ratio
│ Combo Duration: 45.2s        │  Active combo time
│                              │
│ Quick Log:                   │
│ ├─ Fireball: CRIT 2.2k DMG  │  Last 5 actions
│ ├─ Blizzard: 890 DMG         │
│ ├─ Stun Applied              │
│ └─ Buff +25% Duration: 12s   │
│                              │
└──────────────────────────────┘
```

**Layout Code Structure**:
```python
# Skill Stats Panel - Column 2, Row 2
stats_frame = ttk.LabelFrame(
    col2_row2_container,
    text="📈 Skill Performance",
    padding=(8, 6)
)
stats_frame.pack(fill=tk.BOTH, expand=True)

# Components:
# - damage_frame: tk.Frame
#   - total_dps_label: tk.Label
#   - active_skill_dmg_label: tk.Label
#   - buff_bonus_label: tk.Label
# - hitrate_frame: tk.Frame
#   - recent_accuracy_label: tk.Label
#   - crit_rate_label: tk.Label
# - efficiency_frame: tk.Frame
#   - mana_efficiency_label: tk.Label
#   - combo_duration_label: tk.Label
# - action_log_frame: tk.Frame with Scrollbar
#   - log_listbox: tk.Listbox (last 5-10 actions)
```

**Data Binding**:
- Source: `SkillRuntimeService.performance_metrics`
- Update Trigger: After each skill execution, on buff expiration
- Refresh Rate: 100ms (stats aggregation), 200ms (log display)
- DPI Scaling: Font size *= scale_factor, listbox height *= scale_factor

---

## 4. Inter-Panel Data Flow

### 4.1 Panel Communication Diagram

```
┌─────────────────┐
│  Monster Target │
└────────┬────────┘
         │ notifies target_changed()
         │
         ▼
┌─────────────────────────┐
│   Skill Panel (Active)  │  ◄──── AppStateController.skill_slots
│  Shows current combo    │        (loaded from Skill Build tab)
└────────┬────────────────┘
         │ skill selection
         │ changes trigger
         │
         ▼
┌─────────────────┐
│  Status Panel   │  Monitors target health, conditions
└─────────────────┘ Updates from vision engine

         ┌─────────────────────────┐
         │  Stats Panel            │
         │  Tracks skill damage    │
         │  effectiveness          │
         └─────────────────────────┘
```

### 4.2 Update Sequence

1. **User Selects New Skill Combo** (Skill Panel Dropdown)
   ```
   User Action → AppStateController.set_active_combo(combo_id)
   ↓
   AppStateController notifies Skill Panel → Display updated skills
   ↓
   AppStateController notifies Stats Panel → Reset metrics for new combo
   ↓
   BotManager applies new skill sequence to hunt loop
   ```

2. **Target Changes** (Monster Target Panel)
   ```
   Game State Change → BotManager.on_target_changed(new_target)
   ↓
   Broadcasts to Monster Target Panel → Update display
   ↓
   Broadcasts to Status Panel → Reset health/conditions
   ↓
   Broadcasts to Stats Panel → Reset performance metrics
   ```

3. **Real-Time Updates** (Status & Stats Panels)
   ```
   Vision Engine detects game state change (every 50ms)
   ↓
   Updates Status Panel: health bar, status effects
   ↓
   Updates Stats Panel: damage output, hit rate, log
   ↓
   Skill Panel timer updates countdown (every 100ms)
   ```

---

## 5. Linking to Skill Management Screens

### 5.1 Navigation Architecture

```
Hunt Workspace
│
├─ Skill Panel
│  └─ [⚙️ Build Button]
│     └─ → Skill Build Tab (linked screen 1)
│
├─ [📋 Presets Button]
│  └─ → Presets Dialog (quick access)
│
└─ [🔄 Reset Button]
   └─ → Applies default preset from database
```

### 5.2 Screen Linking Details

#### Link 1: Skill Panel → Skill Build Tab
- **Trigger**: User clicks "⚙️ Build" button in Skill Panel
- **Action**: Switch to Skill Build Tab (existing tab structure)
- **Data Flow**: 
  - Pass current_combo_id to Skill Build Tab
  - Display current combo details in edit mode
  - Allow reordering, adding/removing skills
- **Return**: Save changes back to `AppStateController.skill_slots`
- **Visual**: Tab switches; Skill Panel updates to reflect changes

#### Link 2: Skill Panel → Presets Dialog
- **Trigger**: User clicks "📋 Presets" button in Skill Panel
- **Action**: Open modal dialog showing available presets
- **Data Flow**:
  - Load all presets for current class from database
  - Display default preset (marked with ⭐)
  - Display custom presets (marked with ✏️)
- **Selection**: User chooses preset → apply to skill slots
- **Return**: Close dialog; Skill Panel updates with new combo

#### Link 3: Skill Panel ↔ Skill Management
- **Skill Management Tab** (existing):
  - Shows full skill library with descriptions
  - Skills available for adding to combos
  - Search/filter by type, class requirement
- **Two-way Integration**:
  - Skill Build Tab uses skills from Skill Management
  - Changes to skill properties (damage, cooldown) propagate to active combos
  - If skill is modified (e.g., cooldown changed), affected combos marked as "outdated"

---

## 6. Component Implementation Guide

### 6.1 Tkinter Frame Structure

```python
# Hunt Tab Main Container
hunt_tab = ttk.Frame(notebook, name="hunt_tab")

# Main 2-Column Layout
main_container = ttk.PanedWindow(hunt_tab, orient=tk.HORIZONTAL)
main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

# Column 1 (60%)
col1_container = ttk.Frame(main_container)
col1_paned = ttk.PanedWindow(col1_container, orient=tk.VERTICAL)
col1_paned.pack(fill=tk.BOTH, expand=True)

# Column 1, Row 1 (35%)
col1_row1_container = ttk.Frame(col1_paned)
col1_paned.add(col1_row1_container, weight=35)
# → MonsterTargetPanel implementation

# Column 1, Row 2 (65%)
col1_row2_container = ttk.Frame(col1_paned)
col1_paned.add(col1_row2_container, weight=65)
# → SkillPanel implementation

# Column 2 (40%)
col2_container = ttk.Frame(main_container)
col2_paned = ttk.PanedWindow(col2_container, orient=tk.VERTICAL)
col2_paned.pack(fill=tk.BOTH, expand=True)

# Column 2, Row 1 (50%)
col2_row1_container = ttk.Frame(col2_paned)
col2_paned.add(col2_row1_container, weight=50)
# → TargetStatusPanel implementation

# Column 2, Row 2 (50%)
col2_row2_container = ttk.Frame(col2_paned)
col2_paned.add(col2_row2_container, weight=50)
# → SkillStatsPanel implementation

# Add to main container
main_container.add(col1_container, weight=60)
main_container.add(col2_container, weight=40)
```

### 6.2 Panel Classes (Separation of Concerns)

Each panel should be implemented as a separate class in `ui/panels/`:

```
ui/panels/
├─ monster_target_panel.py
│  └─ class MonsterTargetPanel(ttk.LabelFrame)
│
├─ skill_panel.py
│  └─ class SkillPanel(ttk.LabelFrame)
│
├─ target_status_panel.py
│  └─ class TargetStatusPanel(ttk.LabelFrame)
│
└─ skill_stats_panel.py
   └─ class SkillStatsPanel(ttk.LabelFrame)
```

Each panel class:
- Inherits from `ttk.LabelFrame` or `ttk.Frame`
- Accepts parent container and required dependencies (controllers, services)
- Implements update methods (`update_display()`, `refresh()`)
- Registers callbacks for data changes
- Handles its own DPI scaling

---

## 7. DPI Scaling Strategy

### 7.1 Scale Factor Application

```python
class UIScaler:
    def __init__(self, base_scale_factor: float = 1.0):
        self.scale_factor = base_scale_factor
    
    def scale_dimension(self, value: int) -> int:
        """Scale fixed dimensions (padding, borders)"""
        return int(value * self.scale_factor)
    
    def scale_font_size(self, base_size: int) -> int:
        """Scale font sizes"""
        return max(8, int(base_size * self.scale_factor))
    
    def scale_image(self, image: tk.PhotoImage, width: int, height: int) -> tk.PhotoImage:
        """Scale images proportionally"""
        new_w = int(width * self.scale_factor)
        new_h = int(height * self.scale_factor)
        return image.zoom(new_w // width, new_h // height)
```

### 7.2 Implementation in Panels

```python
class SkillPanel(ttk.LabelFrame):
    def __init__(self, parent, app_state_controller, skill_service, scale_factor=1.0):
        self.scale_factor = scale_factor
        
        # Apply scaling to padding
        padding = (int(10 * scale_factor), int(8 * scale_factor))
        super().__init__(parent, text="⚔️ Active Skills", padding=padding)
        
        # Apply scaling to fonts
        self.title_font = ('Arial', self._scale_font(11), 'bold')
        self.normal_font = ('Arial', self._scale_font(10))
        
        # Build UI with scaled components
        self._build_ui()
    
    def _scale_font(self, base_size: int) -> int:
        return max(8, int(base_size * self.scale_factor))
```

---

## 8. Responsive Layout Behavior

### 8.1 Window Resizing

When user resizes window:
1. Main container adjusts column widths (60% / 40%)
2. Each column adjusts row heights (35%/65% for Col1, 50%/50% for Col2)
3. Panels expand/contract to fill available space
4. Text truncates gracefully with ellipsis if necessary
5. Scrollbars appear in action log (Skill Stats Panel) if needed

### 8.2 Minimum Size Constraints

```python
hunt_tab.grid_propagate(False)
hunt_tab.minsize(
    width=int(800 * scale_factor),
    height=int(600 * scale_factor)
)
```

---

## 9. Visual Design Specifications

### 9.1 Color Scheme

| Element | Color | Purpose |
|---------|-------|---------|
| Active Skill | `#2ECC71` (Green) | Ready to execute |
| Cooldown Skill | `#95A5A6` (Gray) | Waiting for cooldown |
| Buff Effect | `#3498DB` (Blue) | Active buff |
| Debuff Status | `#E74C3C` (Red) | Negative effect |
| Panel Border | `#34495E` (Dark Gray) | Separation |
| Selection Highlight | `#F39C12` (Orange) | User interaction |

### 9.2 Font Hierarchy

```
Panel Title:    11pt Bold (Arial)    #2C3E50
Section Header: 10pt Bold (Arial)    #34495E
Normal Text:    10pt Regular (Arial) #7F8C8D
Data Value:     10pt Bold (Arial)    #2C3E50
Status Text:    9pt Italic (Arial)   #95A5A6
```

### 9.3 Icon Usage

All panel headers use emoji icons for quick visual identification:
- 🎯 Monster Target Panel
- ⚔️ Skill Panel
- 📊 Target Status Panel
- 📈 Skill Performance Panel
- ⚙️ Build / Settings
- 📋 Presets / Configuration
- 🔄 Reset / Refresh

---

## 10. Implementation Checklist

### Phase 1: Layout Foundation (Week 1)
- [ ] Create `ui/panels/` directory structure
- [ ] Implement panel frame structure with PanedWindow
- [ ] Define column/row weight ratios (60/40 and 35/65, 50/50)
- [ ] Test responsive resizing

### Phase 2: Panel Components (Week 2)
- [ ] Implement MonsterTargetPanel class
- [ ] Implement SkillPanel class with dropdowns
- [ ] Implement TargetStatusPanel class with progress bars
- [ ] Implement SkillStatsPanel class with action log

### Phase 3: Data Integration (Week 3)
- [ ] Connect panels to AppStateController
- [ ] Implement update callbacks for skill changes
- [ ] Implement real-time health/status updates from BotManager
- [ ] Implement stats tracking in SkillRuntimeService

### Phase 4: Linking & Navigation (Week 4)
- [ ] Add [⚙️ Build] button → Skill Build Tab navigation
- [ ] Add [📋 Presets] button → Presets Dialog
- [ ] Add [🔄 Reset] button → Apply default preset
- [ ] Implement two-way data sync between panels and Skill Build Tab

### Phase 5: Polish & Testing (Week 5)
- [ ] DPI scaling implementation and testing
- [ ] Visual design refinement (colors, fonts, icons)
- [ ] Responsive layout testing across screen sizes
- [ ] Integration testing with hunt loop
- [ ] User feedback and refinement

---

## 11. User Interaction Workflows (Luồng Thao Tác Người Dùng)

### 11.1 Three-Screen Relationship Architecture (Mối Liên Hệ Ba Màn Hình)

```
┌──────────────────────────────────────────────────────────────────┐
│              Hunt Workspace - User Interaction Flow              │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┐
│  Skill Build Tab            │  Screen 1
│  (Configuration)            │  định cấu hình combo
├─────────────────────────────┤
│ • Edit skill order          │
│ • Save as preset            │
│ • Select lane type          │
│ • Manage class combos       │
└────────────┬────────────────┘
             │ Save/Update
             ▼
    ┌────────────────────────────────────────────┐
    │  Database: skill_presets                   │
    │  (Persistent Storage)                      │
    └────────────────────────────────────────────┘
             │ Load Preset
             │ Apply Combo
             ▼
┌─────────────────────────────┐          ┌──────────────────────────┐
│  Hunt Tab - Skill Panel     │ ◄─────►  │  Presets Dialog          │
│  Screen 2                   │ Load/   │  Screen 3 (Modal)        │
│  (Active During Hunt)       │ Switch  │  (Quick Selection)       │
├─────────────────────────────┤          ├──────────────────────────┤
│                             │          │                          │
│ • Display current combo     │          │ • List all presets       │
│ • Show skill readiness      │          │ • Mark default preset ⭐│
│ • Countdown timer           │          │ • Show custom presets ✏️│
│ • Combo mode indicator      │          │ • Apply button           │
│ • Quick skill switcher      │          │ • Delete custom preset   │
│                             │          │                          │
│ [⚙️ Build] [📋 Presets]   │          │ [Apply] [Delete] [Close]│
│ [🔄 Reset]                 │          │                          │
│ [▶️ START COMBO MODE]      │  ─────►  │                          │
│                             │  Link    │                          │
└─────────────────────────────┘          └──────────────────────────┘

KEY INTERACTIONS:
• User arranges skills in Skill Build Tab → Saves as preset
• Presets stored in database with name, description, skill order
• In Hunt Tab, user can quickly switch presets via Presets Dialog
• Combo Mode activation is explicit via "START COMBO MODE" button
• Visual indicator shows current preset name + mode (Default/Custom)
```

### 11.2 Core User Workflows (Luồng Thao Tác Cốt Lõi)

#### **Workflow 1: First-Time Setup (Cấu Hình Lần Đầu)**

```
START
  │
  ▼
┌──────────────────────────────────────────┐
│ User selects class (Mage, Warrior, etc)  │ 1. Select Class
└──────────────┬───────────────────────────┘
               │
               ▼
       ┌───────────────────────┐
       │ Load Default Preset   │ 2. System loads default
       │ for this class        │    preset from database
       └───────────┬───────────┘
                   │
                   ▼
┌──────────────────────────────────────────┐
│ Skill Panel shows:                       │ 3. Display active combo
│                                          │    to user
│ ✅ Combo Status: DEFAULT                 │    (e.g., "Default - Mage")
│ Skills: [Fireball] [Blizzard]...        │
│ Status: Ready                            │
└──────────────┬───────────────────────────┘
               │
               ▼
       ┌───────────────────────┐
       │ Ready to Hunt         │ 4. User can start
       │                       │    hunting with default
       └───────────────────────┘    combo OR customize


DECISION POINT:
├─ Continue with default → Go to Workflow 3 (Hunt)
└─ Customize → Go to Workflow 2 (Build)
```

#### **Workflow 2: Customize Skills (Tùy Chỉnh Kỹ Năng)**

```
START (from Skill Panel)
  │
  ▼
┌──────────────────────────────────────────────┐
│ User clicks [⚙️ Build] button in Skill Panel│ 1. Open Skill Build Tab
└──────────────┬───────────────────────────────┘
               │
               ▼
       ┌──────────────────────────────────┐
       │ Switch to Skill Build Tab        │ 2. UI switches tabs
       │ Shows current combo              │    Display current
       │ Skill picker below               │    combo for editing
       └──────────────┬───────────────────┘
                      │
                      ▼
        ┌────────────────────────────────┐
        │ User edits combo:              │ 3. Make changes
        │ • Drag to reorder skills       │    • Reorder
        │ • Add new skills from library  │    • Add/remove skills
        │ • Remove unwanted skills       │    • Change lane types
        │ • Save as preset               │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ User decides:                  │ 4. Choice: Save or revert
        │ [Apply Changes] [Cancel]       │
        └────────┬──────────────┬────────┘
                 │              │
         [Apply] │              │ [Cancel]
                 │              │
                 ▼              ▼
        ┌──────────────┐  ┌──────────────┐
        │ Save Preset  │  │ Discard      │
        │ (Database)   │  │ Changes      │
        └──────┬───────┘  └──────┬───────┘
               │                 │
               ▼                 ▼
        ┌──────────────────────────────────┐
        │ Return to Hunt Tab               │ 5. Back to main screen
        │ Skill Panel updates with new     │
        │ combo + preset name              │
        └──────────────────────────────────┘
```

#### **Workflow 3: Active Hunting - Combo Mode (Đi Săn - Chế Độ Combo)**

```
START (Hunt Tab is visible)
  │
  ▼
┌──────────────────────────────────────────────────┐
│ Skill Panel shows current combo                  │ PREREQUISITE:
│                                                  │ • Combo defined
│ Combo Status: DEFAULT                            │ • Skills loaded
│ Skills: [Fireball] [Blizzard] [Lightning]       │ • Ready indicator
│ Status: Ready                                    │
└──────────────┬───────────────────────────────────┘
               │
               ▼
        ┌────────────────────────────────┐
        │ User clicks button:            │ 1. EXPLICIT ACTION:
        │ [▶️ START COMBO MODE]         │    Activate combo mode
        │ (Highlighted, visible button)  │    (Required step!)
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │ System Activates Combo Mode:       │ 2. Status change
        │ • Lock skill selections            │    (prevent accidental
        │ • Start skill sequence execution   │     changes)
        │ • Apply hotkeys (Alt+3 executes)   │
        │ • Update visual indicator          │
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │ Skill Panel displays COMBO MODE    │ 3. VISUAL INDICATOR:
        │ ┌──────────────────────────────┐   │    Show user
        │ │ 🟢 COMBO MODE: ACTIVE        │   │    combo is running
        │ │ Current Skill: Fireball      │   │
        │ │ Next Skill: Blizzard (0.8s)  │   │
        │ │ Status: [EXECUTING]          │   │
        │ │                              │   │
        │ │ Hotkey: Alt+3 to execute     │   │    Show hotkey
        │ │                              │   │    reminder
        │ └──────────────────────────────┘   │
        │                                    │
        │ Skill selector DISABLED            │    Prevent changes
        │ (grayed out/locked)                │    during combo
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │ Alt+3 Hotkey Actions:              │ 4. HOTKEY EXECUTION
        │ ┌──────────────────────────────┐   │    (Can repeat many times)
        │ │ User Press: Alt+3             │   │
        │ │            ↓                  │   │
        │ │ Execute: Fireball             │   │
        │ │ Damage dealt, visual effect   │   │
        │ │            ↓                  │   │
        │ │ Auto advance to next skill    │   │
        │ │ Next Skill: Blizzard (0.8s)  │   │    Timer shows
        │ │            ↓                  │   │    when ready
        │ │ Wait cooldown...              │   │
        │ │            ↓                  │   │
        │ │ User Press: Alt+3 (again)    │   │    Can press
        │ │ Execute: Blizzard             │   │    again when ready
        │ │            ↓                  │   │
        │ │ Loop continues...             │   │
        │ └──────────────────────────────┘   │
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │ User decides to END COMBO MODE     │ 5. End Combo Mode
        │ Click: [⏹️ STOP COMBO MODE]       │    (Explicit action)
        │ OR press Escape key                │
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │ System Deactivates Combo Mode:     │ 6. Return to normal
        │ • Unlock skill selections          │    mode
        │ • Stop skill sequence execution    │
        │ • Clear hotkey bindings            │
        │ • Update visual indicator          │
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │ Skill Panel returns to:            │ 7. Back to normal
        │ ⚪ COMBO MODE: INACTIVE           │    state
        │ Skills: [Fireball] [Blizzard]     │
        │ Status: Ready                      │
        │ Skill selector ENABLED             │
        │ (user can modify skills)           │
        └────────────────────────────────────┘

IMPORTANT NOTES:
✓ Combo Mode activation is EXPLICIT (must click button)
✓ System shows CLEAR VISUAL INDICATOR when active
✓ Hotkey (Alt+3) only works when combo mode is ON
✓ Cannot modify skills while combo mode active
✓ Escape key or button to exit combo mode anytime
```

#### **Workflow 4: Quick Preset Switch (Chuyển Preset Nhanh)**

```
START (During hunt, combo mode active)
  │
  ▼
┌──────────────────────────────────────────────┐
│ User clicks [📋 Presets] in Skill Panel       │ 1. Open Presets Dialog
└──────────────┬───────────────────────────────┘
               │
               ▼
       ┌──────────────────────────────────────┐
       │ Presets Dialog appears (Modal)       │ 2. Show all available
       │                                      │    presets
       │ Current Preset: ✅ Default - Mage   │
       │ Available Presets:                   │
       │ ├─ ⭐ Default - Mage (default)      │    Mark current
       │ ├─ ✏️ Custom - Boss Farm           │    with checkmark
       │ ├─ ✏️ Custom - PvP Build           │
       │ └─ ✏️ Custom - Boss 2-Skip         │
       └──────────────┬──────────────────────┘
                      │
                      ▼
         ┌────────────────────────────────┐
         │ User selects new preset:       │ 3. Selection
         │ (click on "Custom - Boss Farm")│
         └────────────┬───────────────────┘
                      │
                      ▼
         ┌────────────────────────────────┐
         │ Confirm & Apply:               │ 4. Confirmation
         │ [Apply] [Delete] [Cancel]     │    (if needed)
         └────────────┬───────────────────┘
                      │
                  [Apply]
                      │
                      ▼
         ┌────────────────────────────────┐
         │ Load new preset from database  │ 5. Update skills
         │ Update Skill Panel:            │
         │ • Skills changed               │
         │ • Hotkey still active (Alt+3)  │
         │ • Combo mode continues         │
         │ • No need to stop/restart      │
         └────────────┬───────────────────┘
                      │
                      ▼
         ┌────────────────────────────────┐
         │ Presets Dialog closes          │ 6. Back to hunting
         │ Continue hunting with new      │
         │ preset skills                  │
         └────────────────────────────────┘

BENEFIT:
✓ No need to stop combo mode
✓ No need to go to Skill Build Tab
✓ Quick switch between saved presets
✓ Perfect for context switching (boss → farming → PvP)
```

### 11.3 Combo Mode Visual Indicators (Chỉ Báo Trạng Thái Combo)

#### **In Skill Panel (Indicator Location)**

```
┌─────────────────────────────────────────┐
│ ⚔️ Active Skills                         │
├─────────────────────────────────────────┤
│                                         │
│ ┌──────────────────────────────────────┐│
│ │🔴 COMBO MODE: INACTIVE               ││ INACTIVE STATE
│ │(Gray color, red dot)                 ││
│ │                                      ││
│ │ Current Skills:                      ││
│ │ ├─ [Fireball] (Ready)               ││
│ │ ├─ [Blizzard] (Ready)               ││
│ │ └─ [Lightning] (Ready)              ││
│ │                                      ││
│ │ Status: Idle                         ││
│ └──────────────────────────────────────┘│
│                                         │
│  [⚙️ Build] [📋 Presets] [🔄 Reset]   │
│  [▶️ START COMBO MODE] (Big, Green)   │  ◄── Button
│                                         │
└─────────────────────────────────────────┘


         ⬇️ (After clicking "START COMBO MODE")


┌─────────────────────────────────────────┐
│ ⚔️ Active Skills                         │
├─────────────────────────────────────────┤
│                                         │
│ ┌──────────────────────────────────────┐│
│ │🟢 COMBO MODE: ACTIVE                 ││ ACTIVE STATE
│ │(Green color, green dot)              ││
│ │                                      ││
│ │ Current Skill: [Fireball]           ││
│ │ Next Skill: [Blizzard] (0.8s)       ││
│ │ Last Execution: 10.2s ago            ││
│ │                                      ││
│ │ Status: [EXECUTING - Press Alt+3]   ││
│ │ Hotkey Reminder: Alt+3 Ready        ││
│ │                                      ││
│ │ Current Preset: Custom - Boss Farm  ││
│ │ Skills Locked (Editing Disabled)    ││
│ └──────────────────────────────────────┘│
│                                         │
│  [⏹️ STOP COMBO MODE] (Big, Red)      │  ◄── Button changes
│  Preset: [📋 SWITCH] [🔄 RESET]       │
│                                         │
└─────────────────────────────────────────┘
```

#### **Visual State Changes**

```
STATE 1: COMBO MODE INACTIVE (默认状态)
┌─────────────────┐
│ 🔴 Status Dot   │  Red/Gray circle
│ Text: "INACTIVE"│  Gray color
│ Skills: Enabled │  Editable dropdowns
│ Button: "START" │  Green button
│ Preset: Name    │  Readable name
└─────────────────┘
           │
        Click START
           ▼
STATE 2: COMBO MODE ACTIVE (运行中)
┌─────────────────┐
│ 🟢 Status Dot   │  Green circle
│ Text: "ACTIVE"  │  Green color
│ Skills: LOCKED  │  Grayed out, disabled
│ Button: "STOP"  │  Red button
│ Hotkey: Alt+3   │  Highlighted reminder
│ Timer: Countdown│  Shows next skill timing
│ Preset: Locked  │  Cannot change skills
└─────────────────┘
```

#### **Color Coding Reference**

```
COMBO MODE INDICATOR COLORS:
├─ 🔴 Red/Gray (Inactive)     → Combo mode OFF, can edit
├─ 🟢 Green (Active)          → Combo mode ON, locked
├─ 🟡 Yellow (Cooldown)       → Waiting for skill ready
├─ 🟠 Orange (Warning)        → Something needs attention
└─ ⚪ White (Ready)           → All systems ready

STATUS TEXT COLORS:
├─ Gray text (Inactive)       → Default/disabled state
├─ Green text (Ready/Active)  → Ready or currently running
├─ Orange text (Waiting)      → Countdown/cooldown active
└─ Red text (Error/Warning)   → Problem detected

SKILL READINESS:
├─ [✅ Ready]    → Green badge, can execute
├─ [⏱️ Cooldown] → Orange badge, timer shows when ready
└─ [❌ Locked]   → Gray badge, disabled during combo mode
```

### 11.4 Relationship Between Three Screens (Mối Liên Hệ Ba Màn Hình)

#### **Screen 1 → Screen 2 Relationship (Skill Build Tab → Hunt Tab)**

```
Skill Build Tab (Configuration)
│
├─ User creates/edits combo
├─ Saves as preset (with name, description)
├─ Stores in database (skill_presets table)
│
└─► Hunt Tab (Active Use)
    │
    ├─ Loads saved preset
    ├─ Displays in Skill Panel
    ├─ Shows as "Current Preset: [Name]"
    │
    └─► User clicks "START COMBO MODE"
        ├─ Activates skill sequence
        ├─ Locks skill selections
        ├─ Enables Alt+3 hotkey
        └─ Shows 🟢 COMBO MODE: ACTIVE indicator
```

#### **Screen 2 ↔ Screen 3 Relationship (Hunt Tab ↔ Presets Dialog)**

```
Hunt Tab - Skill Panel
│
├─ Shows current preset name
├─ Displays active combo skills
├─ Shows combo mode status
│
├─► User clicks [📋 Presets]
│   │
│   └─► Presets Dialog opens (Modal)
│       │
│       ├─ Lists all presets for current class
│       ├─ Marks current preset with ✅
│       ├─ Shows default with ⭐
│       ├─ Shows custom with ✏️
│       │
│       ├─► User selects different preset
│       │   │
│       │   └─► Database loads new preset
│       │       │
│       │       └─► Hunt Tab updates
│       │           ├─ New skills displayed
│       │           ├─ Combo continues with new skills
│       │           ├─ No need to stop combo mode
│       │           └─ Instant preset switch
│       │
│       └─► User closes dialog
│           └─► Return to Hunt Tab
│
└─► Combo mode remains active
    (Skills updated, hotkey still works)
```

#### **Three-Screen Workflow Summary**

```
┌────────────────────────────────────────────────────────┐
│          Complete User Journey                         │
├────────────────────────────────────────────────────────┤
│                                                        │
│ 1. SETUP (One-time or before each hunt)               │
│    Skill Build Tab ──────► Create/Edit Combo          │
│                 │                                      │
│                 └──────► Save as Preset (Database)    │
│                                                        │
│ 2. HUNT PREPARATION (Load hunt screen)                │
│    Hunt Tab ──────► Skill Panel shows preset          │
│           │                                            │
│           └──────► User reviews combo                 │
│                                                        │
│ 3. HUNT START (Explicit combo activation)             │
│    Skill Panel ──────► Click [▶️ START COMBO MODE]   │
│                 │                                      │
│                 └──────► 🟢 ACTIVE indicator shown    │
│                                                        │
│ 4. HUNTING (Flexible preset switching)                │
│    Hunt Tab ──────► Alt+3 (hotkey) executes combo     │
│           │                                            │
│           ├──────► [📋 Presets] → Switch quickly      │
│           │                                            │
│           └──────► Combo continues with new skills    │
│                                                        │
│ 5. HUNT END (Stop combo mode)                         │
│    Skill Panel ──────► Click [⏹️ STOP COMBO MODE]    │
│                 │                                      │
│                 └──────► 🔴 INACTIVE indicator shown  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 12. Migration Path

### From Current Layout to New Layout

**Current State**:
- Hunt Tab has skill list, monster display, status scattered
- No clear panel organization

**Migration Steps**:
1. Extract existing components into separate panel classes
2. Create new frame structure (Column 1/2, Row 1/2)
3. Move components to appropriate panels
4. Update data binding to new panel locations
5. Add inter-panel communication (callbacks)
6. Test and validate all functionality

**No Breaking Changes**:
- Existing logic remains in AppStateController
- Existing data structures (skill_slots, etc.) unchanged
- Only UI presentation layer modified

---

## 12. Accessibility Considerations

- Tab order: Monster Target → Skill Panel → Presets → Build → Status → Stats
- Keyboard shortcuts: Alt+B (Build), Alt+P (Presets), Alt+R (Reset)
- High contrast mode support: Use `tk.SystemButtonFace` for system colors
- Screen reader compatibility: All interactive elements have labels/descriptions

---

## 13. Three-Screen Architecture Reference

For comprehensive specification of the three main screens (Combo Panel, Build Skills Tab, CRUD Skill Tab), including:

- **SCREEN 1: Combo Panel** (Section in Hunt Tab)
  - Display & control active skill preset
  - Hotkey assignment UI
  - Combo mode status indicator & Start/Stop button
  - Cooldown tracking and skill status display
  - See: WORKSPACE-REDESIGN-LOGIC-DESIGN.md § 11.2

- **SCREEN 2: Skill Build Tab** (Separate tab)
  - Create/edit skill presets per class
  - Configure attack_combo and buff_lane slots
  - Skill picker with search/filter
  - Save/load presets from database
  - See: WORKSPACE-REDESIGN-LOGIC-DESIGN.md § 11.3

- **SCREEN 3: CRUD Skill Tab** (Separate tab)
  - Manage individual skill definitions
  - Search/filter skill library
  - Create new skills
  - Edit skill properties
  - Delete skills (with warnings for active presets)
  - See: WORKSPACE-REDESIGN-LOGIC-DESIGN.md § 11.4

**Cross-Screen Integration**:
- Data flows from CRUD Tab (skill creation) → Build Tab (preset definition) → Combo Panel (execution)
- State synchronized across screens via database and AppStateController
- Error handling for skill modifications affecting active presets
- See: WORKSPACE-REDESIGN-LOGIC-DESIGN.md § 11.5

---

## Appendix A: Related Documents

- **WORKSPACE-REDESIGN-LOGIC-DESIGN.md** - Data model, state management, preset system, 3-screen specification
- **UX4.2-AUTO-FIX-PROMPT.md** - Technical fixes for current implementation
- **UX4.2-CORRECTED-GUIDELINE.md** - Original UX4.2 specification

