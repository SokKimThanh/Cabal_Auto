import re
with open('tests/unit/vision/test_target_bar_detector_hwnd.py', 'w') as f:
    f.write('''import pytest
from unittest.mock import MagicMock, patch
from lib.vision.target_bar_detector import TargetBarDetector

class TestTargetBarDetectorHWND:
    @patch('lib.vision.target_bar_detector.win32gui')
    def test_target_bar_detector_uses_client_size(self, mock_win32gui):
        """Verify detector falls back to client rect when HWND is provided."""
        mock_win32gui.GetClientRect.return_value = (0, 0, 1024, 768)

        detector = TargetBarDetector(hwnd=12345)
        # Should call GetClientRect
        assert mock_win32gui.GetClientRect.called
''')
