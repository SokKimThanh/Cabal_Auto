import tkinter as tk
from ui.views.activity_logs_frame import ActivityLogsFrame

root = tk.Tk()
class MockApp:
    def _t(self, key, default=""): return default
    def bind_text(self, widget, key): pass

app = MockApp()
# provide mock methods so it doesn't crash on init if missing
ActivityLogsFrame.do_search = lambda self: None
ActivityLogsFrame.copy_logs = lambda self: None
ActivityLogsFrame.open_log_folder = lambda self: None

frame = ActivityLogsFrame(root, app)
frame.pack(fill="both", expand=True)
root.update()
print("Built successfully.")
