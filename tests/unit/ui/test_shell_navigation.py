import pytest
@pytest.fixture(autouse=True)
def mock_tk_headless():
    pass
import pytest
import sys
from unittest.mock import Mock


@pytest.mark.parametrize("view_key", ['setup', 'help', 'hunt'])
def test_switch_view_updates_current_key(monkeypatch, view_key):
    monkeypatch.setitem(sys.modules, 'lib.system.window_manager', Mock())
    from app_gui import App
    app = App()
    try:
        app.switch_view(view_key)
        assert app.current_view_key == view_key
    finally:
        app.destroy()

def test_switch_view_invalid_key(monkeypatch):
    monkeypatch.setitem(sys.modules, 'lib.system.window_manager', Mock())
    from app_gui import App
    app = App()
    try:
        initial_view = app.current_view_key
        app.switch_view('non_existent_key_123')
        assert app.current_view_key == initial_view
    finally:
        app.destroy()

def test_switch_view_rapid_consecutive_calls(monkeypatch):
    monkeypatch.setitem(sys.modules, 'lib.system.window_manager', Mock())
    from app_gui import App
    app = App()
    try:
        for _ in range(10):
            app.switch_view('setup')
            app.switch_view('hunt')
        assert app.current_view_key == 'hunt'
    finally:
        app.destroy()
def test_layout_conflict_between_pack_and_grid(monkeypatch):
    monkeypatch.setitem(sys.modules, 'lib.system.window_manager', Mock())
    from app_gui import App
    app = App()
    try:
        def walk(widget):
            try:
                slaves_pack = widget.pack_slaves()
                slaves_grid = widget.grid_slaves()
                assert not (slaves_pack and slaves_grid), f"Conflict in {widget}"
            except AttributeError:
                pass
            for child in widget.winfo_children():
                walk(child)
        walk(app.main_shell)
    finally:
        app.destroy()

def test_hunt_continues_while_hidden(monkeypatch):
    monkeypatch.setitem(sys.modules, 'lib.system.window_manager', Mock())
    from app_gui import App
    app = App()
    try:
        app.hunt_orchestrator = Mock()
        app.hunt_orchestrator.hunt_running = True
        app.switch_view('setup')
        assert app.hunt_orchestrator.hunt_running is True
    finally:
        app.destroy()

def test_view_hidden_stops_self_polling(monkeypatch):
    monkeypatch.setitem(sys.modules, 'lib.system.window_manager', Mock())
    from app_gui import App
    app = App()
    try:
        hunt_view = app._views['hunt']
        hunt_view.on_view_hidden = Mock()
        hunt_view.on_view_shown = Mock()

        # Must re-set the view because it defaults to hunt during App().__init__
        app._current_view = hunt_view
        app.current_view_key = 'hunt'

        app.switch_view('setup')
        hunt_view.on_view_hidden.assert_called_once()

        app.switch_view('hunt')
        hunt_view.on_view_shown.assert_called_once()
    finally:
        app.destroy()
