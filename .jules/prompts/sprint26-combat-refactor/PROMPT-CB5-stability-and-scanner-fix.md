# Session Prompt CB5: Window Scanner Dataclass Fix & Dynamic Capture Rect

Timebox: 20-25 minutes.

Objective:
Fix AttributeError in `AutoScanner` when inspecting `WindowInfo` dataclass and prevent `ScreenCapture` crash on window repositioning/resizing.

Target Files:
- Modify: `lib/features/hunt/scanner.py`
- Modify: `lib/system/screen_capture.py`

Implementation Details:
1. In `lib/features/hunt/scanner.py` (`detect_window`):
   - Fix `info.get('style', 0)` bug. Replace with dataclass property access `info.is_minimized` or `getattr(info, 'is_minimized', False)`.
2. In `lib/system/screen_capture.py`:
   - In `_capture_loop()`, refresh `window_rect` dynamically before capture or verify handle validity using `win32gui.GetClientRect(self.hwnd)` to handle window resize without bitmap buffer overrun.
   - Protect against minimized window coordinate errors (`-32000`).

Validation:
- Run `scanner.py` standalone test to ensure no `AttributeError` when inspecting windows.
- Test `ScreenCapture` starting and stopping cleanly without memory leaks.

Session Boundary Gate:
- Report PASSED/REVERTED at minute 25.