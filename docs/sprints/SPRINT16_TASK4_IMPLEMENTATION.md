# Sprint 16 Task #4: Setup Wizard - Welcome Screen
**Status:** ✅ COMPLETED  
**Date:** 2025-01-18  
**LOC Added:** ~450 lines  
**Files Created:** `setup_wizard.py`  
**Files Modified:** `app_gui.py` (+15 lines)

## 1. Overview

Task #4 creates the **Setup Wizard foundation** - a friendly 5-step guide for first-time users to configure Cabal Auto Hunt in ~2 minutes. This task implements:
- Complete wizard UI structure with progress indicator
- Step 1: Welcome screen with language selection (EN/VI)
- Placeholder steps 2-5 (will be implemented in Task #5)
- Integration into main app with "🧙 Setup Wizard" button

### User Experience Goal
- **Before**: Users manually fill 20+ fields, risk misconfiguration
- **After**: Wizard guides through 5 easy steps: Welcome → Window → Monster → Skills → Review

---

## 2. Technical Implementation

### 2.1 Module Structure: `setup_wizard.py`

**File:** `setup_wizard.py` (~450 lines)

```python
"""
Setup Wizard for Cabal Auto Hunt
Sprint 16 Phase 2 - Task #4: Welcome Screen

5-step wizard to guide new users through initial setup:
1. Welcome & Language Selection
2. Game Window Calibration
3. Monster Selection
4. Skill Configuration
5. Final Review & Save
"""
```

### 2.2 SetupWizard Class

**Key Components:**

1. **Initialization:**
   ```python
   class SetupWizard:
       def __init__(self, parent, config_manager=None, on_complete=None):
           self.current_step = 1
           self.total_steps = 5
           self.language = 'en'
           
           self.wizard_data = {
               'language': 'en',
               'window_title': '',
               'monster_name': '',
               'skill_slots': [],
               'timing': {...}
           }
   ```

2. **Dialog Window:**
   - Modal Toplevel (600x500)
   - Centered on screen
   - Blocks interaction with parent until closed
   - `transient()` + `grab_set()` for modality

3. **UI Structure:**
   ```
   ┌─────────────────────────────────────┐
   │ Header (Progress Indicator)         │  60px gray bg
   │   "Step 1 of 5"                     │
   │   ● ○ ○ ○ ○  (progress dots)       │
   ├─────────────────────────────────────┤
   │                                     │
   │ Content Area (White)                │  Expands
   │   [Step-specific UI goes here]     │
   │                                     │
   ├─────────────────────────────────────┤
   │ Footer (Navigation Buttons)         │  60px gray bg
   │   [← Back] [Next →] [Cancel]       │
   └─────────────────────────────────────┘
   ```

### 2.3 Step 1: Welcome Screen

**UI Elements:**

```python
def _build_step1_welcome(self):
    # Title
    "🎉 Welcome to Cabal Auto Hunt!"  # 18pt bold
    
    # Subtitle
    "Let's get you set up in just 5 easy steps"  # 12pt gray
    
    # Info text
    """This wizard will help you:
    ✓ Select your game window
    ✓ Choose monsters to hunt
    ✓ Configure your attack skills
    ✓ Set up optimal timing
    
    It takes about 2 minutes. Let's begin!"""
    
    # Language selector (LabelFrame)
    "Choose Your Language / Chọn ngôn ngữ"
    - 🇬🇧 English (radio button)
    - 🇻🇳 Tiếng Việt (radio button)
    
    # Hint
    "Click 'Next' to get started →"  # Italic gray
```

**Language Selection:**
- `self.language_var` StringVar tracks selection
- `_on_language_change()` updates `wizard_data['language']`
- Future: Will trigger UI text updates when implemented

### 2.4 Placeholder Steps 2-5

Each step has a simple placeholder UI:

```python
def _build_step2_window(self):
    title = "Step 2: Select Game Window"
    placeholder = "[Window selection UI will be implemented in Task #5]"

# Similar for steps 3, 4, 5
```

**Reason:** Task #4 focuses on wizard foundation. Task #5 will implement actual step logic.

### 2.5 Navigation System

**Back/Next/Cancel Buttons:**

```python
def _on_back(self):
    """Navigate to previous step."""
    if self.current_step > 1:
        self._show_step(self.current_step - 1)

def _on_next(self):
    """Navigate to next step or finish wizard."""
    if self.current_step < self.total_steps:
        if self._validate_current_step():  # Validation check
            self._show_step(self.current_step + 1)
    else:
        self._on_finish()  # Last step
```

**Button State Management:**
- Back button: Disabled on step 1, enabled on steps 2-5
- Next button: "Next →" (green) on steps 1-4, "Finish" (blue) on step 5
- Cancel button: Always enabled, shows confirmation dialog

**Progress Indicator:**
- Dots: Green (●) for completed/current steps, Gray (○) for upcoming
- Label: "Step X of 5"
- Updates automatically when `_show_step()` called

### 2.6 Completion Flow

```python
def _on_finish(self):
    """Complete wizard and save configuration."""
    confirm = messagebox.askyesno(
        "Finish Setup",
        "Save this configuration and start hunting?",
        parent=self.dialog
    )
    
    if confirm:
        # Save wizard data via config_manager (Task #5)
        if self.config_manager:
            self._save_wizard_config()
        
        # Call completion callback
        if self.on_complete:
            self.on_complete(self.wizard_data)
        
        # Close wizard
        self.dialog.destroy()
```

**Cancel Flow:**
```python
def _on_cancel(self):
    confirm = messagebox.askyesno(
        "Cancel Setup",
        "Are you sure you want to cancel the setup wizard?",
        parent=self.dialog
    )
    
    if confirm:
        self.dialog.destroy()
```

---

## 3. Integration with `app_gui.py`

### 3.1 Import

Added to imports section (~line 32):
```python
from setup_wizard import show_setup_wizard
```

### 3.2 Localization Strings

**English (line ~94):**
```python
'setup_wizard': '🧙 Setup Wizard',
```

**Vietnamese (line ~247):**
```python
'setup_wizard': '🧙 Trợ lý thiết lập',
```

### 3.3 UI Button

Added to Hunt buttons section (row 14, ~line 948):
```python
# Hunt buttons
hbtn = tk.Frame(frm)
hbtn.grid(row=14, column=0, columnspan=4, pady=(12,0))

# NEW: Setup Wizard button (leftmost position)
tk.Button(hbtn, text=self._t('setup_wizard'), command=self.on_setup_wizard, 
          font=('Arial', 9, 'bold'), fg='#2196F3').pack(side='left')

# Existing buttons
tk.Button(hbtn, text=self._t('save_hunt'), command=self.on_hunt_save).pack(side='left', padx=(8,0))
self.hunt_start_btn = tk.Button(hbtn, text=self._t('start_hunt'), command=self.on_hunt_start)
# ...
```

**Button Style:**
- Bold font (9pt Arial)
- Blue text (#2196F3) to stand out as primary action
- Wizard icon 🧙 for visual appeal

### 3.4 Event Handler

Added method (~line 1350):
```python
def on_setup_wizard(self):
    """Launch setup wizard to guide user through initial configuration."""
    def on_wizard_complete(wizard_data):
        """Callback when wizard completes - apply settings to UI."""
        # Apply wizard data to hunt config
        # (Will be fully implemented in Task #5)
        self.hunt_status.set(f"Wizard completed - Language: {wizard_data.get('language', 'en')}")
    
    # Launch wizard
    show_setup_wizard(self.root, config_manager=self.config_mgr, on_complete=on_wizard_complete)
```

**Callback Pattern:**
- Wizard returns `wizard_data` dict when user clicks Finish
- Callback applies settings to UI and config
- Task #5 will implement full data application logic

---

## 4. Convenience Function

```python
def show_setup_wizard(parent, config_manager=None, on_complete=None):
    """
    Convenience function to show setup wizard.
    
    Args:
        parent: Parent tkinter window
        config_manager: ConfigManager instance (optional)
        on_complete: Callback when wizard completes (optional)
    
    Returns:
        SetupWizard instance
    """
    wizard = SetupWizard(parent, config_manager, on_complete)
    return wizard
```

**Benefits:**
- Simple API: `show_setup_wizard(parent)`
- Optional config_manager integration
- Callback support for data flow

---

## 5. Demo/Test Code

**Standalone test** at end of `setup_wizard.py`:

```python
if __name__ == "__main__":
    # Create test window
    root = tk.Tk()
    root.title("Setup Wizard Test")
    root.geometry("400x300")
    
    def on_wizard_complete(data):
        print("Wizard completed with data:", data)
    
    # Button to launch wizard
    launch_btn = tk.Button(
        root,
        text="Launch Setup Wizard",
        command=lambda: show_setup_wizard(root, on_complete=on_wizard_complete),
        font=('Arial', 12),
        padx=20,
        pady=10
    )
    launch_btn.pack(expand=True)
    
    root.mainloop()
```

**Usage:**
```powershell
.\venv\Scripts\python.exe setup_wizard.py
```

---

## 6. Design Decisions

### 6.1 Modal Dialog
- **Choice:** `Toplevel` + `transient()` + `grab_set()`
- **Reason:** Forces user to complete wizard or cancel, prevents confusion
- **Alternative:** Non-modal would allow clicking main window, could disrupt workflow

### 6.2 Progress Dots
- **Choice:** ● (U+25CF Black Circle) instead of progress bar
- **Reason:** 5 steps fit perfectly, dots are clearer than percentage
- **Alternative:** Progress bar would require more space

### 6.3 White Content Area
- **Choice:** White background for content, gray for header/footer
- **Reason:** Creates visual hierarchy, content stands out
- **Alternative:** All gray would be less inviting

### 6.4 Language Selector in Step 1
- **Choice:** Built into welcome screen, not separate dialog
- **Reason:** Reduces clicks, shows wizard purpose immediately
- **Alternative:** Separate language dialog adds extra step

### 6.5 Placeholder Steps
- **Choice:** Simple "Coming in Task #5" text for steps 2-5
- **Reason:** Task #4 focuses on structure, Task #5 on content
- **Alternative:** Implementing all steps now would exceed task scope

---

## 7. Task #5 Preview

**Next Implementation (Steps 2-5):**

1. **Step 2: Game Window Calibration** (~100 lines)
   - List windows with PID/HWND (reuse `enumerate_windows_info()`)
   - Filter by "Cabal" keyword
   - Selection: Click to select, highlight row
   - Validation: Ensure window selected before Next

2. **Step 3: Monster Selection** (~100 lines)
   - Load `monsters.json`
   - Display monster list with names
   - Thumbnail preview (if templates exist)
   - Selection: Radio buttons or listbox
   - Validation: Ensure monster selected

3. **Step 4: Skill Configuration** (~100 lines)
   - Load `skills.json`
   - Display skill list with icons
   - 9 skill slots (drag-drop or combobox)
   - Clear slots button
   - Validation: At least 1 skill assigned

4. **Step 5: Final Review** (~50 lines)
   - Display summary:
     - Window: "{title}" (PID: {pid})
     - Monster: "{name}" ({X} templates)
     - Skills: [slot1, slot2, ...]
     - Timing: lost_timeout={X}s, attack_duration={Y}s
   - Edit buttons: Go back to specific step
   - Finish: Save to `hunt_config.json`, close wizard, apply to UI

**Estimated Task #5:** ~350 lines

---

## 8. Testing Results

**Manual Testing:**
1. ✅ Wizard launches from main app "Setup Wizard" button
2. ✅ Modal dialog blocks main window interaction
3. ✅ Welcome screen displays with language selector
4. ✅ Language selection updates `wizard_data`
5. ✅ Next button advances to placeholder steps 2-5
6. ✅ Back button navigates to previous steps (disabled on step 1)
7. ✅ Progress dots update correctly (green/gray)
8. ✅ Cancel button shows confirmation dialog
9. ✅ Finish button (step 5) shows confirmation, calls callback
10. ✅ Callback receives `wizard_data` dict
11. ✅ No errors in console

**Code Quality:**
- ✅ No syntax errors (`get_errors` tool)
- ✅ Clean separation: wizard logic in `setup_wizard.py`, integration in `app_gui.py`
- ✅ Modular design: Easy to extend steps in Task #5

---

## 9. Code Statistics

**Lines Added:**
- `setup_wizard.py`: ~450 lines (new file)
  - SetupWizard class: ~380 lines
  - Helper function: ~15 lines
  - Test code: ~40 lines
  - Docstrings/comments: ~15 lines

- `app_gui.py`: +15 lines
  - Import: 1 line
  - Localization (EN): 1 line
  - Localization (VI): 1 line
  - Button: 2 lines
  - Handler method: 10 lines

**Total:** ~465 lines

**Files Created:** 1
- `setup_wizard.py`

**Files Modified:** 1
- `app_gui.py`

---

## 10. Future Enhancements (Post-Sprint 16)

**Potential Improvements:**
1. **Step animations:** Fade in/out transitions between steps
2. **Progress persistence:** Save wizard progress, resume if interrupted
3. **Tooltips:** Hover hints on each step's fields
4. **Preview panel:** Live preview of config as user makes selections
5. **Undo/Redo:** Navigate history without losing changes
6. **Themes:** Light/dark mode for wizard
7. **Auto-skip:** If config already exists, offer "Skip wizard" button
8. **Help button:** Context-sensitive help on each step

**Known Limitations:**
- Steps 2-5 are placeholders (will be fixed in Task #5)
- No validation logic yet (Task #5)
- Language change doesn't update UI text dynamically (not needed for current scope)

---

## 11. Integration Checklist

**Completed:**
- ✅ `setup_wizard.py` module created
- ✅ SetupWizard class with 5-step structure
- ✅ Step 1: Welcome + language selection
- ✅ Placeholder steps 2-5
- ✅ Modal dialog with proper parenting
- ✅ Progress indicator (dots + label)
- ✅ Navigation buttons (Back/Next/Cancel/Finish)
- ✅ Button state management
- ✅ Localization strings (EN/VI)
- ✅ "🧙 Setup Wizard" button in Hunt tab
- ✅ `on_setup_wizard()` handler in `app_gui.py`
- ✅ Callback pattern for data flow
- ✅ Test code for standalone demo
- ✅ No errors, app runs successfully

**Pending (Task #5):**
- ⏳ Step 2: Window calibration UI
- ⏳ Step 3: Monster selection UI
- ⏳ Step 4: Skill configuration UI
- ⏳ Step 5: Review + save logic
- ⏳ Validation at each step
- ⏳ Apply wizard data to hunt config
- ⏳ Update main UI after wizard completion

---

## 12. Lessons Learned

1. **Modal Dialogs:** `transient()` + `grab_set()` is the right pattern for wizards - prevents confusion
2. **Progress Indicators:** Visual feedback (dots) is crucial for multi-step flows
3. **Placeholder Strategy:** Implementing structure first (Task #4), then content (Task #5) keeps tasks focused
4. **Callback Pattern:** Clean separation between wizard logic and main app integration
5. **Standalone Testing:** `if __name__ == "__main__"` test code speeds up development
6. **Button Styling:** Bold + color draws attention to primary actions
7. **Confirmation Dialogs:** Always confirm destructive actions (Cancel, Finish without saving)

---

**Implementation Log:**
- setup_wizard.py created: ~450 lines
- app_gui.py integration: +15 lines
- 0 errors, clean test run
- Modal wizard functional
- Ready for Task #5 step implementation

**Status:** ✅ READY FOR TASK #5
