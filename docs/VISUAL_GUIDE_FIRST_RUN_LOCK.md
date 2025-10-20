# First-Run Lock Feature - Visual Guide

## Feature Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER OPENS SETUP WIZARD                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              _detect_first_run() Method Executes                │
│  • Checks if lib/data/hunt_config.json exists                  │
│  • Validates: window_title, monster_list, skill_slots          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
           ▼                               ▼
    ┌──────────────┐              ┌──────────────┐
    │  INCOMPLETE  │              │   COMPLETE   │
    │  OR MISSING  │              │    CONFIG    │
    └──────┬───────┘              └──────┬───────┘
           │                             │
           │ is_first_run = True         │ is_first_run = False
           │                             │
           ▼                             ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│   FIRST-TIME USER UI    │    │   RETURNING USER UI     │
│                         │    │                         │
│ ○ New User (selected)   │    │ ○ New User (default)    │
│ ⊗ Experienced User      │    │ ○ Experienced User      │
│   (DISABLED/GRAYED)     │    │   (ENABLED/CLICKABLE)   │
│                         │    │                         │
│ ⚠️ Hint Label:          │    │ (No hint label shown)   │
│ "First-time users must  │    │                         │
│  start with New User"   │    │                         │
└─────────────────────────┘    └─────────────────────────┘
```

## Language Switching Flow

```
┌────────────────────────────────────────────────────────────────┐
│            USER CLICKS LANGUAGE TOGGLE (🇺🇸 ↔ 🇻🇳)             │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│           _on_language_change(new_lang) Executes               │
│  • Sets self.lang = new_lang                                   │
│  • Updates all UI texts using self._t(key)                     │
└──────────────────────────┬─────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ Radio      │  │ Description│  │ Hint Label │
    │ Button     │  │ Labels     │  │ (if shown) │
    │ Texts      │  │            │  │            │
    └──────┬─────┘  └──────┬─────┘  └──────┬─────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │   ALL TEXTS UPDATE TO    │
            │   SELECTED LANGUAGE      │
            │   (English/Vietnamese)   │
            └──────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │ Tooltips Auto-Update     │
            │ on Next Hover            │
            │ (via lang_provider)      │
            └──────────────────────────┘
```

## Before vs After: First-Time User

### Before Implementation
```
┌────────────────────────────────────────────┐
│          Setup Wizard - Step 1             │
├────────────────────────────────────────────┤
│                                            │
│  Select Your Experience Level:             │
│                                            │
│  ○ New User                                │
│  ○ Experienced User                        │
│                                            │
│  [Both options clickable]                  │
│                                            │
│  ❌ Problem: New users might accidentally  │
│     select "Experienced User" and skip     │
│     important guided setup steps.          │
│                                            │
└────────────────────────────────────────────┘
```

### After Implementation
```
┌────────────────────────────────────────────┐
│          Setup Wizard - Step 1             │
├────────────────────────────────────────────┤
│                                            │
│  Select Your Experience Level:             │
│                                            │
│  ● New User                                │
│    First time using the bot - I need help  │
│                                            │
│  ⊗ Experienced User (GRAYED OUT)           │
│    I know what I'm doing - skip guidance   │
│                                            │
│  ⚠️ First-time users must start with       │
│     'New User' option                      │
│                                            │
│  ✅ Solution: "Experienced User" is locked │
│     until config is complete. Clear hint   │
│     explains why it's disabled.            │
│                                            │
└────────────────────────────────────────────┘
```

## Before vs After: Language Switching

### Before Implementation
```
[User switches language from English to Vietnamese]

┌────────────────────────────────────────────┐
│  ○ New User                                │
│  ○ Experienced User                        │
│                                            │
│  ❌ Problem: Texts remain in English       │
│     User has to close and reopen wizard    │
│     to see Vietnamese texts.               │
└────────────────────────────────────────────┘
```

### After Implementation
```
[User switches language from English to Vietnamese]

┌────────────────────────────────────────────┐
│  ● 🌱 Người mới                            │
│    Lần đầu dùng bot - Cần hỗ trợ           │
│                                            │
│  ⊗ ⚙️ Người có kinh nghiệm (VÔ HIỆU)       │
│    Tôi đã biết cách sử dụng - Bỏ qua       │
│                                            │
│  ⚠️ Người dùng lần đầu phải bắt đầu với    │
│     tùy chọn 'Người mới'                   │
│                                            │
│  ✅ Solution: All texts update instantly    │
│     when language is changed. No reload    │
│     needed. Tooltips also auto-update.     │
└────────────────────────────────────────────┘
```

## State Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       WIZARD STATE                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │   __init__() called      │
            │  • Calls _detect_first   │
            │    _run()                │
            │  • Sets self.is_first    │
            │    _run flag             │
            └──────────────┬───────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │ _build_step1_welcome()   │
            │  • Creates radio buttons │
            │  • Stores references     │
            │  • Applies lock if       │
            │    is_first_run=True     │
            └──────────────┬───────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │    User Interaction      │
            │  • Selects user level    │
            │  • Changes language      │
            │  • Hovers for tooltips   │
            └──────────────┬───────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │ _on_language_change()    │
            │  • Updates self.lang     │
            │  • Refreshes all texts   │
            │  • Tooltips auto-update  │
            │    on next show          │
            └──────────────────────────┘
```

## Widget Reference System

```
┌────────────────────────────────────────────────────────────┐
│                  Widget Storage Strategy                   │
└────────────────────────────────────────────────────────────┘

Step 1: Create Widgets
├── Radio Button: New User
│   └── Stored as: self.level_new_radio
│
├── Label: New User Description  
│   └── Stored as: self.level_new_desc
│
├── Radio Button: Experienced User
│   └── Stored as: self.level_experienced_radio
│
├── Label: Experienced User Description
│   └── Stored as: self.level_experienced_desc
│
└── Label: First-Time Hint (conditional)
    └── Stored as: self.first_time_hint (if is_first_run=True)

Step 2: Language Change Handler Access
├── Checks if widget exists: hasattr(self, 'widget_name')
├── Checks if widget is valid: widget.winfo_exists()
└── Updates widget text: widget.config(text=self._t('key'))

Benefits:
✅ Dynamic updates possible
✅ Safe reference checks
✅ No widget recreation needed
✅ Memory efficient
```

## Translation Key Mapping

```
┌─────────────────────────────────────────────────────────────┐
│                 Translation Keys Structure                  │
└─────────────────────────────────────────────────────────────┘

SETUP_WIZARD_TRANSLATIONS = {
    'en': {
        'user_level_group': 'Select Your Experience Level',
        'user_level_new': '🌱 New User',
        'user_level_new_desc': 'First time using...',
        'user_level_experienced': '⚙️ Experienced User',
        'user_level_experienced_desc': 'I know what I\'m doing...',
        'first_time_user_hint': 'First-time users must start...',
        'tip_user_level_new': 'Get guided help...',
        'tip_user_level_experienced': 'Skip extra guidance...',
    },
    'vi': {
        'user_level_group': 'Chọn mức độ kinh nghiệm',
        'user_level_new': '🌱 Người mới',
        'user_level_new_desc': 'Lần đầu dùng bot...',
        'user_level_experienced': '⚙️ Người có kinh nghiệm',
        'user_level_experienced_desc': 'Tôi đã biết cách...',
        'first_time_user_hint': 'Người dùng lần đầu phải...',
        'tip_user_level_new': 'Nhận hướng dẫn chi tiết...',
        'tip_user_level_experienced': 'Bỏ qua hướng dẫn...',
    }
}

Mapping to UI Elements:
┌────────────────────────────────┬──────────────────────────┐
│ UI Element                     │ Translation Key          │
├────────────────────────────────┼──────────────────────────┤
│ Radio Button: New User         │ user_level_new           │
│ Description: New User          │ user_level_new_desc      │
│ Radio Button: Experienced      │ user_level_experienced   │
│ Description: Experienced       │ user_level_experienced   │
│                                │   _desc                  │
│ Hint Label                     │ first_time_user_hint     │
│ Tooltip: New User Radio        │ tip_user_level_new       │
│ Tooltip: Experienced Radio     │ tip_user_level           │
│                                │   _experienced           │
└────────────────────────────────┴──────────────────────────┘
```

## Tooltip Auto-Update Mechanism

```
┌────────────────────────────────────────────────────────────┐
│              Tooltip Language Resolution Flow              │
└────────────────────────────────────────────────────────────┘

Widget Creation:
│
├── attach_i18n_tooltip(
│       widget=self.level_new_radio,
│       key='tip_user_level_new',
│       ns='setup_wizard',
│       lang_provider=lambda: self.lang  ← Closure captures wizard
│   )
│
└── Creates I18nToolTip instance
    └── Stores: key, ns, lang_provider

User Hovers Over Widget:
│
├── Tooltip._show() called
│   │
│   ├── lang = self.lang_provider()  ← Executes lambda
│   │   └── Returns: self.lang (current wizard language)
│   │
│   ├── text = i18n_t(key, ns, lang)  ← Gets translation
│   │   └── Looks up: SETUP_WIZARD_TRANSLATIONS[lang][key]
│   │
│   └── Shows tooltip with resolved text
│
└── Result: Tooltip always shows in current language

Key Points:
✅ lang_provider is a lambda: captures wizard's self reference
✅ Evaluated at show-time: always gets current self.lang value
✅ No manual update needed: automatic on every hover
✅ Works across language changes: self.lang changes → tooltip updates
```

## Testing Scenarios Matrix

```
┌────────────────────────────────────────────────────────────┐
│                  Test Scenarios Matrix                     │
└────────────────────────────────────────────────────────────┘

┌─────────────┬──────────────┬──────────────┬──────────────┐
│ User Type   │ Config State │ Expected UI  │ Test File    │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ First-Time  │ Empty/       │ ○ New User   │ Scenario 1   │
│             │ Incomplete   │ ⊗ Experienced│              │
│             │              │ ⚠️ Hint shown │              │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ Returning   │ Complete     │ ○ New User   │ Scenario 2   │
│             │              │ ○ Experienced│              │
│             │              │ (No hint)    │              │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ First-Time  │ Empty +      │ Texts update │ Scenario 3   │
│ (Lang Test) │ Lang Switch  │ to VI        │              │
│             │              │ Lock persists│              │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ Returning   │ Complete +   │ Texts update │ Scenario 4   │
│ (Lang Test) │ Lang Switch  │ to VI        │              │
│             │              │ Both enabled │              │
└─────────────┴──────────────┴──────────────┴──────────────┘

Test Command: python tests\test_wizard_first_run_lock.py
```

## Visual Legend

```
┌────────────────────────────────────────────────────────────┐
│                       Symbol Legend                        │
└────────────────────────────────────────────────────────────┘

UI States:
  ○  = Radio button (unselected, enabled)
  ●  = Radio button (selected, enabled)
  ⊗  = Radio button (disabled/grayed out)

Icons:
  🌱 = New User (beginner icon)
  ⚙️  = Experienced User (settings icon)
  ⚠️  = Warning/Hint (attention icon)
  ✅ = Success/Completed
  ❌ = Problem/Error
  🇺🇸 = English language
  🇻🇳 = Vietnamese language

Flow Symbols:
  │  = Vertical flow
  ├─ = Branch point
  └─ = Terminal branch
  →  = Direction/Arrow
  ↔  = Bidirectional
```

## Common Use Cases

### Use Case 1: Brand New User
```
1. User downloads app for first time
2. Launches app
3. Setup Wizard opens automatically
4. Sees: "New User" selected, "Experienced User" grayed out
5. Reads hint: "First-time users must start with New User option"
6. Completes wizard as New User
7. Gets guided help with skill rotation
```

### Use Case 2: Returning User Wants to Reconfigure
```
1. User has used app before (config exists)
2. Opens Setup Wizard from menu
3. Sees: Both "New User" and "Experienced User" enabled
4. Selects "Experienced User"
5. Skips extra guidance steps
6. Quick reconfiguration
```

### Use Case 3: Language Preference Change
```
1. User opens Setup Wizard (first-time)
2. Default language is English
3. User prefers Vietnamese
4. Clicks language toggle (🇺🇸 → 🇻🇳)
5. All texts instantly update:
   - "New User" → "Người mới"
   - "Experienced User" → "Người có kinh nghiệm"
   - Hint → "Người dùng lần đầu phải..."
6. Continues setup in Vietnamese
```

---

**Visual Guide Version**: 1.0  
**Last Updated**: 2025-01-21  
**Related Docs**: 
- [Feature Documentation](./FEATURE_FIRST_RUN_LOCK.md)
- [Implementation Summary](./SUMMARY_FIRST_RUN_LOCK_IMPLEMENTATION.md)
- [Test Suite](../tests/test_wizard_first_run_lock.py)
