# 🧪 Pytest Markers Guide - Cabal_Auto

**Date**: October 23, 2025  
**Purpose**: Guide for using pytest markers to control test execution across platforms

---

## 📋 Table of Contents

1. [Available Markers](#available-markers)
2. [Platform-Specific Testing](#platform-specific-testing)
3. [Running Tests Locally](#running-tests-locally)
4. [CI/CD Usage](#cicd-usage)
5. [Writing New Tests](#writing-new-tests)
6. [Troubleshooting](#troubleshooting)

---

## 🏷️ Available Markers

All markers are defined in `pytest.ini` and auto-registered via `tests/conftest.py`.

### Platform Markers

#### `@pytest.mark.windows`
**Purpose**: Tests that require Windows platform  
**Auto-skip**: Yes - skipped automatically on Linux/macOS  
**Use for**:
- Tests using `lib.system.win_input` (ctypes.WinDLL)
- Tests importing `app_gui` (which imports win_input)
- Win32 API dependent code

**Example**:
```python
import pytest

@pytest.mark.windows
def test_keyboard_input():
    from lib.system.win_input import tap
    tap('1')
```

Or mark entire file:
```python
import pytest

# Mark all tests in this file as Windows-only
pytestmark = pytest.mark.windows

def test_something():
    # Will be skipped on non-Windows
    pass
```

---

### UI Markers

#### `@pytest.mark.gui`
**Purpose**: Tests that require GUI/display  
**Auto-skip**: No (manual skip with fixtures)  
**Use for**:
- tkinter tests
- Tests requiring $DISPLAY on Linux
- Screen capture tests
- pyautogui interaction tests

**Example**:
```python
import pytest

@pytest.mark.gui
def test_setup_wizard():
    from ui.setup_wizard import SetupWizard
    wizard = SetupWizard()
    # ...
```

**Skip in CI**:
```python
# CI environments have no display
pytestmark = [pytest.mark.gui, pytest.mark.windows]
```

---

### Test Category Markers

#### `@pytest.mark.unit`
**Purpose**: Unit tests (single function/class)  
**Auto-skip**: No  
**Use for**: Fast, isolated tests

#### `@pytest.mark.integration`
**Purpose**: Integration tests (multiple components)  
**Auto-skip**: No  
**Use for**: Tests that involve multiple modules

#### `@pytest.mark.vision`
**Purpose**: Computer vision tests (OpenCV, numpy)  
**Auto-skip**: No  
**Use for**: Image processing, template matching

#### `@pytest.mark.slow`
**Purpose**: Slow-running tests (>1 second)  
**Auto-skip**: No  
**Use for**: Performance tests, load tests

**Examples**:
```python
import pytest

@pytest.mark.unit
def test_calculator():
    assert 1 + 1 == 2

@pytest.mark.integration
def test_hunt_flow():
    # Tests multiple components together
    pass

@pytest.mark.vision
@pytest.mark.slow
def test_template_matching():
    # Vision tests are usually slower
    pass
```

---

## 🖥️ Platform-Specific Testing

### Automatic Platform Detection

The `tests/conftest.py` provides automatic platform detection:

```python
# Available in tests
def test_something(is_windows, is_linux, is_macos):
    if is_windows:
        # Windows-specific code
        pass
    elif is_linux:
        # Linux-specific code
        pass
```

### Platform Detection in Code

```python
import sys
import platform

IS_WINDOWS = sys.platform == 'win32' or platform.system() == 'Windows'
IS_LINUX = sys.platform.startswith('linux') or platform.system() == 'Linux'
IS_MACOS = sys.platform == 'darwin' or platform.system() == 'Darwin'
```

### Auto-Skip Behavior

**Windows marker**:
- ✅ Runs on Windows
- ⏭️ Auto-skipped on Linux/macOS
- 📝 Reason: "Test requires Windows platform"

**GUI marker**:
- ✅ Runs locally (with display)
- 🚫 Should be combined with skip logic in CI
- 📝 Use `skip_if_ci` fixture

---

## 🚀 Running Tests Locally

### Run All Tests
```bash
pytest
```

### Run Specific Markers

**Windows tests only** (on Windows):
```bash
pytest -m windows
```

**Skip Windows tests** (on Linux):
```bash
pytest -m "not windows"
```

**Skip Windows AND GUI tests** (CI-like):
```bash
pytest -m "not windows and not gui"
```

**Run only unit tests**:
```bash
pytest -m unit
```

**Run vision tests**:
```bash
pytest -m vision
```

**Skip slow tests**:
```bash
pytest -m "not slow"
```

### Multiple Markers

**Unit tests that are NOT Windows-only**:
```bash
pytest -m "unit and not windows"
```

**Integration tests on Windows**:
```bash
pytest -m "integration and windows"
```

### Verbose Output
```bash
pytest -v -m "not windows"
```

### With Coverage
```bash
pytest --cov=lib --cov=ui --cov-report=html -m "not windows and not gui"
```

---

## 🔄 CI/CD Usage

### GitHub Actions Configuration

See `.github/workflows/python-app.yml`:

```yaml
- name: Test with pytest
  run: |
    pytest -v --tb=short --strict-markers -m "not windows and not gui"
```

**Flags explained**:
- `-v`: Verbose output
- `--tb=short`: Short traceback format
- `--strict-markers`: Error if unknown marker used
- `-m "not windows and not gui"`: Skip platform-specific tests

### Expected Test Counts

**On Linux CI**:
- Total tests: ~32
- Skipped (Windows): ~6 tests
- Skipped (GUI): ~2 tests
- Running: ~24 tests

**On Windows (local)**:
- Total tests: ~32
- Skipped: ~0 tests (all should run)
- Running: ~32 tests

---

## ✍️ Writing New Tests

### Decision Tree

```
Is test Windows-only?
├─ YES: Add @pytest.mark.windows
└─ NO ──┐
        │
        Does test need GUI/display?
        ├─ YES: Add @pytest.mark.gui
        └─ NO ──┐
                │
                Is test slow (>1s)?
                ├─ YES: Add @pytest.mark.slow
                └─ NO: Add category marker (unit/integration/vision)
```

### Examples

**Windows keyboard test**:
```python
import pytest

@pytest.mark.windows
def test_keyboard_tap():
    from lib.system.win_input import tap
    tap('1')
    # Will auto-skip on Linux
```

**GUI test (cross-platform but needs display)**:
```python
import pytest

@pytest.mark.gui
def test_ui_window(skip_if_ci):
    # skip_if_ci fixture will skip in CI
    import tkinter as tk
    root = tk.Tk()
    # ...
```

**Vision test (cross-platform)**:
```python
import pytest
import cv2
import numpy as np

@pytest.mark.vision
def test_template_matching():
    # Works on any platform with opencv-python
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    template = np.zeros((10, 10, 3), dtype=np.uint8)
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    assert result is not None
```

**Multiple markers**:
```python
import pytest

@pytest.mark.windows
@pytest.mark.gui
@pytest.mark.integration
def test_app_gui():
    from app_gui import App
    app = App()
    # Requires Windows + display
```

---

## 🔍 Troubleshooting

### Problem: Test not skipping on Linux

**Symptom**:
```
tests/test_something.py:10: AttributeError: module 'ctypes' has no attribute 'WinDLL'
```

**Solution**: Add `@pytest.mark.windows`:
```python
import pytest

pytestmark = pytest.mark.windows  # Mark entire file

# Or mark individual test
@pytest.mark.windows
def test_something():
    pass
```

---

### Problem: Unknown marker warning

**Symptom**:
```
PytestUnknownMarkWarning: Unknown pytest.mark.mymarker
```

**Solution**: Add marker to `pytest.ini`:
```ini
[pytest]
markers =
    mymarker: description of marker
```

---

### Problem: GUI test fails in CI

**Symptom**:
```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

**Solution**: Add `@pytest.mark.gui` and skip in CI:
```python
import pytest

@pytest.mark.gui
def test_something(skip_if_ci):
    # skip_if_ci fixture auto-skips in CI
    import tkinter as tk
    # ...
```

---

### Problem: Test runs on wrong platform

**Check markers**:
```bash
pytest --markers
```

**Check what would run**:
```bash
pytest --collect-only -m "not windows"
```

**Check specific file**:
```bash
pytest --collect-only tests/test_something.py
```

---

## 📚 References

- **Pytest markers docs**: https://docs.pytest.org/en/stable/how-to/mark.html
- **Configuration**: `pytest.ini`
- **Fixtures**: `tests/conftest.py`
- **CI workflow**: `.github/workflows/python-app.yml`

---

## 🎯 Quick Reference

| Marker | Auto-Skip | Use Case |
|--------|-----------|----------|
| `windows` | ✅ Yes (on non-Windows) | Win32 APIs, ctypes.WinDLL |
| `gui` | ❌ No (manual with fixture) | tkinter, pyautogui |
| `unit` | ❌ No | Single function tests |
| `integration` | ❌ No | Multi-component tests |
| `vision` | ❌ No | OpenCV, image processing |
| `slow` | ❌ No | Tests >1 second |

**CI runs**: `pytest -m "not windows and not gui"`  
**Local Windows**: `pytest` (all tests)  
**Local Linux**: `pytest` (auto-skips Windows tests)
