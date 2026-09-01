import pytest
import sys
from unittest.mock import Mock

def test_full_loop_view_swapping(monkeypatch):
    monkeypatch.setitem(sys.modules, 'lib.system.window_manager', Mock())
    from app_gui import App
    app = App()
    try:
        assert app.current_view_key == 'hunt'
        app.switch_view('setup')
        assert app.current_view_key == 'setup'
        app.switch_view('help')
        assert app.current_view_key == 'help'
        app.switch_view('hunt')
        assert app.current_view_key == 'hunt'
    finally:
        app.destroy()

def test_zero_geometry_conflict(monkeypatch):
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
