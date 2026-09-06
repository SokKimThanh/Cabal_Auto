# 🔧 LEGACY UISTYLE MIGRATION — Complete Removal & UIStyleV2 Adoption

**Mục đích**: Xóa dứt điểm UIStyle cũ, nâng cấp UIStyleV2 làm nguồn duy nhất, cập nhật toàn bộ app  
**Ngày tạo**: 2026-09-06  
**Trạng thái**: Ready for Execution  
**Thời gian ước tính**: 3-4 ngày

---

## 📊 Tình Hình Hiện Tại

### Files Đang Import UIStyle Cũ (38 files)

**Core App Files** (8 files):
- `dialogs/display_settings.py` — Import UIStyle
- `dialogs/monster_edit.py` — Import UIStyle
- `dialogs/monster_picker.py` — Import UIStyle
- `ui/utils/overlay_settings.py` — Import UIStyle
- `ui/views/activity_logs_frame.py` — Import UIStyle
- `ui/views/monster_manager_frame.py` — Import UIStyle
- `ui/windows/overlay_window.py` — Import UIStyle
- `ui/windows/setup_wizard_vision.py` — Import UIStyle

**Window Manager Files** (2 files):
- `ui/windows/library_manager.py` — Heavy UIStyle usage (70+ lines)
- `ui/windows/monster_manager_win.py` — Heavy UIStyle usage (50+ lines)
- `ui/windows/setup_wizard.py` — Heavy UIStyle usage (80+ lines)

**TTK Theme File** (1 file):
- `ui/theme/ttk_theme.py` — Uses UIStyle.THEME_* constants (60+ references)

**Documentation & Scripts** (27 files):
- `.jules/prompts/ui-main-screen-cleanup/` — References UIStyle constants
- `docs/sprints/sprint26-combat-refactor/` — References UIStyle
- `docs/` — Multiple docs referencing old UIStyle

### Vấn Đề Hiện Tại

| Vấn đề | Ảnh hưởng | Mức độ |
|--------|----------|-------|
| **Hai design system chạy song song** | Confusing, maintenance nightmare | 🔴 CRITICAL |
| **UIStyle cũ = light theme colors** | Không phù hợp dark theme hiện tại | 🔴 CRITICAL |
| **Font sizes nhỏ quá** (UIStyle: 8px) | Khó đọc so với UIStyleV2 (10px+) | 🟡 HIGH |
| **Naming conventions khác** | THEME_BG_APP vs BG_BASE | 🟡 HIGH |
| **Resolve_font_family có 2 version** | Potential bugs, code duplication | 🟠 MEDIUM |
| **ttk_theme.py dùng THEME_* constants** | Sẽ break nếu xóa UIStyle.py | 🟡 HIGH |

---

## 🎯 Target State (UIStyleV2 Complete)

### Required Constants in UIStyleV2

#### 1. Colors (Semantic Naming)
✅ **Backgrounds**
```python
BG_BASE = "#0f0f0f"          # Main app background
BG_SURFACE = "#1a1a1a"       # Panels, cards
BG_ELEVATED = "#111111"      # Sidebar, header
BG_SUBTLE = "#0a0a0a"        # Status bar
```

✅ **Text**
```python
TEXT_PRIMARY = "#d1d5db"      # Main content
TEXT_SECONDARY = "#9ca3af"    # Secondary
TEXT_MUTED = "#6b7280"        # Tertiary
TEXT_SUBTLE = "#374151"       # Placeholders
```

✅ **Accents**
```python
ACCENT_GREEN = "#4ade80"      # Success, active
ACCENT_GREEN_BG = "#1f2d1f"   # Green background tint
ACCENT_AMBER = "#f59e0b"      # Warning, waiting
ACCENT_BLUE = "#38bdf8"       # Info, running
DANGER = "#dc2626"            # Errors
```

✅ **Borders**
```python
BORDER_PRIMARY = "#2a2a2a"    # Standard borders
BORDER_SUBTLE = "#1f1f1f"     # Secondary borders
```

❌ **MISSING: Backward Compat Aliases for TTK**
```python
# TTK theme file currently uses THEME_* constants
# Need to add these aliases to UIStyleV2:
THEME_BG_APP = BG_BASE
THEME_BG_SIDEBAR = BG_ELEVATED
THEME_BG_PANEL = BG_SURFACE
THEME_BG_INPUT = BG_ELEVATED
THEME_BG_TOOLBAR = BG_ELEVATED
THEME_BG_STATUSBAR = BG_SUBTLE

THEME_BORDER_DEFAULT = BORDER_PRIMARY
THEME_BORDER_PANEL = BORDER_PRIMARY

THEME_TEXT_PRIMARY = TEXT_PRIMARY
THEME_TEXT_SECONDARY = TEXT_SECONDARY
THEME_TEXT_MUTED = TEXT_MUTED

THEME_STATE_HUNTING = ACCENT_GREEN
THEME_STATE_HUNTING_BORDER = "#16a34a"  # darker green
THEME_STATE_SELECTED = "#1d4ed8"        # blue
THEME_STATE_INFO = ACCENT_BLUE
THEME_STATE_READY = ACCENT_AMBER
THEME_STATE_DANGER = DANGER
```

#### 2. Typography
✅ **Font Families**
```python
FONT_FAMILY_UI = "Inter"
FONT_FAMILY_UI_FALLBACK = "Segoe UI"
FONT_FAMILY_MONO = "JetBrains Mono"
FONT_FAMILY_MONO_FALLBACK = "Courier New"
FONT_FAMILY = FONT_FAMILY_UI_FALLBACK  # Backward compat
```

✅ **Font Sizes**
```python
SIZE_TITLE = 16
SIZE_HEADER = 14
SIZE_BODY = 13
SIZE_LABEL = 12
SIZE_SMALL = 11
SIZE_TINY = 10
SIZE_TEXT = SIZE_BODY      # Backward compat
SIZE_BUTTON = SIZE_LABEL   # Backward compat
SIZE_SECTION = SIZE_HEADER # Backward compat
```

✅ **Font Tuples**
```python
FONT_TITLE = (FONT_FAMILY_UI_FALLBACK, SIZE_TITLE, "bold")
FONT_SECTION = (FONT_FAMILY_UI_FALLBACK, SIZE_HEADER, "bold")
FONT_HEADER = (FONT_FAMILY_UI_FALLBACK, SIZE_HEADER, "bold")
FONT_BODY = (FONT_FAMILY_UI_FALLBACK, SIZE_BODY)
FONT_LABEL = (FONT_FAMILY_UI_FALLBACK, SIZE_LABEL)
FONT_TEXT = (FONT_FAMILY_UI_FALLBACK, SIZE_BODY)
FONT_BUTTON = (FONT_FAMILY_UI_FALLBACK, SIZE_LABEL)
FONT_SMALL = (FONT_FAMILY_UI_FALLBACK, SIZE_SMALL)
```

#### 3. Spacing
✅ **Constants**
```python
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16
SPACE_XL = 24
# Backward compat aliases
SPACING_2 = 2
SPACING_4 = 4
SPACING_6 = 6
SPACING_8 = 8
SPACING_10 = 10
SPACING_12 = 12
SPACING_16 = 16
SPACING_20 = 20
SPACING_24 = 24
SPACING_32 = 32
```

#### 4. Methods
✅ `resolve_font_family(role="ui")` — Already exists  
✅ `get_font(role, size, weight)` — Already exists  
✅ `get_panel_style()` — Already exists  
✅ `get_button_style(variant)` — Already exists

#### 5. NEW: Sidebar Icons (from IMPLEMENTATION-GUIDE)
✅ **Icon Mapping**
```python
SIDEBAR_ICONS = {
    "tab_hunt": "🎯",
    "tab_setup": "⚙️",
    "btn_skill_manager": "⚔️",
    # ... 6 more
}

@classmethod
def get_sidebar_icon(cls, key: str) -> str:
    return cls.SIDEBAR_ICONS.get(key, "•")
```

---

## 🔄 Migration Strategy

### Phase 1: Enhance UIStyleV2 (1 day)

Add missing constants to UIStyleV2:
1. THEME_* aliases for backward compat
2. SPACING_* aliases (2, 4, 6, 10, 20, 32)
3. Verify all methods exist
4. Add sidebar icon mapping

**Files to modify**: `lib/ui_style_v2.py` (add ~60 lines)

### Phase 2: Prepare Update Map (1 day)

Create detailed mapping:
- File → Old imports → New imports
- Specific line numbers
- Before/after code examples
- Testing steps per file

**Deliverable**: `UISTYLE-MIGRATION-MAPPING.md`

### Phase 3: Update Core Files (1 day)

Priority order (start with easiest):
1. Simple files (dialogs/) — 8 files
2. Heavy files (windows/) — 3 files
3. TTK theme — 1 file
4. Documentation — 27 files

### Phase 4: Final Cleanup (0.5 day)

- Delete old `lib/ui_style.py`
- Run tests
- Verify no import errors
- Commit

---

## 📝 Detailed Implementation Plan

### Task 1: Update UIStyleV2 with All Missing Constants

**File**: `lib/ui_style_v2.py`  
**Time**: 1 hour

Add after existing color definitions (around line 32):

```python
# =========================================================
# BACKWARD COMPATIBILITY: TTK Theme Constants (From UIStyle)
# Mapping old naming to new semantic tokens
# =========================================================

# Background aliases
THEME_BG_APP = BG_BASE
THEME_BG_SIDEBAR = BG_ELEVATED
THEME_BG_PANEL = BG_SURFACE
THEME_BG_INPUT = BG_ELEVATED
THEME_BG_TOOLBAR = BG_ELEVATED
THEME_BG_STATUSBAR = BG_SUBTLE

# Border aliases
THEME_BORDER_DEFAULT = BORDER_PRIMARY
THEME_BORDER_PANEL = BORDER_PRIMARY

# Text aliases
THEME_TEXT_PRIMARY = TEXT_PRIMARY
THEME_TEXT_SECONDARY = TEXT_SECONDARY
THEME_TEXT_MUTED = TEXT_MUTED

# State color aliases
THEME_STATE_HUNTING = ACCENT_GREEN
THEME_STATE_HUNTING_BORDER = "#16a34a"  # Darker green for borders
THEME_STATE_SELECTED = "#1d4ed8"        # Blue for selection
THEME_STATE_INFO = ACCENT_BLUE
THEME_STATE_READY = ACCENT_AMBER
THEME_STATE_DANGER = DANGER

# =========================================================
# BACKWARD COMPATIBILITY: Old Spacing Aliases
# =========================================================

SPACING_2 = 2
SPACING_4 = SPACE_XS
SPACING_6 = 6
SPACING_8 = SPACE_SM
SPACING_10 = 10
SPACING_12 = SPACE_MD
SPACING_16 = SPACE_LG
SPACING_20 = 20
SPACING_24 = SPACE_XL
SPACING_32 = 32
```

Add after font definitions (around line 100):

```python
# =========================================================
# BACKWARD COMPATIBILITY: Old Font Naming
# =========================================================

SIZE_SECTION = SIZE_HEADER  # Old UIStyle naming
```

### Task 2: Update Import Statements in 11 Core Files

#### Type A: Simple Import Change (8 files)

**Files**:
- `dialogs/display_settings.py`
- `dialogs/monster_edit.py`
- `dialogs/monster_picker.py`
- `ui/utils/overlay_settings.py`
- `ui/views/activity_logs_frame.py`
- `ui/views/monster_manager_frame.py`
- `ui/windows/overlay_window.py`
- `ui/windows/setup_wizard_vision.py`

**Current Code**:
```python
from lib.ui_style import UIStyle as UI
```

**New Code**:
```python
from lib.ui_style_v2 import UIStyleV2 as UI
```

**Verification**:
- ✅ If code uses: `UI.FONT_*`, `UI.SIZE_*`, `UI.COLOR_*` → Works (aliases exist)
- ✅ If code uses: `UI.THEME_*`, `UI.SPACING_*` → Works (added in Task 1)
- ⚠️ If code uses: `UI.resolve_font_family()` → Already in UIStyleV2

#### Type B: Heavy Files (3 files) — Needs More Work

**File 1**: `ui/windows/library_manager.py`

Current (line 16-17):
```python
from lib.ui_style import UIStyle
from lib.ui_style import UIStyle as UI
```

New:
```python
from lib.ui_style_v2 import UIStyleV2
from lib.ui_style_v2 import UIStyleV2 as UI
```

**Common patterns to update**:
- `UIStyle.resolve_font_family("body")` → `UI.FONT_BODY` or `UI.FONT_LABEL`
- `UIStyle.FONT_FAMILY` → `UI.FONT_FAMILY`
- `UIStyle.COLOR_*` → `UI.THEME_*` or `UI.ACCENT_*`

**File 2**: `ui/windows/monster_manager_win.py`

Same pattern as library_manager.py

**File 3**: `ui/windows/setup_wizard.py`

Same pattern, but check for font size literals like:
- `font=(UIStyle.resolve_font_family("body"), 14)` 
  → `font=UI.FONT_HEADER` (SIZE_HEADER = 14)

#### Type C: TTK Theme File (1 file)

**File**: `ui/theme/ttk_theme.py`  
**Current**: Imports UIStyle (line 3)  
**Issue**: Uses 60+ THEME_* constants throughout

**Change**:
```python
# Line 3 - Current
from lib.ui_style import UIStyle

# New
from lib.ui_style_v2 import UIStyleV2 as UIStyle
```

**Why it works**: 
- Added THEME_* aliases to UIStyleV2 in Task 1
- All references like `UIStyle.THEME_BG_APP` will still work

### Task 3: Update Documentation Files (27 files)

**Action**: Find-replace in all docs

```
Old: lib.ui_style.UIStyle
New: lib.ui_style_v2.UIStyleV2

Old: from lib.ui_style import
New: from lib.ui_style_v2 import

Old: UIStyle.BTN_PRIMARY_BG
New: UIStyleV2.ACCENT_GREEN or UIStyleV2.ACCENT_AMBER (context-dependent)

Old: UIStyle.BG_PANEL
New: UIStyleV2.BG_SURFACE

Old: UIStyle.THEME_*
New: UIStyleV2.THEME_* (still exists as alias)
```

**Files to update** (grep results):
- `.jules/prompts/ui-main-screen-cleanup/` — 12 files
- `docs/` — 8 files  
- `docs/sprints/sprint26-combat-refactor/` — 5 files
- Other — 2 files

**Tool**: Use find-replace with regex in VS Code

### Task 4: Remove Old UIStyle.py

**File to delete**: `lib/ui_style.py`

**Verification before delete**:
```bash
# Search for any remaining references
grep -r "from lib.ui_style import" . --include="*.py" --exclude-dir=".git"
grep -r "import ui_style[^_v]" . --include="*.py" --exclude-dir=".git"
# Result should be: EMPTY (all migrated)
```

**After deletion**:
- Run app: `python app_gui.py` → No errors
- Run tests: `pytest` → All pass
- Check imports: `python -c "from lib.ui_style_v2 import UIStyleV2"`  → Success

### Task 5: Final Verification

#### Unit Tests
```bash
# Create test file: tests/test_ui_style_migration.py
python -m pytest tests/test_ui_style_migration.py -v
```

Test content:
```python
"""Verify UIStyleV2 has all required constants"""

from lib.ui_style_v2 import UIStyleV2 as UI

def test_all_colors_exist():
    """Check all color constants are defined"""
    required = [
        'BG_BASE', 'BG_SURFACE', 'BG_ELEVATED', 'BG_SUBTLE',
        'BORDER_PRIMARY', 'BORDER_SUBTLE',
        'TEXT_PRIMARY', 'TEXT_SECONDARY', 'TEXT_MUTED', 'TEXT_SUBTLE',
        'ACCENT_GREEN', 'ACCENT_AMBER', 'ACCENT_BLUE', 'DANGER'
    ]
    for attr in required:
        assert hasattr(UI, attr), f"Missing: {attr}"
        assert isinstance(getattr(UI, attr), str), f"Not a string: {attr}"

def test_backward_compat_aliases():
    """Check old UIStyle constants are aliased"""
    required_aliases = [
        'THEME_BG_APP', 'THEME_BG_SIDEBAR', 'THEME_BG_PANEL',
        'THEME_TEXT_PRIMARY', 'THEME_STATE_HUNTING',
        'SPACING_2', 'SPACING_4', 'SPACING_8', 'SPACING_12',
        'SIZE_SECTION'
    ]
    for attr in required_aliases:
        assert hasattr(UI, attr), f"Missing backward compat: {attr}"

def test_all_fonts_exist():
    """Check all font constants"""
    required = [
        'FONT_TITLE', 'FONT_SECTION', 'FONT_HEADER', 'FONT_BODY',
        'FONT_LABEL', 'FONT_TEXT', 'FONT_BUTTON', 'FONT_SMALL'
    ]
    for attr in required:
        assert hasattr(UI, attr), f"Missing: {attr}"
        assert isinstance(getattr(UI, attr), tuple), f"Not a tuple: {attr}"

def test_methods_exist():
    """Check all required methods"""
    methods = ['get_font', 'resolve_font_family', 'get_panel_style', 'get_button_style']
    for method in methods:
        assert hasattr(UI, method), f"Missing method: {method}"

if __name__ == "__main__":
    test_all_colors_exist()
    test_backward_compat_aliases()
    test_all_fonts_exist()
    test_methods_exist()
    print("✅ All UIStyleV2 constants verified!")
```

#### Import Verification
```bash
# Test all modified files can import successfully
python -c "from dialogs.display_settings import *"
python -c "from ui.windows.library_manager import *"
python -c "from ui.theme.ttk_theme import *"
# etc for all 11 core files
```

#### Visual Inspection
```bash
# Run app and verify:
python app_gui.py

# Checklist:
# - [ ] App launches without errors
# - [ ] Sidebar displays correctly (using UIStyleV2 colors)
# - [ ] All dialogs appear with correct styling
# - [ ] TTK theme applied correctly to widgets
# - [ ] No "attribute not found" errors in console
```

---

## 📋 Complete Migration Checklist

### PRE-MIGRATION
- [ ] Read this document fully
- [ ] Backup current code (commit to git)
- [ ] Verify UIStyleV2 exists at `lib/ui_style_v2.py`
- [ ] Create feature branch: `git checkout -b feature/legacy-uistyle-removal`

### PHASE 1: Enhance UIStyleV2
- [ ] Add THEME_* aliases to UIStyleV2 (line 33-60)
- [ ] Add SPACING_* aliases to UIStyleV2 (line 61-78)
- [ ] Add SIZE_SECTION alias to UIStyleV2
- [ ] Verify file has 200+ lines total
- [ ] Test: `python -c "from lib.ui_style_v2 import UIStyleV2 as UI; print(UI.THEME_BG_APP)"`

### PHASE 2: Update Core Import Statements

**Simple Files (8)** — Find/Replace only:
- [ ] `dialogs/display_settings.py` — from lib.ui_style → from lib.ui_style_v2
- [ ] `dialogs/monster_edit.py`
- [ ] `dialogs/monster_picker.py`
- [ ] `ui/utils/overlay_settings.py`
- [ ] `ui/views/activity_logs_frame.py`
- [ ] `ui/views/monster_manager_frame.py`
- [ ] `ui/windows/overlay_window.py`
- [ ] `ui/windows/setup_wizard_vision.py`

Test each file: `python -m py_compile <file>`

**Heavy Files (3)** — Needs careful review:
- [ ] `ui/windows/library_manager.py`
  - [ ] Update import (line 16-17)
  - [ ] Search for `resolve_font_family` calls
  - [ ] Replace with UIStyleV2 constants where possible
  - [ ] Test: `python -m py_compile ui/windows/library_manager.py`

- [ ] `ui/windows/monster_manager_win.py`
  - [ ] Same checks as library_manager.py
  - [ ] Test: `python -m py_compile ui/windows/monster_manager_win.py`

- [ ] `ui/windows/setup_wizard.py`
  - [ ] Same checks as library_manager.py
  - [ ] Test: `python -m py_compile ui/windows/setup_wizard.py`

**TTK Theme (1)**:
- [ ] `ui/theme/ttk_theme.py`
  - [ ] Update import (line 3)
  - [ ] Verify all THEME_* constants exist in UIStyleV2
  - [ ] Test: `python -c "from ui.theme.ttk_theme import *"`

### PHASE 3: Update Documentation (27 files)

- [ ] `.jules/prompts/` — Find/replace 12 files
- [ ] `docs/` — Find/replace 8 files
- [ ] `docs/sprints/` — Find/replace 5 files
- [ ] Other docs — Find/replace 2 files

Pattern:
```
Search: UIStyle\.
Replace: UIStyleV2\.

Search: from lib\.ui_style import
Replace: from lib\.ui_style_v2 import
```

### PHASE 4: Cleanup & Verification

- [ ] Run test file: `pytest tests/test_ui_style_migration.py -v`
- [ ] Run import tests for all 11 core files
- [ ] Start app: `python app_gui.py`
- [ ] Visual check: App displays correctly
- [ ] Check console: No AttributeError or ImportError
- [ ] Delete old file: `rm lib/ui_style.py`
- [ ] Final verification: `grep -r "from lib.ui_style import" . --include="*.py"` → Empty
- [ ] Final verification: `grep -r "import ui_style[^_v]" . --include="*.py"` → Empty

### FINAL
- [ ] Commit: `git add -A && git commit -m "chore: complete legacy UIStyle removal, adopt UIStyleV2"`
- [ ] Push feature branch
- [ ] Create pull request
- [ ] Code review
- [ ] Merge to main

---

## 🚨 Risk Mitigation

### Potential Issues & Solutions

| Issue | Prevention | Recovery |
|-------|-----------|----------|
| **Missing constant in UIStyleV2** | Test file validates all required constants | Use `git log` to find when it was used, add to UIStyleV2 |
| **Font sizes look wrong** | Verify UIStyleV2 font sizes match visual spec | Compare with design mockups, adjust SIZE_* if needed |
| **TTK theme breaks** | Test ttk_theme.py after THEME_* aliases added | Verify all THEME_* constants in UIStyleV2 before merging |
| **Some file still uses old import** | Grep search in final verification step | Find remaining imports, update them |
| **App won't start** | Backup and test each phase independently | Rollback to last working commit, debug imports |

### Rollback Plan
```bash
# If migration fails:
git revert HEAD~1  # Undo last commit
git checkout feature/legacy-uistyle-removal~1  # Go back to pre-migration state
# Fix issue, then re-attempt migration
```

---

## 📊 Migration Metrics

### Before Migration
- 2 Design systems active
- 38 files importing old UIStyle
- 250+ references to UIStyle
- Maintenance burden: HIGH
- Code clarity: POOR

### After Migration
- 1 Design system (UIStyleV2 only)
- 0 files importing old UIStyle
- 0 references to UIStyle
- Maintenance burden: LOW
- Code clarity: EXCELLENT

### Expected Outcomes
✅ Single source of truth for UI styling  
✅ Consistent dark theme across all files  
✅ Easier to maintain and update  
✅ Better code readability  
✅ Reduced bugs from conflicting styles  

---

## 📚 Supporting Documents

- **IMPLEMENTATION-GUIDE-PHASE2.md** — Detailed styling tasks after migration
- **REVIEW-CURRENT-STATE-vs-DESIGN-SPEC.md** — Current state analysis
- **UIStyleV2 Source** — `lib/ui_style_v2.py` (reference for all constants)

---

## 🔗 Quick Reference: Constant Mapping

| Old UIStyle | New UIStyleV2 | Purpose |
|-------------|---------------|---------|
| `BG_DEFAULT` | `BG_BASE` | App background |
| `BG_PANEL` | `BG_SURFACE` | Panel background |
| `BG_SECTION` | `BG_ELEVATED` | Section/sidebar bg |
| `COLOR_TEXT` | `TEXT_PRIMARY` | Main text color |
| `COLOR_SUBTEXT` | `TEXT_SECONDARY` | Secondary text |
| `COLOR_ACCENT` | `ACCENT_GREEN` | Accent/success |
| `COLOR_WARNING` | `ACCENT_AMBER` | Warning state |
| `COLOR_DANGER` | `DANGER` | Error/danger |
| `THEME_STATE_HUNTING` | `ACCENT_GREEN` | Active/hunting |
| `THEME_TEXT_PRIMARY` | `TEXT_PRIMARY` | Text color |
| `FONT_LABEL` | `FONT_LABEL` | ✅ Same |
| `SPACING_8` | `SPACE_SM` or `SPACING_8` | 8px spacing |

---

**Document Version**: 1.0  
**Status**: Ready for Execution  
**Next Step**: Begin Phase 1 (Enhance UIStyleV2)  
**Estimated Total Time**: 3-4 working days
