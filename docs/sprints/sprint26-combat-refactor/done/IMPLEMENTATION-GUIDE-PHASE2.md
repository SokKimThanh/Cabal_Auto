# 📝 IMPLEMENTATION GUIDE — UI Redesign Phase 2

**Document Purpose**: Step-by-step instructions to implement all UI redesign issues  
**Date**: 2026-09-06  
**Target Timeline**: 8-10 working days  
**Difficulty**: Medium (component styling + state management)

---

## 🗂️ Document Structure

This guide is organized by **Phase** and **Priority**:

1. **Foundation Phase** (Days 1-2) — Sidebar branding, icons, active states
2. **Panels Phase** (Days 3-4) — Card styling, borders, tabs  
3. **Typography Phase** (Days 5-6) — Font consistency, hierarchy
4. **Polish Phase** (Days 7-8) — Status badges, animations, empty states

---

## 🎯 Phase 1: Sidebar Redesign (Days 1-2)

### Task 1.1: Add Sidebar Logo/Branding

**File**: `app_gui.py`  
**Location**: In `_build_ui()` method, after line 648 (before sidebar items)  
**Time**: 1 hour

**Current Code** (lines 648-710):
```python
# Vùng C1: Secondary Configuration Sidebar (Spans rows 1 and 2)
self.shell_zone_c1 = tk.Frame(self.main_shell, bg=UI.BG_ELEVATED)
self.shell_zone_c1.grid(row=1, column=0, rowspan=2, sticky="nsew")
self.shell_zone_c1.configure(padx=16, pady=20)
self.shell_zone_c1.grid_propagate(False)

# Build Sidebar Navigation  ← Logo should be added HERE
sidebar_items = [
```

**What to Add** (before `sidebar_items`):
```python
# ========== SIDEBAR HEADER/BRANDING ==========
sidebar_header = tk.Frame(self.shell_zone_c1, bg=UI.BG_ELEVATED)
sidebar_header.pack(fill="x", pady=(0, 16))

# Logo/Icon + Title (using Unicode sword emoji)
logo_frame = tk.Frame(sidebar_header, bg=UI.BG_ELEVATED)
logo_frame.pack(fill="x", pady=(12, 8))

logo_icon = tk.Label(
    logo_frame,
    text="⚔️",  # Sword emoji
    font=(UI.FONT_FAMILY_UI_FALLBACK, 24),
    bg=UI.BG_ELEVATED,
    fg=UI.ACCENT_GREEN
)
logo_icon.pack(side="left", padx=4)

logo_text = tk.Label(
    logo_frame,
    text="CABAL\nASSISTANT",
    font=(UI.FONT_FAMILY_UI_FALLBACK, 9, "bold"),
    bg=UI.BG_ELEVATED,
    fg=UI.ACCENT_GREEN,
    justify="center"
)
logo_text.pack(side="left", padx=(4, 0))

# Divider line
divider = tk.Frame(
    sidebar_header,
    bg=UI.BORDER_PRIMARY,
    height=1
)
divider.pack(fill="x", pady=(8, 0))
```

**After Task 1.1**: Sidebar will show sword icon + "CABAL ASSISTANT" text in green at top

---

### Task 1.2: Create Sidebar Icon Mapping

**File**: `lib/ui_style_v2.py`  
**Location**: Add class attribute at end of UIStyleV2 class  
**Time**: 30 minutes

**What to Add** (at line 110, after font definitions):
```python
# =========================================================
# SIDEBAR ICON MAPPING (Unicode Emoji)
# =========================================================

SIDEBAR_ICONS = {
    "tab_hunt": "🎯",           # Hunt/Target
    "tab_setup": "⚙️",           # Settings/Gear
    "btn_skill_manager": "⚔️",   # Skills/Sword
    "btn_monster_manager": "🐉", # Monster/Dragon
    "btn_library_manager": "📚", # Library/Books
    "sidebar_activity_logs": "📋", # Logs/Clipboard
    "tab_stats": "📊",           # Stats/Chart
    "sidebar_support": "❓",     # Help/Question
    "sidebar_quick_setup": "🔧", # Settings/Wrench
}

@classmethod
def get_sidebar_icon(cls, key: str) -> str:
    """Get icon emoji for sidebar item by key"""
    return cls.SIDEBAR_ICONS.get(key, "•")
```

**After Task 1.2**: Icon mapping available via `UI.get_sidebar_icon("tab_hunt")`

---

### Task 1.3: Modify Sidebar Button Rendering to Show Icons

**File**: `app_gui.py`  
**Location**: Lines 715-728 (sidebar button creation loop)  
**Time**: 1.5 hours

**Current Code**:
```python
for item_idx, item in enumerate(sidebar_items):
    key, command, font, view_target = item
    if command is None:
        # Section label
        lbl = tk.Label(
            self.shell_zone_c1,
            text=f"   {self._t(key)}",
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_SECONDARY,
            font=font,
            anchor="w",
        )
        lbl.pack(fill="x", pady=(10, 4))
        self._sidebar_widgets.append((lbl, key, view_target))
    else:
        # Button
        btn = tk.Button(
            self.shell_zone_c1,
            text=f"   {self._t(key)}",  # ← NEEDS ICON
            command=command,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_SECONDARY,
            font=font,
            anchor="w",
            padx=12,
            pady=8,
            relief="flat",
            cursor="hand2",
        )
```

**Replace With**:
```python
for item_idx, item in enumerate(sidebar_items):
    key, command, font, view_target = item
    if command is None:
        # Section label - unchanged
        lbl = tk.Label(
            self.shell_zone_c1,
            text=f"   {self._t(key)}",
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_SECONDARY,
            font=font,
            anchor="w",
        )
        lbl.pack(fill="x", pady=(10, 4))
        self._sidebar_widgets.append((lbl, key, view_target))
    else:
        # Button - NOW WITH ICON
        icon = UI.get_sidebar_icon(key)
        btn_text = f" {icon}  {self._t(key)}"  # Icon + 2-space gap + label
        
        btn = tk.Button(
            self.shell_zone_c1,
            text=btn_text,
            command=command,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_SECONDARY,
            font=(UI.FONT_FAMILY_UI_FALLBACK, 11),  # 11px for better icon fit
            anchor="w",
            padx=10,
            pady=10,
            relief="flat",
            cursor="hand2",
            activebackground=UI.BORDER_PRIMARY,  # Hover effect
            activeforeground=UI.TEXT_PRIMARY,
        )
```

**After Task 1.3**: Sidebar buttons will show emoji icons + labels

---

### Task 1.4: Implement Active State Styling for Sidebar

**File**: `app_gui.py`  
**Location**: Add new method + update switch_view() method  
**Time**: 1.5 hours

**Step 1**: Add method to track and style active button (add after `__init__`, around line 600):
```python
def _update_sidebar_active_state(self, active_key=None):
    """Update sidebar button styling to reflect active view"""
    for widget, key, view_target in self._sidebar_widgets:
        if isinstance(widget, tk.Button):
            # Check if this is the active button
            is_active = (active_key == key or view_target == active_key)
            
            if is_active:
                # ACTIVE STATE: Green background + text
                widget.config(
                    bg=UI.ACCENT_GREEN_BG,  # #1f2d1f
                    fg=UI.ACCENT_GREEN,     # #4ade80
                    relief="flat",
                    bd=3,  # Left border effect (3px border-left simulation)
                )
            else:
                # INACTIVE STATE: Dark background + gray text
                widget.config(
                    bg=UI.BG_ELEVATED,      # #111111
                    fg=UI.TEXT_SECONDARY,   # #9ca3af
                    relief="flat",
                    bd=0,
                )
```

**Step 2**: Update the `switch_view()` method to call the styling function:

Find this method (around line 1150-1200) and modify:
```python
def switch_view(self, view_name):
    """Switch active view and update UI"""
    # ... existing code ...
    
    # Add this line at the end of the method:
    self._update_sidebar_active_state(view_name)
```

**Step 3**: Call styling on app startup (in `__init__`, after _build_ui()):
```python
# At the end of __init__, after self._build_ui():
self._update_sidebar_active_state("hunt")  # Set hunt as default active
```

**After Task 1.4**: Active sidebar item shows green background (#1f2d1f) + green text (#4ade80)

---

## 🎯 Phase 2: Panel Styling (Days 3-4)

### Task 2.1: Create Custom Styled Panel Component

**File**: Create new file `ui/components/styled_panel.py`  
**Time**: 1 hour

```python
"""Styled panel component matching dark theme design"""

import tkinter as tk
from lib.ui_style_v2 import UIStyleV2 as UI


class StyledPanel(tk.Frame):
    """A panel with border, background, and padding that matches the dark theme"""
    
    def __init__(self, parent, **kwargs):
        # Extract custom kwargs before passing to Frame
        self.title = kwargs.pop("title", None)
        self.show_border = kwargs.pop("show_border", True)
        
        # Initialize frame with dark theme
        super().__init__(parent, bg=UI.BG_SURFACE, **kwargs)
        
        # Add border using a second frame (Tkinter limitation workaround)
        if self.show_border:
            self.border_frame = tk.Frame(
                self,
                bg=UI.BORDER_PRIMARY,
                highlightthickness=0
            )
            self.border_frame.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Actual content frame on top
            self.content_frame = tk.Frame(
                self,
                bg=UI.BG_SURFACE,
                highlightthickness=0
            )
            self.content_frame.place(x=1, y=1, relwidth=1, relheight=1)
        else:
            self.content_frame = self
    
    def get_content_frame(self):
        """Return frame for adding widgets (with padding already applied)"""
        return self.content_frame
```

**After Task 2.1**: Can create panels with borders via `StyledPanel(parent, show_border=True)`

---

### Task 2.2: Apply Panel Styling to Hunt Tab Panels

**File**: `ui/tabs/hunt_tab.py`  
**Location**: Lines where panels are created (around line 50-100)  
**Time**: 2 hours

**Current Code** (approximate):
```python
# Target list panel (no border, no styling)
target_panel = tk.Frame(self.frame, bg=UI.BG_BASE)
target_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

# Tabs inside
tab_frame = tk.Frame(target_panel, bg=UI.BG_ELEVATED)
```

**Replace With**:
```python
from ui.components.styled_panel import StyledPanel

# Target list panel - NOW WITH STYLING
target_panel = StyledPanel(
    self.frame,
    bg=UI.BG_SURFACE,
    show_border=True
)
target_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

# Get content frame for tab placement
content_frame = target_panel.get_content_frame()

# Tabs inside - use content frame
tab_frame = tk.Frame(content_frame, bg=UI.BG_ELEVATED)
```

**Apply to all panels**:
1. Target list panel
2. Target info panel
3. Combo chain panel
4. Buff lane panel
5. Skill stats panel

**After Task 2.2**: All panels have visible 1px borders (#2a2a2a) and proper background

---

### Task 2.3: Style Tab Bar Elements

**File**: `ui/tabs/hunt_tab.py`  
**Location**: Tab creation code (around line 100-150)  
**Time**: 1.5 hours

**Current Code** (typical tab creation):
```python
tab_button = tk.Button(
    tab_frame,
    text="Tab Name",
    bg=UI.BG_ELEVATED,
    fg=UI.TEXT_SECONDARY,
    relief="flat"
)
```

**Update To**:
```python
# Store tab buttons for active state tracking
self.tab_buttons = {}

# When creating each tab button:
tab_button = tk.Button(
    tab_frame,
    text="Tab Name",
    bg=UI.BG_ELEVATED,       # Inactive background
    fg=UI.TEXT_SECONDARY,    # Inactive text
    relief="flat",
    bd=0,
    padx=14,
    pady=10,
    font=(UI.FONT_FAMILY_UI_FALLBACK, 13),
    cursor="hand2",
)

# Store reference
self.tab_buttons["tab_name"] = tab_button
tab_button.pack(side="left")

# Bind click to update state
tab_button.bind("<Button-1>", lambda e: self._update_tab_active_state("tab_name"))
```

**Add method to HuntTab**:
```python
def _update_tab_active_state(self, active_tab):
    """Update tab button styling for active/inactive states"""
    for tab_name, btn in self.tab_buttons.items():
        if tab_name == active_tab:
            # ACTIVE TAB
            btn.config(
                bg=UI.ACCENT_GREEN_BG,  # #1f2d1f
                fg=UI.ACCENT_GREEN,     # #4ade80
            )
        else:
            # INACTIVE TAB
            btn.config(
                bg=UI.BG_ELEVATED,      # #111111
                fg=UI.TEXT_SECONDARY,   # #9ca3af
            )
```

**After Task 2.3**: Tab bars show active state with green highlighting

---

## 🎯 Phase 3: Typography Standardization (Days 5-6)

### Task 3.1: Audit and Update Font Usage

**File**: Create utility script `scripts/audit_fonts.py`  
**Time**: 1 hour (audit only, not implementation)

```python
"""Audit all UI files for font usage"""

import os
import re

def find_font_usages():
    """Find all hardcoded font references in UI code"""
    ui_paths = [
        "app_gui.py",
        "ui/tabs/",
        "ui/panels/",
        "ui/dialogs/",
        "ui/components/"
    ]
    
    hardcoded_patterns = [
        r'font\s*=\s*\(["\'].*?["\'].*?\)',  # font=("Arial", 12)
        r'font=\s*tk\.font',                  # font=tk.font.Font
        r'"Segoe UI"',                        # Direct font names
        r'"Inter"',
    ]
    
    findings = {}
    
    for path in ui_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            for pattern in hardcoded_patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    if filepath not in findings:
                                        findings[filepath] = []
                                    findings[filepath].append((line_num, line.strip()))
    
    return findings

if __name__ == "__main__":
    issues = find_font_usages()
    for filepath, locations in sorted(issues.items()):
        print(f"\n{filepath}")
        for line_num, line in locations:
            print(f"  Line {line_num}: {line}")
```

**Run**: `python scripts/audit_fonts.py`

**After Task 3.1**: You'll have a list of all files needing font updates

---

### Task 3.2: Replace Hardcoded Fonts with UIStyleV2 Constants

**File**: Files identified in Task 3.1  
**Time**: 2 hours

**Pattern Examples**:

Old Code:
```python
font=("Segoe UI", 12)
font=("Inter", 14, "bold")
font=tk.font.Font(family="Arial", size=11)
```

New Code:
```python
font=UI.FONT_LABEL         # 12px
font=UI.FONT_SECTION       # 14px bold
font=UI.FONT_SMALL         # 11px
```

**Files to Modify** (Priority Order):
1. `app_gui.py` — Many font definitions
2. `ui/tabs/hunt_tab.py` — Tab styling
3. `ui/dialogs/preset_dialog.py` — Dialog fonts
4. `ui/panels/skill_panel.py` — Panel fonts
5. Other UI components as found by audit

---

### Task 3.3: Verify Color and Text Contrast

**File**: Create script `scripts/verify_contrast.py`  
**Time**: 30 minutes (verification only)

```python
"""Verify WCAG AA contrast ratios for color combinations"""

def contrast_ratio(color1_rgb, color2_rgb):
    """Calculate contrast ratio between two RGB colors (WCAG formula)"""
    def luminance(rgb):
        r, g, b = [x / 255.0 for x in rgb]
        r = r / 12.92 if r <= 0.03928 else pow((r + 0.055) / 1.055, 2.4)
        g = g / 12.92 if g <= 0.03928 else pow((g + 0.055) / 1.055, 2.4)
        b = b / 12.92 if b <= 0.03928 else pow((b + 0.055) / 1.055, 2.4)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    l1 = luminance(color1_rgb)
    l2 = luminance(color2_rgb)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

# Define color combos to test
test_pairs = {
    "Text on Background": {
        "fg": (209, 213, 219),      # TEXT_PRIMARY #d1d5db
        "bg": (15, 15, 15),         # BG_BASE #0f0f0f
        "required": 4.5  # AA standard
    },
    "Secondary Text on Background": {
        "fg": (156, 163, 175),      # TEXT_SECONDARY #9ca3af
        "bg": (15, 15, 15),         # BG_BASE #0f0f0f
        "required": 4.5
    },
    "Green on Green BG": {
        "fg": (74, 222, 128),       # ACCENT_GREEN #4ade80
        "bg": (31, 45, 31),         # ACCENT_GREEN_BG #1f2d1f
        "required": 4.5
    },
}

print("WCAG AA Contrast Verification\n")
for name, colors in test_pairs.items():
    ratio = contrast_ratio(colors["fg"], colors["bg"])
    status = "✓ PASS" if ratio >= colors["required"] else "✗ FAIL"
    print(f"{status} {name}: {ratio:.2f}:1 (required {colors['required']}:1)")
```

**After Task 3.3**: Verify all text color combos meet accessibility standards

---

## 🎯 Phase 4: Polish & Refinement (Days 7-8)

### Task 4.1: Create Status Badge Component

**File**: Create `ui/components/status_badge.py`  
**Time**: 1.5 hours

```python
"""Status badge component with color variants"""

import tkinter as tk
from lib.ui_style_v2 import UIStyleV2 as UI


class StatusBadge(tk.Frame):
    """Status badge with icon and text"""
    
    STATUS_STYLES = {
        "waiting": {
            "bg": "#292218",        # Dark brown
            "fg": "#f59e0b",        # Amber text
            "icon": "●",
            "label": "Đang chờ"
        },
        "ready": {
            "bg": UI.ACCENT_GREEN_BG,  # Green bg
            "fg": UI.ACCENT_GREEN,      # Green text
            "icon": "●",
            "label": "Sẵn sàng"
        },
        "hunting": {
            "bg": "#1e2d3d",        # Dark blue
            "fg": UI.ACCENT_BLUE,   # Blue text
            "icon": "●",
            "label": "Đang săn",
            "animate": True
        }
    }
    
    def __init__(self, parent, status="waiting", **kwargs):
        super().__init__(parent, **kwargs)
        self.status = status
        self.config(bg=self.BG_BASE, highlightthickness=0)
        
        style = self.STATUS_STYLES.get(status, self.STATUS_STYLES["waiting"])
        
        # Badge background
        self.badge = tk.Frame(
            self,
            bg=style["bg"],
            highlightthickness=0
        )
        self.badge.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Icon + text
        self.icon_label = tk.Label(
            self.badge,
            text=f"{style['icon']} {style['label']}",
            font=(UI.FONT_FAMILY_UI_FALLBACK, 11),
            bg=style["bg"],
            fg=style["fg"],
            padx=8,
            pady=4
        )
        self.icon_label.pack()
        
        # Pulse animation for hunting state
        if style.get("animate"):
            self._animate_pulse()
    
    def _animate_pulse(self):
        """Pulse animation for hunting state"""
        self.pulse_step = 0
        self._pulse_step()
    
    def _pulse_step(self):
        """Single pulse step"""
        # Simplified pulse - just change opacity by swapping colors
        # Real implementation would need more complex rendering
        self.after(500, self._pulse_step)
    
    def set_status(self, status):
        """Update badge status"""
        if status in self.STATUS_STYLES:
            self.status = status
            # Recreate badge with new style
            self.badge.destroy()
            self.__init__(self.master, status=status)


# Usage in app:
# badge = StatusBadge(parent_frame, status="ready")
# badge.pack()
```

**After Task 4.1**: Can create color-coded status badges

---

### Task 4.2: Add Hover Effects to Buttons

**File**: `app_gui.py` and other button-heavy files  
**Time**: 2 hours

**Create Utility Function** (add to UIStyleV2 or new utils file):
```python
def apply_button_hover_effects(button, active_color=None, hover_color=None):
    """Apply hover effects to a Tkinter button"""
    default_bg = button.cget("bg")
    default_fg = button.cget("fg")
    
    active_bg = active_color or UI.ACCENT_GREEN_BG
    active_fg = UI.ACCENT_GREEN if active_color else default_fg
    
    hover_bg = hover_color or UI.BORDER_PRIMARY
    hover_fg = UI.TEXT_PRIMARY if hover_color else default_fg
    
    def on_enter(event):
        button.config(bg=hover_bg, fg=hover_fg, relief="raised")
    
    def on_leave(event):
        button.config(bg=default_bg, fg=default_fg, relief="flat")
    
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
```

**Apply to All Sidebar Buttons** (in app_gui.py):
```python
# After creating each sidebar button:
btn.pack(fill="x", pady=2)

# Add hover effects
apply_button_hover_effects(
    btn,
    hover_color=UI.BORDER_PRIMARY,
    active_color=UI.ACCENT_GREEN_BG
)

self._sidebar_widgets.append((btn, key, view_target))
```

**After Task 4.2**: Buttons show visual feedback on hover

---

### Task 4.3: Implement Empty State Displays

**File**: `ui/components/empty_state.py` (new file)  
**Time**: 1 hour

```python
"""Empty state component for panels with no data"""

import tkinter as tk
from lib.ui_style_v2 import UIStyleV2 as UI


class EmptyState(tk.Frame):
    """Display empty state with icon, message, and guidance"""
    
    def __init__(self, parent, icon="•", message="No data", submessage="", **kwargs):
        super().__init__(parent, bg=UI.BG_BASE, **kwargs)
        
        # Vertical padding
        tk.Frame(self, bg=UI.BG_BASE, height=20).pack()
        
        # Icon (large, muted)
        icon_label = tk.Label(
            self,
            text=icon,
            font=(UI.FONT_FAMILY_UI_FALLBACK, 48),
            bg=UI.BG_BASE,
            fg=UI.TEXT_MUTED,
            fg_opacity=30  # Would need custom rendering for true opacity
        )
        icon_label.pack(pady=(20, 10))
        
        # Main message
        msg_label = tk.Label(
            self,
            text=message,
            font=(UI.FONT_FAMILY_UI_FALLBACK, 14),
            bg=UI.BG_BASE,
            fg=UI.TEXT_PRIMARY
        )
        msg_label.pack(pady=5)
        
        # Sub-message
        if submessage:
            sub_label = tk.Label(
                self,
                text=submessage,
                font=(UI.FONT_FAMILY_UI_FALLBACK, 11),
                bg=UI.BG_BASE,
                fg=UI.TEXT_MUTED,
                wraplength=300
            )
            sub_label.pack(pady=10)


# Usage in Hunt Tab:
# if not target_list:
#     empty = EmptyState(
#         panel,
#         icon="🎯",
#         message="Chưa có mục tiêu",
#         submessage="Nhấn + để thêm hoặc kéo từ danh sách quái"
#     )
#     empty.pack(fill="both", expand=True)
```

**After Task 4.3**: Can show helpful empty states in panels

---

## ✅ Implementation Checklist

### Phase 1: Sidebar (Days 1-2)
- [ ] Task 1.1: Add logo/branding to sidebar
- [ ] Task 1.2: Create icon mapping in UIStyleV2
- [ ] Task 1.3: Render icons in sidebar buttons
- [ ] Task 1.4: Implement active state styling
- [ ] **Test**: Run app, verify sidebar looks like spec

### Phase 2: Panels (Days 3-4)
- [ ] Task 2.1: Create StyledPanel component
- [ ] Task 2.2: Apply panel styling to all panels
- [ ] Task 2.3: Style tab bars with active states
- [ ] **Test**: Run app, verify borders and styling

### Phase 3: Typography (Days 5-6)
- [ ] Task 3.1: Audit font usage
- [ ] Task 3.2: Replace hardcoded fonts
- [ ] Task 3.3: Verify contrast ratios
- [ ] **Test**: Check readability at different zoom levels

### Phase 4: Polish (Days 7-8)
- [ ] Task 4.1: Create status badge component
- [ ] Task 4.2: Add button hover effects
- [ ] Task 4.3: Create empty state component
- [ ] **Test**: Full app testing across all views

---

## 🧪 Testing Protocol

### After Each Phase:

1. **Visual Inspection**:
   ```bash
   python app_gui.py
   # Check:
   # - No Python errors
   # - No layout breaking
   # - Colors match spec
   # - Text is readable
   ```

2. **At Different Resolutions**:
   - 1024×600 (minimum)
   - 1366×768 (target)
   - 1920×1080 (large)

3. **Language Testing**:
   - Switch to Vi (if UI supports)
   - Switch to En
   - Verify no text overlap

4. **Component Interaction**:
   - Click sidebar items → verify active state updates
   - Click tab buttons → verify tab styling updates
   - Hover over buttons → verify effects appear
   - Navigate with keyboard → verify focus is visible

---

## 📊 Implementation Dependency Graph

```
Phase 1 (Sidebar)
├─ Task 1.1 (Logo)
├─ Task 1.2 (Icon Mapping)
├─ Task 1.3 (Icons in Buttons) ← Depends on 1.1 & 1.2
└─ Task 1.4 (Active State) ← Depends on 1.3

Phase 2 (Panels) ← Can start after Phase 1.4
├─ Task 2.1 (StyledPanel Component)
├─ Task 2.2 (Apply to Panels) ← Depends on 2.1
└─ Task 2.3 (Tab Styling) ← Depends on 2.2

Phase 3 (Typography) ← Can start after Phase 2.2
├─ Task 3.1 (Audit)
├─ Task 3.2 (Replace Fonts) ← Depends on 3.1
└─ Task 3.3 (Contrast Check) ← Depends on 3.2

Phase 4 (Polish) ← Can start after Phase 3.3
├─ Task 4.1 (Status Badge)
├─ Task 4.2 (Hover Effects)
└─ Task 4.3 (Empty States)
```

---

## 💾 File Summary

### Files to Create:
- `ui/components/styled_panel.py` — Panel component
- `ui/components/status_badge.py` — Status badge component  
- `ui/components/empty_state.py` — Empty state component
- `scripts/audit_fonts.py` — Font auditing script
- `scripts/verify_contrast.py` — Contrast verification

### Files to Modify:
- `app_gui.py` — Sidebar + overall styling
- `lib/ui_style_v2.py` — Add icon mapping
- `ui/tabs/hunt_tab.py` — Panel and tab styling
- All other UI files — Font/color consistency

---

## ⏱️ Time Estimate Summary

| Phase | Days | Key Tasks |
|-------|------|-----------|
| **Phase 1** | 2 | Logo, icons, active state |
| **Phase 2** | 2 | Panels, borders, tabs |
| **Phase 3** | 2 | Typography, fonts, contrast |
| **Phase 4** | 2-3 | Badges, effects, polish |
| **Testing** | 1 | All resolutions, languages |
| **TOTAL** | 8-10 | Full redesign completion |

---

## 🎯 Success Criteria Checklist

By end of implementation:

- [ ] Sidebar has CABAL ASSISTANT logo with sword icon
- [ ] All menu items have icons (emoji)
- [ ] Active menu item highlighted in green
- [ ] All panels have visible 1px borders
- [ ] Tab bars styled with active state highlighting
- [ ] Font sizes consistent throughout (using UIStyleV2)
- [ ] Text meets WCAG AA contrast standards
- [ ] Status badges show color-coded states
- [ ] Buttons show hover effects
- [ ] Empty states appear in panels with no data
- [ ] App works at 1024×600, 1366×768, 1920×1080
- [ ] No visual glitches or layout breaking
- [ ] Vietnamese and English both display correctly

---

**Document Version**: 1.0  
**Created**: 2026-09-06  
**Next Review**: After Phase 1 completion (Day 2)
