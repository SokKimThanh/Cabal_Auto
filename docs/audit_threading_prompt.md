# Audit Prompt: Python 3.14+ Tkinter Thread-Safety & EventBus Violations

## Objective
The primary goal of this audit is to locate, analyze, and resolve thread-safety issues caused by background threads interacting directly with Tkinter (GUI) components or the internal `EventBus`. Under the strict GIL enforcement in Python 3.14+, any unauthorized access to the Main Thread from a background thread immediately results in a fatal `PyEval_RestoreThread` crash.

## Scope
You must comprehensively review the following areas within the codebase:
- All explicit threading uses: `threading.Thread`, `concurrent.futures`, or `TaskScheduler.run_in_thread`.
- Subsystems operating on asynchronous loops: `VisionEngine`, `ScreenCapture`, `HuntOrchestrator`, `ScanController`, `IconManagerController`.
- Windows API callbacks running on separate threads (e.g., `WM_HOTKEY` via `win32gui` message loops in `HotkeyController`).

## The Audit Checklist

### 1. Identify Background Threads
- [ ] Scan for `threading.Thread(target=...` or `run_in_thread`.
- [ ] Identify the exact `target` function (the "worker").

### 2. Trace Background Execution Paths
For every worker function identified:
- [ ] Does it directly access any Tkinter variable (e.g., `StringVar.set()`, `BooleanVar.get()`)?
- [ ] Does it directly call Tkinter methods (e.g., `widget.config()`, `widget.update()`, `widget.winfo_exists()`, `widget.after()`)?
- [ ] **Crucially:** Does it trigger any `EventBus` events (e.g., `EventBus.trigger(MyEvent())`)?
  *Note: The `EventBus` in this architecture typically invokes listener callbacks synchronously. If a UI component is listening to an event, triggering that event from a background thread will forcefully execute the UI callback on the background thread, causing a crash.*

### 3. Remediation Strategy
If any violations are found, apply the following fixes:

- **For Tkinter direct access:** Wrap the problematic UI manipulation in `UIDispatcher.post()`.
  ```python
  # BAD: Background thread doing UI work directly
  self.status_label.config(text="Scanning...")

  # GOOD: Safely dispatched to the Main Thread
  from lib.events.ui_dispatcher import UIDispatcher
  UIDispatcher.post(lambda: self.status_label.config(text="Scanning..."))
  ```

- **For EventBus triggers:** If an event is heavily relied upon by the UI (like `HuntStatusUpdatedEvent` or `TargetHpUpdatedEvent`), wrap the trigger itself.
  ```python
  # BAD: Triggering UI events from background worker
  EventBus.trigger(HuntStateChangedEvent("running"))

  # GOOD: Dispatch the trigger to the main thread
  UIDispatcher.post(lambda: EventBus.trigger(HuntStateChangedEvent("running")))
  ```

- **Refactoring Note:** Ensure that `UIDispatcher` is imported locally or at the top of the file securely (`from lib.events.ui_dispatcher import UIDispatcher`).

## Verification
- [ ] After applying fixes, perform manual testing (start hunt, stop hunt, trigger auto-scans, run icon sync).
- [ ] Monitor the console/logs for any `PyEval_RestoreThread` errors or silently dropped tasks.
- [ ] Ensure that `UIDispatcher._process_queue` is active and tearing down properly during shutdown (using `threading.Event` tracking).
