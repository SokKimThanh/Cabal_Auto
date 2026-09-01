from unittest.mock import MagicMock
from lib.features.hunt.scanner import AutoScanner

def test_scanner_detect_window_no_attribute_error():
    # Setup mock window manager and info
    mock_vision_engine = MagicMock()
    scanner = AutoScanner(vision_engine=mock_vision_engine)

    mock_window_manager = MagicMock()

    # Create a mock for window_info that has the is_minimized property
    # to simulate the dataclass
    class DummyWindowInfo:
        def __init__(self, is_minimized):
            self.is_minimized = is_minimized

    mock_info = DummyWindowInfo(is_minimized=True)

    mock_window_manager.get_window_info.return_value = mock_info
    mock_window_manager.get_window_rect.return_value = {'width': 1024, 'height': 768}

    # Mock finding the window
    scanner.window_manager = mock_window_manager
    scanner._find_cabal_window = MagicMock(return_value=12345)

    # Run the method
    result = scanner.detect_window()

    # Verify the window info was correctly accessed without AttributeError
    mock_window_manager.get_window_info.assert_called_once_with(12345)
    mock_window_manager.get_window_rect.assert_called_once_with(12345)

    # verify the returned dictionary
    assert result == {'hwnd': 12345, 'rect': {'width': 1024, 'height': 768}}