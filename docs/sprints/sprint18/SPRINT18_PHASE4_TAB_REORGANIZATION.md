# Sprint 18 Phase 4: Tab Reorganization

## Goal
Reorganize app UI into logical tabs for better user experience and workflow clarity.

## Current State
- **Single Tab:** "Hunt" tab contains everything
- **Problems:**
  - Overwhelming for beginners (too many controls in one place)
  - Hard to find settings (scattered across one long page)
  - No clear workflow separation (setup vs execution vs monitoring)
  - Managers in separate windows (Monster/Skill managers)

## Target State
**4 Main Tabs:**
1. **Hunt Tab** - Active hunting controls (streamlined)
2. **Setup Tab** - Configuration and libraries (monsters, skills, settings)
3. **Stats Tab** - Runtime statistics and performance monitoring
4. **Help Tab** - Documentation, tutorials, about

## Design Principles
1. **Workflow-Based:** Group by user workflow stage (setup → execute → monitor → learn)
2. **Progressive Disclosure:** Hide advanced features in appropriate tabs
3. **Context Retention:** Keep frequently used controls accessible
4. **Consistency:** Same look-and-feel across all tabs

---

## Phase 4 Task Breakdown

### Task #1: Create Tab Structure (~50 lines)
**Goal:** Set up 4-tab notebook with placeholders

**Implementation:**
```python
# In _build_ui()
nb = ttk.Notebook(self)
nb.pack(fill='both', expand=True)

# Create 4 tabs
tab_hunt = tk.Frame(nb, padx=12, pady=12)
tab_setup = tk.Frame(nb, padx=12, pady=12)
tab_stats = tk.Frame(nb, padx=12, pady=12)
tab_help = tk.Frame(nb, padx=12, pady=12)

nb.add(tab_hunt, text=self._t('tab_hunt'))
nb.add(tab_setup, text=self._t('tab_setup'))
nb.add(tab_stats, text=self._t('tab_stats'))
nb.add(tab_help, text=self._t('tab_help'))

self._build_hunt_tab(tab_hunt)
self._build_setup_tab(tab_setup)
self._build_stats_tab(tab_stats)
self._build_help_tab(tab_help)
```

**Translations:**
- EN: `tab_setup`, `tab_stats`, `tab_help`
- VI: `Thiết lập`, `Thống kê`, `Trợ giúp`

**Files:** app_gui.py lines ~945-960
**Status:** Not started

---

### Task #2: Refactor Hunt Tab (~80 lines)
**Goal:** Streamline Hunt tab to ONLY active controls

**What Stays in Hunt Tab:**
- Window selection (Find Windows, dropdown, Bring to Front)
- Monster rotation list (with checkboxes, mode dropdown)
- Skill slots (6 slots with checkboxes)
- Start/Stop buttons
- Status display

**What Moves to Setup Tab:**
- UI Mode dropdown (Beginner/Intermediate/Advanced)
- Attack keys textbox (advanced override)
- Advanced timing controls (intervals, timeouts)
- Window bounds display/clear
- Template threshold

**What Moves to Stats Tab:**
- Hunt statistics (runtime, kills, exp/hr)
- Performance metrics (CPU, FPS)

**Implementation:**
```python
def _build_hunt_tab(self, parent):
    # Section 1: Window Selection
    # Section 2: Monster Rotation (existing)
    # Section 3: Skill Slots (existing)
    # Section 4: Start/Stop Controls
    # Section 5: Status Display
    # Remove: Advanced controls → move to Setup
```

**Files:** app_gui.py `_build_hunt_tab()` lines ~951-1600
**Status:** Not started

---

### Task #3: Create Setup Tab (~100 lines)
**Goal:** Centralize all configuration and library management

**Setup Tab Sections:**

**Section 1: Configuration Mode**
- UI Mode dropdown: Beginner / Intermediate / Advanced
- Description label explaining each mode
- Apply button to rebuild UI

**Section 2: Monster Library**
- Button: "Open Monster Manager"
- Quick stats: X monsters, Y templates total
- Last modified date

**Section 3: Skill Library**
- Button: "Open Skills Manager"
- Quick stats: X skills configured
- Last modified date

**Section 4: Advanced Hunt Settings** (Intermediate+)
- Attack keys override textbox
- Template matching:
  - Threshold slider (0.0 - 1.0)
  - Grayscale checkbox
  - Region override (L, T, W, H)
- Timing controls:
  - Search interval (s)
  - Attack interval (s)
  - Lost timeout (s)
  - Target cycle delay (s)

**Section 5: Window Settings** (Advanced)
- Window bounds display
- Clear bounds button
- Bring to front each cycle checkbox
- Auto-minimize GUI checkbox

**Implementation:**
```python
def _build_setup_tab(self, parent):
    # LabelFrame: Configuration Mode
    # LabelFrame: Libraries
    # LabelFrame: Advanced Settings (Intermediate+)
    # LabelFrame: Window Settings (Advanced)
```

**Files:** app_gui.py new method `_build_setup_tab()`
**Status:** Not started

---

### Task #4: Create Stats Tab (~60 lines)
**Goal:** Display runtime statistics and performance metrics

**Stats Tab Sections:**

**Section 1: Hunt Statistics**
- Runtime duration (HH:MM:SS)
- Monsters hunted (count)
- Average kill time
- Exp/hour estimate
- Skills cast (count per skill)

**Section 2: Performance Metrics**
- Template matching FPS
- CPU usage (%)
- Memory usage (MB)
- Screenshot latency (ms)

**Section 3: Rotation History** (if multi-monster)
- Current monster
- Previous monsters
- Time spent on each
- Rotation efficiency

**Section 4: Controls**
- Reset stats button
- Export stats to CSV button
- Refresh rate dropdown (1s / 5s / 10s)

**Implementation:**
```python
def _build_stats_tab(self, parent):
    # LabelFrame: Hunt Statistics
    self.stats_runtime_var = tk.StringVar(value='00:00:00')
    self.stats_kills_var = tk.StringVar(value='0')
    # ... labels to display stats
    
    # LabelFrame: Performance Metrics
    self.stats_fps_var = tk.StringVar(value='--')
    self.stats_cpu_var = tk.StringVar(value='--')
    # ... labels
    
    # Update stats periodically
    self.after(1000, self._update_stats_display)

def _update_stats_display(self):
    if self.hunt_running:
        # Calculate and update stats
        runtime = time.time() - self.hunt_start_time
        self.stats_runtime_var.set(format_duration(runtime))
    self.after(1000, self._update_stats_display)
```

**Files:** app_gui.py new method `_build_stats_tab()`
**Status:** Not started

---

### Task #5: Create Help Tab (~50 lines)
**Goal:** Provide in-app documentation and help resources

**Help Tab Sections:**

**Section 1: Quick Start Guide**
- Step-by-step setup instructions
- Screenshots or diagrams (optional)
- Links to external documentation

**Section 2: Keyboard Shortcuts**
- F9: Stop hunt (global)
- ESC: Stop hunt (in-window)
- Other shortcuts listed

**Section 3: Troubleshooting**
- Common issues and solutions
- FAQ links
- Contact/support information

**Section 4: About**
- App name and version
- Author/contributors
- License information
- GitHub repository link

**Implementation:**
```python
def _build_help_tab(self, parent):
    # LabelFrame: Quick Start
    help_text = """
    1. Click 'Find Windows' to list game windows
    2. Select your game window from dropdown
    3. Configure monsters and skills in Setup tab
    4. Click 'Start Hunt' to begin
    5. Press F9 to stop anytime
    """
    tk.Label(parent, text=help_text, justify='left').pack()
    
    # LabelFrame: Keyboard Shortcuts
    # LabelFrame: Troubleshooting
    # LabelFrame: About
```

**Files:** app_gui.py new method `_build_help_tab()`
**Status:** Not started

---

### Task #6: Add Translations (~20 lines)
**Goal:** Translate all new tab labels and content

**New Translation Keys:**

**English:**
```python
'tab_setup': 'Setup',
'tab_stats': 'Stats',
'tab_help': 'Help',
'setup_mode': 'Configuration Mode',
'setup_mode_desc': 'Select UI complexity level',
'setup_libraries': 'Libraries',
'setup_advanced': 'Advanced Hunt Settings',
'setup_window': 'Window Settings',
'stats_hunt': 'Hunt Statistics',
'stats_performance': 'Performance Metrics',
'stats_rotation': 'Rotation History',
'stats_runtime': 'Runtime',
'stats_kills': 'Monsters Hunted',
'stats_reset': 'Reset Statistics',
'help_quickstart': 'Quick Start Guide',
'help_shortcuts': 'Keyboard Shortcuts',
'help_troubleshooting': 'Troubleshooting',
'help_about': 'About',
```

**Vietnamese:**
```python
'tab_setup': 'Thiết lập',
'tab_stats': 'Thống kê',
'tab_help': 'Trợ giúp',
'setup_mode': 'Chế độ cấu hình',
'setup_mode_desc': 'Chọn mức độ phức tạp giao diện',
'setup_libraries': 'Thư viện',
'setup_advanced': 'Cài đặt săn nâng cao',
'setup_window': 'Cài đặt cửa sổ',
'stats_hunt': 'Thống kê săn',
'stats_performance': 'Hiệu năng',
'stats_rotation': 'Lịch sử luân chuyển',
'stats_runtime': 'Thời gian chạy',
'stats_kills': 'Quái vật đã săn',
'stats_reset': 'Reset thống kê',
'help_quickstart': 'Hướng dẫn nhanh',
'help_shortcuts': 'Phím tắt',
'help_troubleshooting': 'Xử lý lỗi',
'help_about': 'Thông tin',
```

**Files:** app_gui.py lines ~70-80 (EN), ~257-267 (VI)
**Status:** Not started

---

## Benefits

**For Beginners:**
- ✅ Hunt tab is simple and focused (just start/stop)
- ✅ Setup tab clearly labeled for configuration
- ✅ Help tab provides guidance without leaving app

**For Intermediate Users:**
- ✅ Setup tab shows advanced options when ready
- ✅ Stats tab helps optimize hunting efficiency
- ✅ Clear separation of concerns

**For Advanced Users:**
- ✅ All settings accessible in Setup tab
- ✅ Stats tab provides detailed metrics
- ✅ Hunt tab stays clean for monitoring

**General:**
- ✅ Logical workflow: Setup → Hunt → Stats → Help
- ✅ Reduces cognitive load (less overwhelming)
- ✅ Better discoverability (clear labels)
- ✅ Consistent with modern app design patterns

---

## Testing Checklist

**Tab Navigation:**
- [ ] All 4 tabs visible
- [ ] Tab labels translated correctly (EN/VI)
- [ ] Clicking tabs switches content
- [ ] Tab order: Hunt → Setup → Stats → Help

**Hunt Tab:**
- [ ] Window selection works
- [ ] Monster rotation displays correctly
- [ ] Skill slots functional
- [ ] Start/Stop buttons work
- [ ] Status updates correctly

**Setup Tab:**
- [ ] UI mode dropdown works
- [ ] Monster/Skill manager buttons open windows
- [ ] Advanced settings save correctly
- [ ] Window settings apply correctly

**Stats Tab:**
- [ ] Statistics display during hunt
- [ ] Refresh rate configurable
- [ ] Reset button clears stats
- [ ] Export to CSV works (future)

**Help Tab:**
- [ ] Quick start guide readable
- [ ] Keyboard shortcuts listed
- [ ] About section shows version

**Translations:**
- [ ] Switch to English → all tabs in English
- [ ] Switch to Vietnamese → all tabs in Vietnamese
- [ ] No missing translation keys

---

## Implementation Plan

**Sprint 18 Phase 4 - 5 days:**

**Day 1: Tab Structure + Translations**
- Task #1: Create 4-tab structure (50 lines)
- Task #6: Add translations (20 lines)
- Test: Tab navigation works

**Day 2: Refactor Hunt Tab**
- Task #2: Streamline Hunt tab (80 lines)
- Move controls to variables for later migration
- Test: Hunt tab still functional

**Day 3: Create Setup Tab**
- Task #3: Build Setup tab (100 lines)
- Move controls from Hunt tab
- Test: Setup tab works, settings apply

**Day 4: Create Stats + Help Tabs**
- Task #4: Build Stats tab (60 lines)
- Task #5: Build Help tab (50 lines)
- Test: All tabs functional

**Day 5: Integration + Polish**
- Connect stats tracking to hunt loop
- Polish UI spacing and layout
- Full regression testing
- Documentation update

**Total Estimated Lines:** ~360 lines
**Risk:** Low (mostly UI reorganization, no logic changes)

---

## Success Criteria

**Functional:**
- ✅ 4 tabs visible and functional
- ✅ All controls work in new locations
- ✅ Hunt functionality unchanged (backward compatible)
- ✅ Settings persist correctly

**UX:**
- ✅ Hunt tab is simpler and focused
- ✅ Setup tab is discoverable
- ✅ Stats tab provides value
- ✅ Help tab reduces support burden

**Quality:**
- ✅ No syntax errors
- ✅ All translations complete
- ✅ Consistent styling across tabs
- ✅ Tested on Windows 11

---

## Files to Modify

**app_gui.py (~360 lines total):**
- `_build_ui()`: Add 3 new tabs (30 lines)
- `_build_hunt_tab()`: Refactor, remove advanced controls (80 lines)
- `_build_setup_tab()`: New method (100 lines)
- `_build_stats_tab()`: New method (60 lines)
- `_build_help_tab()`: New method (50 lines)
- Translations: Add 20 new keys (EN/VI = 40 lines)

**No changes to:**
- auto_hunt.py (logic unchanged)
- hunt_config.json (schema unchanged)
- monsters.json, skills.json (unchanged)

---

## Status

**Sprint 18 Phase 4:** 🔜 **READY TO START**  
**Estimated Effort:** 5 days, ~360 lines  
**Risk Level:** 🟢 Low (UI only, no logic changes)  
**Dependencies:** None (standalone UI refactor)

---

*Date: October 18, 2025*  
*Phase: Sprint 18 - Phase 4 Planning*  
*Next Action: Start Task #1 - Create Tab Structure*
