import time
import tkinter as tk
from app_gui import App
from lib.system.hunt_logger import get_hunt_logger

def test_log_queue():
    app = App()

    logger = get_hunt_logger()
    logger.log_info("Test log message 1")
    logger.log_info("Test log message 2")

    # Process Tkinter events to trigger the after() callbacks
    app.update()
    time.sleep(0.6)
    app.update()

    # Assert logs reached the text widget
    content = app.logs_text_widget.get("1.0", tk.END)
    assert "Test log message 1" in content
    assert "Test log message 2" in content
    print("Log queue test passed!")

    app.destroy()

if __name__ == '__main__':
    test_log_queue()
