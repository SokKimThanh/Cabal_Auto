# Feature: Monster Editor Refactor

**Branch:** `feature/monster-editor-refactor`  
**Type:** Feature Enhancement  
**Priority:** High  
**Status:** In Progress

## 🎯 Objective

Create a standalone Monster Editor module that is **independent** from Library Manager. This module will handle CRUD operations for monsters, template capture, and recognition testing with a clean architecture.

## 📋 Tasks Breakdown

### Task 1: Core Monster Manager (lib/features/monster_manager.py)
**Goal:** Create the core CRUD engine for monster data management.

**Deliverables:**
- `MonsterManager` class with CRUD methods
- JSON file I/O for monster data
- Validation and error handling
- Thread-safe operations

**API:**
```python
class MonsterManager:
    def list_monsters(self) -> List[Dict[str, Any]]
    def get_monster(self, monster_id: str) -> Optional[Dict[str, Any]]
    def create_monster(self, monster_data: Dict[str, Any]) -> str  # Returns monster_id
    def update_monster(self, monster_id: str, data: Dict[str, Any]) -> bool
    def delete_monster(self, monster_id: str) -> bool
    def add_template(self, monster_id: str, template_path: str, threshold: float) -> bool
    def test_template(self, monster_id: str, template_id: str) -> Dict[str, Any]
```

**Events Emitted:**
- `monster_created(monster_id, data)`
- `monster_updated(monster_id, changes)`
- `monster_deleted(monster_id)`
- `template_added(monster_id, template_id)`
- `template_tested(monster_id, template_id, result)`

---

### Task 2: Background Worker System (lib/features/worker.py)
**Goal:** Handle heavy operations (capture, match, I/O) in background threads.

**Deliverables:**
- `WorkerThread` class with queue-based task system
- Signal/callback mechanism for UI updates
- Task cancellation and timeout support
- Progress reporting

**API:**
```python
class WorkerThread:
    def start_worker(self) -> None
    def enqueue(self, task_type: str, params: Dict, callback: Callable) -> str  # Returns task_id
    def cancel_task(self, task_id: str) -> bool
    def get_task_status(self, task_id: str) -> Dict[str, Any]
```

**Events Emitted:**
- `task_started(task_id, task_type)`
- `task_progress(task_id, progress)`
- `task_done(task_id, result)`
- `task_cancelled(task_id)`
- `task_error(task_id, error)`

---

### Task 3: Template Capture Helper (lib/features/capture_helper.py)
**Goal:** Capture screen regions for template creation.

**Deliverables:**
- Region selection UI (crosshair overlay)
- Screenshot capture with ROI
- Image preprocessing (resize, crop, save)
- Preview functionality

**API:**
```python
class CaptureHelper:
    def select_region(self, callback: Callable) -> None
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray
    def save_template(self, image: np.ndarray, path: str) -> bool
    def preview_template(self, image: np.ndarray) -> None
```

---

### Task 4: Input Adapter (lib/system/input_adapter.py)
**Goal:** Queue-based input system for thread-safe key sending.

**Deliverables:**
- Task queue for input operations
- Thread-safe enqueue/execute
- Logging and error handling

**API:**
```python
class InputAdapter:
    def enqueue_send_key(self, key: str, delay: float = 0) -> str  # Returns task_id
    def enqueue_mouse_click(self, x: int, y: int) -> str
    def get_task_status(self, task_id: str) -> str
```

---

### Task 5: Hotkey Manager Integration (lib/hotkey/hotkey_manager.py)
**Goal:** Centralized hotkey registration with capability reporting.

**Deliverables:**
- Register monster editor hotkeys (Ctrl+Shift+M)
- Capability report for debugging
- Conflict detection

**API:**
```python
class HotkeyManager:
    def register_hotkey(self, key_combo: str, callback: Callable, description: str) -> bool
    def unregister_hotkey(self, key_combo: str) -> bool
    def capability_report(self) -> Dict[str, Any]
    def list_registered_hotkeys(self) -> List[Dict[str, str]]
```

**Events Emitted:**
- `hotkey_registered(key_combo, description)`
- `hotkey_triggered(key_combo)`
- `hotkey_conflict(key_combo, existing)`

---

### Task 6: Structured Hunt Logger (lib/system/hunt_logger.py)
**Goal:** Structured logging with JSON schema for hunt operations.

**Deliverables:**
- `HuntLogger` class with schema validation
- Log rotation and cleanup
- Session ID tracking
- No logs committed to repo

**API:**
```python
class HuntLogger:
    def get_hunt_logger(session_id: Optional[str] = None) -> HuntLogger
    def set_log_dir(self, log_dir: str) -> None
    def log(self, event: str, level: str, payload: Dict) -> None
    def log_task_start(self, task_id: str, task_type: str) -> None
    def log_task_done(self, task_id: str, result: Any) -> None
    def log_task_cancel(self, task_id: str, reason: str) -> None
```

**Schema:**
```json
{
  "timestamp": "2025-10-24T10:30:00.123Z",
  "session_id": "uuid-v4",
  "event": "monster_created",
  "level": "info",
  "source": "monster_manager",
  "payload": {}
}
```

---

### Task 7: UI Components

#### 7.1 Quick Monster Editor (ui/quick_monster_editor.py)
**Goal:** Modal dialog for quick monster edit (hotkey Ctrl+Shift+M).

**Features:**
- Lightweight modal window (topmost)
- Basic fields: name, level, threshold
- Quick capture button
- Save/Cancel buttons

#### 7.2 Full Monster Editor (ui/monster_editor.py)
**Goal:** Comprehensive monster management UI.

**Features:**
- Monster list/grid view
- Full CRUD forms
- Template list with add/remove/test
- Capture panel with region selection
- Progress indicators (spinners)

#### 7.3 Template Capture Panel (ui/capture_panel.py)
**Goal:** Template capture and test interface.

**Features:**
- Region selection button
- Preview area
- Test recognition button
- Result display (matches, confidence)

---

### Task 8: Testing Suite

#### 8.1 Unit Tests
**Files:**
- `tests/unit/test_monster_manager.py` - CRUD operations
- `tests/unit/test_worker.py` - Task queue and cancellation
- `tests/unit/test_capture_helper.py` - Image capture/save
- `tests/unit/test_input_adapter.py` - Input queueing
- `tests/unit/test_hotkey_manager.py` - Hotkey registration
- `tests/unit/test_hunt_logger.py` - Logging schema

#### 8.2 Integration Tests
**Files:**
- `tests/integration/test_monster_editor_flow.py` - Full workflow
- `tests/integration/test_capture_to_test_flow.py` - Capture → Add → Test

**Mock Requirements:**
- No actual screen capture
- No actual file I/O (use tmp_path)
- No logs written to repo (monkeypatch LOG_DIR)

---

## ✅ Acceptance Criteria

### Functional Requirements
- ✅ Monster CRUD operations work correctly
- ✅ Template capture with region selection
- ✅ Template recognition testing
- ✅ Quick editor opens with Ctrl+Shift+M
- ✅ All heavy operations run in background
- ✅ UI remains responsive during operations
- ✅ Cancel operations work correctly

### Technical Requirements
- ✅ All labels use `lib.i18n` (EN/VI translations)
- ✅ All tooltips use `lib.ui.tooltip`
- ✅ No widget updates from worker threads
- ✅ Hotkeys registered via `hotkey_manager.py`
- ✅ Logging uses `hunt_logger` with schema
- ✅ No log files committed to repo
- ✅ `.gitignore` includes `logs/`, `*.log`, `*.jsonl`

### Code Quality
- ✅ Type hints on all functions
- ✅ Docstrings with Args/Returns
- ✅ None checks before widget access
- ✅ Error handling with try-except
- ✅ Unit test coverage > 80%
- ✅ Integration tests pass

### Documentation
- ✅ API documentation in docstrings
- ✅ Event schema documented
- ✅ Log schema documented
- ✅ README with usage examples

---

## 📁 File Structure

```
lib/
├── features/
│   ├── monster_manager.py      # Core CRUD engine
│   ├── worker.py                # Background worker system
│   └── capture_helper.py        # Template capture
├── system/
│   ├── input_adapter.py         # Queue-based input
│   └── hunt_logger.py           # Structured logging
└── hotkey/
    └── hotkey_manager.py        # Hotkey registration

ui/
├── monster_editor.py            # Full editor UI
├── quick_monster_editor.py      # Quick modal editor
└── capture_panel.py             # Capture UI component

tests/
├── unit/
│   ├── test_monster_manager.py
│   ├── test_worker.py
│   ├── test_capture_helper.py
│   ├── test_input_adapter.py
│   ├── test_hotkey_manager.py
│   └── test_hunt_logger.py
└── integration/
    ├── test_monster_editor_flow.py
    └── test_capture_to_test_flow.py

docs/
└── branches/
    └── feature-monster-editor-refactor.md  # This file
```

---

## 🔗 Dependencies

**Internal:**
- `lib.i18n` - Internationalization
- `lib.ui.tooltip` - Tooltip system
- `lib.ui_style` - UI styling
- `lib.vision.vision_engine` - Template matching

**External:**
- `tkinter` - GUI framework
- `opencv-python` - Image processing
- `numpy` - Array operations
- `keyboard` - Hotkey handling
- `pytest` - Testing framework

---

## 🚀 Implementation Plan

### Phase 1: Core Infrastructure (Days 1-2)
1. Create `monster_manager.py` skeleton
2. Create `worker.py` skeleton
3. Create `hunt_logger.py` skeleton
4. Set up `.gitignore` for logs

### Phase 2: Capture & Input (Days 3-4)
5. Implement `capture_helper.py`
6. Implement `input_adapter.py`
7. Implement `hotkey_manager.py`

### Phase 3: UI Components (Days 5-6)
8. Implement `quick_monster_editor.py`
9. Implement `monster_editor.py`
10. Implement `capture_panel.py`
11. Add i18n translations

### Phase 4: Testing (Days 7-8)
12. Write unit tests
13. Write integration tests
14. Fix bugs and edge cases

### Phase 5: Documentation & PR (Day 9)
15. Write API documentation
16. Update README
17. Create PR with label `ready-for-review`, `area/ui`, `area/lib`

---

## 📝 Commit Message Format

```
<type>: <short-description> (skeleton|implementation|test)

Examples:
feat: monster manager CRUD operations (skeleton)
feat: background worker with queue system (implementation)
test: unit tests for monster manager (test)
docs: add API documentation for worker system
refactor: extract capture logic to helper class
fix: prevent widget updates from worker thread
```

---

## 🔍 Review Checklist

Before marking as ready-for-review:
- [ ] All skeleton files created
- [ ] Type hints on all functions
- [ ] Docstrings complete
- [ ] i18n keys defined (EN/VI)
- [ ] No widget updates from threads
- [ ] Logging uses hunt_logger
- [ ] No logs in repo
- [ ] Tests written and passing
- [ ] PR description complete

---

**Created:** October 24, 2025  
**Author:** SokKimThanh  
**Status:** Skeleton Phase
