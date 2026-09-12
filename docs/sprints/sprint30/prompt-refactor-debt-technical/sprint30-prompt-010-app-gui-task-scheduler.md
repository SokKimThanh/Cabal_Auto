# Sprint 30: Refactor Debt Technical - App GUI
**File:** `sprint30-prompt-010-app-gui-task-scheduler.md`
**Previous Context:** `sprint30-prompt-009-app-gui-dialog-service.md`
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Extract Task Scheduler & Timer Manager
**Objective:** Resolve the severe "Timer/after dispersion" architectural flaw (Item 2) by replacing raw `self.after` and unmanaged `Thread` calls with a centralized `TaskScheduler` to prevent memory leaks and race conditions.

## 2. Context
Throughout `app_gui.py` and various views, there are calls like `self.after(100, update_loop)`. If the frame is destroyed or the app state changes, these timers keep firing, causing zombie loops, memory leaks, and Tkinter thread exceptions. All recurring UI tasks and background threads must be registered with a central manager that can cancel them safely on teardown.

## 3. Files to Modify
- `lib/system/task_scheduler.py` (Create)
- `ui/app_gui.py`
- Selected views with heavy polling (e.g., hunt views or scan controllers)

## 4. Detailed Implementation Guide

### Step 4.1: Implement TaskScheduler
Create a class `TaskScheduler` that accepts the root Tk instance.
It needs:
- `schedule_task(task_id, interval_ms, callback)`: Uses `root.after` but tracks the Tkinter timer ID in a dictionary.
- `cancel_task(task_id)`: Uses `root.after_cancel`.
- `cancel_all()`: Cancels everything on shutdown.
- Optional: `run_in_thread(task_id, target, daemon=True)`: Starts a thread and tracks it.

### Step 4.2: Replace `self.after` in App
Search `app_gui.py` for `.after(`.
Instead of calling `self.root.after(...)`, call `self.task_scheduler.schedule_task("main_update_loop", 100, self._update_loop)`.
Ensure that the loop function calls `schedule_task` again, or implement a `schedule_recurring_task` wrapper in the manager.

### Step 4.3: App Teardown
In the `App.on_closing` method (or equivalent window destroy protocol), call `self.task_scheduler.cancel_all()` to ensure clean exits before `root.destroy()` is invoked.

## 5. Pitfalls & Notes
- Recursive `after` loops (where a function calls `after` at the end of itself) need to be carefully migrated. The `TaskScheduler` should handle re-registration cleanly using the same `task_id`.
- Do not attempt to fix all `Thread` instances in the entire project in this 30-minute block; focus strictly on cleaning up the UI polling loops (`after`) in `app_gui.py`.

## 6. Acceptance Criteria
- [ ] A `TaskScheduler` or `TimerManager` class is implemented.
- [ ] `app_gui.py` uses the scheduler instead of calling `.after` directly.
- [ ] The app closes cleanly without "RuntimeError: main thread is not in main loop" or zombie timer exceptions.

## 7. Identified Risks & Current State Assessment (Auto-Updated)
**Current State Analysis:**
- `app_gui.py` uses raw `self.root.after(...)` calls for updating system status, hunt status, and timers.

**Identified Risks & Pitfalls:**
- **Double Registration:** The standard pattern for `after` loops is `def loop(): ... self.after(100, loop)`. When porting to `TaskScheduler`, ensure the scheduler doesn't append duplicate tracker IDs endlessly, leading to memory leaks within the tracker dictionary itself. A recurring task wrapper is safer.
- **Teardown Exceptions:** Canceling a task that has already fired or canceling during an active shutdown sequence can throw Tkinter TclErrors. The `TaskScheduler.cancel_all()` method must catch and safely swallow these specific errors to ensure clean application exit.
- **Thread Daemonization:** If `TaskScheduler` is extended to manage Threads as suggested, ensure all threads are explicitly marked as `daemon=True` so they do not block the application from closing if `cancel_all` fails.
