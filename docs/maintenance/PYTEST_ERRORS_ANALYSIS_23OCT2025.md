# 🔍 Pytest Errors Analysis - Code Merge Issues

**Date**: October 23, 2025  
**Platform**: Linux (GitHub Actions CI)  
**Python**: 3.10.18  
**Total Errors**: 11/32 tests failed to collect

---

## 📊 TỔNG QUAN LỖI

### Phân loại lỗi:

```
1. Windows-specific API (ctypes.WinDLL)    : 6 errors ⛔
2. Missing dependencies (cv2, numpy, etc)  : 4 errors ⚠️
3. Import errors (ui module)               : 1 error  ⚠️
4. Display errors (Tkinter)                : 1 error  ✅ (expected)
```

---

## 🔴 LỖI NGHIÊM TRỌNG

### 1. **Windows-specific ctypes.WinDLL** ⛔⛔⛔

**Affected Files** (6 errors):
```
✗ tests/integration/test_template_matcher_integration.py
✗ tests/test_exclusivity.py
✗ tests/test_hunt_skill_flow.py
✗ tests/test_key_diagnostics.py
✗ tests/test_skill_rotation_manual.py
✗ tests/test_template_matching.py
```

**Root Cause**:
```python
# lib/system/win_input.py:11
user32 = ctypes.WinDLL('user32', use_last_error=True)
```

**Error**:
```
AttributeError: module 'ctypes' has no attribute 'WinDLL'
```

**Explanation**:
- `WinDLL` chỉ có trên Windows
- CI chạy trên Linux → không có attribute này
- Tất cả tests import `app_gui.py` → import `win_input.py` → crash

**Impact**: 🔴 **CRITICAL** - Blocking 6/32 tests (18.75%)

---

### 2. **Module Import Path Issues** ⚠️

**Error 1: ModuleNotFoundError: No module named 'ui'**

```
tests/integration/test_phase3_comprehensive.py:18
from ui.auto_hunt import load_cfg
```

**Explanation**:
- `ui/` không trong PYTHONPATH
- Hoặc test chạy từ sai working directory

**Error 2: ModuleNotFoundError: No module named 'pyautogui'**

```
auto_hunt.py import failed: No module named 'pyautogui'
```

**Explanation**:
- `pyautogui` không được install trong CI environment
- Missing từ `requirements.txt` hoặc không install trước khi test

---

### 3. **Missing Dependencies** ⚠️

**Missing Packages**:
```
✗ cv2 (opencv-python)       - 1 test
✗ numpy                      - 1 test  
✗ pyautogui                  - multiple tests
```

**Files Affected**:
```
tests/vision_basic_test.py:16    → import cv2
tests/vision_perf_test.py:15     → import numpy
```

---

### 4. **Display Environment** ✅ (Expected)

**Error**:
```
tests/unit/test_setup_wizard_button.py
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

**Explanation**:
- Tkinter cần X11 display
- CI không có GUI environment
- **THIS IS EXPECTED** - cần xvfb hoặc skip marker

---

## 🔧 GIẢI PHÁP CHI TIẾT

### Solution 1: Platform Detection cho win_input.py ⭐⭐⭐⭐⭐

**Priority**: CRITICAL  
**Time**: 30 phút

**Implementation**:

```python
# lib/system/win_input.py
import sys
import ctypes
from typing import Optional

# Platform detection
IS_WINDOWS = sys.platform == 'win32'

if IS_WINDOWS:
    from ctypes import wintypes
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    # ... rest of Windows-specific code
else:
    # Mock for non-Windows platforms
    user32 = None
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    # ... mock constants

def tap(key: str, hold_ms: Optional[int] = None):
    """Send key press. Mock on non-Windows."""
    if not IS_WINDOWS:
        print(f"[MOCK] tap({key}, {hold_ms})")
        return
    
    # Real Windows implementation
    ...
```

**Benefits**:
- ✅ Tests có thể import trên Linux
- ✅ Không cần thay đổi test code
- ✅ Production code vẫn hoạt động trên Windows

---

### Solution 2: Fix requirements.txt ⭐⭐⭐⭐

**Priority**: HIGH  
**Time**: 10 phút

**Missing Dependencies**:

```txt
# requirements.txt - Add these:
opencv-python==4.12.0.132
numpy==2.2.1
pyautogui==0.9.54
pillow==11.0.0
```

**Verify có đầy đủ**:
```bash
pip freeze | grep -E "(opencv|numpy|pyautogui|pillow)"
```

---

### Solution 3: Pytest Markers cho Platform-Specific Tests ⭐⭐⭐⭐

**Priority**: HIGH  
**Time**: 20 phút

**Create pytest.ini**:

```ini
# pytest.ini
[pytest]
markers =
    windows: Tests that require Windows platform
    gui: Tests that require display/GUI
    integration: Integration tests
    unit: Unit tests
```

**Mark Windows-specific tests**:

```python
# tests/test_exclusivity.py
import pytest
import sys

pytestmark = pytest.mark.skipif(
    sys.platform != 'win32',
    reason="Windows-only test"
)

def test_something():
    from app_gui import App  # Now safe to import
    ...
```

**Mark GUI tests**:

```python
# tests/unit/test_setup_wizard_button.py
import pytest
import os

pytestmark = pytest.mark.skipif(
    not os.environ.get('DISPLAY') and sys.platform != 'win32',
    reason="Requires display"
)
```

---

### Solution 4: Fix Import Paths ⭐⭐⭐

**Priority**: MEDIUM  
**Time**: 15 phút

**Option A: Add conftest.py**

```python
# tests/conftest.py
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

**Option B: Fix relative imports**

```python
# tests/integration/test_phase3_comprehensive.py
# Before:
from ui.auto_hunt import load_cfg

# After:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from ui.auto_hunt import load_cfg
```

---

### Solution 5: CI Configuration ⭐⭐⭐⭐⭐

**Priority**: HIGH  
**Time**: 30 phút

**Update .github/workflows/test.yml**:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests (Linux-compatible only)
        run: |
          pytest tests/ \
            -v \
            -m "not windows and not gui" \
            --cov=lib \
            --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  test-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run all tests
        run: |
          pytest tests/ -v --cov=lib --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 📋 ACTION PLAN (Priority Order)

### Phase 1: Quick Fixes (1 giờ) ⚡

```
1. ✅ Fix requirements.txt (10 phút)
   - Add opencv-python, numpy, pyautogui
   - Commit: "fix: add missing test dependencies"

2. ✅ Add pytest.ini with markers (10 phút)
   - Define windows, gui, integration markers
   - Commit: "test: add pytest markers"

3. ✅ Fix win_input.py platform detection (30 phút)
   - Add IS_WINDOWS check
   - Mock tap() on Linux
   - Commit: "fix: add platform detection for win_input"

4. ✅ Add tests/conftest.py (10 phút)
   - Fix import paths
   - Commit: "test: add conftest for import paths"
```

**Result**: 10/11 errors fixed

---

### Phase 2: Test Refactoring (2 giờ) 🔧

```
5. ✅ Mark Windows-specific tests (30 phút)
   - @pytest.mark.windows for 6 tests
   - Commit: "test: mark windows-only tests"

6. ✅ Mark GUI tests (20 phút)
   - @pytest.mark.gui for Tkinter tests
   - Commit: "test: mark gui tests"

7. ✅ Update CI workflow (30 phút)
   - Separate Linux/Windows jobs
   - Skip marked tests appropriately
   - Commit: "ci: add platform-specific test jobs"

8. ✅ Test locally (30 phút)
   pytest -m "not windows" -v
   pytest -m "windows" -v (on Windows)
```

**Result**: All tests categorized and runnable

---

### Phase 3: Documentation (30 phút) 📚

```
9. ✅ Update tests/README.md
   - Document markers
   - Document platform requirements
   - How to run tests

10. ✅ Add TESTING.md
    - Test structure
    - Platform-specific tests
    - CI behavior
```

---

## 🎯 EXPECTED RESULTS

### Before Fix:
```
collected 32 items / 11 errors
11 errors in 1.39s
❌ FAILURE
```

### After Phase 1:
```
collected 32 items / 1 deselected
21 passed, 1 skipped (gui), 10 deselected (windows)
✅ SUCCESS (Linux CI)
```

### After Full Fix:
```
Linux CI:
  21 passed, 11 skipped (windows/gui markers)
  ✅ SUCCESS

Windows CI:
  32 passed
  ✅ SUCCESS
```

---

## 🔍 ROOT CAUSE ANALYSIS

### Vì sao lỗi xảy ra khi merge?

**Scenario**:
1. Code được phát triển trên Windows
2. `win_input.py` dùng `ctypes.WinDLL` (Windows-only)
3. Tests import `app_gui.py` → import `win_input.py`
4. CI chạy trên Linux → `WinDLL` không tồn tại
5. **11 tests crash** khi collect

**Lesson Learned**:
- ❌ Không test cross-platform trước khi merge
- ❌ Không có platform detection
- ❌ CI không có separate Windows/Linux jobs
- ❌ Missing dependencies trong requirements.txt

---

## ✅ PREVENTION CHECKLIST

### Pre-merge Checklist:
```
[ ] Test locally với pytest
[ ] Test trên Linux (WSL/VM/Docker)
[ ] Verify requirements.txt complete
[ ] Platform-specific code có detection
[ ] CI green trước khi merge
[ ] Code review check platform compatibility
```

### Code Standards:
```python
# ✅ Good - Platform detection
if sys.platform == 'win32':
    from ctypes import WinDLL
else:
    WinDLL = None  # Mock

# ❌ Bad - No detection
from ctypes import WinDLL  # Crashes on Linux
```

---

## 📊 IMPACT ASSESSMENT

### Severity: 🔴 **HIGH**

**Why**:
- 34% tests failing (11/32)
- Blocking CI pipeline
- Prevents merge to main
- Affects all future PRs

### Effort to Fix: 🟢 **LOW-MEDIUM**

**Why**:
- Clear root causes identified
- Solutions straightforward
- 1-2 hours total fix time
- No architecture changes needed

### Risk: 🟢 **LOW**

**Why**:
- Fixes are isolated
- No production code impact
- Only test infrastructure
- Easy to rollback if needed

---

## 🚀 NEXT STEPS

### Immediate (Today):
1. ✅ Implement Phase 1 fixes (1 giờ)
2. ✅ Push fix branch
3. ✅ Verify CI green
4. ✅ Merge to feature branch

### Short-term (This week):
1. ✅ Complete Phase 2 refactoring (2 giờ)
2. ✅ Add documentation (30 phút)
3. ✅ Test on both platforms
4. ✅ Update team on best practices

### Long-term (Next sprint):
1. 🎯 Add pre-commit hooks (platform checks)
2. 🎯 Docker test environment (Linux consistency)
3. 🎯 Automated cross-platform testing
4. 🎯 Better mocking framework

---

## 📝 COMMIT MESSAGES (Suggested)

```bash
git checkout -b fix/pytest-platform-errors

# Phase 1
git commit -m "fix: add missing test dependencies to requirements.txt"
git commit -m "test: add pytest.ini with platform markers"
git commit -m "fix: add platform detection for win_input module"
git commit -m "test: add conftest.py for import path resolution"

# Phase 2
git commit -m "test: mark windows-only tests with pytest marker"
git commit -m "test: mark gui tests with display requirement marker"
git commit -m "ci: add separate windows/linux test jobs"

# Phase 3
git commit -m "docs: update test documentation with platform requirements"

git push origin fix/pytest-platform-errors
```

---

## 🎓 LESSONS FOR SPRINT 22

### Apply to Monster Editor Refactor:

1. **Platform Detection từ đầu**:
   ```python
   # lib/input/input_adapter.py
   if IS_WINDOWS:
       from interception import ...
   else:
       # Mock implementation
   ```

2. **Test Markers ngay từ đầu**:
   ```python
   @pytest.mark.windows
   def test_windows_specific():
       ...
   ```

3. **CI Configuration hoàn chỉnh**:
   - Linux CI: skip Windows tests
   - Windows CI: run all tests
   - Clear documentation

4. **Requirements phân tầng**:
   ```
   requirements.txt         # Cross-platform
   requirements-win.txt     # Windows extras
   requirements-linux.txt   # Linux extras
   ```

---

**Status**: ⚠️ **NEEDS IMMEDIATE FIX**  
**Owner**: Development Team  
**ETA**: 1-2 hours  
**Priority**: P0 (Blocking)

---

Last Updated: October 23, 2025
