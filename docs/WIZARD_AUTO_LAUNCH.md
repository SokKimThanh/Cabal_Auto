# Setup Wizard Auto-Launch Documentation

## 📋 Overview

The Setup Wizard now **automatically detects first-time users** and offers to guide them through initial configuration. This eliminates confusion about how to start using the application.

## 🔍 How It Works

### **1. Application Startup**

When you run `app_gui.py`:

```python
def __init__(self):
    # ... load config and build UI ...
    self._build_ui()
    
    # Auto-launch wizard check (500ms delay to ensure UI is ready)
    self.after(500, self._check_first_time_setup)
```

### **2. First-Time Detection Logic**

The app checks if you're a **new user** by looking at `hunt_config.json`:

```python
def _check_first_time_setup(self):
    """Check if this is first-time user and auto-launch wizard if needed."""
    is_new_user = (
        not self.hunt_cfg.get('window_title') or      # No game window configured
        not self.hunt_cfg.get('monster_selected_name') or  # No monster selected
        not self.hunt_cfg.get('skill_slots')           # No skills configured
    )
```

**You are considered a NEW USER if:**
- ❌ No game window has been selected (`window_title` missing)
- ❌ No monster has been chosen (`monster_selected_name` missing)
- ❌ No skills have been configured (`skill_slots` empty/missing)

**You are considered an EXISTING USER if:**
- ✅ All three settings above are present in `hunt_config.json`

### **3. User Prompt**

If you're detected as a new user, you'll see this dialog:

```
╔══════════════════════════════════════════════════╗
║  Welcome to Cabal Auto Hunt!                     ║
║                                                  ║
║  It looks like this is your first time using    ║
║  Cabal Auto Hunt.                                ║
║                                                  ║
║  Would you like to run the Setup Wizard to      ║
║  configure your settings?                        ║
║                                                  ║
║  The wizard will guide you through:             ║
║    • Selecting your game window                 ║
║    • Choosing a monster to hunt                 ║
║    • Configuring your attack skills             ║
║                                                  ║
║  You can always run the wizard later by         ║
║  clicking the '🧙 Setup Wizard' button.          ║
║                                                  ║
║          [  Yes  ]        [  No  ]              ║
╚══════════════════════════════════════════════════╝
```

### **4. User Choices**

#### **Option A: Click "Yes"**
- ✅ Wizard launches immediately
- 🧙 You'll go through 5 steps:
  1. **Welcome** - Choose language (EN/VI)
  2. **Window** - Select game window (auto-searched)
  3. **Monster** - Choose monster from library
  4. **Skills** - Configure 9 skill slots
  5. **Review** - Verify settings and save

#### **Option B: Click "No"**
- ⏭️ Wizard is skipped
- 💡 Status bar shows hint:
  - EN: `"Setup wizard skipped. Click '🧙 Setup Wizard' button to run it later."`
  - VI: `"Đã bỏ qua trợ lý. Nhấn nút '🧙 Trợ lý thiết lập' để chạy sau."`
- 🔘 Manual wizard button remains available in Hunt tab

## 🎯 Use Cases

### **Scenario 1: Brand New User**

```
1. Download project
2. Run: python app_gui.py
3. See welcome dialog → Click "Yes"
4. Complete wizard (2-3 minutes)
5. Start hunting immediately
```

**Result:** ✅ Fully configured, ready to hunt

---

### **Scenario 2: Returning User**

```
1. Already have hunt_config.json with:
   - window_title: "Cabal Online"
   - monster_selected_name: "Coc go~"
   - skill_slots: ["Dark Explosion", "Fire Ball", ...]
2. Run: python app_gui.py
3. NO wizard prompt (auto-detected as existing user)
4. App loads previous settings
```

**Result:** ✅ No interruption, seamless continuation

---

### **Scenario 3: Partial Setup (Returning but Incomplete)**

```
1. Previously configured window + monster
2. BUT deleted skill_slots from config
3. Run: python app_gui.py
4. See welcome dialog (detected as incomplete setup)
5. Choose Yes/No
```

**Result:** ✅ Catches incomplete configurations

---

### **Scenario 4: Manual Wizard Launch**

```
1. Existing user wants to reconfigure
2. Click '🧙 Setup Wizard' button in Hunt tab
3. Wizard launches (same 5 steps)
4. Can update window/monster/skills
5. Overwrites previous config
```

**Result:** ✅ Full reconfiguration anytime

## 🔧 Technical Details

### **Timing**

- **Delay:** 500ms after UI build
- **Why?** Ensures main window is fully rendered before showing dialog
- **Method:** `self.after(500, self._check_first_time_setup)`

### **Config Check**

```python
# Loaded from hunt_config.json
self.hunt_cfg = load_hunt_config()

# Checked fields:
window_title          # String - game window title
monster_selected_name # String - monster name
skill_slots           # Array - list of skill configs
```

### **Dialog Blocking**

- ✅ Modal dialog (blocks main window until answered)
- ✅ Must click Yes/No (cannot ignore)
- ✅ ESC closes dialog = same as clicking "No"

### **Localization**

Both English and Vietnamese messages:

```python
'wizard_first_time_title': {
    'en': 'Welcome to Cabal Auto Hunt!',
    'vi': 'Chào mừng đến Cabal Auto Hunt!'
}

'wizard_first_time_message': {
    'en': 'It looks like this is your first time...',
    'vi': 'Có vẻ đây là lần đầu bạn sử dụng...'
}
```

## 🚀 Benefits

### **For New Users:**
1. ✅ **No confusion** - Clear prompt on first run
2. ✅ **Guided setup** - Step-by-step wizard
3. ✅ **Time-saving** - 2-3 minutes to full configuration
4. ✅ **Skippable** - Can skip if prefer manual setup

### **For Existing Users:**
1. ✅ **No interruption** - Auto-detected, no prompts
2. ✅ **Seamless** - Loads previous settings
3. ✅ **Reconfigurable** - Manual wizard button always available

### **For Developers:**
1. ✅ **User-friendly** - Reduces support questions
2. ✅ **Onboarding** - Better first impression
3. ✅ **Testable** - Clear detection logic
4. ✅ **Maintainable** - Single method (`_check_first_time_setup`)

## 📝 Code Changes Summary

### **Files Modified:**
- `app_gui.py`: +60 lines

### **New Methods:**
```python
def _check_first_time_setup(self):
    """Auto-detect new user and prompt for wizard."""
    # Check if basic config exists
    # Show Yes/No dialog
    # Launch wizard or show skip hint
```

### **New Strings (Localized EN/VI):**
- `wizard_first_time_title`
- `wizard_first_time_message`
- `wizard_skipped_hint`

### **Initialization Hook:**
```python
self._build_ui()
self.after(500, self._check_first_time_setup)  # NEW
```

## 🧪 Testing

### **Test Case 1: Fresh Install**
1. Delete `hunt_config.json`
2. Run `python app_gui.py`
3. **Expected:** See welcome dialog

### **Test Case 2: Existing Config**
1. Ensure `hunt_config.json` has window + monster + skills
2. Run `python app_gui.py`
3. **Expected:** NO dialog, loads normally

### **Test Case 3: Empty Config**
1. Create `hunt_config.json` with `{}`
2. Run `python app_gui.py`
3. **Expected:** See welcome dialog

### **Test Case 4: Partial Config**
1. `hunt_config.json` has window only (no monster/skills)
2. Run `python app_gui.py`
3. **Expected:** See welcome dialog

### **Test Case 5: Manual Button**
1. Click '🧙 Setup Wizard' button
2. **Expected:** Wizard launches regardless of config state

## 🎓 User Journey

```
┌──────────────────────────────────────────────────┐
│  First Run: python app_gui.py                    │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│  Load hunt_config.json                           │
│  Check: window? monster? skills?                 │
└──────────────┬───────────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
   ALL EXIST      MISSING
        │             │
        ▼             ▼
┌─────────────┐  ┌─────────────────────────────┐
│ Skip wizard │  │ Show "Welcome" Dialog       │
│ Load config │  │ "Run wizard?" [Yes] [No]    │
│ Start app   │  └──────────┬──────────────────┘
└─────────────┘             │
                      ┌─────┴─────┐
                      │           │
                    YES          NO
                      │           │
                      ▼           ▼
              ┌────────────┐  ┌──────────────┐
              │ Launch     │  │ Show hint    │
              │ Wizard     │  │ in status    │
              │ (5 steps)  │  │ bar          │
              └────────────┘  └──────────────┘
```

## 📚 Related Documentation

- [SPRINT16_TASK4_IMPLEMENTATION.md](sprints/SPRINT16_TASK4_IMPLEMENTATION.md) - Wizard welcome screen
- [SPRINT16_TASK5_IMPLEMENTATION.md](sprints/SPRINT16_TASK5_IMPLEMENTATION.md) - Wizard steps 2-5
- [setup_wizard.py](../setup_wizard.py) - Wizard implementation

## 🔮 Future Enhancements

1. **Smart Re-prompting:** If user skips wizard 3+ times, show reminder hint
2. **Onboarding Checklist:** Visual checklist showing configuration progress
3. **Tutorial Mode:** Optional tutorial overlay during first hunt
4. **Config Migration:** Auto-upgrade old configs and prompt re-wizard
5. **First-Run Tips:** Show tooltips on first interaction with each UI element

---

**Last Updated:** 2025-01-18 (Sprint 16 Phase 2)
