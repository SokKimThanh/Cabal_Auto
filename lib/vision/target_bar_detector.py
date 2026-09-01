import cv2
import numpy as np
import logging

# Actively set DPI awareness if on Windows
try:
    import ctypes
    if hasattr(ctypes, 'windll') and hasattr(ctypes.windll, 'shcore'):
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 2 = per-monitor DPI aware
except Exception as e:
    logging.debug(f"Could not set DPI awareness (might not be on Windows): {e}")

try:
    import win32gui
except ImportError:
    win32gui = None
    logging.debug("win32gui not available.")

class TargetBarDetector:
    def __init__(self, window_bounds=None, hwnd=None):
        """
        Initializes the TargetBarDetector.
        :param window_bounds: dict or list [x, y, w, h] representing the window dimensions.
        :param hwnd: Optional handle to the window to fetch client rect dynamically.
        """
        self.hwnd = hwnd

        if window_bounds is None:
            self.window_bounds = [0, 0, 1920, 1080] # Default fallback
        elif isinstance(window_bounds, dict):
            self.window_bounds = [
                window_bounds.get('x', 0),
                window_bounds.get('y', 0),
                window_bounds.get('w', 1920),
                window_bounds.get('h', 1080)
            ]
        else:
            self.window_bounds = list(window_bounds)

        # ROI constants (relative)
        self.roi_top_frac = 0.048
        self.roi_bottom_frac = 0.065
        self.roi_left_frac = 0.42
        self.roi_right_frac = 0.58

        # HSV Bounds
        self.lower_hsv = np.array([12, 130, 130])
        self.upper_hsv = np.array([32, 255, 255])

        # Thresholds
        self.threshold_ratio = 0.02
        self.min_pixel_floor = 10

    def _get_client_size(self):
        """Fetches the actual client canvas size if hwnd is provided, otherwise falls back to window_bounds."""
        if self.hwnd and win32gui:
            try:
                rect = win32gui.GetClientRect(self.hwnd)
                # GetClientRect returns (left, top, right, bottom) where left=0, top=0 usually.
                # Width = right - left, Height = bottom - top
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                if width > 0 and height > 0:
                    return width, height
            except Exception as e:
                logging.debug(f"Failed to get client rect for hwnd {self.hwnd}: {e}")

        return self.window_bounds[2], self.window_bounds[3]

    def _get_roi_coords(self, frame_height, frame_width):
        """Computes absolute coordinates for the ROI based on frame size."""
        top = int(frame_height * self.roi_top_frac)
        bottom = int(frame_height * self.roi_bottom_frac)
        left = int(frame_width * self.roi_left_frac)
        right = int(frame_width * self.roi_right_frac)
        return top, bottom, left, right

    def _get_roi(self, frame):
        """Validates the frame and extracts the ROI."""
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0 or len(frame.shape) < 2:
            return None

        # Using the actual client size if available to compute ROI
        # This addresses the edge case where the frame includes OS window borders
        # and we need strictly the inner client dimensions.
        w, h = self._get_client_size()

        # If the frame is smaller or larger than the default/detected client size,
        # it means the frame dimensions should be trusted over the static fallback bounds
        if frame.shape[1] != w or frame.shape[0] != h:
            h, w = frame.shape[:2]

        top, bottom, left, right = self._get_roi_coords(h, w)

        # Boundary checks
        if top < 0 or bottom > h or left < 0 or right > w or top >= bottom or left >= right:
            return None

        roi = frame[top:bottom, left:right]
        return roi

    def is_target_alive(self, frame: np.ndarray) -> bool:
        """
        Determines if the target is alive based on the target bar in the ROI.
        """
        roi = self._get_roi(frame)
        if roi is None:
            return False

        # Black-frame detection
        if len(roi.shape) == 3:
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray_roi = roi

        mean_intensity = np.mean(gray_roi)
        if mean_intensity < 5:
            return False

        # Convert ROI to HSV and apply mask
        if len(roi.shape) == 3 and roi.shape[2] == 3:
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        else:
            # If not BGR, cannot properly apply HSV mask
            return False

        mask = cv2.inRange(hsv_roi, self.lower_hsv, self.upper_hsv)

        roi_area = mask.shape[0] * mask.shape[1]
        threshold = max(self.min_pixel_floor, roi_area * self.threshold_ratio)

        return cv2.countNonZero(mask) > threshold

    def get_hp_percentage(self, frame: np.ndarray) -> float:
        """
        Calculates the target's HP percentage by scanning the masked ROI column-by-column.
        """
        roi = self._get_roi(frame)
        if roi is None:
            return 0.0

        if len(roi.shape) == 3 and roi.shape[2] == 3:
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        else:
            return 0.0

        mask = cv2.inRange(hsv_roi, self.lower_hsv, self.upper_hsv)

        # Scan column by column
        # mask is of shape (height, width)
        # We can check if any pixel in each column is non-zero
        columns_any_nonzero = np.any(mask > 0, axis=0)
        filled_columns = np.sum(columns_any_nonzero)
        total_columns = mask.shape[1]

        if total_columns == 0:
            return 0.0

        hp_percentage = (filled_columns / total_columns) * 100.0
        return float(hp_percentage)
