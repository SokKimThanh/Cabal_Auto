import re

with open("app_gui.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "self.task_scheduler.schedule_recurring_task(\"poll_log_queue\"" in line:
        continue
    if "self.task_scheduler.schedule_recurring_task(\"update_logs_metrics\"" in line:
        continue

    if "def _update_logs_metrics(self):" in line or \
       "def _poll_log_queue(self):" in line or \
       "def _icon(" in line or \
       "def _create_tooltip(self, widget, text):" in line or \
       "def _destroy_widget_tooltip(self, widget):" in line:
        skip = True
        continue

    if skip:
        # Check if we're entering a new function (or end of file/class)
        # But handle docstrings and nested functions carefully.
        # Since these are methods in App, let's just use simple indent tracking
        if line.startswith("    def ") and not ("_update_logs_metrics" in line or "_poll_log_queue" in line or "_icon(" in line or "_create_tooltip(" in line or "_destroy_widget_tooltip(" in line):
            skip = False

    if not skip:
        new_lines.append(line)

with open("app_gui.py", "w") as f:
    f.writelines(new_lines)
