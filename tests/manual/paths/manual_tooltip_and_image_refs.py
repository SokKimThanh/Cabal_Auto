import unittest
import tkinter as tk
from ui.helpers.tooltip import attach_i18n_tooltip, I18nToolTip
from ui.windows.library_manager import LibraryManagerWindow

class TooltipAndImageRefsTests(unittest.TestCase):
    def setUp(self):
        # Create a root Tk instance but do not show window
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_attach_i18n_tooltip_sets_attribute(self):
        btn = tk.Button(self.root, text='X')
        tip = attach_i18n_tooltip(btn, key='window_select_tooltip', ns='library_manager', lang_provider=lambda: 'en')
        # After attaching, the widget should have _i18n_tooltip attribute referencing an I18nToolTip
        self.assertTrue(hasattr(btn, '_i18n_tooltip'))
        self.assertIsInstance(getattr(btn, '_i18n_tooltip'), I18nToolTip)
        # Tip should be usable (no exceptions on show/hide)
        try:
            tip._show()
            tip._hide()
        except Exception:
            self.fail('I18nToolTip show/hide raised an exception')

    def test_make_icon_button_keeps_image_ref(self):
        # Create a lightweight LibraryManagerWindow object without calling full __init__
        lm = LibraryManagerWindow.__new__(LibraryManagerWindow)
        lm.lang = 'en'
        lm._image_refs = []
        # Provide a minimal _icon method that returns a Tk PhotoImage
        def fake_icon(name, fallback, size=16):
            return tk.PhotoImage(width=1, height=1)
        lm._icon = fake_icon

        # Call _make_icon_button with a parent; function should append image to _image_refs
        btn = lm._make_icon_button(self.root, 'test', 'T', 'tip_apply_all', command=lambda: None)
        # If image was available, it should have been appended to _image_refs
        self.assertTrue(hasattr(lm, '_image_refs'))
        self.assertTrue(len(lm._image_refs) >= 1)
        # The stored object should be a PhotoImage (or similar)
        self.assertTrue(any(isinstance(x, tk.PhotoImage) for x in lm._image_refs))

if __name__ == '__main__':
    unittest.main()
