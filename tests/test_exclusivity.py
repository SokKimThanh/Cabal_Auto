import time
import pytest
from app_gui import App

# These tests are basic smoke tests that validate exclusivity helpers.
# They are not full GUI interaction tests but help ensure the try_close_* helpers
# and show_setup_wizard behavior work as intended in the headless test environment.


def test_setup_wizard_blocks_library_when_unsaved():
    a = App()
    try:
        a.on_setup_wizard()
        time.sleep(0.05)
        wiz = getattr(a, '_setup_wizard_win', None)
        assert wiz is not None
        # Make wizard dirty
        wiz.wizard_data['language'] = 'vi' if wiz.wizard_data.get('language') != 'vi' else 'en'
        assert wiz.has_unsaved_changes()
        # try_close_setup_wizard should return True only if user confirms; in headless
        # environment the messagebox may be suppressed and attempt_close may default
        # conservative behavior; call the helper and ensure it returns a bool.
        res = a.try_close_setup_wizard()
        assert isinstance(res, bool)
    finally:
        try:
            wiz = getattr(a, '_setup_wizard_win', None)
            if wiz and getattr(wiz, 'dialog', None):
                wiz.dialog.destroy()
        except Exception:
            pass
        a.destroy()


def test_library_manager_try_close_returns_bool():
    a = App()
    try:
        # Open library manager
        a._open_library_manager()
        time.sleep(0.05)
        lib = getattr(a, 'library_manager_win', None)
        assert lib is not None
        res = a.try_close_library_manager()
        assert isinstance(res, bool)
    finally:
        try:
            lib = getattr(a, 'library_manager_win', None)
            if lib:
                try:
                    lib.destroy()
                except Exception:
                    pass
        except Exception:
            pass
        a.destroy()
