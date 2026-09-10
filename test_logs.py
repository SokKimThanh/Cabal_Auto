import tkinter as tk
from app_gui import App
from ui.views.activity_logs_frame import ActivityLogsFrame

root = tk.Tk()
class MockApp:
    def _t(self, key, default=""): return default
    def bind_text(self, widget, key): pass

app = MockApp()
frame = ActivityLogsFrame(root, app)
frame.pack(fill="both", expand=True)

# Test search, etc later. Just verify it builds.
root.update()
print("Built successfully.")
