import cv2
import numpy as np
import logging

import shutil

try:
    import pytesseract
except ImportError:
    pytesseract = None
    logging.debug("pytesseract not available. OCR will fail fast.")

TESSERACT_CMD = shutil.which("tesseract")


class TargetNameReader:
    def __init__(self, window_bounds=None, hwnd=None):
        self.hwnd = hwnd
        if window_bounds is None:
            self.window_bounds = [0, 0, 1920, 1080]
        elif isinstance(window_bounds, dict):
            self.window_bounds = [
                window_bounds.get('x', 0),
                window_bounds.get('y', 0),
                window_bounds.get('w', 1920),
                window_bounds.get('h', 1080)
            ]
        else:
            self.window_bounds = list(window_bounds)

        self.roi_top_frac = 0.025
        self.roi_bottom_frac = 0.048
        self.roi_left_frac = 0.40
        self.roi_right_frac = 0.60

    def _get_client_size(self):
        try:
            import win32gui
            if self.hwnd and win32gui:
                rect = win32gui.GetClientRect(self.hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                if width > 0 and height > 0:
                    return width, height
        except Exception:
            pass
        return self.window_bounds[2], self.window_bounds[3]

    def _get_roi(self, frame):
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0 or len(frame.shape) < 2:
            return None
        w, h = self._get_client_size()
        if frame.shape[1] != w or frame.shape[0] != h:
            h, w = frame.shape[:2]

        top = int(h * self.roi_top_frac)
        bottom = int(h * self.roi_bottom_frac)
        left = int(w * self.roi_left_frac)
        right = int(w * self.roi_right_frac)

        if top < 0 or bottom > h or left < 0 or right > w or top >= bottom or left >= right:
            return None
        return frame[top:bottom, left:right]

    def read_name(self, frame):
        if pytesseract is None:
            logging.error("pytesseract is not installed.")
            raise RuntimeError("Tesseract Python wrapper missing")

        if not TESSERACT_CMD:
            logging.error("tesseract binary is not on PATH.")
            raise RuntimeError("Tesseract binary missing from PATH")

        roi = self._get_roi(frame)
        if roi is None:
            return ""

        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi

        _, binarized = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        try:
            text = pytesseract.image_to_string(binarized, config='--psm 7').strip()
            return text
        except Exception as e:
            logging.error(f"OCR failed: {e}")
            return ""
