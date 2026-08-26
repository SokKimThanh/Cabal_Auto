import sys
from unittest.mock import MagicMock, patch
import pytest

# Mock modules before importing controller
with patch.dict('sys.modules', {
    'tkinter': MagicMock(),
    'tkinter.messagebox': MagicMock(),
    'PIL': MagicMock(),
    'PIL.ImageTk': MagicMock()
}):
    from ui.controllers.library_manager_controller import LibraryManagerController

@patch('ui.windows.library_manager.LibraryManagerWindow')
def test_duplicate_window_prevention(mock_window_class):
    # Setup mock app
    app = MagicMock()
    app.library_manager_win = None
    app.hunt_cfg = {}
    app.monsters = []
    app.skills = []
    app.lang = 'vi'

    controller = LibraryManagerController(app)

    # Call the first time
    controller.open_library_manager()
    mock_window_class.assert_called_once()

    # Simulate window creation
    mock_window_instance = MagicMock()
    mock_window_instance.winfo_exists.return_value = True
    app.library_manager_win = mock_window_instance

    # Call the second time
    controller.open_library_manager()

    # Assert constructor not called again
    assert mock_window_class.call_count == 1

    # Assert window operations
    mock_window_instance.deiconify.assert_called_once()
    mock_window_instance.lift.assert_called_once()
    mock_window_instance.focus_force.assert_called_once()
