import re

with open("ui/tabs/hunt_tab.py", "r", encoding="utf-8") as f:
    content = f.read()

toast_code = """    def show_toast(self, message: str, duration_ms: int = 2000, level: str = "warn"):
        if getattr(self, "toast_timer", None):
            self.after_cancel(self.toast_timer)
            self.toast_timer = None

        if not hasattr(self, "toast_label"):
            self.toast_label = tk.Label(
                self,
                text="",
                bg=UI.COLOR_WARNING if level == "warn" else (UI.COLOR_DANGER if level == "error" else UI.COLOR_INFO),
                fg="white",
                font=(UI.FONT_FAMILY, 10),
                relief="flat",
                anchor="center"
            )

        self.toast_label.config(
            text=message,
            bg=UI.COLOR_WARNING if level == "warn" else (UI.COLOR_DANGER if level == "error" else UI.COLOR_INFO)
        )
        self.toast_label.place(relx=0.5, rely=0.9, anchor="center")

        def _hide():
            self.toast_label.place_forget()
            self.toast_timer = None

        self.toast_timer = self.after(duration_ms, _hide)

"""

if "def show_toast" not in content:
    content = re.sub(r'(class HuntTab\(ttk\.Frame\):[\s\S]*?def __init__\(self, parent, app\):\n(?:.*\n)*?        self._build_ui\(\)\n)', r'\1\n' + toast_code, content)

    with open("ui/tabs/hunt_tab.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched.")
else:
    print("Already has show_toast")
