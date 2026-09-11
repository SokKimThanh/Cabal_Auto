import tkinter as tk
import unittest
from unittest.mock import MagicMock
from ui.panels.skill_panel import SkillPanel

class DummyIconHelper:
    def __init__(self, root):
        self.img = tk.PhotoImage(width=1, height=1)
    def get_icon(self, name, size=None):
        return self.img

class TestSkillPanel(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_update_toggle_button_visuals(self):
        # Mock what we need to bypass constructor
        panel = SkillPanel.__new__(SkillPanel)
        panel.widgets = {"btn_toggle_skills": tk.Button(self.root)}
        panel._show_all_skills = True
        panel._icon_helper = DummyIconHelper(self.root)
        panel._update_toggle_button_visuals()

        # Test it doesn't crash when dummy image is passed
        self.assertEqual(panel.widgets["btn_toggle_skills"].cget("text"), "")

        # Test fallback
        panel._icon_helper.get_icon = MagicMock(return_value="❓")
        panel._update_toggle_button_visuals()
        self.assertEqual(panel.widgets["btn_toggle_skills"].cget("text"), "[🌐 All Skills]")

if __name__ == '__main__':
    unittest.main()
