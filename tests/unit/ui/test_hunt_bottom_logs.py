import pytest
import tkinter as tk
import unittest.mock
import sys

# Mock dependencies before importing App

from app_gui import App

pytestmark = pytest.mark.unit


@pytest.fixture
def app():
    try:
        instance = App()
    except tk.TclError as exc:
        pytest.skip(f"Tk cannot initialize in this environment: {exc}")
    yield instance
    instance.destroy()

@pytest.mark.ui
def test_hunt_tab_geometry_with_collapsed_logs(app):
    # Requirements:
    # 1. 1366x768 geometry
    # 2. Logs collapsed
    # 3. bottom of skill_strip_frame <= bottom of hunt_tab
    # 4. bottom of hunt_tab <= top of logs_header_frame

    app.geometry("1366x768")

    # Simulate logs collapsed state - this forces row 2 to exactly 36px
    # and row 1 (the workspace) receives the rest
    app.main_shell.rowconfigure(2, minsize=36, weight=0)

    # Give Tkinter time to layout
    app.update_idletasks()

    # 1. Find Hunt Tab
    hunt_tab = None
    def find_hunt_tab(widget):
        if hasattr(widget, 'skill_strip_frame'):
            return widget
        for child in widget.winfo_children():
            res = find_hunt_tab(child)
            if res: return res
        return None
    hunt_tab = find_hunt_tab(app)

    assert hunt_tab is not None, "Could not find hunt_tab in App"

    # 2. Get skill strip and check coordinates
    skill_strip = hunt_tab.skill_strip_frame
    assert skill_strip is not None, "Skill strip frame not found"

    skill_strip_y = skill_strip.winfo_rooty()
    skill_strip_h = skill_strip.winfo_height()
    skill_strip_bottom = skill_strip_y + skill_strip_h

    hunt_tab_y = hunt_tab.winfo_rooty()
    hunt_tab_h = hunt_tab.winfo_height()
    hunt_tab_bottom = hunt_tab_y + hunt_tab_h

    assert skill_strip_bottom <= hunt_tab_bottom, (
        f"Skill strip bottom Y ({skill_strip_bottom}) exceeds hunt tab bottom Y ({hunt_tab_bottom})"
    )

    # 3. Check logs header frame overlap
    logs_header = app.logs_header_frame
    assert logs_header is not None, "Logs header frame not found"

    logs_header_y = logs_header.winfo_rooty()

    assert hunt_tab_bottom <= logs_header_y, (
        f"Hunt tab overlaps logs header! Hunt tab bottom Y: {hunt_tab_bottom}, Logs header Y: {logs_header_y}"
    )

    # 4. Logs inside client bounds
    logs_header_h = logs_header.winfo_height()
    logs_bottom = logs_header_y + logs_header_h
    app_y = app.winfo_rooty()
    app_h = app.winfo_height()

    assert logs_header_y >= app_y, "Logs header is above app window"
    assert logs_bottom <= app_y + app_h, "Logs header bottom extends below app window bounds"

    # 5. Treeview is present and requested height is at least roughly two rows (Treeview gives requested size internally)
    stats_tree = app.skill_stats_tree
    assert stats_tree.winfo_reqheight() > 10, f"Stats tree requested height is too small ({stats_tree.winfo_reqheight()})"
