import time
import traceback

try:
    from app_gui import App
except Exception as e:
    print('IMPORT_APP_FAILED:', e)
    traceback.print_exc()
    raise

try:
    app = App()
    # wait briefly to allow registration prints to appear
    time.sleep(1)
    try:
        diag = getattr(app, '_failed_hotkeys', {})
        handlers = list(getattr(app, '_registered_hotkey_handlers', {}).keys())
        ok = getattr(app, '_hotkeys_registered_ok', None)
        print('HOTKEYS_FAILED:', diag)
        print('REGISTERED_HANDLERS:', handlers)
        print('HOTKEYS_OK:', ok)
    except Exception as e:
        print('DIAG_CAPTURE_FAILED:', e)
        traceback.print_exc()
    try:
        app.destroy()
    except Exception as e:
        print('APP_DESTROY_FAILED:', e)
    print('PROBE_DONE')
except Exception as e:
    print('PROBE_EXCEPTION:', e)
    traceback.print_exc()
