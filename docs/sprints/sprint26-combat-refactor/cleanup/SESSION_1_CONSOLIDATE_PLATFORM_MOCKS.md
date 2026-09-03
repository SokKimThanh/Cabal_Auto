# 🔧 Session 1: Consolidate Platform Mocks

## 📋 Overview

| Aspect | Value |
|--------|-------|
| **Objective** | Remove duplicated `sys.modules` patches from test files into centralized conftest.py |
| **Duration** | 2-3 hours |
| **Effort** | 🟢 Low |
| **Impact** | 🟡 Medium (5-10% mock reduction = 30-50 mocks saved) |
| **Difficulty** | Easy (copy-paste, straightforward refactoring) |
| **Risk Level** | 🟢 Very Low (no breaking changes) |
| **Prerequisites** | None (can do independently) |
| **Files to Modify** | 6 files (5 test files + 1 conftest.py) |

---

## 🎯 Objective

**Current Problem**:
```python
# Duplicated across 5+ test files:
sys.modules['win32gui'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['win32con'] = MagicMock()
sys.modules['win32process'] = MagicMock()
sys.modules['win32api'] = MagicMock()
sys.modules['pywintypes'] = MagicMock()
```

**After Session 1**:
- ✅ All platform mocks centralized in `tests/conftest.py`
- ✅ Test files import from fixtures instead
- ✅ Single source of truth for platform compatibility
- ✅ 30-50 fewer mock instances in test code

---

## 🔍 Problem Analysis

### Why Platform Mocks Exist?
1. **Cross-Platform Testing**: Cabal Auto runs on Windows, but CI runs on Linux
2. **Windows APIs Not Available**: `win32gui`, `win32api`, `pywintypes` don't exist on Linux
3. **OpenCV Headless**: CV2 and NumPy need special setup on headless Linux
4. **Import-Time Failures**: Without these mocks, test imports would fail at runtime

### Why It's Duplicated?
- Developers independently added platform mocks to their test files
- No centralized fixture existed to consolidate them
- Each file needed these to run without breaking on Linux CI

### The Cost of Duplication
```
Current State:
- 15 sys.modules patches
- Scattered across 5+ test files
- Hard to update if dependencies change
- Developers don't know where mocks are defined

Problem:
If we need to add/update platform mocks:
1. Search 5+ files to find all occurrences
2. Make the same change multiple times
3. Risk missing some files
4. Test maintenance becomes nightmare
```

---

## 💡 Solution Design

### Architecture

```
Before:
┌─────────────────────────────────────────┐
│ tests/unit/test_action_bar.py           │
│   sys.modules['win32gui'] = Mock()      │
│   sys.modules['cv2'] = Mock()           │
│   sys.modules['numpy'] = Mock()         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ tests/ui/test_footer_visibility.py      │
│   sys.modules['win32gui'] = Mock()      │  ← DUPLICATED!
│   sys.modules['cv2'] = Mock()           │  ← DUPLICATED!
│   sys.modules['numpy'] = Mock()         │  ← DUPLICATED!
└─────────────────────────────────────────┘

After:
┌─────────────────────────────────────────┐
│ tests/conftest.py                       │
│   @pytest.fixture(autouse=True)         │
│   def setup_platform_mocks():           │
│       sys.modules['win32gui'] = Mock()  │
│       sys.modules['cv2'] = Mock()       │
│       sys.modules['numpy'] = Mock()     │
│       # Central location ✅             │
└─────────────────────────────────────────┘

All test files automatically get mocks!
```

### Key Features
1. **Auto-Use Fixture**: Applies to all tests automatically
2. **Platform Detection**: Only mocks on non-Windows (Linux CI)
3. **Centralized**: Single file to maintain
4. **Easy to Extend**: Just add to dict

---

## 📁 Files to Update

### Affected Test Files
These files currently have duplicated platform mocks:

1. ✅ `tests/unit/test_action_bar.py` - Has 7 sys.modules patches
2. ✅ `tests/ui/test_footer_visibility.py` - Has platform patches
3. ✅ `tests/ui/test_hunt_bottom_logs.py` - Has platform patches
4. ✅ `tests/unit/features/hunt/test_orchestrator_ocr_fallback.py` - Has platform patches
5. ✅ `tests/unit/features/hunt/test_window_selection_service.py` - Has platform patches
6. ✅ `tests/unit/ui/controllers/test_hotkey_controller.py` - Has platform patches

### Main Infrastructure File
- ✅ `tests/conftest.py` - Will add platform mock fixtures

---

## 🔧 Step-by-Step Implementation

### Step 1: Analyze Current Platform Mocks

First, let's identify all platform mocks:

```bash
cd f:\Cabal_Auto
grep -r "sys\.modules\[.*\].*Mock" tests/ --include="*.py" | head -20
```

Expected output will show all places where platform mocks are defined.

### Step 2: Create Platform Mock Fixtures in tests/conftest.py

Add this to `tests/conftest.py`:

```python
# ============================================================================
# Platform Compatibility Mocks
# ============================================================================

@pytest.fixture(scope='session', autouse=True)
def setup_platform_mocks():
    """
    Auto-setup platform mocks for CI/Linux environments.
    
    These mocks prevent import errors on non-Windows platforms where
    Windows-specific APIs (win32gui, etc.) and heavy libraries (cv2, numpy)
    are not available or not needed for testing.
    
    This fixture is:
    - Auto-use: Automatically applied to all tests
    - Session-scoped: Set up once per test session
    - Platform-aware: Only activates on non-Windows
    
    Usage: No explicit use needed - it runs automatically for all tests
    """
    if not IS_WINDOWS:
        # Windows API mocks
        sys.modules['win32gui'] = MagicMock()
        sys.modules['win32con'] = MagicMock()
        sys.modules['win32process'] = MagicMock()
        sys.modules['win32api'] = MagicMock()
        sys.modules['pywintypes'] = MagicMock()
        
        # Heavy library mocks
        sys.modules['cv2'] = MagicMock()
        sys.modules['numpy'] = MagicMock()
    
    yield
    
    # Cleanup (optional, but good practice)
    if not IS_WINDOWS:
        for module_name in ['win32gui', 'win32con', 'win32process', 
                            'win32api', 'pywintypes', 'cv2', 'numpy']:
            if module_name in sys.modules:
                del sys.modules[module_name]
```

### Step 3: Remove Duplicated Mocks from Test Files

For each test file, **remove** the sys.modules patches:

#### File: tests/unit/test_action_bar.py
```python
# REMOVE these lines:
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['win32gui'] = MagicMock()
sys.modules['win32con'] = MagicMock()
sys.modules['win32process'] = MagicMock()
sys.modules['win32api'] = MagicMock()
sys.modules['pywintypes'] = MagicMock()
```

#### File: tests/ui/test_footer_visibility.py
```python
# REMOVE:
sys.modules['win32gui'] = unittest.mock.MagicMock()
```

#### Similar changes for:
- `tests/ui/test_hunt_bottom_logs.py`
- `tests/unit/features/hunt/test_orchestrator_ocr_fallback.py`
- `tests/unit/features/hunt/test_window_selection_service.py`
- `tests/unit/ui/controllers/test_hotkey_controller.py`

**Keep only**:
- Import statements
- Test code
- Other non-platform mocks

### Step 4: Verify Imports in conftest.py

Make sure `tests/conftest.py` has these imports at the top:

```python
import sys
from unittest.mock import MagicMock

# Platform detection (should already be there)
IS_WINDOWS = sys.platform == 'win32' or platform.system() == 'Windows'
```

### Step 5: Test the Changes

```bash
# Run all tests to verify platform mocks are working
pytest tests/ -v

# Specifically test on Linux CI simulation
# (or just verify they import without errors)
pytest tests/unit/test_action_bar.py -v
pytest tests/ui/test_footer_visibility.py -v

# Count remaining mocks
python analyze_mocks.py
```

### Step 6: Commit the Changes

```bash
git add tests/conftest.py tests/unit/test_action_bar.py tests/ui/*.py tests/unit/features/hunt/*.py

git commit -m "refactor: consolidate platform mocks in conftest.py

- Move duplicated sys.modules patches to tests/conftest.py
- Create setup_platform_mocks fixture with session scope
- Fixture is auto-use, applies to all tests
- Remove duplicate mocks from 6 test files
- Reduces mock instances by ~30 (5% total reduction)

Files modified:
- tests/conftest.py: Added platform mock fixture
- tests/unit/test_action_bar.py: Removed sys.modules patches
- tests/ui/test_footer_visibility.py: Removed sys.modules patches
- tests/ui/test_hunt_bottom_logs.py: Removed sys.modules patches
- tests/unit/features/hunt/test_orchestrator_ocr_fallback.py: Removed sys.modules patches
- tests/unit/features/hunt/test_window_selection_service.py: Removed sys.modules patches
- tests/unit/ui/controllers/test_hotkey_controller.py: Removed sys.modules patches"
```

---

## ✅ Testing Checklist

After completing all changes:

### Local Testing
- [ ] Run `pytest tests/ -v` → All tests pass ✅
- [ ] Run `python analyze_mocks.py` → Verify mock count reduced by ~30
- [ ] Check test import times → Should not increase
- [ ] Verify on Windows machine (if available) → Should not break anything

### Verification Steps
```python
# Verify fixture is working
def test_platform_mocks_active(monkeypatch):
    """Verify that platform mocks are automatically set up."""
    # If not on Windows, mocks should be active
    if not IS_WINDOWS:
        assert 'win32gui' in sys.modules
        assert isinstance(sys.modules['win32gui'], MagicMock)
        assert 'cv2' in sys.modules
```

### Git Verification
```bash
# Verify the changes
git diff HEAD~1..HEAD --stat

# Verify mock count reduction
git show HEAD~1:analyze_mocks.py | python - > before.txt
python analyze_mocks.py > after.txt
diff before.txt after.txt
```

---

## 📊 Expected Results

### Before Session 1
```
Total Mock/Patch Instances: 674
sys.modules patches: 15 (scattered in 6 files)
```

### After Session 1
```
Total Mock/Patch Instances: 644
sys.modules patches: 15 (all in conftest.py, centralized)
Duplicate patches removed: 7 files
Single source of truth: ✅ Established
```

### Mock Reduction by File
| File | Before | After | Reduction |
|------|--------|-------|-----------|
| tests/unit/test_action_bar.py | 49 | 42 | 7 |
| tests/ui/test_footer_visibility.py | 4 | 3 | 1 |
| tests/ui/test_hunt_bottom_logs.py | 4 | 3 | 1 |
| tests/unit/features/hunt/test_orchestrator_ocr_fallback.py | 43 | 38 | 5 |
| tests/unit/features/hunt/test_window_selection_service.py | 6 | 4 | 2 |
| tests/unit/ui/controllers/test_hotkey_controller.py | 22 | 16 | 6 |
| tests/conftest.py | - | +15 | -15 (centralized) |
| **TOTAL** | **674** | **644** | **-30** |

---

## 🎓 What You'll Learn

1. **Fixture Scoping**: `scope='session'` for one-time setup
2. **Auto-use Fixtures**: Apply to all tests without explicit imports
3. **Module Mocking**: `sys.modules` manipulation for import-time mocks
4. **Platform Detection**: Conditional mock setup based on platform
5. **Centralization**: Single source of truth for shared test infrastructure

---

## ⚠️ Common Issues & Solutions

### Issue 1: Platform Detection Not Working
**Problem**: Mocks not being set up on CI
**Solution**: Verify `IS_WINDOWS` is defined correctly:
```python
import platform
IS_WINDOWS = sys.platform == 'win32' or platform.system() == 'Windows'
```

### Issue 2: Tests Still Failing on Import
**Problem**: Mock not in place when module imports
**Solution**: Ensure fixture is `scope='session'` (runs before test collection)

### Issue 3: Mock Not Cleaned Up Between Sessions
**Problem**: Mocks persist across multiple test runs
**Solution**: Add cleanup in fixture (see Step 2 - yield section)

### Issue 4: Test Works Locally but Fails on CI
**Problem**: Platform detection issue
**Solution**: Add debug output:
```python
print(f"IS_WINDOWS={IS_WINDOWS}, sys.platform={sys.platform}")
```

---

## 📝 Code Diff Preview

### changes to tests/conftest.py
```diff
# At the end of conftest.py file, add:

+ # ============================================================================
+ # Platform Compatibility Mocks
+ # ============================================================================
+
+ @pytest.fixture(scope='session', autouse=True)
+ def setup_platform_mocks():
+     """Auto-setup platform mocks for CI/Linux environments."""
+     if not IS_WINDOWS:
+         sys.modules['win32gui'] = MagicMock()
+         sys.modules['win32con'] = MagicMock()
+         sys.modules['win32process'] = MagicMock()
+         sys.modules['win32api'] = MagicMock()
+         sys.modules['pywintypes'] = MagicMock()
+         sys.modules['cv2'] = MagicMock()
+         sys.modules['numpy'] = MagicMock()
+     yield
+     if not IS_WINDOWS:
+         for module_name in ['win32gui', 'win32con', 'win32process',
+                             'win32api', 'pywintypes', 'cv2', 'numpy']:
+             if module_name in sys.modules:
+                 del sys.modules[module_name]
```

### changes to tests/unit/test_action_bar.py
```diff
import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock

import sys
from unittest.mock import MagicMock

- sys.modules['cv2'] = MagicMock()
- sys.modules['numpy'] = MagicMock()
- sys.modules['win32gui'] = MagicMock()
- sys.modules['win32con'] = MagicMock()
- sys.modules['win32process'] = MagicMock()
- sys.modules['win32api'] = MagicMock()
- sys.modules['pywintypes'] = MagicMock()
mock_wm = MagicMock()
sys.modules['lib.system.window_manager'] = mock_wm

# Rest of file unchanged...
```

---

## 📚 Additional Resources

### Related Documentation
- [Python unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Pytest fixtures documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Pytest fixture scope](https://docs.pytest.org/en/stable/how-to/fixtures.html#scope-sharing-fixtures-across-classes-modules-packages-and-sessions)

### Files to Reference
- `tests/conftest.py` - Root conftest for session setup
- `conftest.py` - Project-level conftest

---

## 🎯 Session Complete Criteria

✅ **This session is complete when:**
1. All `sys.modules` patches moved to `tests/conftest.py`
2. 6 test files cleaned of duplicate platform mocks
3. All tests pass on both Windows and Linux (CI)
4. Mock count reduced from 674 → 644 (~30 mocks saved)
5. Changes committed with proper commit message
6. No breaking changes to existing tests

---

**Status**: 🟢 Ready to Implement
**Estimated Time**: 2-3 hours
**Next Session**: [SESSION_2_TEST_FIXTURES.md](SESSION_2_TEST_FIXTURES.md)

---

## 🚀 Quick Start Command

```bash
# Navigate to project
cd f:\Cabal_Auto

# Analyze current mocks before changes
python analyze_mocks.py > before_session1.txt

# After making changes:
python analyze_mocks.py > after_session1.txt

# Compare
diff before_session1.txt after_session1.txt

# Run tests to verify
pytest tests/ -v
```
