import pytest
import tkinter as tk
from unittest.mock import MagicMock
from lib.events.event_bus import EventBus, HuntStatusUpdatedEvent, HuntStateChangedEvent
from ui.components.hunt_status_ticker import HuntStatusTicker
from lib.ui_style_v2 import UIStyleV2 as UI

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

def test_hunt_status_ticker_initialization(root, app_mock):
    ticker = HuntStatusTicker(root, app_mock)
    assert ticker.msg_label.cget("text") == "translated_hunt_status_ticker.idle"
    ticker.destroy()

def test_hunt_status_ticker_status_updated_event(root, app_mock):
    ticker = HuntStatusTicker(root, app_mock)
    ticker.pack()

    EventBus.trigger(HuntStatusUpdatedEvent("Custom warning message"))

    # Process main thread queue
    root.update()

    assert ticker.msg_label.cget("text") == "Custom warning message"
    ticker.destroy()

def test_hunt_status_ticker_state_changed_event(root, app_mock):
    ticker = HuntStatusTicker(root, app_mock)
    ticker.pack()

    # Note: the icon logic now sets empty text if icon loaded or fallback string.
    # To test UI colors we just check the msg_label and icon_label fg

    # Test error state
    EventBus.trigger(HuntStateChangedEvent("error"))
    root.update()
    assert ticker.msg_label.cget("fg") == UI.COLOR_DANGER
    assert ticker.msg_label.cget("text") == "translated_hunt_status_ticker.error"

    # Test running state
    EventBus.trigger(HuntStateChangedEvent("running"))
    root.update()
    assert ticker.msg_label.cget("fg") == UI.TEXT_PRIMARY

    # Test searching state
    EventBus.trigger(HuntStateChangedEvent("searching"))
    root.update()
    assert ticker.msg_label.cget("fg") == UI.ACCENT_AMBER

    # Test idle state
    EventBus.trigger(HuntStateChangedEvent("idle"))
    root.update()
    assert ticker.msg_label.cget("fg") == UI.TEXT_MUTED

    ticker.destroy()

def test_hunt_status_ticker_priority(root, app_mock):
    ticker = HuntStatusTicker(root, app_mock)
    ticker.pack()

    # Trigger custom status update followed immediately by state changed to error
    EventBus.trigger(HuntStatusUpdatedEvent("Detailed custom error context"))
    EventBus.trigger(HuntStateChangedEvent("error"))

    root.update()

    # Should retain the detailed error message since they fired concurrently
    assert ticker.msg_label.cget("text") == "Detailed custom error context"
    # Should still have updated the color for the error state
    assert ticker.msg_label.cget("fg") == UI.COLOR_DANGER

    ticker.destroy()
