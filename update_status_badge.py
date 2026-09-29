with open('ui/components/status_badge.py', 'r') as f:
    content = f.read()

content = content.replace('"icon": "●",', '"icon": "record",')

content = content.replace(
    'self.icon_label = tk.Label(',
    '''from ui.components.icon_button import create_icon_label
        self.icon_label = create_icon_label(
            parent=self.badge,
            icon_name=style["icon"],
            icon_fallback="●",
            text=style["label"],
            font=UI.FONT_SMALL,
            bg=style["bg"],
            fg=style["fg"],
            element_id=f"badge_{self.status}"
        )
        # remove remaining tk.Label kwargs by skipping them'''
)

print("Let's do this manually instead of script")
