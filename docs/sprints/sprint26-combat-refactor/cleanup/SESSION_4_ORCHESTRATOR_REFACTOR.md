# 🎯 Session 4: Refactor HuntOrchestrator (MAJOR)

## 📋 Overview

| Aspect | Value |
|--------|-------|
| **Objective** | Reduce HuntOrchestrator callbacks from 15 to 1 via callback handler object |
| **Duration** | 3-5 days (distributed effort) |
| **Effort** | 🔴 High |
| **Impact** | 🔴 Critical (30% mock reduction = 200-300 mocks saved) |
| **Difficulty** | High (refactoring touches 15+ files) |
| **Risk Level** | 🟡 Medium (requires integration testing) |
| **Prerequisites** | Sessions 1-2 should be complete |
| **Files to Modify** | 15+ files (orchestrator, app, tests) |

---

## 🎯 Objective

**Current Problem**:
```python
class HuntOrchestrator:
    def __init__(
        self,
        on_status_update: Callable[[str], None],           # Callback 1
        on_state_change: Callable[[str], None],            # Callback 2
        locate_target: Callable[[Dict], tuple],            # Callback 3
        prepare_skill_runtime: Callable[[Dict], list],     # Callback 4
        try_cast_skills: Callable,                         # Callback 5
        bring_window_to_front: Callable[[str], bool],      # Callback 6
        bring_window_to_front_by_hwnd: Callable[[int]],    # Callback 7
        bring_window_to_front_by_pid: Callable[[int]],     # Callback 8
        iconify_app: Callable[[], None],                   # Callback 9
        update_skill_stats_display: Callable[[dict]],      # Callback 10
        get_hunt_selected: Callable[[], Dict],             # Callback 11
        schedule_ui_task: Callable[[Callable]],            # Callback 12
        clear_target_ui: Callable[[], None] = None,        # Callback 13
        set_target_info: Callable[[str], None] = None,     # Callback 14
        on_scene_monsters_detected: Callable[[tuple]] = None  # Callback 15
    ):
    # This is callback hell! 😱
```

**After Session 4**:
```python
class HuntStatusHandler:
    """Single handler object for all hunt-related callbacks."""
    def on_status_update(self, msg: str) -> None: pass
    def on_state_change(self, state: str) -> None: pass
    def locate_target(self, params: Dict) -> tuple: pass
    # ... all 15 callbacks grouped logically

class HuntOrchestrator:
    def __init__(
        self,
        handler: HuntStatusHandler,        # Just 1 object! ✅
        bot_manager: BotManager,           # Services, not callbacks
        vision_engine: VisionEngine,
        skill_runtime: SkillRuntimeService
    ):
    # Clean, maintainable, testable! 🎯
```

---

## 🔍 Problem Analysis

### The Callback Hell Anti-Pattern

**What's Wrong**:
1. **Too Many Parameters**: 15 callbacks is excessive
2. **Mixed Concerns**: UI callbacks, game logic, window management all mixed
3. **Testing Nightmare**: Each test must mock all 15 callbacks
4. **Single Responsibility Violation**: Orchestrator depends on too many things
5. **Hard to Extend**: Adding new callback? All tests break!

**Evidence from Current Code**:
- `test_hunt_orchestrator.py`: 73 mocks (30 just for init)
- `test_orchestrator_ocr_fallback.py`: 43 mocks (20 for init)
- `test_orchestrator_loop.py`: 42 mocks (18 for init)
- **Just initializing this class requires 60+ mocks total!**

### Root Cause

The callbacks are grouped by **where they come from** (UI layer) instead of **what they do** (state transitions, resource management, etc.).

**Current grouping** (BAD):
```
┌─ on_status_update
├─ on_state_change
├─ locate_target
├─ prepare_skill_runtime
├─ bring_window_to_front  
├─ bring_window_to_front_by_hwnd  ← Window management
├─ bring_window_to_front_by_pid
├─ iconify_app
├─ update_skill_stats_display  ← UI updates
├─ schedule_ui_task  ← UI scheduling
└─ ... 5 more ...
```

All mixed together!

**Better grouping** (GOOD):
```
HuntStatusHandler
├─ UI Updates
│  ├─ on_status_update()      ← What status to show
│  ├─ on_state_change()       ← When state changes
│  ├─ update_skill_stats_display()
│  ├─ set_target_info()
│  └─ clear_target_ui()
├─ Window Management
│  ├─ bring_window_to_front()
│  ├─ bring_window_to_front_by_hwnd()
│  ├─ bring_window_to_front_by_pid()
│  └─ iconify_app()
├─ Game Logic
│  ├─ locate_target()
│  ├─ prepare_skill_runtime()
│  ├─ try_cast_skills()
│  └─ on_scene_monsters_detected()
└─ Utilities
   ├─ get_hunt_selected()
   ├─ schedule_ui_task()
```

---

## 💡 Solution Design

### Architecture

#### Design 1: Handler Object Pattern (Recommended)

```python
class HuntStatusHandler(ABC):
    """Abstract base for orchestrator status callbacks."""
    
    @abstractmethod
    def on_status_update(self, message: str) -> None:
        """Status message to display in UI."""
        pass
    
    @abstractmethod
    def on_state_change(self, state: str) -> None:
        """Hunt state changed (running, idle, error, etc)."""
        pass
    
    @abstractmethod
    def locate_target(self, params: Dict[str, Any]) -> Optional[tuple]:
        """Find target on screen using vision."""
        pass
    
    # ... other methods grouped by concern
```

**Implementation in app_gui.py**:
```python
class AppHuntHandler(HuntStatusHandler):
    """Implementation of HuntStatusHandler in the App class."""
    
    def __init__(self, app: 'App'):
        self.app = app
    
    def on_status_update(self, message: str) -> None:
        self.app.hunt_status_label.config(text=message)
    
    def on_state_change(self, state: str) -> None:
        if state == "running":
            self.app.start_stop_button.config(text="Stop Hunt")
        elif state == "idle":
            self.app.start_stop_button.config(text="Start Hunt")
    
    def locate_target(self, params: Dict[str, Any]) -> Optional[tuple]:
        # Delegate to vision engine
        return self.app.vision_engine.locate_template(params)
```

**Usage in HuntOrchestrator**:
```python
class HuntOrchestrator:
    def __init__(
        self,
        handler: HuntStatusHandler,  # Single object!
        bot_manager: BotManager,
        vision_engine: VisionEngine,
        skill_runtime: SkillRuntimeService,
        hunt_logger: HuntLogger = None
    ):
        self.handler = handler
        self.bot_manager = bot_manager
        self.vision_engine = vision_engine
        self.skill_runtime = skill_runtime
        self.hunt_logger = hunt_logger or get_hunt_logger()
        self.hunt_running = False
    
    def start_hunt(self, config: Dict[str, Any]) -> None:
        self.hunt_running = True
        self.handler.on_state_change("running")
        # Start hunt loop
```

#### Design 2: Callback Interface (Alternative)

If you prefer not to create an abstract base:

```python
@dataclass
class HuntCallbacks:
    """Container for hunt-related callbacks."""
    on_status_update: Callable[[str], None]
    on_state_change: Callable[[str], None]
    locate_target: Callable[[Dict], tuple]
    prepare_skill_runtime: Callable[[Dict], list]
    # ... etc
```

**Pros**: Simpler, no inheritance
**Cons**: No type checking for missing methods

---

## 📁 Files to Modify

### Phase 1: Create Handler Base Class
- ✅ Create `lib/features/hunt/hunt_status_handler.py` (new file)

### Phase 2: Refactor Orchestrator
- ✅ `lib/features/hunt/hunt_orchestrator.py` - Update __init__, all methods

### Phase 3: Implement Handler in App
- ✅ `app_gui.py` - Implement AppHuntHandler

### Phase 4: Update All Tests
- ✅ `tests/test_hunt_orchestrator.py` - Update fixtures
- ✅ `tests/unit/features/hunt/test_orchestrator_ocr_fallback.py` - Update
- ✅ `tests/integration/test_orchestrator_loop.py` - Update
- ✅ `tests/unit/features/hunt/*.py` - 5+ test files
- ✅ `tests/unit/test_action_bar.py` - Update UI tests

### Phase 5: Integration Testing
- ✅ `tests/integration/` - Verify hunt flow works
- ✅ Manual testing on Windows

---

## 🔧 Step-by-Step Implementation

### **Day 1: Create Handler Base Class**

#### Step 1: Define HuntStatusHandler Interface

Create `lib/features/hunt/hunt_status_handler.py`:

```python
"""
Hunt Status Handler - Interface for orchestrator callbacks.

This module defines the callback interface that HuntOrchestrator uses
to communicate with the UI layer and other components.

Instead of passing 15 individual callbacks, the orchestrator now
receives a single handler object that implements all callbacks.
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Optional, Tuple


class HuntStatusHandler(ABC):
    """
    Abstract interface for hunt-related status callbacks.
    
    The orchestrator uses this handler to communicate with the UI layer,
    without being tightly coupled to UI implementation details.
    
    Methods are grouped by concern:
    - State changes: on_state_change, on_status_update
    - UI updates: update_skill_stats_display, set_target_info, clear_target_ui
    - Window management: bring_window_to_front, iconify_app
    - Game logic: locate_target, prepare_skill_runtime, try_cast_skills
    - Scene detection: on_scene_monsters_detected
    - Configuration: get_hunt_selected, schedule_ui_task
    """
    
    # ========== STATE CHANGES ==========
    
    @abstractmethod
    def on_state_change(self, state: str) -> None:
        """
        Notify handler that hunt state has changed.
        
        Args:
            state: New state ("running", "idle", "error", "paused", etc)
        """
        pass
    
    @abstractmethod
    def on_status_update(self, message: str) -> None:
        """
        Notify handler of status message to display.
        
        Args:
            message: Status message for UI
        """
        pass
    
    # ========== UI UPDATES ==========
    
    @abstractmethod
    def update_skill_stats_display(self, stats: Dict[str, Any]) -> None:
        """Update UI with skill statistics."""
        pass
    
    @abstractmethod
    def set_target_info(self, info: str) -> None:
        """Set target information in UI."""
        pass
    
    @abstractmethod
    def clear_target_ui(self) -> None:
        """Clear target-related UI elements."""
        pass
    
    # ========== WINDOW MANAGEMENT ==========
    
    @abstractmethod
    def bring_window_to_front(self, window_name: str) -> bool:
        """Bring game window to front."""
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
        """Minimize bot application."""
        pass
    
    # ========== GAME LOGIC ==========
    
    @abstractmethod
    def locate_target(self, params: Dict[str, Any]) -> Optional[Tuple]:
        """
        Locate target on screen using vision.
        
        Returns:
            (box, match_info) tuple or None if not found
        """
        pass
    
    @abstractmethod
    def prepare_skill_runtime(self, config: Dict[str, Any]) -> list:
        """Prepare skill execution runtime."""
        pass
    
    @abstractmethod
    def try_cast_skills(self) -> None:
        """Execute skill casting logic."""
        pass
    
    @abstractmethod
    def on_scene_monsters_detected(self, monsters: Tuple) -> None:
        """Notify handler that monsters were detected in scene."""
        pass
    
    # ========== UTILITIES ==========
    
    @abstractmethod
    def get_hunt_selected(self) -> Dict[str, Any]:
        """Get currently selected hunt config."""
        pass
    
    @abstractmethod
    def schedule_ui_task(self, task: Callable) -> None:
        """Schedule a task to run on UI thread."""
        pass
```

#### Step 2: Update HuntOrchestrator Constructor

Modify `lib/features/hunt/hunt_orchestrator.py`:

```python
from lib.features.hunt.hunt_status_handler import HuntStatusHandler

class HuntOrchestrator:
    """
    Main hunt automation orchestrator.
    
    Refactored to receive a single HuntStatusHandler instead of
    15 individual callbacks. This improves:
    - Testability: Mock 1 object instead of 15 callbacks
    - Maintainability: Clear interface
    - Extensibility: Add callbacks without changing constructor
    """
    
    def __init__(
        self,
        handler: HuntStatusHandler,  # CHANGE: Was 15 separate Callables!
        bot_manager: BotManager,
        vision_engine: VisionEngine,
        skill_runtime: SkillRuntimeService,
        hunt_logger: HuntLogger = None
    ):
        """
        Initialize HuntOrchestrator.
        
        Args:
            handler: HuntStatusHandler implementation for callbacks
            bot_manager: Bot manager for screen capture and input
            vision_engine: Vision engine for target detection
            skill_runtime: Skill execution runtime
            hunt_logger: Logger for hunt events (optional)
        """
        self.handler = handler
        self.bot_manager = bot_manager
        self.vision_engine = vision_engine
        self.skill_runtime = skill_runtime
        self.hunt_logger = hunt_logger or get_hunt_logger()
        self.hunt_running = False
    
    # ========== PUBLIC API ==========
    
    def start_hunt(self, config: Dict[str, Any]) -> None:
        """Start the hunt loop."""
        if self.hunt_running:
            return  # Already running
        
        self.hunt_running = True
        self.handler.on_state_change("running")
        self.handler.on_status_update("Hunt started...")
        
        # Start hunt loop in thread (existing implementation)
        thread = threading.Thread(target=self._hunt_loop, args=(config,))
        thread.daemon = True
        thread.start()
    
    def stop_hunt(self) -> None:
        """Stop the hunt loop."""
        self.hunt_running = False
        self.handler.on_state_change("idle")
        self.handler.on_status_update("Hunt stopped")
    
    # ========== PRIVATE METHODS (unchanged) ==========
    
    def _hunt_loop(self, config: Dict[str, Any]) -> None:
        """Main hunt loop (implementation details unchanged)."""
        # Use self.handler instead of individual callbacks
        # Example:
        # self.handler.on_status_update("Searching for target...")
        # target = self.handler.locate_target(config)
        # if target:
        #     self.handler.on_state_change("attacking")
        # etc.
        pass
```

### **Day 2-3: Implement Handler in app_gui.py**

#### Step 3: Create AppHuntHandler

Add to `app_gui.py`:

```python
from lib.features.hunt.hunt_status_handler import HuntStatusHandler

class AppHuntHandler(HuntStatusHandler):
    """
    HuntStatusHandler implementation in the App.
    
    Bridges between HuntOrchestrator and the Tkinter UI.
    All callback methods update the UI when called.
    """
    
    def __init__(self, app: 'App'):
        self.app = app
    
    def on_state_change(self, state: str) -> None:
        """Update UI based on hunt state."""
        if state == "running":
            self.app.hunt_status_var.set("🎮 Running")
            self.app.start_stop_button.config(text="Stop Hunt", state="normal")
        elif state == "idle":
            self.app.hunt_status_var.set("⏹️ Idle")
            self.app.start_stop_button.config(text="Start Hunt", state="normal")
        elif state == "paused":
            self.app.hunt_status_var.set("⏸️ Paused")
            self.app.start_stop_button.config(text="Resume", state="normal")
        elif state == "error":
            self.app.hunt_status_var.set("❌ Error")
            self.app.start_stop_button.config(state="disabled")
    
    def on_status_update(self, message: str) -> None:
        """Update status message in UI."""
        self.app.hunt_log.insert("end", f"{message}\n")
        self.app.hunt_log.see("end")  # Auto-scroll to bottom
    
    def update_skill_stats_display(self, stats: Dict[str, Any]) -> None:
        """Update skill statistics in UI."""
        # Update skill cooldowns, stats, etc.
        if 'skill_name' in stats:
            self.app.skill_list.delete(0, "end")
            for skill in stats.get('skills', []):
                self.app.skill_list.insert("end", f"{skill['name']}: {skill['cd']}s")
    
    def set_target_info(self, info: str) -> None:
        """Display target information."""
        self.app.target_label.config(text=f"Target: {info}")
    
    def clear_target_ui(self) -> None:
        """Clear target-related UI."""
        self.app.target_label.config(text="Target: None")
    
    def bring_window_to_front(self, window_name: str) -> bool:
        """Bring game window to front."""
        from lib.system.window_manager import WindowManager
        wm = WindowManager()
        return wm.bring_to_front(window_name)
    
    def bring_window_to_front_by_hwnd(self, hwnd: int) -> bool:
        """Bring window to front by handle."""
        from lib.system.window_manager import WindowManager
        wm = WindowManager()
        return wm.bring_to_front_by_hwnd(hwnd)
    
    def bring_window_to_front_by_pid(self, pid: int) -> bool:
        """Bring window to front by process ID."""
        from lib.system.window_manager import WindowManager
        wm = WindowManager()
        return wm.bring_to_front_by_pid(pid)
    
    def iconify_app(self) -> None:
        """Minimize the bot app."""
        self.app.iconify()
    
    def locate_target(self, params: Dict[str, Any]) -> Optional[Tuple]:
        """Locate target using vision engine."""
        return self.app.vision_engine.locate_template(params)
    
    def prepare_skill_runtime(self, config: Dict[str, Any]) -> list:
        """Prepare skill runtime."""
        return self.app.skill_runtime_service.prepare(config)
    
    def try_cast_skills(self) -> None:
        """Execute skill casting."""
        self.app.skill_runtime_service.execute_skills()
    
    def on_scene_monsters_detected(self, monsters: Tuple) -> None:
        """Handle scene monster detection."""
        self.app.monster_list.delete(0, "end")
        for monster in monsters:
            self.app.monster_list.insert("end", monster.get('name', 'Unknown'))
    
    def get_hunt_selected(self) -> Dict[str, Any]:
        """Get selected hunt from UI."""
        return {
            'hwnd': self.app.selected_hwnd,
            'config': self.app.hunt_cfg
        }
    
    def schedule_ui_task(self, task: Callable) -> None:
        """Schedule task on UI thread."""
        self.app.after(0, task)
```

#### Step 4: Update App Initialization

In `app_gui.py`, update the App.__init__ to create and use handler:

```python
class App(tk.Tk):
    def __init__(self):
        # ... existing init code ...
        
        # Create handler (was: individual callbacks)
        self.hunt_handler = AppHuntHandler(self)
        
        # Create orchestrator with handler (was: 15 callback params)
        self.hunt_orchestrator = HuntOrchestrator(
            handler=self.hunt_handler,  # NEW: Single handler!
            bot_manager=self.bot_manager,
            vision_engine=self.vision_engine,
            skill_runtime=self.skill_runtime_service,
            hunt_logger=get_hunt_logger()
        )
```

### **Day 3-4: Update All Test Fixtures**

#### Step 5: Update mock_orchestrator Fixture

In `tests/conftest.py`, update the fixture:

```python
@pytest.fixture
def mock_orchestrator(monkeypatch):
    """
    Fully mocked HuntOrchestrator with handler-based callbacks.
    
    CHANGED: Now uses HuntStatusHandler instead of 15 individual callbacks.
    This reduces mock instances from 15+ to 1.
    """
    from lib.features.hunt.hunt_orchestrator import HuntOrchestrator
    from lib.features.hunt.hunt_status_handler import HuntStatusHandler
    
    # Create mock handler (just 1 mock instead of 15!)
    mock_handler = MagicMock(spec=HuntStatusHandler)
    mock_handler.on_status_update = MagicMock()
    mock_handler.on_state_change = MagicMock()
    mock_handler.locate_target = MagicMock(return_value=None)
    mock_handler.get_hunt_selected = MagicMock(return_value={"hwnd": 123})
    
    # Create mock services
    mock_bot_manager = MagicMock()
    mock_bot_manager.screen_capture = MagicMock()
    mock_bot_manager.screen_capture.hwnd = 123
    mock_bot_manager.screen_capture.get_latest_frame = MagicMock(return_value="mock_frame")
    
    mock_vision_engine = MagicMock()
    mock_skill_runtime = MagicMock()
    
    # Create orchestrator with handler
    orch = HuntOrchestrator(
        handler=mock_handler,  # NEW: Single handler!
        bot_manager=mock_bot_manager,
        vision_engine=mock_vision_engine,
        skill_runtime=mock_skill_runtime
    )
    
    return orch
```

#### Step 6: Update Test Functions

**Before** (15 callback mocks):
```python
def test_orchestrator_init():
    orchestrator = HuntOrchestrator(
        on_status_update=MagicMock(),
        on_state_change=MagicMock(),
        locate_target=MagicMock(),
        prepare_skill_runtime=MagicMock(),
        # ... 11 more callbacks ...
    )
    assert orchestrator.hunt_running is False
```

**After** (1 handler mock):
```python
def test_orchestrator_init(mock_orchestrator):
    assert mock_orchestrator.hunt_running is False
```

#### Step 7: Update 15+ Test Files

Apply similar pattern to:
- `tests/test_hunt_orchestrator.py` - 20 test functions
- `tests/unit/features/hunt/test_orchestrator_ocr_fallback.py` - 5 tests
- `tests/integration/test_orchestrator_loop.py` - 3 tests
- `tests/unit/test_action_bar.py` - 3 tests
- `tests/unit/features/hunt/test_target_name_reader_ocr.py` - 4 tests
- `tests/unit/features/hunt/test_orchestrator_publish_callback.py` - 2 tests
- Similar updates to 8+ more test files

### **Day 4-5: Integration Testing & Verification**

#### Step 8: Manual Integration Testing

Test on actual Windows machine:
```bash
# Run the app
python app_gui.py

# Test hunt flow:
1. Select a hunt area
2. Click "Start Hunt"
3. Verify orchestrator receives status callbacks via handler
4. Verify UI updates correctly
5. Click "Stop Hunt"
6. Verify orchestrator.hunt_running = False
```

#### Step 9: Full Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run orchestrator tests specifically
pytest tests/test_hunt_orchestrator.py -v
pytest tests/unit/features/hunt/ -v
pytest tests/integration/ -v

# Check mock count reduction
python analyze_mocks.py
```

#### Step 10: Code Review Checklist

Before committing:
- [ ] HuntStatusHandler interface is clear and complete
- [ ] AppHuntHandler implements all methods
- [ ] HuntOrchestrator receives handler instead of callbacks
- [ ] All test files updated to use handler
- [ ] All tests pass (green)
- [ ] Mock count reduced 200-300 instances
- [ ] No functionality changes (behavior identical)
- [ ] Documentation updated

---

## ✅ Testing Checklist

### Unit Tests
- [ ] `pytest tests/test_hunt_orchestrator.py -v` → All pass
- [ ] `pytest tests/unit/features/hunt/ -v` → All pass
- [ ] `pytest tests/integration/ -v` → All pass
- [ ] `pytest tests/unit/test_action_bar.py -v` → All pass

### Integration Tests
- [ ] Manual app launch: `python app_gui.py` → No errors
- [ ] Start/Stop hunt flow works
- [ ] UI updates on status changes
- [ ] Handler callbacks are invoked correctly

### Verification
- [ ] Mock count: 464 → ~200-250 (reduce by 200-300)
- [ ] No test regressions
- [ ] Orchestrator behavior unchanged
- [ ] App functionality preserved

---

## 📊 Expected Results

### Before Session 4
```
Total Mock/Patch Instances: 464 (after Session 3)
HuntOrchestrator callback mocks: ~300 (15 per test × 20 tests)
Test files with 40+ mocks: 4 files
```

### After Session 4
```
Total Mock/Patch Instances: ~200-250
HuntOrchestrator callback mocks: ~50 (1 handler mock × 20 tests)
Test files with 40+ mocks: 0 files
Callback mocks reduction: 250 instances saved!
```

### Impact by File
| File | Before | After | Reduction |
|------|--------|-------|-----------|
| test_hunt_orchestrator.py | 73 | 35 | -38 |
| test_orchestrator_ocr_fallback.py | 38 | 15 | -23 |
| test_orchestrator_loop.py | 42 | 18 | -24 |
| test_action_bar.py | 22 | 12 | -10 |
| test_target_name_reader_ocr.py | 10 | 5 | -5 |
| Other test files | ~50 | ~30 | -20 |
| conftest.py (fixture updates) | -15 old | +5 new | -10 |
| **TOTAL** | **464** | **250** | **-214** |

---

## 🎓 Key Learnings

1. **Handler Pattern**: Grouping related callbacks into objects
2. **Abstract Base Classes**: Using ABC for callback interfaces
3. **Dependency Injection**: How DI improves testability and decoupling
4. **Refactoring Large Objects**: Strategies for breaking up god objects
5. **Backward Compatibility**: Keeping behavior while changing structure

---

## ⚠️ Common Issues & Solutions

### Issue 1: Handler Method Not Implemented
**Problem**: `AttributeError: 'MagicMock' object has no attribute 'on_status_update'`
**Solution**: Ensure mock_handler is created with `spec=HuntStatusHandler`

### Issue 2: Handler Callbacks Not Called
**Problem**: Tests pass but handlers are never invoked in code
**Solution**: Verify orchestrator code uses `self.handler.method()` not old callback names

### Issue 3: UI Doesn't Update
**Problem**: After refactoring, UI doesn't respond to hunt events
**Solution**: Check AppHuntHandler methods are properly bound to UI elements

### Issue 4: Breaking Existing Code
**Problem**: Other code depends on old callback signatures
**Solution**: Search for all uses of HuntOrchestrator constructor and update them

---

## 📝 Commit Strategy

This is a large refactor. Consider breaking into 3-4 commits:

### Commit 1: Create Handler Interface
```bash
git add lib/features/hunt/hunt_status_handler.py

git commit -m "feat: add HuntStatusHandler interface

- Define abstract HuntStatusHandler class
- Group related callbacks by concern
- Prepare for orchestrator refactoring
- No behavior changes yet"
```

### Commit 2: Refactor Orchestrator
```bash
git add lib/features/hunt/hunt_orchestrator.py tests/conftest.py

git commit -m "refactor: update HuntOrchestrator to use handler object

- Change from 15 callbacks to single HuntStatusHandler
- Update orchestrator constructor signature
- Update all mock fixtures
- Reduces init mock count from 15 to 1

Tests passing: 40/40"
```

### Commit 3: Implement Handler in App
```bash
git add app_gui.py

git commit -m "refactor: implement AppHuntHandler in app_gui.py

- Implement HuntStatusHandler in App class
- Bridge between orchestrator and Tkinter UI
- Update App initialization to use handler
- Maintain UI behavior"
```

### Commit 4: Update All Tests
```bash
git add tests/test_hunt_orchestrator.py tests/unit/features/hunt/ tests/unit/test_action_bar.py

git commit -m "refactor: update tests for handler-based orchestrator

- Update test_hunt_orchestrator.py (20 tests)
- Update test_orchestrator_ocr_fallback.py (5 tests)
- Update test_orchestrator_loop.py (3 tests)
- Update test_action_bar.py (3 tests)
- Similar updates to 8+ test files
- Reduces mock instances by 200+ (30% total)

Tests passing: 150+/150+"
```

---

## 🎯 Session Complete Criteria

✅ **This session is complete when:**
1. HuntStatusHandler interface created and documented
2. HuntOrchestrator refactored to use handler (not 15 callbacks)
3. AppHuntHandler implemented in app_gui.py
4. All 15+ test files updated to use new signature
5. All tests pass (pytest 150+/150+)
6. Mock count reduced from 464 → 200-250
7. Manual testing on Windows confirms functionality
8. Code reviewed and approved
9. All commits pushed with proper messages
10. **No behavioral changes** - app works exactly the same

---

**Status**: 🟡 Ready (depends on Sessions 1-3)
**Estimated Time**: 3-5 days
**Impact**: 🔴 Critical (200+ mock reduction, architectural improvement)
**Next Session**: [SESSION_5_TEST_SEPARATION.md](SESSION_5_TEST_SEPARATION.md)

---

## 🚀 Quick Reference

### Key Files to Create/Modify
```
Create:
  - lib/features/hunt/hunt_status_handler.py        (new)

Modify:
  - lib/features/hunt/hunt_orchestrator.py          (major)
  - app_gui.py                                       (implement handler)
  - tests/conftest.py                               (update fixtures)
  - tests/test_hunt_orchestrator.py                 (update tests)
  - tests/unit/features/hunt/*.py                   (15+ test files)
```

### Before/After Comparison
```
BEFORE:
orchestrator = HuntOrchestrator(
    on_status_update=MagicMock(),
    on_state_change=MagicMock(),
    locate_target=MagicMock(),
    # ... 12 more ...
)

AFTER:
orchestrator = HuntOrchestrator(
    handler=mock_handler,  # 1 object!
    bot_manager=mock_bot_manager,
    vision_engine=mock_vision_engine,
    skill_runtime=mock_skill_runtime
)

Mock reduction: 15 → 1 (93% reduction per test!)
```

---

## 📚 Additional Resources

### Design Patterns
- [Handler Pattern](https://refactoring.guru/design-patterns/observer)
- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)
- [Single Responsibility Principle](https://en.wikipedia.org/wiki/Single-responsibility_principle)

### Python Resources
- [ABC - Abstract Base Classes](https://docs.python.org/3/library/abc.html)
- [Type Hints Guide](https://docs.python.org/3/library/typing.html)

---

**Generated**: 2026-09-03
**Session Level**: 🔴 CRITICAL (Major refactor, highest impact)
**Recommended for**: After Sessions 1-3 complete
