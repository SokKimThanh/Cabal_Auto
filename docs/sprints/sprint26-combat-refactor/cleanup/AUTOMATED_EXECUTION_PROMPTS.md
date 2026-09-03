# 🤖 Automated Execution Prompts - Sprint 26 Cleanup Sessions

> Convert each session into an automated prompt that can be executed via subagent or direct instruction

---

## 📋 Master Execution Plan

Run sessions in this order (dependencies):
```
Session 1 → Session 2 → Session 3 (parallel) ↓
                        ↓
                    Session 4 → Session 5
```

**Timeline**: 2-3 weeks (distributed)
**Total Effort**: ~3-4 developer-weeks
**Risk Level**: Low-Medium (refactoring heavy, but well-isolated)

---

## 🎯 Session 1: Consolidate Platform Mocks

### Automated Execution Prompt

```
TASK: Consolidate duplicated sys.modules platform mocks into tests/conftest.py

OBJECTIVE:
- Remove platform mock duplication from 6+ test files
- Create centralized auto-use fixture in tests/conftest.py
- Platform mocks: win32gui, cv2, numpy, win32con, win32process, win32api, pywintypes
- Expected result: 30-50 fewer mock instances, single source of truth

IMPLEMENTATION STEPS:

1. ANALYSIS PHASE (10 min)
   □ Search all test files for sys.modules patches:
     grep -r "sys\.modules\[" tests/ --include="*.py"
   □ Create inventory of all mocked modules
   □ List affected test files

2. CREATE FIXTURE PHASE (20 min)
   □ Add to tests/conftest.py:
     @pytest.fixture(autouse=True, scope='session')
     def setup_platform_mocks():
         """Centralized platform compatibility mocks for cross-platform testing."""
         import sys
         if platform.system() != 'Windows':
             mocks_dict = {
                 'win32gui': MagicMock(),
                 'cv2': MagicMock(),
                 'numpy': MagicMock(),
                 'win32con': MagicMock(),
                 'win32process': MagicMock(),
                 'win32api': MagicMock(),
                 'pywintypes': MagicMock(),
             }
             for module_name, mock_module in mocks_dict.items():
                 sys.modules[module_name] = mock_module
             yield
             # Cleanup if needed
         else:
             yield

3. REMOVE DUPLICATION PHASE (30 min)
   Target files (in order):
   □ tests/unit/test_action_bar.py
   □ tests/ui/test_footer_visibility.py
   □ tests/ui/test_hunt_bottom_logs.py
   □ tests/unit/features/hunt/test_orchestrator_ocr_fallback.py
   □ tests/unit/features/hunt/test_window_selection_service.py
   □ tests/unit/ui/controllers/test_hotkey_controller.py
   
   For each file:
   - Remove sys.modules patches
   - Remove import statements for platform mocks if present
   - Keep all other fixtures and setup intact

4. VERIFICATION PHASE (15 min)
   □ Run: pytest tests/ -v --tb=short
   □ Confirm: All tests pass
   □ Confirm: No platform import errors on Linux CI
   □ Confirm: No duplicate sys.modules patches remain

5. CLEANUP PHASE (10 min)
   □ Remove any unused imports from modified files
   □ Update file comments if they mention platform mocks
   □ Verify no orphaned mock cleanup code remains

EXPECTED OUTCOME:
✅ tests/conftest.py has centralized platform mock fixture
✅ 6 test files cleaned of duplication
✅ Platform mock coverage maintained
✅ All tests pass on Windows and Linux
```

### Acceptance Criteria

- [ ] No `sys.modules['win32*']` patches outside conftest.py
- [ ] Fixture applies to all test runs (autouse=True)
- [ ] Full test suite passes: `pytest tests/`
- [ ] Platform mocks only applied on non-Windows (use platform.system() check)
- [ ] Single source of truth: one place to update platform mocks

---

## 🎯 Session 2: Create Standard Test Fixtures

### Automated Execution Prompt

```
TASK: Create reusable test fixtures to eliminate mock boilerplate

OBJECTIVE:
- Reduce mock setup duplication across 12+ test files
- Expected result: 100-150 fewer mock instances
- Create 4-5 major fixtures in tests/conftest.py
- Update high-mock test files to use new fixtures
- Dependency: Session 1 must be complete

IMPLEMENTATION STEPS:

1. ANALYSIS PHASE (30 min)
   □ Identify mock-heavy test files:
     - tests/test_hunt_orchestrator.py (73 mocks)
     - tests/unit/test_action_bar.py (49 mocks)
     - tests/unit/features/hunt/test_orchestrator_ocr_fallback.py (43 mocks)
     - tests/unit/features/hunt/test_orchestrator_loop.py (42 mocks)
     - tests/unit/ui/test_monster_manager_pending_changes.py (24 mocks)
     - tests/unit/dialogs/test_monster_picker.py (28 mocks)
     - 5-6 more similar files
   
   □ For each file, identify common patterns:
     - How many callback mocks?
     - Are bot_manager mocks shared?
     - Do they mock vision engine?
     - Common initialization patterns?

2. DESIGN FIXTURES PHASE (30 min)
   Design 4 main fixtures in tests/conftest.py:
   
   Fixture 1: mock_bot_manager
   - BotManager instance
   - screen_capture mocked
   - All APIs mocked
   
   Fixture 2: mock_orchestrator
   - HuntOrchestrator instance
   - All 12+ callbacks pre-mocked
   - Uses mock_bot_manager fixture
   
   Fixture 3: mock_hunt_app
   - App instance
   - hunt_orchestrator set to mock_orchestrator
   - UI components mocked
   
   Fixture 4: mock_vision_engine
   - VisionEngine fully mocked
   - Can detect templates
   - Can detect monsters

3. IMPLEMENT FIXTURES PHASE (1.5 hours)
   □ Add mock_bot_manager fixture:
     @pytest.fixture
     def mock_bot_manager():
         mgr = MagicMock(spec=BotManager)
         mgr.screen_capture = MagicMock()
         mgr.screen_capture.return_value = np.zeros((1080, 1920, 3))
         # Add more specific mocks...
         return mgr

   □ Add mock_orchestrator fixture:
     @pytest.fixture
     def mock_orchestrator(mock_bot_manager):
         orch = HuntOrchestrator(
             on_status_update=MagicMock(),
             on_state_change=MagicMock(),
             # ... all 12+ callbacks ...
         )
         orch.bot_manager = mock_bot_manager
         return orch
   
   □ Add mock_hunt_app fixture:
     @pytest.fixture
     def mock_hunt_app(mock_orchestrator):
         app = MagicMock(spec=App)
         app.hunt_orchestrator = mock_orchestrator
         return app
   
   □ Add mock_vision_engine fixture:
     @pytest.fixture
     def mock_vision_engine():
         engine = MagicMock(spec=VisionEngine)
         engine.detect_templates = MagicMock(return_value=[])
         engine.detect_monsters = MagicMock(return_value=[])
         return engine

4. REFACTOR TEST FILES PHASE (2-3 hours)
   Target files (process in batches):
   
   Batch 1 (Critical - 73 mocks):
   □ tests/test_hunt_orchestrator.py
     - Find: All setup code creating HuntOrchestrator
     - Replace: Use mock_orchestrator fixture instead
     - Update: All test signatures to use fixture parameter
   
   Batch 2 (High - 40+ mocks):
   □ tests/unit/features/hunt/test_orchestrator_ocr_fallback.py
   □ tests/unit/features/hunt/test_orchestrator_loop.py
   □ tests/unit/test_action_bar.py
   
   Batch 3 (Medium - 20-30 mocks):
   □ tests/unit/ui/test_monster_manager_pending_changes.py
   □ tests/unit/dialogs/test_monster_picker.py
   □ Similar 4-5 files

5. VERIFICATION PHASE (1 hour)
   □ Run: pytest tests/ -v
   □ Confirm: All tests pass
   □ Confirm: No orphaned mock setup code
   □ Confirm: Fixture usage is consistent
   □ Count: Mock count reduction (before/after)

EXPECTED OUTCOME:
✅ 4-5 reusable fixtures in tests/conftest.py
✅ 12+ test files using fixtures instead of boilerplate
✅ 100-150 fewer total mock instances
✅ All tests pass
✅ Mock setup 5-10x simpler to read
```

### Acceptance Criteria

- [ ] `mock_orchestrator` fixture exists with all 12+ callbacks pre-mocked
- [ ] `mock_bot_manager`, `mock_hunt_app`, `mock_vision_engine` fixtures exist
- [ ] Fixtures properly compose (mock_orchestrator uses mock_bot_manager)
- [ ] At least 8 test files refactored to use fixtures
- [ ] Mock count reduced by 100+ instances
- [ ] All tests pass: `pytest tests/`

---

## 🎯 Session 3: Replace Nested Patch Chains

### Automated Execution Prompt

```
TASK: Convert nested patch() context managers to clean decorator syntax

OBJECTIVE:
- Replace 3-5 level nested with patch() chains with @patch decorators
- Improve readability and maintainability
- Can run in parallel with Sessions 1-2
- Expected result: ~3% mock reduction, much cleaner code

IMPLEMENTATION STEPS:

1. IDENTIFY PROBLEMATIC FILES (20 min)
   □ Search for nested patches:
     grep -n "with patch" tests/unit/ui/ -A 3 --include="*.py"
   
   Priority files (with 3+ level nesting):
   □ tests/unit/ui/test_monster_editor_left_panel.py (Lines 78, 104, 139, 178+)
   □ tests/unit/ui/test_monster_editor_save.py
   □ tests/unit/ui/test_monster_editor_data.py

2. ANALYZE PATTERNS (30 min)
   For each file:
   □ Count number of with patch() statements
   □ Check if patches are used in multiple tests (candidate for fixture)
   □ Note any inter-dependencies between patches
   □ Check parameter usage for each patch

3. REFACTOR TO DECORATORS (2 hours)
   For each test function with nested patches:
   
   Conversion pattern:
   ─────────────────
   BEFORE:
   def test_something():
       with patch('path1', mock1), \\
            patch('path2', mock2), \\
            patch('path3', mock3):
           # Test code

   AFTER:
   @patch('path3', mock3)
   @patch('path2', mock2)
   @patch('path1', mock1)
   def test_something(mock1, mock2, mock3):
       # Test code
   
   KEY RULE: Decorator order reverses parameter order!
             Top decorator = rightmost parameter

   Examples to refactor:
   □ tests/unit/ui/test_monster_editor_left_panel.py::test_create (Line 78)
   □ tests/unit/ui/test_monster_editor_left_panel.py::test_save (Line 104)
   □ tests/unit/ui/test_monster_editor_left_panel.py::test_validate (Line 139)
   □ tests/unit/ui/test_monster_editor_save.py - all tests with patches
   □ tests/unit/ui/test_monster_editor_data.py - all tests with patches

4. EXTRACT COMMON PATTERNS TO FIXTURES (1 hour)
   If same patch chain appears in 3+ tests:
   □ Extract to shared fixture in conftest.py or test file
   □ Update tests to use fixture instead of decorators
   
   Example:
   ─────────
   @pytest.fixture
   def patched_monster_editor():
       with patch('ui.monster_editor.load_data'), \\
            patch('ui.monster_editor.save_data'), \\
            patch('tkinter.messagebox'):
           yield

   def test_one(patched_monster_editor):
       # Use fixture

5. VERIFICATION (30 min)
   □ Run: pytest tests/unit/ui/ -v
   □ Confirm: All tests pass
   □ Verify: No changes in test behavior (same assertions)
   □ Code review: Check decorator order is correct

EXPECTED OUTCOME:
✅ No nested patch chains >2 levels deep
✅ All patches using decorator syntax
✅ Improved readability (test code at proper indentation)
✅ Common patch patterns extracted to fixtures
✅ All tests pass with identical behavior
```

### Acceptance Criteria

- [ ] No `with patch(...):` blocks nesting more than 2 levels deep
- [ ] `@patch` decorators used instead of nested context managers
- [ ] Decorator order reversal properly handled (correct parameter mapping)
- [ ] All 3 target files refactored
- [ ] Tests behave identically (same assertions, same passing)
- [ ] All tests pass: `pytest tests/unit/ui/`

---

## 🎯 Session 4: Refactor HuntOrchestrator (MAJOR)

### Automated Execution Prompt

```
TASK: Reduce HuntOrchestrator callbacks from 15 to 1 via handler object pattern

OBJECTIVE:
- Refactor orchestrator to accept single HuntStatusHandler object
- Move 15+ callbacks into structured handler with clear responsibilities
- Expected result: 30% mock reduction (200-300 mocks saved)
- This is a MAJOR refactoring affecting 15+ files
- Dependency: Sessions 1-2 should be complete
- Duration: 3-5 days (distributed effort)

IMPLEMENTATION STEPS:

PHASE A: DESIGN (1 day)
─────────────────────────

1. DEFINE HANDLER ABSTRACT CLASS (2 hours)
   □ Create lib/orchestrator/hunt_status_handler.py:
   
   from abc import ABC, abstractmethod
   from typing import Dict, Tuple, Callable, Optional
   
   class HuntStatusHandler(ABC):
       """Abstract base class for orchestrator status callbacks."""
       
       # UI Update callbacks
       @abstractmethod
       def on_status_update(self, message: str) -> None:
           """Status message to display in UI."""
           pass
       
       @abstractmethod
       def on_state_change(self, state: str) -> None:
           """Hunt state changed."""
           pass
       
       @abstractmethod
       def update_skill_stats_display(self, stats: dict) -> None:
           """Update skill statistics in UI."""
           pass
       
       @abstractmethod
       def set_target_info(self, info: str) -> None:
           """Set target information display."""
           pass
       
       @abstractmethod
       def clear_target_ui(self) -> None:
           """Clear target information from UI."""
           pass
       
       # Window Management callbacks
       @abstractmethod
       def bring_window_to_front(self, window_name: str) -> bool:
           """Bring window to foreground."""
           pass
       
       @abstractmethod
       def bring_window_to_front_by_hwnd(self, hwnd: int) -> bool:
           """Bring window to front by handle."""
           pass
       
       @abstractmethod
       def bring_window_to_front_by_pid(self, pid: int) -> bool:
           """Bring window to front by process ID."""
           pass
       
       @abstractmethod
       def iconify_app(self) -> None:
           """Minimize application."""
           pass
       
       # Game Logic callbacks
       @abstractmethod
       def locate_target(self, params: Dict) -> Tuple[int, int]:
           """Locate target position."""
           pass
       
       @abstractmethod
       def prepare_skill_runtime(self, skill_def: Dict) -> list:
           """Prepare skill for execution."""
           pass
       
       @abstractmethod
       def try_cast_skills(self) -> None:
           """Attempt to cast skills."""
           pass
       
       @abstractmethod
       def on_scene_monsters_detected(self, monsters: Tuple) -> None:
           """Monsters detected in scene."""
           pass
       
       # Utility callbacks
       @abstractmethod
       def get_hunt_selected(self) -> Dict:
           """Get currently selected hunt."""
           pass
       
       @abstractmethod
       def schedule_ui_task(self, task: Callable[[], None]) -> None:
           """Schedule task to run on UI thread."""
           pass

2. UPDATE ORCHESTRATOR SIGNATURE (1 hour)
   □ Modify lib/orchestrator/hunt_orchestrator.py:
   
   BEFORE:
   def __init__(
       self,
       on_status_update: Callable,
       on_state_change: Callable,
       locate_target: Callable,
       prepare_skill_runtime: Callable,
       try_cast_skills: Callable,
       bring_window_to_front: Callable,
       bring_window_to_front_by_hwnd: Callable,
       bring_window_to_front_by_pid: Callable,
       iconify_app: Callable,
       update_skill_stats_display: Callable,
       get_hunt_selected: Callable,
       schedule_ui_task: Callable,
       ...  # 3 more
   ):
   
   AFTER:
   def __init__(
       self,
       handler: HuntStatusHandler,
       bot_manager: BotManager,
       vision_engine: VisionEngine,
       skill_runtime: SkillRuntimeService
   ):
   
   □ Update all internal callback invocations:
     OLD: self.on_status_update("message")
     NEW: self.handler.on_status_update("message")

3. CREATE ADAPTER FOR APP (1 hour)
   □ In app_gui.py, create adapter:
   
   class AppHuntHandler(HuntStatusHandler):
       """Adapts App UI callbacks to HuntStatusHandler interface."""
       
       def __init__(self, app):
           self.app = app
       
       def on_status_update(self, message: str) -> None:
           self.app.after(0, lambda: self.app.update_status(message))
       
       # ... implement all methods, calling app methods through after()

PHASE B: UPDATE LIBRARY (2 days)
────────────────────────────────

4. REFACTOR ALL CALLBACK INVOCATIONS (1 day)
   Files to update:
   □ lib/orchestrator/hunt_orchestrator.py (main file)
     - Replace all self.on_*() calls with self.handler.*()
     - Verify no orphaned callback references
   
   □ lib/orchestrator/hunt_runner.py (if exists)
     - Update to pass handler instead of individual callbacks
   
   □ lib/features/hunt/* (all hunt-related modules)
     - Any code that invokes callbacks → update to use handler

5. UPDATE TEST MOCK FIXTURES (1 day)
   □ Update mock_orchestrator fixture in tests/conftest.py:
   
   BEFORE:
   @pytest.fixture
   def mock_orchestrator():
       return HuntOrchestrator(
           on_status_update=MagicMock(),
           on_state_change=MagicMock(),
           # ... 15 more ...
       )
   
   AFTER:
   @pytest.fixture
   def mock_orchestrator():
       handler = MagicMock(spec=HuntStatusHandler)
       return HuntOrchestrator(
           handler=handler,
           bot_manager=MagicMock(),
           vision_engine=MagicMock(),
           skill_runtime=MagicMock()
       )

PHASE C: UPDATE APP LAYER (1 day)
────────────────────────────────

6. REFACTOR APP INITIALIZATION (1 day)
   □ In app_gui.py HuntTab.__init__():
   
   BEFORE:
   self.hunt_orchestrator = HuntOrchestrator(
       on_status_update=self.update_status,
       on_state_change=self.update_hunt_state,
       # ... pass 15 individual callbacks ...
   )
   
   AFTER:
   handler = AppHuntHandler(self)
   self.hunt_orchestrator = HuntOrchestrator(
       handler=handler,
       bot_manager=self.bot_manager,
       vision_engine=self.vision_engine,
       skill_runtime=self.skill_runtime
   )

PHASE D: VERIFICATION (1 day)
─────────────────────────────

7. TEST ALL FUNCTIONALITY (1 day)
   □ Unit tests: pytest tests/test_hunt_orchestrator.py -v
   □ Integration: pytest tests/integration/test_hunt_flow.py -v
   □ Manual: Run app, verify hunt starts/stops correctly
   □ Verify: All callbacks still fire correctly
   □ Verify: No callback invocation errors

EXPECTED OUTCOME:
✅ HuntStatusHandler abstract class exists
✅ HuntOrchestrator accepts single handler instead of 15 callbacks
✅ AppHuntHandler adapter in app_gui.py
✅ All library code updated to use handler
✅ All tests updated with new fixture
✅ 200-300 fewer mock instances
✅ All unit + integration tests pass
✅ App functional with hunt flow working
```

### Acceptance Criteria

- [ ] `HuntStatusHandler` abstract class created
- [ ] `HuntOrchestrator.__init__()` takes `handler: HuntStatusHandler` instead of 15 callbacks
- [ ] `AppHuntHandler` adapter created in app_gui.py
- [ ] All internal callback invocations updated (`self.on_*()` → `self.handler.*()`)
- [ ] Mock fixture updated to use handler
- [ ] Mock count reduced by 200+ instances across test suite
- [ ] All tests pass: `pytest tests/`
- [ ] App runs and hunt flow works end-to-end

---

## 🎯 Session 5: Split Integration/Unit Tests

### Automated Execution Prompt

```
TASK: Separate integration tests from unit tests into distinct directories

OBJECTIVE:
- Reorganize test directory structure for clarity
- Enable fast unit test runs (5-10 seconds vs 50+ seconds)
- Dependency: Sessions 1-4 should be complete
- Expected result: Clear test hierarchy, faster feedback loop
- Duration: 2-3 days (mostly file movement and import fixing)

IMPLEMENTATION STEPS:

PHASE A: ANALYSIS & CLASSIFICATION (1 day)
───────────────────────────────────────────

1. CLASSIFY ALL TESTS (4 hours)
   □ Examine every test file to classify:
     - Unit Test: Tests 1 component in isolation, <100ms, all mocks
     - Integration Test: Tests multiple components, 100ms-5s, some real I/O
   
   UNIT TEST EXAMPLES:
   ✅ test_target_name_reader.py (parses text, returns strings)
   ✅ test_skill_stats.py (calculates cooldowns, pure logic)
   ✅ test_color_picker.py (RGB to hex conversion)
   ✅ test_hunt_state_machine.py (state transitions, all mocked)
   
   INTEGRATION TEST EXAMPLES:
   ✅ test_orchestrator_loop.py (real hunt flow, threading)
   ✅ test_monster_editor_flow.py (editor save/load/display)
   ✅ test_vision_integration.py (vision engine with templates)
   ✅ test_window_selection_service.py (real window APIs)
   
   RULES:
   - If test uses 30+ mocks → likely integration
   - If test has 1-3 mocks → likely unit
   - If test uses threading/timing → integration
   - If test mocks only dependency → unit
   - If test uses real I/O (files, DB) → integration

2. CREATE CLASSIFICATION DOCUMENT (1 hour)
   Create file: tests/CLASSIFICATION.md
   
   # Test Classification Results
   
   ## Unit Tests (Fast, <100ms each)
   - tests/unit/test_target_name_reader.py
   - tests/unit/features/hunt/test_skill_stats.py
   - ... (30-40 files)
   
   ## Integration Tests (Slower, 100ms-5s each)
   - tests/integration/features/hunt/test_orchestrator_loop.py
   - tests/integration/ui/test_monster_editor_flow.py
   - ... (8-15 files)
   
   ## Stats
   - Unit tests: 350+ tests, ~5 seconds total
   - Integration tests: 50+ tests, ~3 minutes total

PHASE B: REORGANIZE FILES (1 day)
──────────────────────────────────

3. CREATE NEW DIRECTORY STRUCTURE (2 hours)
   
   Target structure:
   ┌─ tests/
   ├─ conftest.py                          ← Shared fixtures
   ├─ unit/
   │  ├─ conftest_unit.py                  ← Unit-specific fixtures
   │  ├─ test_*.py                         ← Single-unit tests
   │  ├─ features/
   │  │  ├─ hunt/
   │  │  │  ├─ test_skill_stats.py
   │  │  │  ├─ test_target_reader.py
   │  │  │  └─ test_state_machine.py
   │  │  └─ skills/
   │  │     └─ test_cooldown_calc.py
   │  └─ ui/
   │     └─ test_color_picker.py
   ├─ integration/
   │  ├─ conftest_integration.py            ← Integration fixtures (real I/O)
   │  ├─ features/
   │  │  ├─ hunt/
   │  │  │  ├─ test_orchestrator_loop.py
   │  │  │  └─ test_vision_integration.py
   │  │  └─ skills/
   │  └─ ui/
   │     ├─ test_monster_editor_flow.py
   │     └─ test_window_management.py
   └─ e2e/
      └─ test_full_hunt_flow.py             ← Manual/CI only

4. MOVE UNIT TEST FILES (2 hours)
   □ Create directories:
     mkdir -p tests/unit/features/hunt
     mkdir -p tests/unit/features/skills
     mkdir -p tests/unit/ui
   
   □ Move unit tests:
     mv tests/unit/test_*.py tests/unit/
     mv tests/unit/features/hunt/test_*_unit.py tests/unit/features/hunt/
     (Keep integration-looking files for Phase C)

5. MOVE INTEGRATION TEST FILES (1.5 hours)
   □ Create directories:
     mkdir -p tests/integration/features/hunt
     mkdir -p tests/integration/features/skills
     mkdir -p tests/integration/ui
   
   □ Move integration tests:
     mv tests/unit/features/hunt/test_orchestrator_*.py tests/integration/features/hunt/
     mv tests/unit/features/hunt/test_*_flow.py tests/integration/ui/
     mv tests/ui/ tests/integration/ui/
     (Update as per CLASSIFICATION.md)

PHASE C: FIX IMPORTS & CONFTEST (1 day)
──────────────────────────────────────

6. CREATE CONFTEST FILES (1 hour)
   
   □ tests/conftest.py (shared by all tests):
     - Platform mock fixtures (from Session 1)
     - mock_bot_manager, mock_orchestrator (from Session 2)
     - Don't import real modules or set up real I/O
   
   □ tests/unit/conftest_unit.py (unit test fixtures):
     - Additional unit-specific fixtures if needed
     - Mock-heavy fixtures
   
   □ tests/integration/conftest_integration.py (integration fixtures):
     - Fixtures that do real I/O
     - Fixtures that use real file/DB paths
     - Fixtures with longer setup time

7. FIX ALL IMPORTS (3 hours)
   For each moved file:
   □ Update import statements:
     OLD: from lib.orchestrator import HuntOrchestrator
     (still works, no path change needed)
     
     OLD: from tests.conftest import mock_orchestrator
     NEW: from conftest import mock_orchestrator
     (if tests/ was in path)
   
   □ Fix relative imports:
     Files in tests/unit/features/hunt/ might need:
     OLD: from ...conftest import fixture
     NEW: from tests.conftest import fixture
     or: from conftest import fixture (if pytest adds to path)
   
   Tool: Use IDE refactor-all-imports or manual grep+sed
   
   Verification: pytest tests/unit/ --collect-only (should find all)

8. PYTEST CONFIGURATION (30 min)
   □ Update pytest.ini:
   
   [pytest]
   testpaths = tests
   python_files = test_*.py
   python_classes = Test*
   python_functions = test_*
   
   # Markers for test selection
   markers =
       unit: unit test (run with -m unit)
       integration: integration test (run with -m integration)
       e2e: end-to-end test (run with -m e2e)
       slow: slow test (skip with -m 'not slow')
       db: database test
       ui: UI test
   
   □ Add pytest markers to test files:
   
   @pytest.mark.unit
   def test_something():
       pass
   
   @pytest.mark.integration
   def test_workflow():
       pass

PHASE D: VERIFICATION & OPTIMIZATION (1 day)
──────────────────────────────────────────

9. VERIFY TEST DISCOVERY (1 hour)
   □ Run: pytest tests/unit/ --collect-only | wc -l
     Expected: 350+ unit tests collected
   
   □ Run: pytest tests/integration/ --collect-only | wc -l
     Expected: 50+ integration tests collected
   
   □ Run: pytest tests/ --collect-only | wc -l
     Expected: 400+ total tests

10. VERIFY TEST EXECUTION (1 hour)
    □ Run unit tests only:
      pytest tests/unit/ -v
      Expected: ~5-10 seconds, all pass
    
    □ Run integration tests:
      pytest tests/integration/ -v
      Expected: ~3 minutes, all pass
    
    □ Run all tests:
      pytest tests/ -v
      Expected: ~3-4 minutes, all pass

11. OPTIMIZE CI WORKFLOW (30 min)
    □ Update CI/CD config (.github/workflows/test.yml):
    
    jobs:
      unit-tests:
        runs-on: ubuntu-latest
        steps:
          - run: pytest tests/unit/ -v  # Fast feedback
      
      integration-tests:
        runs-on: ubuntu-latest
        if: github.event_name == 'pull_request'  # Only on PR
        steps:
          - run: pytest tests/integration/ -v
      
      all-tests:
        runs-on: ubuntu-latest
        if: github.ref == 'main'  # Only on main push
        steps:
          - run: pytest tests/ -v  # Full suite

EXPECTED OUTCOME:
✅ tests/unit/ contains only fast unit tests (<100ms each)
✅ tests/integration/ contains integration tests
✅ conftest files properly structured
✅ All imports fixed and tests discoverable
✅ Unit test run time: 5-10 seconds
✅ Integration test run time: 2-3 minutes
✅ CI optimized for fast feedback (unit tests first)
✅ All 400+ tests pass
```

### Acceptance Criteria

- [ ] New directory structure created: `tests/unit/`, `tests/integration/`
- [ ] All unit tests moved to `tests/unit/` and pass in <15 seconds
- [ ] All integration tests moved to `tests/integration/` 
- [ ] `tests/conftest.py` has shared fixtures
- [ ] `tests/unit/conftest_unit.py` has unit-specific fixtures
- [ ] `tests/integration/conftest_integration.py` has integration fixtures
- [ ] All imports fixed and tests discoverable
- [ ] Pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`) applied
- [ ] All tests pass: `pytest tests/`
- [ ] Fast feedback: `pytest tests/unit/` runs in <15 seconds
- [ ] CI config optimized to run unit tests first

---

## 🚀 Execution Guide

### How to Run Sessions Automatically

#### Option 1: Run All Sessions (Full Cleanup)
```bash
# Full automated execution (requires agent)
python scripts/run_cleanup_sessions.py --all --config AUTOMATED_EXECUTION_PROMPTS.md
```

#### Option 2: Run Individual Sessions
```bash
# Session 1 only
python scripts/run_cleanup_sessions.py --session 1

# Sessions 1-3 (independent tasks)
python scripts/run_cleanup_sessions.py --sessions 1,2,3

# After Session 3, run Session 4
python scripts/run_cleanup_sessions.py --session 4
```

#### Option 3: Manual Execution via Subagent
1. Copy prompt for target session (e.g., Session 1)
2. Paste into GitHub Copilot chat
3. Add: `Execute this task using automated tools`
4. Let subagent execute steps

### Monitoring Progress

After each session:
```bash
# Verify tests still pass
pytest tests/ -q

# Count remaining duplicates
grep -r "sys\.modules\[" tests/ --include="*.py" | wc -l

# Count total mocks in test files
grep -r "MagicMock()" tests/ --include="*.py" | wc -l

# Measure test execution time
time pytest tests/ -q
```

### Rollback Plan

If any session causes issues:
```bash
# Restore from git
git checkout HEAD -- tests/

# Restart that specific session
# All changes are isolated and can be reverted easily
```

---

## 📊 Success Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Platform mock duplication | 5+ files | 1 file | ✅ |
| Total mocks in tests | 500+ | 250-300 | ✅ |
| Mock setup lines per test | 20-30 | 1-2 | ✅ |
| Callback parameters | 15 | 1 handler | ✅ |
| Unit test execution time | 50s | <15s | ✅ |
| Test file organization | Confused | Clear | ✅ |
| Nested patch depth | 5 levels | 1-2 levels | ✅ |

---

## 📝 Notes

- Each session is designed to be **independent** where possible
- Sessions 1-3 can run in parallel; Sessions 4-5 are sequential
- Total effort: ~3-4 developer-weeks
- Risk level: Low-Medium (refactoring only, well-tested)
- Rollback capability: Each commit is reversible via git

