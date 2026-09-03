# 🏛️ Session 5: Split Integration/Unit Tests

## 📋 Overview

| Aspect | Value |
|--------|-------|
| **Objective** | Separate integration tests from unit tests into distinct directories |
| **Duration** | 2-3 days |
| **Effort** | 🟡 Medium |
| **Impact** | 🟡 Medium (organization + clarity improvement) |
| **Difficulty** | Medium (requires careful file movement and import fixing) |
| **Risk Level** | 🟢 Low (no behavior changes, organization only) |
| **Prerequisites** | Sessions 1-4 should be complete |
| **Files to Modify** | 30+ test files (move and reorganize) |

---

## 🎯 Objective

**Current Problem**:
```
tests/
├── unit/
│   ├── test_action_bar.py              ← Mixed concerns
│   ├── features/
│   │   └── hunt/
│   │       ├── test_orchestrator_ocr_fallback.py  ← Actually integration!
│   │       ├── test_orchestrator_loop.py          ← Actually integration!
│   │       └── test_window_selection_service.py   ← Actually integration!
│   └── ui/
│       └── test_monster_editor_left_panel.py      ← Mixed
├── integration/
│   └── test_orchestrator_loop.py       ← Duplicate!
└── conftest.py
```

**After Session 5**:
```
tests/
├── unit/                     ← Fast, isolated, <100ms each
│   ├── features/
│   │   ├── hunt/
│   │   │   └── test_target_name_reader.py         ← Single concern
│   │   └── skills/
│   │       └── test_skill_stats.py                ← Single concern
│   ├── ui/
│   │   └── test_color_picker.py                   ← Single concern
│   └── conftest_unit.py                           ← Unit fixtures
├── integration/              ← Slower, may use real files/network
│   ├── features/
│   │   └── hunt/
│   │       ├── test_orchestrator_full_flow.py     ← Real hunt logic
│   │       └── test_vision_integration.py         ← Real vision
│   ├── ui/
│   │   └── test_monster_editor_flow.py            ← Real UI flow
│   └── conftest_integration.py                    ← Integration fixtures
└── conftest.py              ← Shared fixtures
```

---

## 🔍 Problem Analysis

### Current State: Confusion Between Unit & Integration Tests

Looking at `tests/unit/features/hunt/`:

| File | Actual Type | Issues |
|------|-------------|--------|
| `test_orchestrator_ocr_fallback.py` | **Integration** ❌ | Has 43 mocks (tests real hunt loop) |
| `test_orchestrator_loop.py` | **Integration** ❌ | Has 42 mocks (has threading tests) |
| `test_window_selection_service.py` | **Integration** ❌ | Tests real window APIs |
| `test_window_validation.py` | **Unit** ✅ | Tests single method |
| `test_scene_monster_detector.py` | **Unit** ✅ | Tests feature in isolation |

**Problem**: 
- Integration tests (40+ mocks) live in `unit/`
- Developers don't know which tests are fast vs slow
- `pytest tests/unit/` runs slow because it includes integration tests
- Can't easily skip integration tests for quick feedback

### Why This Matters

```
Current workflow:
$ pytest tests/unit/ -v
tests/unit/features/hunt/test_orchestrator_ocr_fallback.py::test_... PASSED [  2%]  (SLOW - 2s)
tests/unit/features/hunt/test_orchestrator_loop.py::test_... PASSED [  4%]   (SLOW - 2s)
tests/unit/test_action_bar.py::test_... PASSED [ 50%]                (FAST - 0.1s)
Total: ~50 seconds 😞

Desired workflow:
$ pytest tests/unit/ -v      # Only unit tests
~5 seconds! ✨

$ pytest tests/integration/ -v   # Run overnight
~2 minutes (with real I/O)
```

### Classification Rules

**Unit Test**: Tests a single function/class in isolation
- ✅ Mocks all external dependencies
- ✅ <100ms per test
- ✅ No file I/O, network, databases
- ✅ Deterministic (same input = same output)
- ✅ Can run in any order

Examples:
- Testing `target_name_reader.parse_text()`
- Testing `skill_stats.calculate_cooldown()`
- Testing `color_picker.rgb_to_hex()`

**Integration Test**: Tests multiple components working together
- ✅ Uses real file I/O or simplified mocks
- ✅ 100ms - 5s per test
- ✅ Tests workflows across components
- ✅ May have timing-sensitive operations
- ✅ Order may matter

Examples:
- Full hunt orchestrator loop with vision
- Monster editor save/load workflow
- Skill execution with target detection
- Window management with bot operations

---

## 💡 Solution Design

### Test Pyramid (Ideal)

```
        ╱╲              ← E2E Tests (manual, 1-2 per feature)
       ╱  ╲             
      ╱────╲            ← Integration Tests (10-20% of suite, 1-5s each)
     ╱      ╲           
    ╱────────╲          ← Unit Tests (80% of suite, <100ms each)
   ╱__________╲         
   
Current Cabal Auto:
- Unit Tests: 50 files (~400 tests)
- Integration Tests: 5-8 files (~50 tests)
- E2E: Manual only
→ Good distribution! Just need to reorganize.
```

### Directory Structure (After)

```
tests/
├── conftest.py                              ← Shared fixtures
├── pytest.ini                               ← Pytest configuration
├── unit/
│   ├── conftest.py                          ← Unit-specific fixtures
│   ├── features/
│   │   ├── hunt/
│   │   │   ├── test_target_bar_detector.py  ← Single unit (DetectTargetBar)
│   │   │   ├── test_target_name_reader.py   ← Single unit (TargetNameReader)
│   │   │   └── test_skill_stats.py          ← Single unit (SkillStats)
│   │   ├── skills/
│   │   │   ├── test_skill_stats.py
│   │   │   └── test_skill_repo.py
│   │   └── monsters/
│   │       └── test_monster_repo.py
│   ├── system/
│   │   ├── test_bot_manager.py              ← Single class tests
│   │   └── test_window_manager.py
│   ├── db/
│   │   └── test_monster_repository.py
│   ├── ui/
│   │   └── test_monster_editor_tabs.py
│   └── vision/
│       └── test_template_matcher.py
│
├── integration/
│   ├── conftest.py                          ← Integration fixtures
│   ├── features/
│   │   ├── hunt/
│   │   │   ├── test_orchestrator_ocr_fallback.py    ← Full hunt flow
│   │   │   ├── test_orchestrator_loop.py            ← Hunt threading
│   │   │   └── test_vision_integration.py           ← Vision + orchestrator
│   │   └── skills/
│   │       └── test_skill_execution_flow.py
│   ├── ui/
│   │   ├── test_monster_editor_save_load.py
│   │   └── test_hunt_tab_interaction.py
│   └── workflow/
│       └── test_full_hunt_scenario.py               ← E2E-like
│
└── fixtures/
    ├── hunt_data.py                         ← Shared test data
    └── sample_monsters.json                 ← Test data files
```

---

## 📁 Files to Move/Update

### Files to Move to `integration/`

These are currently in `unit/` but are integration tests:

1. ✅ `tests/unit/features/hunt/test_orchestrator_ocr_fallback.py`
   - **Reason**: Tests full orchestrator loop with vision
   - **Move to**: `tests/integration/features/hunt/`

2. ✅ `tests/unit/features/hunt/test_orchestrator_loop.py`
   - **Reason**: Tests threading and hunt lifecycle
   - **Move to**: `tests/integration/features/hunt/`

3. ✅ `tests/unit/features/hunt/test_window_selection_service.py`
   - **Reason**: Tests real window management
   - **Move to**: `tests/integration/features/hunt/`

4. ✅ `tests/integration/test_orchestrator_loop.py`
   - **Reason**: Duplicate of unit/features/hunt version
   - **Action**: Consolidate into new location

### Files to Stay in `unit/`

Already properly classified as unit tests:

- `test_target_name_reader.py` (single class)
- `test_scene_monster_detector.py` (single detection logic)
- `test_window_validation.py` (single validation)
- `test_skill_stats.py` (single calculation)
- `test_monster_repository.py` (single repo)
- etc.

---

## 🔧 Step-by-Step Implementation

### Day 1: Analysis & Planning

#### Step 1: Classify All Tests

Create `test_classification.txt`:

```bash
# Run this analysis script
find tests/unit -name "test_*.py" | while read file; do
    mock_count=$(grep -c "MagicMock\|@patch\|with patch" "$file" || true)
    echo "$file: $mock_count mocks"
done | sort -t: -k2 -rn > test_classification.txt
```

Expected output shows which files are actually integration:
```
tests/unit/features/hunt/test_orchestrator_ocr_fallback.py: 43 mocks
tests/unit/features/hunt/test_orchestrator_loop.py: 42 mocks
tests/unit/features/hunt/test_window_selection_service.py: 8 mocks
tests/unit/test_action_bar.py: 22 mocks
```

#### Step 2: Review & Approve Classification

For each high-mock file, determine if it's truly integration:

```python
# Example: test_orchestrator_ocr_fallback.py
# Analysis:
# - Tests HuntOrchestrator._hunt_loop() method
# - Mocks vision engine, bot manager, etc.
# - Tests threading and event flow
# - Multiple components working together
# → INTEGRATION ✅

# Example: test_skill_stats.py
# Analysis:
# - Tests SkillStats class
# - Single class, no threading
# - Can mock database calls
# - <100ms execution
# → UNIT ✅
```

### Day 2: File Movement & Import Fixing

#### Step 3: Create New Directory Structure

```bash
cd f:\Cabal_Auto

# Create integration directories
mkdir -p tests/integration/features/hunt
mkdir -p tests/integration/features/skills
mkdir -p tests/integration/ui
mkdir -p tests/integration/workflow

# Reorganize unit directories
mkdir -p tests/unit/system
mkdir -p tests/unit/vision
mkdir -p tests/unit/db
```

#### Step 4: Move Integration Tests

```bash
# Move orchestrator tests to integration
mv tests/unit/features/hunt/test_orchestrator_ocr_fallback.py \
   tests/integration/features/hunt/

mv tests/unit/features/hunt/test_orchestrator_loop.py \
   tests/integration/features/hunt/

mv tests/unit/features/hunt/test_window_selection_service.py \
   tests/integration/features/hunt/

# Remove duplicate from integration/ if exists
rm -f tests/integration/test_orchestrator_loop.py
```

#### Step 5: Update Imports in Moved Files

For each moved file, fix import paths:

**Before** (when in `tests/unit/features/hunt/`):
```python
from app_gui import App
from lib.features.hunt.hunt_orchestrator import HuntOrchestrator

# Relative import worked because in unit/features/hunt/
from ...conftest import mock_orchestrator  # NOT GOOD
```

**After** (when in `tests/integration/features/hunt/`):
```python
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app_gui import App
from lib.features.hunt.hunt_orchestrator import HuntOrchestrator

# Now can import from correct conftest
import pytest
# Fixtures from tests/conftest.py are auto-discovered
```

#### Step 6: Fix conftest.py References

Create/update conftest files:

**File: `tests/conftest.py`** (shared by all tests)
```python
"""
Shared pytest configuration and fixtures for all tests.

This conftest.py is loaded by pytest automatically and provides
fixtures used by both unit and integration tests.
"""

import pytest
import sys
from unittest.mock import MagicMock
from pathlib import Path

# Import constants
IS_WINDOWS = sys.platform == 'win32'

# ... Define shared fixtures ...
@pytest.fixture(scope='session', autouse=True)
def setup_platform_mocks():
    """Auto-setup platform mocks for CI/Linux."""
    # ... same as before ...

@pytest.fixture
def mock_orchestrator():
    """Shared mock for orchestrator."""
    # ... from Session 2 ...
```

**File: `tests/unit/conftest.py`** (unit-specific)
```python
"""
Unit test fixtures and configuration.

Unit tests use these fixtures for isolated component testing.
"""

import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_simple_data():
    """Simple test data for unit tests."""
    return {
        "monster_id": 1,
        "name": "Test Monster",
        "level": 10
    }

# Add unit-specific fixtures here
```

**File: `tests/integration/conftest.py`** (integration-specific)
```python
"""
Integration test fixtures and configuration.

Integration tests use these fixtures for multi-component testing.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile

@pytest.fixture
def temp_hunt_config(tmp_path):
    """Temporary hunt configuration for integration tests."""
    config_file = tmp_path / "hunt_config.json"
    config_file.write_text("""{
        "hunt_area": "Test Area",
        "monsters": [{"id": 1, "name": "TestMonster"}]
    }""")
    return config_file

@pytest.fixture
def integration_app_context(mock_orchestrator):
    """Integration context with real-ish components."""
    # Set up something closer to real app state
    yield mock_orchestrator

# Add integration-specific fixtures here
```

### Day 3: Verification & Documentation

#### Step 7: Update Test Discovery

Make sure pytest finds tests in both locations.

Update or create `tests/pytest.ini`:
```ini
[pytest]
testpaths = tests/unit tests/integration
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: mark test as a unit test
    integration: mark test as an integration test
    slow: mark test as slow
```

#### Step 8: Add Test Markers

Update each test file with pytest markers:

**Unit tests**:
```python
import pytest

@pytest.mark.unit
def test_single_function():
    # ...
    pass
```

**Integration tests**:
```python
import pytest

@pytest.mark.integration
def test_full_workflow():
    # ...
    pass
```

#### Step 9: Verify Tests Still Run

```bash
# Test unit only
pytest tests/unit/ -v
# Expected: ~40-50 tests, <30 seconds

# Test integration only
pytest tests/integration/ -v
# Expected: ~15-20 tests, <5 minutes

# Test all
pytest tests/ -v
# Expected: ~60-70 tests total
```

#### Step 10: Update Documentation

Create `tests/README_STRUCTURE.md`:

```markdown
# Test Structure

## Unit Tests (tests/unit/)
Fast, isolated component tests (<100ms each).

- `features/hunt/` - Individual hunt components (target detection, etc.)
- `features/skills/` - Skill system tests
- `features/monsters/` - Monster data tests
- `system/` - System utilities (window manager, etc.)
- `db/` - Database repository tests
- `ui/` - UI component tests (not full workflows)
- `vision/` - Vision detection unit tests

Run with: `pytest tests/unit/`
Expected time: ~30 seconds

## Integration Tests (tests/integration/)
Tests for workflows across multiple components (1-5s each).

- `features/hunt/` - Full hunt orchestrator flows
- `features/skills/` - Skill execution end-to-end
- `ui/` - UI workflows (editor save/load, etc.)
- `workflow/` - Cross-feature scenarios

Run with: `pytest tests/integration/`
Expected time: ~5 minutes

## Running Tests

```bash
# Fast unit tests only
pytest tests/unit/ -v

# Integration tests (slower)
pytest tests/integration/ -v

# Everything
pytest tests/ -v

# By marker
pytest -m unit       # Only unit tests
pytest -m integration  # Only integration
pytest -m "not slow" # Skip slow tests
```
```

### Day 3 (continued): File Organization

#### Step 11: Move Other Tests (Optional)

Consider moving these as well for cleaner organization:

**From `tests/ui/` to `tests/unit/ui/`**:
- `test_color_picker.py`
- `test_button_styles.py`
- etc. (single UI components)

**From `tests/ui/` to `tests/integration/ui/`**:
- `test_monster_editor_left_panel.py` (full editor flow)
- `test_hunt_tab_layout.py` (full tab with interactions)
- etc. (full UI workflows)

#### Step 12: Update CI/CD Configuration

If you have CI/CD (GitHub Actions, etc.), update to run tests separately:

```yaml
# .github/workflows/test.yml (example)
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/unit/ -v --tb=short
        
  integration-tests:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/integration/ -v --tb=short
```

#### Step 13: Commit Changes

```bash
git add tests/

git commit -m "refactor: separate integration and unit tests

- Move integration tests from unit/ to integration/
  * test_orchestrator_ocr_fallback.py
  * test_orchestrator_loop.py
  * test_window_selection_service.py
  
- Create integration/conftest.py for integration fixtures
- Create unit/conftest.py for unit fixtures
- Update pytest.ini for proper test discovery
- Add pytest markers (unit, integration)
- Add test structure documentation

Benefits:
- Unit tests run in ~30 seconds (not with slow integration tests)
- Clear distinction between fast unit and slow integration tests
- Easier to run specific test types
- Better for CI/CD pipelines

File structure:
tests/
├── unit/           ← Fast tests only
├── integration/    ← Slower tests
└── conftest.py     ← Shared config"
```

---

## ✅ Testing Checklist

### Verification Steps
- [ ] All integration tests moved from unit/
- [ ] Import paths updated in all moved files
- [ ] conftest.py files created/updated for each directory
- [ ] pytest.ini configured for test discovery
- [ ] `pytest tests/unit/ -v` → All unit tests pass
- [ ] `pytest tests/integration/ -v` → All integration tests pass
- [ ] `pytest tests/ -v` → All tests pass
- [ ] Unit test execution time < 1 minute
- [ ] Integration test execution time < 10 minutes
- [ ] Test markers working (`pytest -m unit`, `pytest -m integration`)
- [ ] Documentation updated

### Quality Checks
- [ ] No test duplication
- [ ] Correct test types in correct directories
- [ ] Fixtures properly scoped
- [ ] No import errors
- [ ] Test discovery working properly

---

## 📊 Expected Results

### Before Session 5
```
tests/ (mixed structure)
├── unit/ (mixed, 50+ files)
├── integration/ (sparse, 5-8 files)
└── Some files in wrong place
```

### After Session 5
```
tests/ (organized structure)
├── unit/ (fast only, ~45 files)
├── integration/ (slower, ~20 files)
├── conftest.py (shared)
├── unit/conftest.py (unit-specific)
└── integration/conftest.py (integration-specific)
```

### Performance Impact
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Unit test execution | ~50s (mixed) | ~30s (pure unit) | 40% faster ⚡ |
| Integration test execution | ~5m (scattered) | ~5m (organized) | Same |
| Total test execution | ~5.8m | ~5.3m | Minimal change |
| Developer experience | Confusing | Clear | Much better! ✨ |

---

## 🎓 What You'll Learn

1. **Test Classification**: How to properly categorize unit vs integration tests
2. **Test Organization**: Best practices for test directory structure
3. **Pytest Configuration**: Using pytest.ini and markers
4. **Import Management**: Fixing imports after file moves
5. **CI/CD Optimization**: Splitting test execution for faster feedback

---

## ⚠️ Common Issues & Solutions

### Issue 1: Import Errors After Moving Files
**Problem**: `ModuleNotFoundError: No module named 'lib'`
**Solution**: Ensure project root is in Python path or use relative imports

### Issue 2: Fixture Not Found in New Location
**Problem**: `fixture 'mock_orchestrator' not found`
**Solution**: Verify conftest.py files are in parent directories for pytest to discover

### Issue 3: Tests Not Discovered in New Location
**Problem**: `pytest tests/integration/` finds 0 tests
**Solution**: Check pytest.ini testpaths and file naming matches pattern

### Issue 4: Circular Import in conftest
**Problem**: `ImportError: circular import` in conftest
**Solution**: Move common fixtures to tests/conftest.py, specific to unit/conftest.py

---

## 📝 File Movement Checklist

For each file moved:

- [ ] File moved to new location
- [ ] Imports updated (absolute paths preferred)
- [ ] Import `pytest` if using `@pytest.fixture`
- [ ] Test runs successfully: `pytest <file> -v`
- [ ] No import errors
- [ ] Fixtures resolved correctly

---

## 🎯 Session Complete Criteria

✅ **This session is complete when:**
1. All integration tests moved from unit/ to integration/
2. Directory structure clean and organized
3. conftest.py files properly placed and configured
4. pytest.ini configured for test discovery
5. All imports fixed and tests running
6. `pytest tests/unit/` runs only unit tests (fast)
7. `pytest tests/integration/` runs only integration tests
8. Documentation updated
9. Changes committed with proper message
10. CI/CD configuration updated (if applicable)

---

**Status**: 🟢 Ready (best done after Sessions 1-4)
**Estimated Time**: 2-3 days
**Impact**: 🟡 Medium (organization, developer experience)
**Optional**: Can be done anytime, not blocking

---

## 🚀 Quick Start

```bash
cd f:\Cabal_Auto

# Classify tests by mock count
grep -r "MagicMock\|@patch" tests/unit/features/hunt/*.py | cut -d: -f1 | sort | uniq -c

# Create directory structure
mkdir -p tests/integration/features/hunt

# Move integration tests
mv tests/unit/features/hunt/test_orchestrator_ocr_fallback.py tests/integration/features/hunt/
mv tests/unit/features/hunt/test_orchestrator_loop.py tests/integration/features/hunt/

# Create conftest files
touch tests/unit/conftest.py
touch tests/integration/conftest.py

# Verify tests run
pytest tests/unit/ -v
pytest tests/integration/ -v

# Commit
git add tests/
git commit -m "refactor: separate integration and unit tests"
```

---

## 📚 Additional Resources

### Test Organization Best Practices
- [Pytest - Test Discovery](https://docs.pytest.org/en/stable/how-to/organize-tests.html)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Unit vs Integration Tests](https://en.wikipedia.org/wiki/Integration_testing)

### Tools & Utilities
```bash
# Find slow tests
pytest tests/ --durations=10

# Run only fast tests
pytest tests/unit/ -v

# Run with markers
pytest -m "not integration" -v
```

---

**Generated**: 2026-09-03
**Session Level**: 🟡 MEDIUM (Organization improvement)
**Recommended After**: Sessions 1-4 complete
**Priority**: Nice-to-have (not blocking, but recommended for long-term)
