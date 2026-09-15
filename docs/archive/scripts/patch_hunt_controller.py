with open("lib/ui/controllers/hunt_controller.py", "r") as f:
    content = f.read()

new_methods = """
    def on_start_stop_clicked(self):
        if self.app_root._action_locked:
            return

        self.app_root._action_locked = True

        if hasattr(self.app_root.start_stop_btn, "configure"):
            self.app_root.start_stop_btn.configure(state="disabled")
        elif hasattr(self.app_root.start_stop_btn, "config"):
            self.app_root.start_stop_btn.config(state="disabled")

        is_running = self.state_controller.is_bot_running()
        if is_running:
            self.request_stop_hunt()
        else:
            self.request_start_hunt()

        if hasattr(self.app_root, "task_scheduler"):
            self.app_root.task_scheduler.schedule_task("reenable_start_stop_btn", 500, self.reenable_start_stop_btn, recurring=False)

    def reenable_start_stop_btn(self):
        self.app_root._action_locked = False
        if hasattr(self.app_root.start_stop_btn, "configure"):
            self.app_root.start_stop_btn.configure(state="normal")
        elif hasattr(self.app_root.start_stop_btn, "config"):
            self.app_root.start_stop_btn.config(state="normal")
        self.refresh_start_stop_visual()

    def refresh_start_stop_visual(self):
        if not hasattr(self.app_root, "start_stop_btn"):
            return
        is_running = self.state_controller.is_bot_running()
        if is_running:
            self.app_root.start_stop_btn.config(
                text=self.app_root._t("btn_stop"),
                bg="#e74c3c",
                activebackground="#c0392b"
            )
        else:
            self.app_root.start_stop_btn.config(
                text=self.app_root._t("btn_start"),
                bg="#2ecc71",
                activebackground="#27ae60"
            )
"""
content += new_methods

with open("lib/ui/controllers/hunt_controller.py", "w") as f:
    f.write(content)
