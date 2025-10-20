# Setup Wizard First-Run Lock Feature

## Overview
The Setup Wizard now includes a **first-run detection system** that automatically locks the "Experienced User" option for first-time users, preventing accidental misconfigurations. The feature also ensures all UI texts update dynamically when the language is changed.

## Features

### 1. First-Run Detection
- **Detection Method**: Checks `lib/data/hunt_config.json` for completeness
- **First-Run Criteria**: User is considered "first-time" if any of these are missing or empty:
  - `window_title` is empty or missing
  - `monster_list` is empty or missing
  - `skill_slots` is empty or missing

### 2. Locked "Experienced User" Option
- **When Locked**: First-time users (incomplete or missing config)
- **Visual Indicators**:
  - Radio button is disabled (grayed out, not clickable)
  - Hint label appears: "First-time users must start with 'New User' option"
  - Bilingual hint (English + Vietnamese)
  
- **When Unlocked**: Returning users (complete config exists)
  - Both "New User" and "Experienced User" are selectable
  - No restriction hint is shown

### 3. Dynamic Language Updates
- **What Updates**: When language is switched (English ↔ Vietnamese), the following UI elements update:
  - Radio button labels ("New User" ↔ "Người mới")
  - Radio button descriptions
  - User level group title
  - First-time hint text (if visible)
  - Radio button tooltips (auto-update on hover)

- **How It Works**:
  - Language change handler refreshes all user level texts
  - Tooltips use `lang_provider` lambda to resolve language at show-time
  - No page refresh needed - updates happen instantly

## Technical Implementation

### Files Modified

#### 1. `ui/setup_wizard.py`
**New Methods:**
- `_detect_first_run()`: Checks hunt_config.json completeness
  - Returns `True` if config is missing or incomplete
  - Returns `False` if config has all required fields

**New State:**
- `self.is_first_run`: Boolean flag stored in wizard instance
  - Set during `__init__` by calling `_detect_first_run()`
  - Used to control radio button state

**Enhanced Methods:**
- `_build_step1_welcome()`: 
  - Stores radio button references: `self.level_new_radio`, `self.level_experienced_radio`
  - Disables "Experienced User" radio if `self.is_first_run=True`
  - Shows hint label if `self.is_first_run=True`
  
- `_on_language_change()`:
  - Updates radio button texts using `self._t()`
  - Updates description label texts
  - Updates hint label text (if visible)
  - All updates respect current language setting

#### 2. `lib/i18n/translations.py`
**New Translation Keys:**

**English (`SETUP_WIZARD_TRANSLATIONS['en']`):**
```python
'first_time_user_hint': 'First-time users must start with \'New User\' option',
```

**Vietnamese (`SETUP_WIZARD_TRANSLATIONS['vi']`):**
```python
'first_time_user_hint': 'Người dùng lần đầu phải bắt đầu với tùy chọn \'Người mới\'',
```

## Usage

### For Developers

#### Testing First-Run Detection
```python
# Run the comprehensive test suite
python tests\test_wizard_first_run_lock.py
```

The test suite provides 4 scenarios:
1. **First-Time User (Locked)**: Verifies "Experienced User" is disabled
2. **Returning User (Unlocked)**: Verifies both options are enabled
3. **Language Switching (Locked)**: Tests dynamic updates with lock
4. **Language Switching (Unlocked)**: Tests dynamic updates without lock

#### Simulating First-Time User
```python
# Create incomplete config
config_path = Path('lib/data/hunt_config.json')
incomplete_config = {
    "version": "1.0",
    "window_title": "",     # Empty triggers first-run
    "monster_list": [],      # Empty triggers first-run
    "skill_slots": []        # Empty triggers first-run
}
with open(config_path, 'w') as f:
    json.dump(incomplete_config, f, indent=2)
```

#### Simulating Returning User
```python
# Create complete config
complete_config = {
    "version": "1.0",
    "window_title": "CABAL Online",
    "monster_list": ["Dummy Monster"],
    "skill_slots": [
        {"slot": 1, "name": "Skill 1", "key": "1"}
    ]
}
with open(config_path, 'w') as f:
    json.dump(complete_config, f, indent=2)
```

### For End Users

#### First-Time Setup
1. Launch the application
2. Setup Wizard opens automatically
3. In Step 1, notice:
   - "New User" option is pre-selected
   - "Experienced User" option is grayed out (disabled)
   - Hint message explains why it's locked
4. Complete the wizard as "New User" to get guided help

#### Returning User Setup
1. Launch the application (with existing config)
2. Open Setup Wizard from menu
3. In Step 1, notice:
   - Both "New User" and "Experienced User" are selectable
   - No restriction hint is shown
4. Choose your preferred level

#### Changing Language
1. Open Setup Wizard
2. Click language toggle (🇺🇸 ↔ 🇻🇳)
3. Notice all texts update instantly:
   - Radio button labels
   - Descriptions
   - Group titles
   - Hint messages (if visible)
4. Hover over radio buttons to verify tooltips update

## Benefits

### For New Users
- **Prevents Mistakes**: Can't accidentally skip guided setup
- **Clear Guidance**: Hint explains why option is locked
- **Smooth Onboarding**: Ensures proper configuration from the start

### For Experienced Users
- **No Restrictions**: Full access after first setup
- **Time Savings**: Can skip extra guidance steps
- **Flexibility**: Choose level based on familiarity

### For Developers
- **Automatic Detection**: No manual flag management
- **Bilingual Support**: Works seamlessly in both languages
- **Maintainable**: Uses existing i18n system

## Code Examples

### First-Run Detection Logic
```python
def _detect_first_run(self) -> bool:
    """Detect if this is the first time the user is running the wizard."""
    config_path = Path(__file__).parent.parent / 'lib' / 'data' / 'hunt_config.json'
    
    if not config_path.exists():
        return True  # No config = first run
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check for required fields
        window_title = config.get('window_title', '')
        monster_list = config.get('monster_list', [])
        skill_slots = config.get('skill_slots', [])
        
        # First-run if any required field is missing or empty
        if not window_title or not monster_list or not skill_slots:
            return True
        
        return False  # Config is complete
    except Exception:
        return True  # Error reading config = first run
```

### Radio Button Lock Logic
```python
# In _build_step1_welcome():
# Store radio button references for dynamic updates
self.level_new_radio = tk.Radiobutton(...)
self.level_experienced_radio = tk.Radiobutton(...)

# Lock experienced option for first-time users
if self.is_first_run:
    self.level_experienced_radio.config(state='disabled')
    
    # Show hint label
    hint = tk.Label(
        level_frame,
        text=self._t('first_time_user_hint'),
        fg='#856404',
        bg='#fff3cd',
        font=('Arial', 9, 'italic'),
        anchor='w'
    )
    hint.pack(fill='x', padx=10, pady=(5, 0))
    self.first_time_hint = hint  # Store reference for language updates
```

### Dynamic Language Update
```python
def _on_language_change(self, new_lang: str):
    """Update all UI texts when language changes."""
    self.lang = new_lang
    
    # ... other UI updates ...
    
    # Update user level texts if widgets exist
    if hasattr(self, 'level_new_radio') and self.level_new_radio.winfo_exists():
        self.level_new_radio.config(text=self._t('user_level_new'))
    
    if hasattr(self, 'level_new_desc') and self.level_new_desc.winfo_exists():
        self.level_new_desc.config(text=self._t('user_level_new_desc'))
    
    if hasattr(self, 'level_experienced_radio') and self.level_experienced_radio.winfo_exists():
        self.level_experienced_radio.config(text=self._t('user_level_experienced'))
    
    if hasattr(self, 'level_experienced_desc') and self.level_experienced_desc.winfo_exists():
        self.level_experienced_desc.config(text=self._t('user_level_experienced_desc'))
    
    # Update first-time hint if visible
    if hasattr(self, 'first_time_hint') and self.first_time_hint.winfo_exists():
        self.first_time_hint.config(text=self._t('first_time_user_hint'))
```

## Testing Checklist

### Manual Testing
- [ ] First-time user sees locked "Experienced User" option
- [ ] First-time hint is visible and correct
- [ ] Returning user can select both options
- [ ] No hint shown for returning users
- [ ] Language switch updates all texts (first-time user)
- [ ] Language switch updates all texts (returning user)
- [ ] Tooltips show in correct language after switch
- [ ] Radio button state persists across language changes

### Automated Testing
Run the test suite:
```bash
python tests\test_wizard_first_run_lock.py
```

Test all 4 scenarios:
1. First-Time User (Locked Option)
2. Returning User (Unlocked Option)
3. Language Switching (First-Time User)
4. Language Switching (Returning User)

## Known Limitations

1. **Config Detection Only**: Only checks hunt_config.json, doesn't verify other setup aspects
2. **Manual Override Not Available**: No way for user to manually override the lock (by design)
3. **Cache Reset Required**: Deleting/emptying hunt_config.json resets to first-run state

## Future Enhancements

1. **Setup Progress Tracking**: Track which wizard steps have been completed
2. **User Preference Override**: Allow advanced users to bypass lock via settings
3. **Multi-File Detection**: Check additional config files for completeness
4. **First-Run Tutorial**: Add interactive tutorial for new users

## Troubleshooting

### Issue: "Experienced User" is locked but I'm not a first-time user
**Solution**: Check `lib/data/hunt_config.json` and ensure it has:
- Non-empty `window_title`
- Non-empty `monster_list`
- Non-empty `skill_slots`

### Issue: Language switch doesn't update texts
**Solution**: 
1. Verify translations exist in `lib/i18n/translations.py`
2. Check widget references are stored correctly
3. Ensure `_on_language_change()` is called on language toggle

### Issue: Tooltips show wrong language
**Solution**: Tooltips use `lang_provider` lambda - they should auto-update. If not:
1. Check tooltip uses `attach_i18n_tooltip()` with `lang_provider=lambda: self.lang`
2. Verify `self.lang` is updated in `_on_language_change()`

## Related Documentation

- [Setup Wizard User Guide](./HUONG_DAN_NGUOI_MOI.md)
- [i18n System Documentation](../lib/i18n/README.md)
- [Sprint 20 Context](./sprints/CONTEXT_UPDATE_SPRINT18_PHASE4.md)

## Changelog

### Version 1.0 (Current)
- ✅ Implemented first-run detection using hunt_config.json
- ✅ Added radio button lock for first-time users
- ✅ Added bilingual hint label
- ✅ Implemented dynamic language updates for user level section
- ✅ Auto-updating tooltips via lang_provider
- ✅ Created comprehensive test suite

---

**Last Updated**: 2025-01-21  
**Author**: Development Team  
**Status**: Completed ✅
