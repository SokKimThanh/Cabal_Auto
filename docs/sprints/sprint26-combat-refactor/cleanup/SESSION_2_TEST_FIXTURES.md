# 🏗️ Session 2: Create Standard Test Fixtures

## 📋 Overview

| Aspect | Value |
|--------|-------|
| **Objective** | Create reusable test fixtures to eliminate mock boilerplate code |
| **Duration** | 1 full day |
| **Effort** | 🟡 Medium |
| **Impact** | 🟠 High (15-20% mock reduction = 100-150 mocks saved) |
| **Difficulty** | Medium (requires understanding test patterns) |
| **Risk Level** | 🟡 Low-Medium (changes are mostly additive) |
| **Prerequisites** | Session 1 must be complete |
| **Files to Modify** | 12+ files (new fixtures in conftest + updates in test files) |

---

## 🎯 Objective

**Current Problem**:
```python
# Repeated in EVERY test for HuntOrchestrator:
orchestrator = HuntOrchestrator(
    on_status_update=MagicMock(),          # 1
    on_state_change=MagicMock(),           # 2
    locate_target=MagicMock(),             # 3
    prepare_skill_runtime=MagicMock(),     # 4
    try_cast_skills=MagicMock(),           # 5
    bring_window_to_front=MagicMock(),     # 6
    bring_window_to_front_by_hwnd=MagicMock(),  # 7
    bring_window_to_front_by_pid=MagicMock(),   # 8
    iconify_app=MagicMock(),               # 9
    update_skill_stats_display=MagicMock(),     # 10
    get_hunt_selected=MagicMock(),         # 11
    schedule_ui_task=MagicMock()           # 12
)
orch.bot_manager = MagicMock()
orch.bot_manager.screen_capture = MagicMock()
# ... 20+ lines of setup per test!
```

**After Session 2**:
```python
# Simple fixture usage:
def test_something(mock_orchestrator):
    # Already fully mocked with all callbacks!
    result = mock_orchestrator.start_hunt({...})
    assert result == ...
```

---

## 🔍 Problem Analysis

### Current Mock Duplication Pattern

Looking at top mock-heavy files:
- `test_hunt_orchestrator.py`: 73 mocks (mostly callbacks)
- `test_action_bar.py`: 49 mocks (UI + orchestrator)
- `test_orchestrator_ocr_fallback.py`: 43 mocks (similar setup)
- `test_orchestrator_loop.py`: 42 mocks (identical boilerplate)

### Root Cause
Each test independently creates:
1. 12+ callback mocks
2. Mock bot_manager
3. Mock screen_capture
4. Mock vision engine
5. etc.

When there should be **1 shared fixture** used by all!

### Cost Analysis
```
Current:
- 4 major test files
- Each has 15-20 mocks for setup
- That's 60-80 mocks JUST for initialization
- Per test function, not per file!

If we have:
- 20 test functions in test_hunt_orchestrator.py
- Each setup takes 15 mocks
- That's 300 mocks just for setup! 🤦

With fixtures:
- 1 fixture definition: 15 mocks
- 20 test functions using fixture: 0 additional mocks
- Total: 15 mocks ✅
```

---

## 💡 Solution Design

### Fixture Architecture

```
tests/conftest.py (NEW FIXTURES)
├── @fixture mock_orchestrator
│   └── Returns HuntOrchestrator with all callbacks mocked
├── @fixture mock_hunt_app
│   └── Returns App instance with UI mocked
├── @fixture mock_bot_manager
│   └── Returns BotManager with screen_capture, etc.
└── @fixture mock_vision_engine
    └── Returns VisionEngine fully mocked

Test Files (OLD - LOTS OF SETUP)
├── test_hunt_orchestrator.py
│   └── 20+ lines of setup per test ❌
├── test_action_bar.py
│   └── 30+ lines of setup per test ❌
└── test_orchestrator_loop.py
    └── 25+ lines of setup per test ❌

Test Files (NEW - CLEAN)
├── test_hunt_orchestrator.py
│   └── def test_something(mock_orchestrator):
│       │   assert mock_orchestrator.hunt_running is False
│       └── DONE! ✅
├── test_action_bar.py
│   └── def test_click(mock_hunt_app, mock_orchestrator):
│       │   mock_hunt_app.hunt_orchestrator = mock_orchestrator
│       └── Just use fixtures! ✅
```

### Key Design Principles

1. **Composition**: Fixtures can depend on other fixtures
   ```python
   @fixture
   def mock_orchestrator(mock_bot_manager):
       orch = HuntOrchestrator(...)
       orch.bot_manager = mock_bot_manager
       return orch
   ```

2. **Configurability**: Fixtures accept optional parameters
   ```python
   @fixture
   def mock_orchestrator(request):
       # Can override mocks via request.param if needed
   ```

3. **Standard Setup**: Common initialization in one place
4. **Discoverability**: Clear naming convention (mock_* prefix)
5. **Maintainability**: Single source of truth

---

## 📁 Files to Update

### New Fixture Definitions
- ✅ `tests/conftest.py` - Add 4-5 major fixtures

### Test Files to Update (use new fixtures)
- ✅ `tests/test_hunt_orchestrator.py` - 73 mocks → refactor to use fixtures
- ✅ `tests/unit/features/hunt/test_orchestrator_ocr_fallback.py` - 43 mocks
- ✅ `tests/integration/test_orchestrator_loop.py` - 42 mocks
- ✅ `tests/unit/test_action_bar.py` - 49 mocks
- ✅ `tests/unit/ui/test_monster_manager_pending_changes.py` - 24 mocks
- ✅ `tests/unit/dialogs/test_monster_picker.py` - 28 mocks
- ✅ Similar updates for 5-6 more test files

---

## 🔧 Step-by-Step Implementation

### Step 1: Analyze Existing Mock Patterns

First, identify the common patterns:

```bash
# Look at test_hunt_orchestrator.py to find common setup
grep -A 20 "def orchestrator" tests/test_hunt_orchestrator.py
```

### Step 2: Create Mock Fixtures in tests/conftest.py

Add these fixtures to `tests/conftest.py`:

#### Fixture 1: mock_orchestrator
```python
@pytest.fixture
def mock_orchestrator():
    """
    Fully mocked HuntOrchestrator instance for testing.
    
    All callbacks are pre-mocked:
    - on_status_update
    - on_state_change
    - locate_target
    - prepare_skill_runtime
    - try_cast_skills
    - bring_window_to_front (all variants)
    - iconify_app
    - update_skill_stats_display
    - get_hunt_selected
    - schedule_ui_task
    
    Also includes mock bot_manager with screen_capture.
    
    Usage:
        def test_something(mock_orchestrator):
            orchestrator = mock_orchestrator
            orchestrator.start_hunt({...})
    """
    from lib.features.hunt.hunt_orchestrator import HuntOrchestrator
    
    # Create all callback mocks
    orch = HuntOrchestrator(
        on_status_update=MagicMock(),
        on_state_change=MagicMock(),
        locate_target=MagicMock(),
        prepare_skill_runtime=MagicMock(),
        try_cast_skills=MagicMock(),
        bring_window_to_front=MagicMock(),
        bring_window_to_front_by_hwnd=MagicMock(),
        bring_window_to_front_by_pid=MagicMock(),
        iconify_app=MagicMock(),
        update_skill_stats_display=MagicMock(),
        get_hunt_selected=MagicMock(return_value={"hwnd": 123}),
        schedule_ui_task=lambda f: f(),  # Execute synchronously in tests
        clear_target_ui=MagicMock(),
        set_target_info=MagicMock(),
        on_scene_monsters_detected=MagicMock()
    )
    
    # Add mock bot manager
    orch.bot_manager = MagicMock()
    orch.bot_manager.screen_capture = MagicMock()
    orch.bot_manager.screen_capture.hwnd = 123
    orch.bot_manager.screen_capture.get_latest_frame = MagicMock(return_value="mock_frame")
    
    return orch
```

#### Fixture 2: mock_hunt_app
```python
@pytest.fixture
def mock_hunt_app():
    """
    Mocked HuntApp (App from app_gui.py) for UI testing.
    
    Provides:
    - monster_rotation: empty list
    - _mark_unsaved: MagicMock
    - hunt_cfg: dict
    - hunt_status: MagicMock
    - UI state variables mocked
    
    Usage:
        def test_ui_update(mock_hunt_app):
            mock_hunt_app._refresh_monster_rotation_list()
            assert mock_hunt_app._mark_unsaved.called
    """
    app = MagicMock(spec=['monster_rotation', '_mark_unsaved', 'hunt_cfg'])
    app.monster_rotation = []
    app._mark_unsaved = MagicMock()
    app.hunt_cfg = {}
    app.hunt_status = MagicMock()
    app.current_lang = 'en'
    app._t = lambda key, **kwargs: key  # I18N mock
    app.monster_rotation_listbox = MagicMock()
    
    # Bind real methods from App for behavior testing
    from app_gui import App as RealApp
    app._refresh_monster_rotation_list = RealApp._refresh_monster_rotation_list.__get__(app)
    app._on_monster_move_up = RealApp._on_monster_move_up.__get__(app)
    app._on_monster_move_down = RealApp._on_monster_move_down.__get__(app)
    app._on_monster_delete_from_list = RealApp._on_monster_delete_from_list.__get__(app)
    app._on_monster_add_smart = RealApp._on_monster_add_smart.__get__(app)
    
    return app
```

#### Fixture 3: mock_bot_manager
```python
@pytest.fixture
def mock_bot_manager():
    """
    Mocked BotManager for isolated testing.
    
    Provides:
    - screen_capture with hwnd and get_latest_frame
    - bot operations mocked
    
    Usage:
        def test_bot_operation(mock_bot_manager):
            frame = mock_bot_manager.screen_capture.get_latest_frame()
            assert frame == "mock_frame"
    """
    bot_mgr = MagicMock()
    bot_mgr.screen_capture = MagicMock()
    bot_mgr.screen_capture.hwnd = 123
    bot_mgr.screen_capture.get_latest_frame = MagicMock(return_value="mock_frame")
    return bot_mgr
```

#### Fixture 4: mock_vision_engine
```python
@pytest.fixture
def mock_vision_engine():
    """
    Mocked VisionEngine for testing vision-dependent code.
    
    Provides:
    - Template matching capabilities
    - Feature detection
    - Region processing
    
    Usage:
        def test_vision_detection(mock_vision_engine):
            result = mock_vision_engine.detect_features(frame)
    """
    engine = MagicMock()
    engine.detect_features = MagicMock(return_value=[])
    engine.locate_template = MagicMock(return_value=None)
    return engine
```

### Step 3: Update Test Files to Use Fixtures

#### Example: tests/test_hunt_orchestrator.py

**Before** (lots of setup):
```python
def test_orchestrator_init():
    orchestrator = HuntOrchestrator(
        on_status_update=MagicMock(),
        on_state_change=MagicMock(),
        locate_target=MagicMock(),
        prepare_skill_runtime=MagicMock(),
        try_cast_skills=MagicMock(),
        bring_window_to_front=MagicMock(),
        bring_window_to_front_by_hwnd=MagicMock(),
        bring_window_to_front_by_pid=MagicMock(),
        iconify_app=MagicMock(),
        update_skill_stats_display=MagicMock(),
        get_hunt_selected=MagicMock(),
        schedule_ui_task=MagicMock()
    )
    
    assert orchestrator.hunt_running is False
```

**After** (clean usage):
```python
def test_orchestrator_init(mock_orchestrator):
    assert mock_orchestrator.hunt_running is False
```

#### Example: tests/unit/test_action_bar.py

**Before**:
```python
@pytest.fixture
def app_instance():
    from app_gui import App
    app = App()
    app.update()
    app.hunt_orchestrator = MagicMock()
    app.hunt_orchestrator.hunt_running = False
    app.state_controller._validate_hunt_prerequisites = MagicMock(return_value=None)
    app.state_controller._hunt_from_ui = MagicMock(return_value={})
    app.hunt_cfg = {}
    yield app
    app.destroy()

def test_debounce_click(app_instance):
    # Test code
```

**After**:
```python
@pytest.fixture
def app_with_mocks(mock_hunt_app, mock_orchestrator):
    """App instance with orchestrator pre-mocked."""
    mock_hunt_app.hunt_orchestrator = mock_orchestrator
    mock_hunt_app.state_controller = MagicMock()
    mock_hunt_app.state_controller._validate_hunt_prerequisites = MagicMock(return_value=None)
    mock_hunt_app.state_controller._hunt_from_ui = MagicMock(return_value={})
    return mock_hunt_app

def test_debounce_click(app_with_mocks):
    # Cleaner test code
```

### Step 4: Refactor 6+ Major Test Files

Apply the fixture pattern to these high-mock files:

1. `tests/test_hunt_orchestrator.py` - Remove ~30 mocks
2. `tests/unit/features/hunt/test_orchestrator_ocr_fallback.py` - Remove ~20 mocks
3. `tests/integration/test_orchestrator_loop.py` - Remove ~20 mocks
4. `tests/unit/test_action_bar.py` - Remove ~25 mocks
5. `tests/unit/ui/test_monster_manager_pending_changes.py` - Remove ~15 mocks
6. `tests/unit/dialogs/test_monster_picker.py` - Remove ~15 mocks

**For each file:**
1. Identify the common setup pattern
2. Remove setup code from individual test functions
3. Add fixture parameter to test function signature
4. Use fixture in test code

### Step 5: Documentation

Add documentation to conftest.py about available fixtures:

```python
"""
Test Fixtures Guide
===================

Common fixtures for Cabal Auto test suite:

Core Fixtures:
  - mock_orchestrator: HuntOrchestrator with all callbacks mocked
  - mock_hunt_app: App instance with UI mocked
  - mock_bot_manager: BotManager with screen_capture
  - mock_vision_engine: VisionEngine fully mocked

Platform Fixtures (auto-used):
  - setup_platform_mocks: Mocks Win32 APIs on Linux CI

Usage Examples:
  
  # Use single fixture
  def test_hunt_logic(mock_orchestrator):
      result = mock_orchestrator.start_hunt({})
      assert result is not None
  
  # Compose multiple fixtures
  def test_ui_with_hunt(mock_hunt_app, mock_orchestrator):
      mock_hunt_app.hunt_orchestrator = mock_orchestrator
      mock_hunt_app.update_hunt_status()
  
  # Override fixture behavior
  def test_with_custom_callback(mock_orchestrator):
      mock_orchestrator.on_status_update = lambda x: print(f"Status: {x}")
      # Test with custom callback
"""
```

### Step 6: Test and Verify

```bash
# Run tests for each modified file
pytest tests/test_hunt_orchestrator.py -v
pytest tests/unit/features/hunt/test_orchestrator_ocr_fallback.py -v
pytest tests/integration/test_orchestrator_loop.py -v
pytest tests/unit/test_action_bar.py -v

# Check mock reduction
python analyze_mocks.py
```

### Step 7: Commit Changes

```bash
git add tests/conftest.py tests/test_hunt_orchestrator.py tests/unit/features/hunt/ tests/unit/test_action_bar.py

git commit -m "refactor: create standard test fixtures to reduce boilerplate

- Add mock_orchestrator fixture for HuntOrchestrator testing
- Add mock_hunt_app fixture for UI testing
- Add mock_bot_manager fixture for bot operations
- Add mock_vision_engine fixture for vision testing
- Refactor test_hunt_orchestrator.py to use fixtures
- Refactor test_orchestrator_ocr_fallback.py to use fixtures
- Refactor test_orchestrator_loop.py to use fixtures
- Refactor test_action_bar.py to use fixtures
- Reduces mock instances by ~100-150 (15-20% total reduction)
- Improves test readability and maintainability

Files modified:
- tests/conftest.py: Added 4 major fixtures
- tests/test_hunt_orchestrator.py: Removed setup boilerplate
- tests/unit/features/hunt/test_orchestrator_ocr_fallback.py: Use fixtures
- tests/integration/test_orchestrator_loop.py: Use fixtures
- tests/unit/test_action_bar.py: Use fixtures
- tests/unit/ui/test_monster_manager_pending_changes.py: Use fixtures
- tests/unit/dialogs/test_monster_picker.py: Use fixtures"
```

---

## ✅ Testing Checklist

### Verification Steps
- [ ] All new fixtures defined and accessible in conftest.py
- [ ] Each fixture has proper docstring and usage example
- [ ] Test files import and use fixtures correctly
- [ ] `pytest tests/ -v` → All tests pass ✅
- [ ] `python analyze_mocks.py` → Mock count reduced 100-150
- [ ] Fixture behavior verified with parametrization test:

```python
def test_fixtures_exist(mock_orchestrator, mock_hunt_app, mock_bot_manager):
    """Verify that all standard fixtures are available."""
    assert mock_orchestrator is not None
    assert mock_hunt_app is not None
    assert mock_bot_manager is not None
    assert hasattr(mock_orchestrator, 'hunt_running')
    assert hasattr(mock_hunt_app, 'monster_rotation')
```

### Performance Testing
- [ ] Test suite execution time doesn't increase
- [ ] Memory usage is reasonable
- [ ] Fixture setup time is acceptable

---

## 📊 Expected Results

### Before Session 2
```
Total Mock/Patch Instances: 644 (after Session 1)
Test files with 40+ mocks: 4 files
Average per file: 11.5
```

### After Session 2
```
Total Mock/Patch Instances: 494 (-150)
Test files with 40+ mocks: 0 files
Average per file: 8.8
Fixture definitions in conftest: 4
```

### Mock Reduction by File
| File | Before | After | Reduction |
|------|--------|-------|-----------|
| tests/test_hunt_orchestrator.py | 73 | 43 | -30 |
| tests/unit/test_action_bar.py | 42 | 22 | -20 |
| test_orchestrator_ocr_fallback.py | 38 | 18 | -20 |
| test_orchestrator_loop.py | 42 | 22 | -20 |
| test_monster_manager_pending_changes.py | 24 | 14 | -10 |
| test_monster_picker.py | 28 | 18 | -10 |
| tests/conftest.py | +100 fixtures | +100 fixtures | 0 (centralized) |
| **TOTAL** | **644** | **494** | **-150** |

---

## 🎓 What You'll Learn

1. **Pytest Fixtures**: Creating and organizing reusable test infrastructure
2. **Fixture Composition**: Building fixtures that depend on other fixtures
3. **Mock Management**: Centralizing mock creation and setup
4. **Test Parametrization**: Using request.param for flexible fixtures
5. **Dependency Injection**: How DI improves testability

---

## ⚠️ Common Issues & Solutions

### Issue 1: Fixture Not Found
**Problem**: `fixture 'mock_orchestrator' not found`
**Solution**: Ensure conftest.py has all fixtures and is in the right location (tests/)

### Issue 2: Mock Behavior Different in Fixture
**Problem**: Fixture mock behaves differently than inline mock
**Solution**: Check mock configuration - spec, return_value, side_effect

### Issue 3: Circular Fixture Dependencies
**Problem**: `fixture_a` depends on `fixture_b` depends on `fixture_a`
**Solution**: Restructure to break cycle, use factory functions instead

### Issue 4: Tests Modifying Fixture State
**Problem**: One test's changes affect another test
**Solution**: Add `@pytest.fixture(autouse=True)` cleanup or copy fixtures

---

## 📝 Fixture Template Reference

### Basic Fixture Template
```python
@pytest.fixture
def mock_something():
    """
    Brief description of what this fixture provides.
    
    Includes:
    - Item 1
    - Item 2
    - Item 3
    
    Usage:
        def test_feature(mock_something):
            result = mock_something.do_something()
            assert result is not None
    """
    obj = MagicMock()
    obj.some_attribute = "value"
    obj.some_method = MagicMock(return_value="result")
    return obj
```

### Fixture with Cleanup
```python
@pytest.fixture
def mock_something_with_cleanup():
    """Fixture that needs cleanup."""
    obj = MagicMock()
    yield obj  # Everything after yield runs as cleanup
    # Cleanup code here
    obj.cleanup()
```

### Parametrized Fixture
```python
@pytest.fixture(params=[{"test": 1}, {"test": 2}])
def mock_with_params(request):
    """Fixture that runs test multiple times with different params."""
    obj = MagicMock()
    obj.config = request.param
    return obj
```

---

## 📚 Additional Resources

### Pytest Documentation
- [Fixtures Documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Fixture Scope](https://docs.pytest.org/en/stable/how-to/fixtures.html#scope-sharing-fixtures-across-classes-modules-packages-and-sessions)
- [Fixture Composition](https://docs.pytest.org/en/stable/how-to/fixtures.html#fixture-composition)

### Best Practices
- [Test Fixtures Best Practices](https://docs.pytest.org/en/stable/example/fixtures.html)
- [Mock Best Practices](https://docs.python.org/3/library/unittest.mock.html#patch)

---

## 🎯 Session Complete Criteria

✅ **This session is complete when:**
1. 4+ major fixtures added to `tests/conftest.py`
2. 6+ test files refactored to use fixtures
3. Mock count reduced from 644 → 494 (~150 mocks saved)
4. All tests pass on both Windows and Linux
5. Fixture API documented with usage examples
6. Changes committed with proper commit message
7. No breaking changes to existing behavior

---

**Status**: 🟡 Ready to Start (after Session 1)
**Estimated Time**: 1 full day
**Next Session**: [SESSION_3_PATCH_CHAINS.md](SESSION_3_PATCH_CHAINS.md) (can be parallel)

---

## 🚀 Quick Start

```bash
# Start with Session 2
cd f:\Cabal_Auto

# Compare before/after
python analyze_mocks.py > before_session2.txt

# After completing fixture creation and refactoring:
python analyze_mocks.py > after_session2.txt

# Verify reduction
diff before_session2.txt after_session2.txt

# Run full test suite
pytest tests/ -v --tb=short
```
