# Session Prompt CB5: Window Scanner Dataclass Fix & Dynamic Capture Rect

Timebox: 20-25 minutes.

Objective:
Fix AttributeError in `AutoScanner` when inspecting `WindowInfo` dataclass and prevent `ScreenCapture` crash on window repositioning/resizing.

Target Files:
- Modify: `lib/features/hunt/scanner.py`
- Modify: `lib/system/screen_capture.py`

## Implementation Details

1. In `lib/features/hunt/scanner.py` (`detect_window`):
   - Fix the `info.get('style', 0)` bug (treating a dataclass instance like a dict). Replace with **direct attribute access**: `info.is_minimized`. Do not use `getattr(info, 'is_minimized', False)` here — a silent default would mask the exact class of bug being fixed (wrong access pattern on a dataclass field) if the field is ever renamed again; a direct attribute access fails loudly and immediately, which is what you want for a dataclass with a known, stable field.
2. In `lib/system/screen_capture.py`:
   - In `_capture_loop()`, on each capture cycle, do **both** of the following (not either/or):
     1. Verify the window handle is still valid (`win32gui.IsWindow(self.hwnd)` or equivalent) — if invalid, the window was closed. Stop the capture loop cleanly, surface a "capture target lost" signal to whatever owns the capture, and do not attempt further Win32 calls on the stale handle.
        - Define the signal concretely: expose a `threading.Event` (e.g. `self.capture_lost_event`) that the capture loop sets once, plus an optional `on_capture_lost: Optional[callable]` constructor param invoked once from the loop thread. `HuntOrchestrator`/the hunt session owner polls or subscribes to this to stop/pause rather than looping on exceptions. Do not use a bare exception as the signaling mechanism, since the loop must exit cleanly rather than propagate.
     2. If the handle is still valid, refresh `window_rect` via `win32gui.GetClientRect(self.hwnd)` before capturing.
   - Buffer reallocation: when the freshly-read rect's dimensions differ from the currently allocated capture buffer/bitmap, reallocate the buffer to the new size before writing into it. Simply updating the stored `window_rect` value without resizing the underlying bitmap is not sufficient — it is the mismatch between an old, smaller buffer and a newly resized window that causes the overrun this session is meant to fix.
   - **Thread-safety with concurrent readers (cross-reference CB6):** `get_latest_frame()` (added in CB6) reads/copies `self._latest_frame` from a different thread than `_capture_loop()`. Protect the buffer swap/reallocation and the read-copy with a single lightweight `threading.Lock` (e.g. `self._frame_lock`), held only for the brief assignment/copy, not for the full capture+processing work — so a reallocation in progress can never be observed mid-write by a concurrent `get_latest_frame()` call.
   - Minimized window handling: detect the `-32000` coordinate pattern (or `IsIconic(self.hwnd)`) before attempting a capture. When minimized, skip the capture for that cycle and return the **last known good frame** (cached from the previous successful capture) rather than `None` or a zero-sized buffer — this keeps compatibility with existing consumers (e.g. `TargetBarDetector.is_target_alive`, CB4A's HP reader) that already treat a `None`/empty frame as "no target," which would be misleading here since minimizing doesn't mean the target died. If no prior good frame exists yet (e.g. minimized before the first successful capture), returning `None` is acceptable and relies on the existing boundary checks from CB1.

## Validation

- Run `scanner.py` standalone test to ensure no `AttributeError` when inspecting windows.
- Test `ScreenCapture` starting and stopping cleanly without memory leaks.
- (Added) Resize-during-capture test: start capture at one window size, simulate a resize event (different `GetClientRect` dimensions on a subsequent poll), and assert the buffer is reallocated to match — no overrun, no stale-size crash, and the next captured frame has the correct new dimensions.
- (Added) Minimize test: simulate `IsIconic`/`-32000` coordinates mid-capture, assert the loop does not crash, skips that cycle, and returns the last known good frame (or `None` if none exists yet) instead of a corrupted/zero-sized frame.
- (Added) Window-closed test: simulate `IsWindow` returning `False` mid-loop, assert the capture loop stops cleanly and emits the "capture target lost" signal exactly once (verify `capture_lost_event` is set and/or `on_capture_lost` is invoked exactly once), without looping on repeated exceptions.
- (Added) Concurrent access during reallocation test: trigger a buffer reallocation in `_capture_loop()` and call `get_latest_frame()` from another thread at the same moment; assert the returned frame is always either the old, fully-valid frame or the new, fully-valid frame — never a partially-written or mismatched-size buffer.

## Session Boundary Gate

- Confirm `info.is_minimized` uses direct attribute access, not a silent `getattr` fallback.
- Confirm both handle-validity check and rect refresh happen every cycle (not one substituting for the other).
- Confirm the capture buffer is reallocated on size change, not just the stored rect value.
- Confirm the buffer swap/reallocation and `get_latest_frame()` (CB6) reads are protected by the same lock, with no window where a concurrent reader can observe a partially-written buffer.
- Confirm the "capture target lost" signal has a concrete, documented mechanism (`Event` + optional callback), not an implicit/undefined notification.
- Confirm minimized-window behavior returns the last known good frame (or `None` only when no prior frame exists), and window-closed behavior stops the loop cleanly rather than looping on exceptions.
- Report PASSED/REVERTED at minute 25.