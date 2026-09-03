import re

with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

# Make sure to bind Enter and Double-Click on detected list
search_bind = """        self.app.btn_promote_monster.pack(pady=(0, 4))
        self.app._create_tooltip(
            self.app.btn_promote_monster, self.app._t("monster_promote")
        )

        tk.Label(self.configured_container"""

replace_bind = """        self.app.btn_promote_monster.pack(pady=(0, 4))
        self.app._create_tooltip(
            self.app.btn_promote_monster, self.app._t("monster_promote")
        )

        # Bindings for promotion
        self.app.detected_monsters_listbox.bind("<Double-1>", lambda e: getattr(self.app, 'promote_detected_monster', lambda x: None)(self.app.detected_monsters_listbox.curselection()))
        self.app.detected_monsters_listbox.bind("<Return>", lambda e: getattr(self.app, 'promote_detected_monster', lambda x: None)(self.app.detected_monsters_listbox.curselection()))

        # Basic Drag-and-Drop setup
        def on_drag_start(event):
            if not self.app.detected_monsters_listbox.curselection():
                return
            idx = self.app.detected_monsters_listbox.curselection()[0]
            # Payload is the idx (to look up the snapshot item)
            event.widget._dnd_data = idx
            event.widget.config(cursor="hand2")

        def on_drag_motion(event):
            event.widget.config(cursor="hand2")

        def on_drag_release(event):
            event.widget.config(cursor="")
            # Check if released over configured listbox
            x, y = event.widget.winfo_pointerxy()
            target = event.widget.winfo_containing(x, y)
            if target == getattr(self.app, 'monster_rotation_listbox', None):
                if hasattr(event.widget, '_dnd_data'):
                    idx = event.widget._dnd_data
                    getattr(self.app, 'promote_detected_monster', lambda x: None)((idx,))

        self.app.detected_monsters_listbox.bind("<ButtonPress-1>", on_drag_start)
        self.app.detected_monsters_listbox.bind("<B1-Motion>", on_drag_motion)
        self.app.detected_monsters_listbox.bind("<ButtonRelease-1>", on_drag_release)

        tk.Label(self.configured_container"""

content = content.replace(search_bind, replace_bind)

with open("ui/tabs/hunt_tab.py", "w") as f:
    f.write(content)
