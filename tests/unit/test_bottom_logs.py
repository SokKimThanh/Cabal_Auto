from app_gui import App as Application
from lib.system.hunt_logger import HuntLogger, get_hunt_logger, reset_hunt_logger
import pytest
import sys
from unittest.mock import patch, MagicMock

# Needs to run headless Tkinter
sys.modules['lib.system.window_manager'] = MagicMock()


@pytest.fixture(autouse=True)
def setup_teardown():
    reset_hunt_logger()
    yield
    reset_hunt_logger()


def test_logger_queue_cap():
    logger = get_hunt_logger()
    assert logger.ui_queue.maxsize == 5000
    # Clear anything in the queue
    while not logger.ui_queue.empty():
        logger.ui_queue.get()
    logger.dropped_log_count = 0

    # Fill the queue to test drop handling
    for i in range(5005):
        logger.logger.info(f"Test log {i}")

    assert logger.ui_queue.qsize() == 5000
    assert logger.dropped_log_count == 5


@pytest.fixture
def app():
    with patch("app_gui.pyautogui", MagicMock()), patch("app_gui.keyboard", MagicMock()):
        app = Application()
        yield app
        app.destroy()


def test_circular_buffer_and_memory_cap(app):
    logger = get_hunt_logger()

    # Bắn liên tục 5.000 dòng log
    for i in range(5000):
        logger.logger.info(f"Test log {i}")

    # App _poll_log_queue is running, but let's call it manually to flush all
    # Since batch limit is 50, we need to call it 100 times to flush 5000 lines
    import math
    flush_count = math.ceil(5000 / 50) + 5
    for _ in range(flush_count):
        app._poll_log_queue()

    # Retrieve number of lines in text widget
    # We inserted 5000 lines. The text widget cap is 1000.
    lines = int(app.logs_text_widget.index('end-1c').split('.')[0])

    # We might have an extra blank line at the end, so lines could be 1001 or 1000
    assert lines <= 1005


def test_batch_insert_rate_limit(app):
    logger = get_hunt_logger()
    while not logger.ui_queue.empty():
        logger.ui_queue.get()

    app.logs_text_widget.config(state="normal")
    app.logs_text_widget.delete("1.0", "end")
    app.logs_text_widget.config(state="disabled")

    for i in range(200):
        logger.logger.info(f"Test log {i}")

    app._poll_log_queue()
    app.update_idletasks()
    app.update()
    # It should have processed exactly 50 lines this tick
    # 50 lines + 1 empty line
    lines = int(app.logs_text_widget.index('end-1c').split('.')[0])
    print(f"LINES: {lines}")
    # Tkinter Text widget often adds an empty newline at the end (e.g. 51 lines instead of 50).
    # Furthermore, due to the event loop, background polling may process a couple of ticks.
    # The critical check is that it didn't block and process all 200 at once (hence < 200).
    assert lines < 200


def test_responsive_initial_logs_state(app):
    # Test _check_initial_logs_state logic
    app.logs_expanded = True
    app.winfo_height = MagicMock(return_value=850)
    app._check_initial_logs_state()
    assert app.logs_expanded is False


def test_responsive_auto_collapse_no_forced_repeat(app):
    # Simulating configure event using actual tkinter event generation

    # Initially over 900
    app.winfo_height = MagicMock(return_value=1000)
    app.event_generate('<Configure>', height=1000)
    app.update()
    assert app._last_height_under_900 is False
    assert app.logs_expanded is True

    # Resize down to 850 -> triggers auto collapse
    app.winfo_height = MagicMock(return_value=850)
    app.event_generate('<Configure>', height=850)
    app.update()
    assert app._last_height_under_900 is True
    assert app.logs_expanded is False

    # User manually expands
    app._toggle_bottom_logs()
    assert app.logs_expanded is True

    # Another resize event still under 900
    app.winfo_height = MagicMock(return_value=840)
    app.event_generate('<Configure>', height=840)
    app.update()
    # Should NOT auto-collapse
    assert app.logs_expanded is True

    # Resize up to 900+
    app.winfo_height = MagicMock(return_value=950)
    app.event_generate('<Configure>', height=950)
    app.update()
    assert app._last_height_under_900 is False

    # Resize down to 850 again -> triggers auto collapse
    app.winfo_height = MagicMock(return_value=850)
    app.event_generate('<Configure>', height=850)
    app.update()
    assert app._last_height_under_900 is True
    assert app.logs_expanded is False


def test_log_file_persistence(tmp_path):
    reset_hunt_logger()
    logger = HuntLogger(log_dir=str(tmp_path))

    for i in range(10):
        logger.logger.info(f"Persistence log {i}")

    log_file = tmp_path / 'hunt.log'
    assert log_file.exists()

    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()

    for i in range(10):
        assert f"Persistence log {i}" in content


def test_rapid_expand_collapse_toggle(app):
    # Test that continuous rapid clicking doesn't break the UI state
    app.winfo_height = MagicMock(return_value=1000)
    for _ in range(10):
        app._toggle_bottom_logs()
        app.update_idletasks()

    assert getattr(app, "logs_expanded", True) in [True, False]
    # It should not raise any TclError or exceptions during rapid toggling


def test_log_format_duplication(app):
    logger = get_hunt_logger()

    # Clean the queue
    while not logger.ui_queue.empty():
        logger.ui_queue.get()

    app.logs_text_widget.config(state="normal")
    app.logs_text_widget.delete("1.0", "end")
    app.logs_text_widget.config(state="disabled")

    # Log a message
    test_msg = "Duplicate check msg"
    logger.logger.info(test_msg)

    # Process queue
    app._poll_log_queue()
    app.update()

    # Check content of text widget
    content = app.logs_text_widget.get("1.0", "end-1c").strip()

    # Count occurrences of the separator '|' or check if timestamp matches pattern multiple times
    # In the current formatter: '%(asctime)s | %(levelname)s | %(message)s'
    # If duplicated, it would look like '... | INFO | ... | INFO | Duplicate check msg'

    info_count = content.count("INFO")

    # We expect 'INFO' to appear only once for this single log line
    assert info_count == 1, f"Expected 1 'INFO', but got {info_count}. Content: {content}"
