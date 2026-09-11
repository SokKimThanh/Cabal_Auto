import tkinter as tk
from ui.panels.skill_panel import SkillPanel

class MockApp:
    def __init__(self):
        self.root = self
        self._callbacks = {}
        self.skill_slots = {'attack_combo': [], 'buff_lane': []}
        self._current_class_id = 1

    def _t(self, x):
        return x

    def register_callback(self, *args, **kwargs):
        pass

root = tk.Tk()
app = MockApp()
panel = SkillPanel(root, app)
print("SkillPanel loaded successfully")
