# Pytest Template for CI/CD Environments

## 📋 Quick Reference Template

```python
"""
Test Module: [Module Name]
Description: [What this test validates]
"""

import sys
import pytest
from typing import Any
from pathlib import Path

# ============================================================================
# STEP 1: PLATFORM & ENVIRONMENT CHECKS
# ============================================================================

# For Windows-only tests (GUI, ctypes.wintypes, win32api, etc.)
pytestmark = [pytest.mark.windows, pytest.mark.gui]

if sys.platform != "win32":
    pytest.skip("Requires Windows environment", allow_module_level=True)

# For tests requiring GUI/DISPLAY
# pytestmark = pytest.mark.gui
# if not os.environ.get('DISPLAY'):
#     pytest.skip("Requires DISPLAY", allow_module_level=True)

# ============================================================================
# STEP 2: OPTIONAL IMPORTS (for cross-platform compatibility)
# ============================================================================

# Method A: Try-except with fallback
try:
    import optional_module
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False
    optional_module = None  # type: ignore

# Method B: Type-safe optional imports (prevents 'possibly unbound' warnings)
from types import ModuleType
from typing import Optional, cast

cv2: Optional[ModuleType] = None
try:
    import cv2 as cv2_module
    cv2 = cv2_module
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

# ============================================================================
# STEP 3: PROJECT IMPORTS
# ============================================================================

# Add project root to path if needed
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import your modules
from lib.your_module import your_function

# ============================================================================
# STEP 4: FIXTURES (Shared test setup)
# ============================================================================

@pytest.fixture
def sample_data():
    """Provide test data."""
    return {"key": "value"}

@pytest.fixture
def temp_file(tmp_path):
    """Create temporary file for testing."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    return test_file

# ============================================================================
# STEP 5: TEST FUNCTIONS
# ============================================================================

def test_basic_functionality():
    """Test basic feature - always runs on all platforms."""
    result = your_function(input_value)
    
    # Clear assertions with messages
    assert result is not None, "Function should return a value"
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert result["status"] == "success", f"Expected success, got {result['status']}"

@pytest.mark.skipif(not HAS_MODULE, reason="Module not available")
def test_with_optional_dependency():
    """Test that requires optional module."""
    assert optional_module is not None
    result = optional_module.do_something()
    assert result is not None

@pytest.mark.windows
def test_windows_only_feature():
    """Test Windows-specific functionality."""
    # This automatically skips on non-Windows platforms
    result = windows_specific_function()
    assert result is not None

@pytest.mark.gui
def test_gui_component():
    """Test GUI component (requires DISPLAY)."""
    # This skips when running with -m "not gui"
    window = create_window()
    assert window is not None

@pytest.mark.slow
def test_performance_heavy():
    """Test that takes long time (skip in quick runs)."""
    # Skip with: pytest -m "not slow"
    result = expensive_operation()
    assert result is not None

# ============================================================================
# STEP 6: PARAMETRIZED TESTS (Test multiple inputs)
# ============================================================================

@pytest.mark.parametrize("input_val,expected", [
    (1, 2),
    (5, 10),
    (0, 0),
])
def test_multiple_cases(input_val, expected):
    """Test with multiple input/output pairs."""
    result = double(input_val)
    assert result == expected, f"double({input_val}) should be {expected}, got {result}"

# ============================================================================
# STEP 7: ERROR HANDLING TESTS
# ============================================================================

def test_exception_raised():
    """Test that function raises expected exception."""
    with pytest.raises(ValueError, match="Invalid input"):
        your_function(invalid_input)

def test_file_not_found_handling():
    """Test graceful handling of missing files."""
    result = load_config("nonexistent.json")
    assert result is not None, "Should return default config"
    assert result.get("default") is True

# ============================================================================
# STEP 8: CLEANUP (if needed)
# ============================================================================

def teardown_module():
    """Clean up after all tests in this module."""
    # Close connections, delete temp files, etc.
    pass
```

## 🎯 CI/CD Best Practices Checklist

### ✅ Platform Compatibility

```python
# ❌ BAD: No platform check
import ctypes.wintypes  # Fails on Linux!

# ✅ GOOD: Skip entire module on non-Windows
if sys.platform != "win32":
    pytest.skip("Requires Windows", allow_module_level=True)
import ctypes.wintypes  # Safe now
```

### ✅ GUI/Display Tests

```python
# ❌ BAD: Imports pyautogui at module level
import pyautogui  # Crashes on headless CI!

# ✅ GOOD: Mark and skip appropriately
pytestmark = [pytest.mark.windows, pytest.mark.gui]
if sys.platform != "win32":
    pytest.skip("Requires Windows", allow_module_level=True)
import pyautogui  # Only loads on Windows
```

### ✅ Optional Dependencies

```python
# ❌ BAD: Assume library is always available
import cv2
result = cv2.imread(path)  # Fails if cv2 not installed

# ✅ GOOD: Check availability and skip gracefully
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

@pytest.mark.skipif(not HAS_CV2, reason="OpenCV not available")
def test_image_processing():
    assert cv2 is not None
    result = cv2.imread(path)
```

### ✅ File Path Handling

```python
# ❌ BAD: Hardcoded paths
config = load_config("C:\\Users\\Me\\config.json")

# ✅ GOOD: Relative paths from project root
project_root = Path(__file__).parent.parent.parent
config_path = project_root / "config" / "default.json"
config = load_config(config_path)

# ✅ EVEN BETTER: Use tmp_path fixture for test files
def test_save_config(tmp_path):
    config_file = tmp_path / "test_config.json"
    save_config(config_file, data)
    assert config_file.exists()
```

### ✅ Clear Assertions

```python
# ❌ BAD: Unclear failure messages
assert result
assert len(items) > 0

# ✅ GOOD: Descriptive messages
assert result is not None, "Function should return a value, got None"
assert len(items) > 0, f"Expected non-empty list, got {len(items)} items"
assert result["status"] == "ok", f"Expected status 'ok', got '{result['status']}'"
```

### ✅ Avoid Module-Level Code Execution

```python
# ❌ BAD: Runs at import time (causes collection errors)
print("Testing...")
root = tk.Tk()  # Crashes on headless CI!
sys.exit(1)  # Kills pytest collection!

# ✅ GOOD: Wrap in test functions
def test_tkinter_window():
    """Test window creation."""
    root = tk.Tk()
    root.title("Test")
    root.destroy()  # Clean up
```

## 🏷️ Pytest Markers Reference

```ini
# pytest.ini
[pytest]
markers =
    windows: Tests requiring Windows OS
    gui: Tests requiring GUI/DISPLAY
    integration: Integration tests (slower)
    unit: Unit tests (fast)
    slow: Slow tests (skip in quick runs)
    vision: Computer vision tests
```

### Usage in CI Workflow

```yaml
# .github/workflows/python-app.yml
- name: Test with pytest
  run: |
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    export DISPLAY=:99
    # Skip Windows-only and GUI tests on Linux CI
    pytest -v --tb=short --strict-markers -m "not windows and not gui"
```

## 📊 Common CI/CD Error Patterns & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'ui.setup_wizard'` | Module imports Windows-only code | Add `pytest.skip()` before import |
| `Xlib.error.XauthError: ~/.Xauthority` | pyautogui requires DISPLAY | Mark as `@pytest.mark.gui` and skip |
| `KeyError: 'DISPLAY'` | GUI library needs X11 | Setup Xvfb in CI or skip with marker |
| `"cv2" is possibly unbound` | Type checker sees optional import | Use `Optional[ModuleType]` + `cast()` |
| `SystemExit: 1` during collection | Module-level `sys.exit()` | Move code into test functions |
| `FileNotFoundError: test_data.json` | Hardcoded absolute path | Use `Path(__file__).parent` relative paths |

## 🚀 Quick Start: Adding New Test

1. **Copy template above**
2. **Add platform checks** if needed (Windows/GUI)
3. **Import with try-except** for optional deps
4. **Write test functions** (prefix with `test_`)
5. **Add clear assertions** with messages
6. **Run locally**: `pytest tests/your_test.py -v`
7. **Check markers work**: `pytest -m "not windows and not gui"`
8. **Commit and verify CI passes** ✅

## 📚 Further Reading

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Markers Guide](https://docs.pytest.org/en/stable/mark.html)
- [Testing in CI/CD](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
- Project: `docs/architecture/GLOBAL_HOTKEYS_EXTENDED_ARCHITECTURE.md` (testing patterns)

---

**Last Updated**: 2025-10-23  
**Maintainer**: Development Team  
**Related**: `pytest.ini`, `.github/workflows/python-app.yml`
