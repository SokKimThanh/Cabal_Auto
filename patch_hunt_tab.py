import re

with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

search = """        # Debug Vision Action Bar
        self.debug_action_frame = tk.Frame(self.left_col_frame, bg=UI.BG_BASE)
        self.debug_action_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(UI.SPACE_MD, 0))

        from ui.components.vision_snapshot_debugger import VisionSnapshotDebugger
        self.vision_debugger = VisionSnapshotDebugger(self.app)

        from ui.components.icon_button import create_icon_button
        self.btn_debug_vision = create_icon_button(
            self.debug_action_frame,
            icon_name="search",
            text=self.app._t("vision_debugger.button") if hasattr(self.app, "_t") else "Debug Vision",
            command=self.vision_debugger.open_debugger,
            button_type="neutral"
        )
        self.btn_debug_vision.pack(side=tk.RIGHT)"""

replace = """        # Embedded Vision Snapshot Debugger Panel
        self.debug_action_frame = tk.Frame(self.left_col_frame, bg=UI.BG_BASE)
        self.debug_action_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(UI.SPACE_MD, 0))

        from ui.components.vision_snapshot_debugger import VisionSnapshotDebugger
        self.vision_debugger = VisionSnapshotDebugger(self.debug_action_frame, self.app)
        self.vision_debugger.pack(fill=tk.BOTH, expand=True)
        self.vision_debugger.start_listening()

        # Cleanup when the widget is destroyed
        self.vision_debugger.bind("<Destroy>", lambda e: self.vision_debugger.stop_listening() if str(e.widget) == str(self.vision_debugger) else None)"""

new_content = content.replace(search, replace)

if new_content == content:
    print("Replace failed")
else:
    with open("ui/tabs/hunt_tab.py", "w") as f:
        f.write(new_content)
    print("Replace success")
