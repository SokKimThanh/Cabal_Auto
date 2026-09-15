import pytest
import tkinter as tk
from lib.events.event_bus import EventBus, LanguageChangedEvent
from ui.helpers.translation_binder import TranslationBinder

pytestmark = [pytest.mark.integration, pytest.mark.gui]

def test_translation_binder_live_update():
    """
    Verifies that TranslationBinder successfully updates widget text
    when refresh_all is called (simulating a LanguageChangedEvent).
    """
    root = tk.Tk()

    try:
        # 1. Setup mock dictionary & binder
        mock_db = {
            "en": {"test_key": "Hello"},
            "vi": {"test_key": "Xin chào"}
        }
        current_lang = "en"

        def mock_translator(key, **kwargs):
            return mock_db.get(current_lang, {}).get(key, key)

        binder = TranslationBinder()

        # 2. Create widget & bind
        lbl = tk.Label(root, text="Initial")
        binder.bind(lbl, "test_key")

        # Verify initial binding sets text (if we trigger first refresh)
        binder.refresh_all(mock_translator)
        assert lbl.cget("text") == "Hello"

        # 3. Simulate language change (as app_gui.py would do)
        current_lang = "vi"
        binder.refresh_all(mock_translator)

        # 4. Assert text updated to Vietnamese
        assert lbl.cget("text") == "Xin chào"

    finally:
        root.destroy()
