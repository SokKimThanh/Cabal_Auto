import pytest
from unittest.mock import MagicMock, patch
from lib.vision.target_bar_detector import TargetBarDetector

pytestmark = pytest.mark.unit


class TestTargetBarDetectorHWND:
    @patch('lib.vision.target_bar_detector.win32gui')
    def test_target_bar_detector_uses_client_size(self, mock_win32gui):
        """Verify detector falls back to client rect when HWND is provided."""
        mock_win32gui.GetClientRect.return_value = (0, 0, 1024, 768)

        detector = TargetBarDetector(hwnd=12345)
        # Should call GetClientRect
        assert mock_win32gui.GetClientRect.called
