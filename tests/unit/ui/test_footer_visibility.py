import pytest
import tkinter as tk
import unittest.mock
import sys
import time


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
def test_footer_visibility(app):
    app.geometry("1366x768")
    app.update()
    app.update_idletasks()

    app.after(100)
    app.update()

    # AC-F1
    global_apply = app.global_apply_btn
    db_status = app._db_status_bar

    # Need to check master frames for mapped if inside other unmapped frames
    assert global_apply.winfo_ismapped() == 1, "Global apply button is not mapped"
    assert db_status.winfo_ismapped() == 1, "DB status bar is not mapped"

    apply_frame = global_apply.master

    # Bottom chrome is effectively these elements
    app_y = app.winfo_rooty()
    app_h = app.winfo_height()
    app_bottom = app_y + app_h

    # AC-F2
    # Apply frame is inside client area
    apply_frame_y = apply_frame.winfo_rooty()
    apply_frame_h = apply_frame.winfo_height()
    apply_frame_bottom = apply_frame_y + apply_frame_h

    assert apply_frame_y >= app_y
    assert apply_frame_bottom <= app_bottom

    # db_status is inside client area
    db_status_y = db_status.winfo_rooty()
    db_status_h = db_status.winfo_height()
    db_status_bottom = db_status_y + db_status_h

    assert db_status_y >= app_y
    assert db_status_bottom <= app_bottom

    # AC-F3
    main_shell = app.main_shell
    main_shell_y = main_shell.winfo_rooty()
    main_shell_h = main_shell.winfo_height()
    main_shell_bottom = main_shell_y + main_shell_h

    # The elements are at the bottom of the window.
    # Check if main_shell goes beyond apply frame.
    assert main_shell_bottom <= apply_frame_y, "Main shell overlaps footer"
