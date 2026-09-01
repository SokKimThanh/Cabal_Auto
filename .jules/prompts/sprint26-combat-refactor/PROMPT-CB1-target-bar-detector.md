# Session Prompt CB1: Implement TargetBarDetector

Timebox: 25-30 minutes.

Objective:
Create a dedicated, lightweight vision module `lib/vision/target_bar_detector.py` that checks whether a targeted monster is alive by reading the HP bar at the top-center HUD instead of scanning the full 3D viewport.

Target Files:
- Create: `lib/vision/target_bar_detector.py`
- Modify: `lib/vision/__init__.py` (if applicable)
- Create Test: `tests/unit/test_target_bar_detector.py`

## Implementation Details

1. Define class `TargetBarDetector`:
   - Inputs: `window_bounds` dict or list `[x, y, w, h]`.
   - Call `win32gui.GetClientRect(hwnd)` to get the exact internal canvas size, ignoring OS window borders.
   - Before computing any pixel coordinates, actively set DPI awareness (do not just check it):
     ```python
     import ctypes
     ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 2 = per-monitor DPI aware
     ```
     This must run once at process/module init, before any `GetClientRect`/`GetWindowRect` call, otherwise coordinates will be scaled incorrectly on displays with >100% scaling.
   - Define the ROI as a normalized rectangle relative to client canvas (final, authoritative values — supersedes any earlier draft):
     * Top: 0.048 to 0.065 (relative height)
     * Left: 0.42 to 0.58 (relative width, i.e. `left_frac` to `right_frac`; width = `right_frac - left_frac`)
   - Color bounds for Cabal Target Bar (final, authoritative values — supersedes any earlier draft):
     * Lower HSV: `np.array([12, 130, 130])`
     * Upper HSV: `np.array([32, 255, 255])`
   - Implement `is_target_alive(frame: np.ndarray) -> bool`:
     - Validate frame not None, shape valid.
     - Crop ROI.
     - Convert ROI to HSV.
     - Apply the HSV mask defined above.
     - Compute `threshold = max(min_pixel_floor, roi_area * threshold_ratio)`, where `threshold_ratio` (e.g. `0.02`, i.e. 2% of ROI area) scales with resolution, and `min_pixel_floor` (e.g. `10px`) prevents false positives on tiny ROIs. Do not use a fixed absolute pixel count (e.g. a flat `30px`), since ROI size varies with screen resolution (1080p vs 4K).
     - Return `True` if `cv2.countNonZero(mask) > threshold`, else `False`.
   - Implement `get_hp_percentage(frame: np.ndarray) -> float`:
     - Algorithm: scan the cropped, masked ROI column-by-column (left to right) along the horizontal axis of the bar.
     - For each column, mark it "filled" if it contains at least one masked (non-zero) pixel.
     - `hp_percentage = (number of filled columns / total columns) * 100`.
     - This measures how far the bar visually extends, rather than raw `countNonZero / total_area`, which would be distorted by bar height/border pixels.
2. Add safe boundary checks:
   - Return `False` from `is_target_alive` if frame is `None`, has invalid shape, or ROI is out-of-bounds.
   - Black-frame detection: compute mean pixel intensity of the cropped ROI (grayscale); treat as "black/empty" if `mean < 5`. Use this threshold explicitly rather than an arbitrary raw pixel check, since it also correctly ignores bars that are simply dark-colored but non-empty (a truly black/empty ROI has near-zero mean across all channels, whereas a dark-colored bar still has localized saturated pixels within the HSV mask range).

## Validation & Test

- Run: `pytest tests/unit/test_target_bar_detector.py`
- Test with:
  1. Synthetic test frame with yellow bar → asserts `True`.
  2. Synthetic empty/black frame → asserts `False`.
  3. None/corrupted frame → asserts `False` without raising exception.
  4. (Added) Synthetic frame at two different resolutions (e.g. 1920x1080 and 3840x2160) with proportionally equivalent bars → both assert `True`, verifying the ratio-based threshold scales correctly.
  5. (Added) Synthetic frame with a very dark-colored (but non-empty) bar → asserts `True`, verifying it is not misclassified as a black frame.

## Session Boundary Gate

- Verify no dependency on full-screen HSV search.
- Verify DPI awareness is set before any coordinate calculation.
- Verify HSV bounds and ROI values match the final authoritative values above (no leftover references to the earlier draft values).
- Report PASSED/REVERTED at minute 25.