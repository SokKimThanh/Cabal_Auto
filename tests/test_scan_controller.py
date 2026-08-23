from unittest.mock import MagicMock
from lib.features.hunt.scan_controller import ScanController

def test_scan_controller_init():
    mock_getter = MagicMock()
    mock_set_text = MagicMock()
    mock_set_icon = MagicMock()
    mock_show = MagicMock()

    class DummyIcons:
        SCANNING = "scaning"

    controller = ScanController(
        vision_engine_getter=mock_getter,
        set_status_text=mock_set_text,
        set_status_icon=mock_set_icon,
        show_results=mock_show,
        icons=DummyIcons
    )

    assert controller.vision_engine_getter == mock_getter

def test_scan_controller_run_scan():
    mock_getter = MagicMock()
    mock_set_text = MagicMock()
    mock_set_icon = MagicMock()
    mock_show = MagicMock()

    class DummyIcons:
        SCANNING = "scaning"
        SCAN_SCREEN = "scan-screen"
        SCAN_COMPLETE = "scan-complete"
        SCAN_FAILED = "scan-failed"

    controller = ScanController(
        vision_engine_getter=mock_getter,
        set_status_text=mock_set_text,
        set_status_icon=mock_set_icon,
        show_results=mock_show,
        icons=DummyIcons
    )

    controller.run_scan(manual=True)

    mock_set_text.assert_any_call("🔍 Đang quét…")
    mock_set_icon.assert_any_call("scaning")
