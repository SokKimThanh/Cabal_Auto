### File 2: `PROMPT-CB1-target-bar-detector.md` (Session 1: Module đọc Target Bar)

```markdown
# Session Prompt CB1: Implement TargetBarDetector

Timebox: 25-30 minutes.

Objective:
Create a dedicated, lightweight vision module `lib/vision/target_bar_detector.py` that checks whether a targeted monster is alive by reading the HP bar at the top-center HUD instead of scanning the full 3D viewport.

Target Files:
- Create: `lib/vision/target_bar_detector.py`
- Modify: `lib/vision/__init__.py` (if applicable)
- Create Test: `tests/unit/test_target_bar_detector.py`

Implementation Details:
1. Define class `TargetBarDetector`:
   - Inputs: `window_bounds` dict or list `[x, y, w, h]`.
   - Compute relative ROI for Cabal target HP bar: y: ~4.5%-6.5%, x: ~42%-58% of client area.
   - Implement `is_target_alive(frame: np.ndarray) -> bool`:
     - Validate frame not None, shape valid.
     - Crop ROI.
     - Convert ROI to HSV.
     - Apply mask for Yellow/Orange/Red HP bar colors (e.g. Yellow HSV `[12, 120, 120]` to `[35, 255, 255]`).
     - Return `True` if `cv2.countNonZero(mask) > threshold_pixel_count` (e.g., 30px), else `False`.
   - Implement `get_hp_percentage(frame: np.ndarray) -> float`.
2. Add safe boundary checks: Return `False` if frame is empty, black, or out-of-bounds.

Validation & Test:
- Run: `pytest tests/unit/test_target_bar_detector.py`
- Test with:
  1. Synthetic test frame with yellow bar -> asserts True.
  2. Synthetic empty/black frame -> asserts False.
  3. None/corrupted frame -> asserts False without raising exception.

Session Boundary Gate:
- Verify no dependency on full-screen HSV search.
- Report PASSED/REVERTED at minute 25.

# Bổ sung vào Implementation Details của CB1:
- Call `win32gui.GetClientRect(hwnd)` to get exact internal canvas size, ignoring OS window borders.
- Define normalized ROI relative to client canvas:
  * Top: 0.048 to 0.065
  * Left: 0.42 to 0.58
- Color bounds for Cabal Target Bar:
  * Lower HSV: np.array([12, 130, 130])
  * Upper HSV: np.array([32, 255, 255])
- Ensure DPI Awareness is checked before calculating pixel coordinates.