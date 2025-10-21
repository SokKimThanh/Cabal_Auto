# Bug Fix: Language & User Level Persistence in Setup Wizard

## Problem Description

### Original Issue
Khi người dùng điều hướng trong Setup Wizard (Next → Back), ngôn ngữ và user level bị reset về giá trị mặc định:
- Language luôn reset về **English** 
- User level luôn reset về **New User**

### Root Cause
Trong phương thức `_build_step1_welcome()` (được gọi mỗi khi Step 1 được hiển thị lại):

```python
# ❌ BUG: Tạo mới StringVar với giá trị mặc định
self.language_var = tk.StringVar(value='en')      # Luôn reset về 'en'
self.user_level_var = tk.StringVar(value='new')   # Luôn reset về 'new'
```

Mỗi khi người dùng:
1. Chọn ngôn ngữ Vietnamese (vi)
2. Bấm "Next →" để sang Step 2
3. Bấm "← Back" để quay lại Step 1
4. `_build_step1_welcome()` được gọi lại
5. **`language_var` bị tạo mới với `value='en'`** → Ngôn ngữ bị reset!

### Impact
- **User Experience**: Người dùng phải chọn lại ngôn ngữ mỗi khi quay lại Step 1
- **Confusion**: Không rõ liệu việc chọn ngôn ngữ có được lưu hay không
- **Navigation Problems**: Khó kiểm tra/sửa thông tin ở Step 1 sau khi đã điều hướng tiếp

## Solution

### Code Changes

#### File: `ui/setup_wizard.py`

**Change 1: Restore language_var from wizard state**
```python
# Line ~477 (in _build_step1_welcome)

# ❌ BEFORE (Bug):
self.language_var = tk.StringVar(value='en')

# ✅ AFTER (Fixed):
# Restore language from wizard state (fixes persistence bug when navigating back)
self.language_var = tk.StringVar(value=self.language)
```

**Change 2: Restore user_level_var from wizard state**
```python
# Line ~519 (in _build_step1_welcome)

# ❌ BEFORE (Bug):
self.user_level_var = tk.StringVar(value='new')

# ✅ AFTER (Fixed):
# Restore user level from wizard state (fixes persistence bug when navigating back)
self.user_level_var = tk.StringVar(value=self.user_level)
```

### How It Works

#### Data Flow
```
┌─────────────────────────────────────────────────────────────┐
│                   Language Selection Flow                   │
└─────────────────────────────────────────────────────────────┘

Step 1: User selects Vietnamese
│
├── Radio button clicked: value='vi'
├── _on_language_change() called
├── self.language = 'vi'           ← Stored in wizard instance
├── self.wizard_data['language'] = 'vi'  ← Stored in data dict
└── UI texts update to Vietnamese

Step 2: User clicks Next
│
├── _on_next() called
├── _validate_current_step() returns True
├── _show_step(2) called
└── Step 2 content displayed

Step 3: User clicks Back
│
├── _on_back() called
├── _show_step(1) called
├── _build_step1_welcome() called  ← Step 1 rebuilt!
│
├── ✅ NEW: self.language_var = tk.StringVar(value=self.language)
│   └── Uses self.language (still 'vi') instead of hardcoded 'en'
│
└── Radio button restores to Vietnamese selection!
```

#### State Preservation
The wizard maintains language state in **two places**:
1. **`self.language`**: Current language (used by `self.lang` property)
2. **`self.wizard_data['language']`**: Collected data for final config

When Step 1 is rebuilt:
- `self.language_var` is created **using `self.language` as initial value**
- This ensures radio button reflects the previously selected language
- User sees the language they selected, not the default 'en'

### Variable Naming Clarification

The wizard uses **three language-related variables**:

1. **`self.language`** (str): Primary storage of current language
   - Set in `__init__`: `self.language = 'en'`
   - Updated in `_on_language_change()`: `self.language = self.language_var.get()`
   - Used to restore `language_var` when rebuilding Step 1

2. **`self.lang`** (property → str): Read-only property for tooltips
   ```python
   @property
   def lang(self) -> str:
       return str(self.language)
   ```
   - Used by `lang_provider` lambdas in tooltips
   - Always returns current `self.language` value

3. **`self.language_var`** (tk.StringVar): Radio button variable
   - Created in `_build_step1_welcome()`
   - Bound to language radio buttons
   - **NOW restored from `self.language`** instead of hardcoded 'en'

## Testing

### Test Suite Created
**File**: `tests/test_language_persistence.py`

**Test Scenarios**:
1. **Language Persistence**:
   - Select Vietnamese → Next → Back → Verify language is still Vietnamese
   - Select English → Next → Back → Verify language is still English
   - Multiple navigation cycles

2. **User Level Persistence**:
   - Keep "New User" → Next → Back → Verify "New User" still selected
   - (For returning users) Select "Experienced User" → Next → Back → Verify still selected

### How to Run Tests
```powershell
cd e:\Cabal_Auto
python tests\test_language_persistence.py
```

Select test from menu:
- 1️⃣ Test Language Persistence
- 2️⃣ Test User Level Persistence

### Manual Test Steps

#### Test 1: Language Persistence (EN → VI)
1. Open Setup Wizard
2. Verify default language is English
3. Select "🇻🇳 Tiếng Việt"
4. Verify all texts update to Vietnamese
5. Click "Next →" (go to Step 2)
6. Click "← Back" (return to Step 1)
7. ✅ **VERIFY**: "🇻🇳 Tiếng Việt" is still selected
8. ✅ **VERIFY**: All texts are still in Vietnamese

#### Test 2: Language Persistence (VI → EN)
1. Continue from Test 1 (currently in Vietnamese)
2. Select "🇬🇧 English"
3. Verify all texts update to English
4. Click "Next →" (go to Step 2)
5. Click "← Back" (return to Step 1)
6. ✅ **VERIFY**: "🇬🇧 English" is still selected
7. ✅ **VERIFY**: All texts are still in English

#### Test 3: Multiple Navigation Cycles
1. Select Vietnamese
2. Next → Back → Next → Back → Next → Back
3. ✅ **VERIFY**: Language remains Vietnamese after each cycle

## Files Modified

### Changed Files
1. **`ui/setup_wizard.py`**
   - Line ~477: Restore `language_var` from `self.language`
   - Line ~519: Restore `user_level_var` from `self.user_level`
   - Changes: 2 lines modified
   - Impact: Fixes persistence bug for language and user level

### New Files
2. **`tests/test_language_persistence.py`**
   - Lines: 400+ lines
   - Purpose: Test suite for language & user level persistence
   - Scenarios: 2 interactive test scenarios

3. **`docs/BUGFIX_LANGUAGE_PERSISTENCE.md`**
   - Lines: This file
   - Purpose: Documentation of bug and fix

## Verification

### Before Fix (Bug Behavior)
```
User Action              | language_var Value | Visual Result
------------------------|--------------------|------------------
Open Wizard             | 'en'               | English selected ✅
Select Vietnamese       | 'vi'               | Vietnamese selected ✅
Click Next (→ Step 2)   | N/A (destroyed)    | Step 2 shown ✅
Click Back (→ Step 1)   | 'en' (RESET!)      | English selected ❌
```

### After Fix (Correct Behavior)
```
User Action              | language_var Value | Visual Result
------------------------|--------------------|------------------
Open Wizard             | 'en'               | English selected ✅
Select Vietnamese       | 'vi'               | Vietnamese selected ✅
Click Next (→ Step 2)   | N/A (destroyed)    | Step 2 shown ✅
Click Back (→ Step 1)   | 'vi' (RESTORED!)   | Vietnamese selected ✅
```

## Technical Details

### Why Was This Bug Not Noticed Earlier?

1. **First-Time User Flow**: Most users go through wizard once (Step 1 → 2 → 3 → 4 → 5 → Finish)
   - No back navigation → bug not triggered

2. **Default Language**: English is default language
   - English users never change language → bug not visible

3. **User Level**: "New User" is default
   - First-time users are locked to "New User" → selection doesn't change
   - Even if reset, still shows "New User" → bug not visible

4. **Only Visible When**:
   - User selects **Vietnamese**
   - Then navigates **Back** to Step 1
   - This specific scenario exposed the bug

### Related Code Patterns

This same pattern might exist in other wizards/dialogs:
```python
# ⚠️ Anti-pattern to avoid:
def _build_step():
    self.some_var = tk.StringVar(value='default')  # ❌ Always resets!

# ✅ Correct pattern:
def _build_step():
    self.some_var = tk.StringVar(value=self.stored_value)  # ✅ Restores!
```

**Rule**: When rebuilding UI that can be navigated back to, always restore state from instance variables, not hardcoded defaults.

## Impact Assessment

### User Experience
- **Before**: Frustrating - language resets unexpectedly
- **After**: Smooth - language persists as expected

### Code Quality
- **Before**: State management inconsistency
- **After**: Consistent state preservation

### Testing
- **Before**: No specific tests for navigation persistence
- **After**: Comprehensive test suite for persistence scenarios

## Future Improvements

### Short-Term
1. Add similar persistence checks for other wizard steps
2. Add unit tests for state restoration logic
3. Document state management patterns

### Long-Term
1. Refactor wizard to use single state object
2. Implement state history for undo/redo
3. Add state validation on navigation

## Related Issues

### Fixed
- ✅ Language persistence bug (this document)
- ✅ User level persistence bug (same fix)

### Not Affected
- ✅ Window selection (Step 2): Uses different pattern, no persistence issue
- ✅ Monster selection (Step 3): Uses different pattern, no persistence issue
- ✅ Skill configuration (Step 4): State collected on Next, not rebuilt on Back

## Conclusion

**Bug Status**: ✅ **FIXED**

**Changes Required**: Minimal (2 lines)

**Testing**: Comprehensive test suite created

**Impact**: High user experience improvement with minimal code change

**Lessons Learned**: 
- Always restore UI state from instance variables when rebuilding
- Test navigation scenarios (forward AND backward)
- State management patterns should be consistent across wizard

---

**Bug Report Date**: 2025-01-21  
**Fixed Date**: 2025-01-21  
**Developer**: Development Team  
**Status**: ✅ Verified and Documented
