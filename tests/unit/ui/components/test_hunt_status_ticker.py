import pytest
import tkinter as tk
from unittest.mock import MagicMock
from ui.components.hunt_status_ticker import HuntStatusTicker
from lib.events.event_bus import EventBus, HuntStatusUpdatedEvent, HuntStateChangedEvent
from lib.ui_style_v2 import UIStyleV2 as UI

@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()

@pytest.fixture
def mock_app():
    app = MagicMock()
    app._t = MagicMock(side_effect=lambda key: f"translated_{key}")
    return app

@pytest.fixture
def ticker(root, mock_app, mocker):
    EventBus.clear()
    ticker = HuntStatusTicker(root, mock_app)

    # Mock `after` so we don't rely on the Tkinter mainloop or DummyTk for delayed execution in tests
    def mock_after(ms, func=None, *args):
        if func:
            func(*args)
    mocker.patch.object(ticker, "after", side_effect=mock_after)

    ticker.pack()
    root.update()
    return ticker

def test_initialization(ticker, mock_app):
    # Check if app._t was called for default text
    mock_app._t.assert_called_with("hunt.status_ready")

    assert ticker.icon_label.cget("text") == "ℹ"
    assert ticker.message_label.cget("text") == "translated_hunt.status_ready"

def test_hunt_status_updated_event(ticker, root):
    # Test normal message
    EventBus.trigger(HuntStatusUpdatedEvent("Some info message"))
    root.update()  # Process 'after' events

    assert ticker.message_label.cget("text") == "Some info message"

    # Test error message
    EventBus.trigger(HuntStatusUpdatedEvent("Error: connection lost"))
    root.update()

    assert ticker.icon_label.cget("text") == "⚠"
    assert ticker.message_label.cget("text") == "Error: connection lost"
    assert ticker.message_label.cget("fg") == UI.COLOR_DANGER

    # Test retrying message
    EventBus.trigger(HuntStatusUpdatedEvent("Retrying connection..."))
    root.update()

    assert ticker.icon_label.cget("text") == "↻"
    assert ticker.message_label.cget("text") == "Retrying connection..."
    assert ticker.message_label.cget("fg") == UI.ACCENT_AMBER

def test_hunt_state_changed_event(ticker, root, mock_app):
    # Test hunting state
    EventBus.trigger(HuntStateChangedEvent("hunting"))
    root.update()

    assert ticker.icon_label.cget("text") == "⚡"
    assert ticker.message_label.cget("text") == "translated_hunt.state_hunting"
    assert ticker.message_label.cget("fg") == UI.ACCENT_BLUE

    # Test error state
    EventBus.trigger(HuntStateChangedEvent("error"))
    root.update()

    assert ticker.icon_label.cget("text") == "⚠"
    assert ticker.message_label.cget("fg") == UI.COLOR_DANGER

    # Test scanning state
    EventBus.trigger(HuntStateChangedEvent("scanning"))
    root.update()

    assert ticker.icon_label.cget("text") == "↻"
    assert ticker.message_label.cget("text") == "translated_hunt.state_scanning"
    assert ticker.message_label.cget("fg") == UI.ACCENT_AMBER
