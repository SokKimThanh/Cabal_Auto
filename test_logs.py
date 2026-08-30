from app_gui import App

def test_bottom_logs_toggle():
    app = App()

    # Verify initial state
    assert hasattr(app, 'logs_toggle_btn')
    assert hasattr(app, 'logs_content_frame')
    assert app.logs_expanded is True

    # Toggle off
    app._toggle_bottom_logs()
    assert app.logs_expanded is False
    assert app.main_shell.rowconfigure(2)['minsize'] == 36

    # Toggle back on
    app._toggle_bottom_logs()
    assert app.logs_expanded is True
    assert app.main_shell.rowconfigure(2)['minsize'] == 200

    app.destroy()
