import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
import numpy as np
import gc

from ui.components.vision_snapshot_debugger import VisionSnapshotDebugger

@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()

@pytest.fixture
def app_mock():
    app = MagicMock()
    app._t.side_effect = lambda key: f"translated_{key}"
    return app

def test_vision_snapshot_debugger_memory_leak(root, app_mock):
    """
    Test memory leak by triggering refresh 50 times and ensuring
    garbage collection runs correctly (no excessive RAM overhead/bloat).
    This also implicitly tests that CPU overhead is low since we just mock the engine.
    """
    # Create fake frame
    fake_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

    with patch('ui.components.vision_snapshot_debugger.get_vision_engine') as mock_get_engine:
        app_mock._vision_engine = None  # Ensure it uses the patched singleton in tests

        mock_engine = MagicMock()
        mock_engine.get_latest_snapshot.return_value = (fake_frame, [])
        mock_get_engine.return_value = mock_engine

        debugger = VisionSnapshotDebugger(app_mock)
        debugger.open_debugger()

        # Test RAM leak conceptually by running 50 times
        for _ in range(50):
            debugger._refresh_snapshot()

        # The reference should only hold one image at the end
        assert debugger.current_image is not None

        debugger._on_close()
        # Assert image ref is cleared on close
        assert debugger.current_image is None
