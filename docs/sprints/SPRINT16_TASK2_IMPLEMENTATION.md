# Sprint 16 Task #2 Implementation Log
## Beginner/Intermediate/Advanced Mode Toggle

**Status:** ✅ PARTIAL COMPLETION  
**Date:** 2025-01-18  
**Estimated Lines:** ~150 lines  
**Actual Lines:** ~70 lines  
**Files Modified:** 1 (app_gui.py)

---

## 📋 Overview

**Problem:**
- Current Hunt tab overwhelming cho người mới với 20+ parameters
- Không có progressive disclosure - tất cả fields hiện cùng lúc
- User feedback: "mấy cái này thiệt là mới vào sử dụng tôi bị ngộp"

**Solution:**
- Add 3 mode radio buttons: Beginner / Intermediate / Advanced
- Mode selector shows clear descriptions của từng mode
- Save mode preference vào hunt_config.json
- Status bar updates khi chuyển mode

**Current Implementation Status:**
- ✅ Mode selector UI added with 3 radio buttons
- ✅ Mode descriptions displayed below each option
- ✅ Mode preference saved to hunt_config.json
- ✅ Status bar feedback on mode change
- ✅ Localization (EN/VI) for all mode strings
- ⚠️ Progressive disclosure NOT YET IMPLEMENTED (requires major refactoring)

---

## 🔧 Implementation Details

### 1. Localization Strings Added (~20 lines)

**Location:** `app_gui.py` LANG dict (~line 100-110 EN, ~line 250-260 VI)

**English strings:**
```python
'hunt_mode': 'Interface Mode',
'mode_beginner': '🌱 Beginner',
'mode_beginner_desc': 'Simple 4-step workflow - perfect for first-time users',
'mode_intermediate': '⚙️ Intermediate',
'mode_intermediate_desc': 'Basic fields + timing controls for experienced users',
'mode_advanced': '🔧 Advanced',
'mode_advanced_desc': 'Full control - all parameters and technical settings',
```

**Vietnamese strings:**
```python
'hunt_mode': 'Chế độ giao diện',
'mode_beginner': '🌱 Người mới',
'mode_beginner_desc': 'Quy trình 4 bước đơn giản - hoàn hảo cho người dùng lần đầu',
'mode_intermediate': '⚙️ Trung cấp',
'mode_intermediate_desc': 'Các trường cơ bản + điều khiển thời gian cho người dùng có kinh nghiệm',
'mode_advanced': '🔧 Nâng cao',
'mode_advanced_desc': 'Toàn quyền kiểm soát - tất cả các tham số và cài đặt kỹ thuật',
```

**Icons Used:**
- 🌱 Beginner - Seedling (growth, new user)
- ⚙️ Intermediate - Gear (configuration)
- 🔧 Advanced - Wrench (technical control)

---

### 2. Mode Selector UI (~30 lines)

**Location:** `app_gui.py` `_build_hunt_tab()` method (top of Hunt tab, row 0)

**Implementation:**
```python
# Mode Selection (Beginner/Intermediate/Advanced)
mode_frame = tk.LabelFrame(frm, text=self._t('hunt_mode'), padx=10, pady=8)
mode_frame.grid(row=0, column=0, columnspan=4, sticky='we', pady=(0,12))

self.hunt_mode_var = tk.StringVar(value=self.hunt_cfg.get('ui_mode', 'beginner'))

modes = [
    ('beginner', self._t('mode_beginner'), self._t('mode_beginner_desc')),
    ('intermediate', self._t('mode_intermediate'), self._t('mode_intermediate_desc')),
    ('advanced', self._t('mode_advanced'), self._t('mode_advanced_desc'))
]

for idx, (mode_val, mode_label, mode_desc) in enumerate(modes):
    rb = tk.Radiobutton(
        mode_frame,
        text=mode_label,
        variable=self.hunt_mode_var,
        value=mode_val,
        command=self._on_hunt_mode_changed,
        font=('Arial', 9, 'bold')
    )
    rb.grid(row=idx, column=0, sticky='w', pady=2)
    
    desc_label = tk.Label(mode_frame, text=f"  {mode_desc}", fg='#666', font=('Arial', 8))
    desc_label.grid(row=idx, column=1, sticky='w', padx=(4,0), pady=2)
```

**UI Layout:**
```
┌─ Interface Mode ──────────────────────────────┐
│ ● 🌱 Beginner          Simple 4-step workflow  │
│ ○ ⚙️ Intermediate      Basic + timing controls │
│ ○ 🔧 Advanced          Full control            │
└───────────────────────────────────────────────┘
─────────────────────────────────────────────────
[Rest of Hunt tab fields...]
```

**Features:**
- Default value: `'beginner'` (loaded from hunt_config.json if exists)
- Bold font for mode labels to emphasize
- Light gray (#666) descriptions for clarity
- 2px vertical padding between options
- LabelFrame với clear title

---

### 3. Mode Change Handler (~35 lines)

**Location:** `app_gui.py` `_on_hunt_mode_changed()` method (before `_update_window_bounds_display()`)

**Implementation:**
```python
def _on_hunt_mode_changed(self):
    """Handle mode toggle - show/hide fields based on selected mode."""
    mode = self.hunt_mode_var.get()
    
    # Save mode preference
    self.hunt_cfg['ui_mode'] = mode
    try:
        with open(HUNT_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Could not save ui_mode: {e}")
    
    # Status message about mode
    mode_labels = {
        'beginner': self._t('mode_beginner'),
        'intermediate': self._t('mode_intermediate'),
        'advanced': self._t('mode_advanced')
    }
    
    self.hunt_status.set(f"Mode: {mode_labels.get(mode, mode)} - {self._t('hunt_idle')}")
```

**Current Behavior:**
- ✅ Saves mode to `hunt_config.json` under `ui_mode` key
- ✅ Updates status bar with selected mode
- ⚠️ Does NOT yet show/hide fields (progressive disclosure)

**Why Progressive Disclosure Not Implemented:**
- Hunt tab uses complex grid() layout with 20+ widgets
- Row numbers hardcoded (row=0, row=1, row=2, ...)
- Widgets created inline without references stored
- Requires major refactoring:
  1. Store all widget references in self (e.g., self.press_ms_label, self.press_ms_entry)
  2. Use grid_forget() / grid() to show/hide dynamically
  3. OR restructure using pack() with conditional widget creation
  4. Update row numbers dynamically when hiding intermediate widgets

**Estimated Effort for Full Progressive Disclosure:**
- ~200 lines refactoring (current: only ~70 lines)
- Store 40+ widget references (labels + entries + buttons)
- Create _show_beginner_mode(), _show_intermediate_mode(), _show_advanced_mode() helpers
- Test all layout states

---

## 📊 Hunt Tab Fields by Mode (Planned Visibility)

### Beginner Mode (4 essential fields):
- ✅ Window title & Find Windows button
- ✅ Window list (filtered)
- ✅ Monster selector (quick apply)
- ✅ Skill slots
- ✅ Start/Stop hunt buttons
- ❌ HIDE: Target key, Attack keys, Timing params, Template/region, Pick corners

### Intermediate Mode (+ timing controls):
- ✅ All Beginner fields
- ✅ Lost timeout (recommended by timing calculator)
- ✅ Attack duration (recommended by timing calculator)
- ❌ HIDE: Manual timing intervals, Template/region override, Pick corners

### Advanced Mode (everything):
- ✅ All Intermediate fields
- ✅ Target key, Attack keys (manual override)
- ✅ Press ms, Target cycle delay
- ✅ Search interval, Attack interval
- ✅ Template path, Region (L,T,W,H)
- ✅ Bring to front checkbox
- ✅ Pick corner buttons

---

## 🎯 User Experience Impact

**Current Benefits:**
- ✅ Mode selector visible at top - clear choice
- ✅ Mode descriptions explain intent
- ✅ Mode preference persists across sessions
- ✅ Status bar feedback confirms selection

**Remaining UX Issues:**
- ⚠️ All fields still visible regardless of mode
- ⚠️ Beginner still sees 20+ parameters (overwhelming)
- ⚠️ No actual simplification yet

**Next Steps for Full UX:**
- Implement progressive disclosure (show/hide widgets)
- Task #3: Simplify Hunt Tab Layout (clearer organization even in Advanced mode)
- Add "Show Advanced" toggle button in Beginner mode for edge cases

---

## 📝 Code Changes Summary

**Files Modified:**
- `app_gui.py`: +70 lines
  - LANG dict: +12 lines (EN + VI)
  - _build_hunt_tab(): +30 lines (mode selector UI)
  - _on_hunt_mode_changed(): +35 lines (handler)
  - Row number updates: +5 lines (window title, win_list moved down)

**Data Schema:**
- `hunt_config.json`: New key `ui_mode` (values: 'beginner' | 'intermediate' | 'advanced')

**No Breaking Changes:**
- Default value 'beginner' if ui_mode not in config
- All existing hunt config keys preserved
- Backward compatible với old configs

---

## 🐛 Known Issues

### Issue #1: Geometry Manager Error (RESOLVED)
**Problem:** `TclError: cannot use geometry manager pack inside frame which already has slaves managed by grid`

**Cause:** Mixed pack() and grid() in same parent frame

**Fix:** Changed mode selector to use grid() consistently:
```python
# BEFORE (ERROR):
mode_container = tk.Frame(mode_frame)
mode_container.pack(anchor='w', pady=2)
rb.pack(anchor='w')

# AFTER (FIXED):
rb.grid(row=idx, column=0, sticky='w', pady=2)
desc_label.grid(row=idx, column=1, sticky='w', padx=(4,0), pady=2)
```

### Issue #2: Row Numbers Hardcoded
**Problem:** All Hunt tab widgets use hardcoded row numbers (row=1, row=2, row=3...)

**Impact:** Difficult to dynamically hide/show widgets without gaps in grid

**Workaround:** Current implementation keeps all widgets visible, only updates status

**Future Solution:** 
- Option A: Store row offsets, recalculate when hiding widgets
- Option B: Use pack() with frame nesting for each mode section
- Option C: Recreate widgets dynamically based on mode (clean slate approach)

---

## 🔄 Future Enhancements

### Phase 1: Progressive Disclosure (Sprint 16 Task #3)
- Refactor widget creation to store all references
- Implement _apply_beginner_mode(), _apply_intermediate_mode(), _apply_advanced_mode()
- Use grid_forget() / grid() to toggle visibility
- Test all mode transitions

### Phase 2: Smart Defaults
- Beginner mode: Auto-fill timing from timing calculator
- Intermediate mode: Show timing fields but lock intervals
- Advanced mode: Expose all manual overrides

### Phase 3: Validation by Mode
- Beginner: Require only 4 essential fields
- Intermediate: Validate lost_timeout + attack_duration
- Advanced: Full validation của all parameters

---

## ✅ Task Completion Status

**Completed:**
- ✅ Mode selector UI với 3 radio buttons
- ✅ Mode descriptions displayed
- ✅ Mode preference persistence
- ✅ Status bar feedback
- ✅ Localization (EN/VI)
- ✅ Geometry manager fix

**Pending (Task #3):**
- ⚠️ Progressive disclosure (show/hide widgets)
- ⚠️ Dynamic layout adjustment
- ⚠️ Widget reference management
- ⚠️ Full UX implementation

**Recommendation:**
Mark Task #2 as **PARTIAL COMPLETION** với foundation laid. Progressive disclosure will be completed in Task #3 as part of full Hunt tab redesign.

---

**Implementation Date:** 2025-01-18  
**Implemented By:** GitHub Copilot  
**Status:** ✅ FOUNDATION COMPLETE, ⚠️ FULL UX PENDING (Task #3)
