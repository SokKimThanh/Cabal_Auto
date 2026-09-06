# PROMPT: Cập nhật Style cho Tất cả Các Màn Hình (Sprint 26)

## 📋 Context
- **UIStyleV2** đã được triển khai với design system dark theme modern
- **ScreenStatePanel** và **SetupTab** đã được cập nhật thành công
- Cần cập nhật style cho tất cả các màn hình UI khác

## 🎯 Mục Tiêu

Cập nhật tất cả các component UI để sử dụng UIStyleV2 thay vì các hardcoded colors, đảm bảo:
1. Một design system thống nhất trên toàn bộ ứng dụng
2. Dễ bảo trì và thay đổi theme
3. Tuân theo chuẩn semantic tokens của UIStyleV2

## 📁 Danh Sách Màn Hình Cần Cập Nhật

### Priority 1: Core Tabs (Directly in main window)
- [x] `ui/tabs/setup_tab.py` - DONE
- [ ] `ui/tabs/hunt_tab.py`
- [ ] `ui/tabs/stats_tab.py`
- [ ] `ui/tabs/help_tab.py`

### Priority 2: Panels
- [x] `ui/panels/screen_state_panel.py` - DONE
- [ ] `ui/panels/skill_panel.py`

### Priority 3: Dialogs (in dialogs/ folder)
- [ ] `dialogs/preset_dialog.py`
- [ ] `dialogs/monster_picker.py`
- [ ] `dialogs/monster_edit.py`
- [ ] `dialogs/display_settings.py`

### Priority 4: Views & Other UI Components
- [ ] `ui/views/*` (if exists)
- [ ] `app_gui.py` main window styling

## 🎨 Style Migration Pattern

### Pattern: Import UIStyleV2
```python
from lib.ui_style_v2 import UIStyleV2 as UI  # or UIStyle, UIStyleV2 based on preference
```

### Pattern: Update Colors in Frame/Widget Creation

**OLD:**
```python
frame = tk.Frame(parent, bg="#1a1a1a", fg="#d1d5db")
label = tk.Label(parent, text="Text", bg="#0f0f0f", fg="#d1d5db", font=("Arial", 10))
button = tk.Button(parent, bg="#4ade80", fg="#000000", activebackground="#22c55e")
```

**NEW:**
```python
frame = tk.Frame(parent, bg=UI.BG_SURFACE, fg=UI.TEXT_PRIMARY)
label = tk.Label(parent, text="Text", bg=UI.BG_BASE, fg=UI.TEXT_PRIMARY, font=UI.FONT_LABEL)
button = tk.Button(parent, bg=UI.BTN_PRIMARY_BG, fg=UI.BTN_PRIMARY_FG, activebackground=UI.ACCENT_GREEN)
```

## 🔑 Key Style Tokens to Use

### Background Colors
| Token | Value | Usage |
|-------|-------|-------|
| `UI.BG_BASE` | #0f0f0f | Main app background |
| `UI.BG_SURFACE` | #1a1a1a | Panels, cards, content areas |
| `UI.BG_ELEVATED` | #111111 | Sidebar, headers, inputs |
| `UI.BG_SUBTLE` | #0a0a0a | Status bar, dividers |

### Text Colors
| Token | Value | Usage |
|-------|-------|-------|
| `UI.TEXT_PRIMARY` | #d1d5db | Main content text |
| `UI.TEXT_SECONDARY` | #9ca3af | Secondary/help text |
| `UI.TEXT_MUTED` | #6b7280 | Tertiary/disabled text |
| `UI.TEXT_SUBTLE` | #374151 | Placeholders |

### Accent Colors
| Token | Value | Usage |
|-------|-------|-------|
| `UI.ACCENT_GREEN` | #4ade80 | Active, success, primary actions |
| `UI.ACCENT_AMBER` | #f59e0b | Warning, waiting state |
| `UI.ACCENT_BLUE` | #38bdf8 | Info, running/active state |
| `UI.DANGER` | #dc2626 | Errors, critical, health low |

### Borders
| Token | Value | Usage |
|-------|-------|-------|
| `UI.BORDER_PRIMARY` | #2a2a2a | Standard panel borders |
| `UI.BORDER_SUBTLE` | #1f1f1f | Subtle dividers |

### Font Constants
```python
UI.FONT_TITLE    # (FONT_FAMILY_UI_FALLBACK, 16, "bold")
UI.FONT_SECTION  # (FONT_FAMILY_UI_FALLBACK, 14, "bold")
UI.FONT_HEADER   # (FONT_FAMILY_UI_FALLBACK, 14, "bold")
UI.FONT_BODY     # (FONT_FAMILY_UI_FALLBACK, 10)
UI.FONT_LABEL    # (FONT_FAMILY_UI_FALLBACK, 9)
UI.FONT_BUTTON   # (FONT_FAMILY_UI_FALLBACK, 9)
UI.FONT_SMALL    # (FONT_FAMILY_UI_FALLBACK, 8)
```

### Button Styles (Predefined)
```python
# Primary Button (Green - for main actions)
bg=UI.BTN_PRIMARY_BG          # #4ade80
fg=UI.BTN_PRIMARY_FG          # #000000
activebackground=UI.ACCENT_GREEN

# Neutral Button (Gray - for secondary actions)
bg=UI.BTN_NEUTRAL_BG          # #111111
fg=UI.BTN_NEUTRAL_FG          # #d1d5db

# Danger Button (Red - for destructive actions)
bg=UI.BTN_DANGER_BG           # #dc2626
fg=UI.BTN_DANGER_FG           # #ffffff

# Info Button (Blue - for info/link actions)
bg=UI.BTN_INFO_BG             # #38bdf8
fg=UI.BTN_INFO_FG             # #000000
```

## 🛠️ Implementation Checklist

For each file to update:

### 1. Import Section
- [ ] Add `from lib.ui_style_v2 import UIStyleV2 as UI`
- [ ] Keep existing i18n imports
- [ ] Remove any hardcoded color definitions

### 2. Color Updates
- [ ] Replace all `bg="#..."` with appropriate `UI.BG_*`
- [ ] Replace all `fg="#..."` with appropriate `UI.TEXT_*` or `UI.ACCENT_*`
- [ ] Update button colors to use `UI.BTN_*` constants
- [ ] Update border colors to use `UI.BORDER_*`
- [ ] Update accent colors for states (success, warning, error)

### 3. Font Updates
- [ ] Replace `font=("Arial", 10)` with `font=UI.FONT_LABEL` (or appropriate constant)
- [ ] Ensure font consistency across similar component types

### 4. Testing
- [ ] Visual check: colors match design system
- [ ] Text readability: contrast is sufficient
- [ ] State consistency: hover/active/disabled states work correctly
- [ ] i18n compatibility: labels still translate correctly

### 5. Code Quality
- [ ] Black formatting: `black ui/tabs/*.py ui/panels/*.py dialogs/*.py`
- [ ] Flake8 linting: `flake8 ui/tabs/*.py ui/panels/*.py dialogs/*.py`
- [ ] No hardcoded colors remain in UI code

## 📝 Example: Hunt Tab Update

### Before (hunt_tab.py):
```python
class HuntTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#0f0f0f")
        self.label = tk.Label(self, text="Hunt", bg="#0f0f0f", fg="#d1d5db")
        self.start_btn = tk.Button(self, text="Start", bg="#4ade80", fg="#000000")
        self.status_label = tk.Label(self, text="Ready", bg="#1a1a1a", fg="#9ca3af")
```

### After (hunt_tab.py):
```python
from lib.ui_style_v2 import UIStyleV2 as UI

class HuntTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=UI.BG_BASE)
        self.label = tk.Label(self, text="Hunt", bg=UI.BG_BASE, fg=UI.TEXT_PRIMARY, font=UI.FONT_SECTION)
        self.start_btn = tk.Button(self, text="Start", bg=UI.BTN_PRIMARY_BG, fg=UI.BTN_PRIMARY_FG)
        self.status_label = tk.Label(self, text="Ready", bg=UI.BG_SURFACE, fg=UI.TEXT_SECONDARY, font=UI.FONT_LABEL)
```

## 🔍 Files to Scan for Hardcoded Colors

Run this command to find files with hardcoded colors:
```bash
grep -r "#[0-9a-fA-F]\{6\}" --include="*.py" ui/ dialogs/ app_gui.py | grep -E "(bg|fg|background|foreground).*#"
```

Or use Python to find:
```python
import re
import os

pattern = r'(bg|fg|background|foreground)\s*=\s*["\']#[0-9a-fA-F]{6}["\']'
for root, dirs, files in os.walk('ui/'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path) as f:
                for i, line in enumerate(f, 1):
                    if re.search(pattern, line):
                        print(f"{path}:{i}: {line.strip()}")
```

## 🎯 Success Criteria

- [ ] All tabs use UIStyleV2 colors
- [ ] All panels use UIStyleV2 colors
- [ ] All dialogs use UIStyleV2 colors
- [ ] No hardcoded colors (#xxx) in UI code
- [ ] App launches without errors
- [ ] Visual consistency across all screens
- [ ] All tests pass
- [ ] Code formatted with black
- [ ] No linting errors with flake8

## 📊 Definition of Done

1. ✅ All files updated with UIStyleV2
2. ✅ Colors migrated from hardcoded to semantic tokens
3. ✅ Fonts updated to use UI constants
4. ✅ Visual testing completed
5. ✅ Unit tests pass
6. ✅ Code formatting & linting pass
7. ✅ PR created and reviewed

## 🔗 Related Documentation

- `lib/ui_style_v2.py` - Full style constants definition
- `ui/panels/screen_state_panel.py` - Reference implementation
- `ui/tabs/setup_tab.py` - Reference implementation
- Copilot instructions: `.github/copilot-instructions.md`

## 📌 Notes

- Use `from lib.ui_style_v2 import UIStyleV2 as UI` for consistency
- Keep backward compatibility aliases (THEME_*, legacy names)
- Prefer semantic tokens (BG_BASE, TEXT_PRIMARY) over legacy names
- For state-specific colors, use THEME_STATE_* aliases
- Test in dark mode only (modern design system)
