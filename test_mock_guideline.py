import tkinter as tk
root = tk.Tk()
from ui.tabs.hunt_tab import HuntTab

class MockApp:
    def __init__(self):
        self.hunt_cfg = {"combo": {"combo_start_key": "Alt+1"}}
        self.skills = [{"name": "SkillBuff", "key": "1", "type": "buff"}]
        self.skill_slot_vars = [tk.StringVar() for _ in range(6)]
        self.skill_slot_boxes = []
        self.skill_slot_key_labels = []
        self.skill_slot_stats_labels = [tk.Label(root) for _ in range(6)]
        self._t = lambda x: x
        self.auto_combo_var = tk.BooleanVar()
    def _refresh_monster_select_options(self): pass

app = MockApp()
tab = HuntTab(root, app)
print(tab.toast_label.winfo_class() if hasattr(tab, 'toast_label') else "No toast label")
tab.show_toast("Message")
print(tab.toast_label.winfo_manager())
root.destroy()
