from app_gui import App
import tkinter as tk
import unittest.mock
import sys

sys.modules['win32gui'] = unittest.mock.MagicMock()
sys.modules['lib.system.window_manager'] = unittest.mock.MagicMock()
sys.modules['lib.features.hunt.window_selection_service'] = unittest.mock.MagicMock()
sys.modules['lib.vision.vision_engine'] = unittest.mock.MagicMock()

app = App()
app.geometry("1366x768")
for _ in range(10):
    app.update_idletasks()
    app.update()

apply_frame = app.global_apply_btn.master

# Check what the direct children of `app` are.
for child in app.winfo_children():
    print(f"Child: {child}, Type: {type(child)}")
    print(f"  pack_info: {child.pack_info() if child.winfo_manager() == 'pack' else 'Not packed'}")
    print(f"  winfo_ismapped: {child.winfo_ismapped()}")
    print(f"  winfo_height: {child.winfo_height()}")
    print(f"  winfo_reqheight: {child.winfo_reqheight()}")
