import re

with open("ui/views/activity_logs_frame.py", "r") as f:
    content = f.read()

import_pattern = re.compile(r'(from lib.ui_style_v2 import UIStyleV2 as UI\n)')
content = import_pattern.sub(r'\1import queue\nfrom datetime import datetime\nfrom lib.system.hunt_logger import get_hunt_logger\n', content)

# Inject init tasks
init_pattern = re.compile(r'(self\.text_widget\.config\(yscrollcommand=self\.scrollbar\.set\)\n)')
init_injection = r"""\1
        # Start background polling loops via the TaskScheduler
        if hasattr(self.app, "task_scheduler"):
            self.app.task_scheduler.schedule_recurring_task("poll_log_queue", 100, self._poll_log_queue)
            self.app.task_scheduler.schedule_recurring_task("update_logs_metrics", 1000, self._update_logs_metrics)
"""
content = init_pattern.sub(init_injection, content)

# Append methods
methods = """
    def _poll_log_queue(self):
        \"\"\"Poll log messages from HuntLogger and append to UI.\"\"\"
        try:
            logger = get_hunt_logger()
            if hasattr(logger, "ui_queue"):
                if getattr(logger, "dropped_log_count", 0) > 0:
                    dropped = logger.dropped_log_count
                    logger.dropped_log_count = 0
                    warn_msg = f"[!] Đã bỏ qua {dropped} dòng log do quá tải"
                    self.append_message(warn_msg)

                lines_processed = 0
                while lines_processed < 50:
                    try:
                        record = logger.ui_queue.get_nowait()
                        # QueueHandler.prepare() automatically formats the message into record.message in Python 3.2+
                        if hasattr(record, "message"):
                            msg = record.message
                        else:
                            msg = record.getMessage()

                        # Pass both formatted string and record level name for filtering
                        self.append_message(msg, record.levelname)
                        lines_processed += 1
                    except queue.Empty:
                        break

                if lines_processed > 0:
                    self.trim_to_limit(1000)

        except Exception as e:
            print(f"Error polling logs: {e}")

    def _update_logs_metrics(self):
        \"\"\"Update metrics on the bottom logs header.\"\"\"
        try:
            fps = 0.0
            scans = 0
            running_time = "00:00:00"

            logger = get_hunt_logger()
            if hasattr(logger, "session_start"):
                duration = (datetime.now() - logger.session_start).total_seconds()
                h = int(duration // 3600)
                m = int((duration % 3600) // 60)
                s = int(duration % 60)
                running_time = f"{h:02d}:{m:02d}:{s:02d}"

            if hasattr(self.app, "logs_metrics_label") and self.app.logs_metrics_label:
                self.app.logs_metrics_label.config(
                    text=f"⚡ FPS: {fps:.1f} | 🎯 Quét: {scans} | ⏱ Chạy: {running_time}"
                )

        except Exception:
            pass
"""
content += methods

with open("ui/views/activity_logs_frame.py", "w") as f:
    f.write(content)
