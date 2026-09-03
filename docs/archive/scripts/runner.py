
from app_gui import App
import tkinter as tk
import unittest.mock
import sys
import json

sys.modules['win32gui'] = unittest.mock.MagicMock()
sys.modules['lib.system.window_manager'] = unittest.mock.MagicMock()
sys.modules['lib.features.hunt.window_selection_service'] = unittest.mock.MagicMock()
sys.modules['lib.vision.vision_engine'] = unittest.mock.MagicMock()

app = App()
app.geometry("1366x768")
app.tk.call('tk', 'scaling', 1.5 * 72 / 72.0)

app.update_idletasks()
app.update()
app.after(50)
app.update()

global_apply = app.global_apply_btn
hunt_tab = None
def find_hunt_tab(widget):
    if hasattr(widget, 'skill_strip_frame'):
        return widget
    for child in widget.winfo_children():
        res = find_hunt_tab(child)
        if res: return res
    return None
hunt_tab = find_hunt_tab(app)

skill_strip_y = hunt_tab.skill_strip_frame.winfo_rooty() if hunt_tab else 0
skill_strip_h = hunt_tab.skill_strip_frame.winfo_height() if hunt_tab else 0
logs_header_y = app.logs_header_frame.winfo_rooty()

overlap_logs = (skill_strip_y + skill_strip_h) > logs_header_y

app_y = app.winfo_rooty()
app_h = app.winfo_height()
app_bottom = app_y + app_h

apply_frame = global_apply.master
apply_frame_bottom = apply_frame.winfo_rooty() + apply_frame.winfo_height()

overlap_chrome = apply_frame_bottom > app_bottom

print(json.dumps({"overlap_logs": overlap_logs, "overlap_chrome": overlap_chrome}))
