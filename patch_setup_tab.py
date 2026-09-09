import re

with open("ui/tabs/setup_tab.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Default to expanded
content = content.replace(
    "is_visible_var = tk.BooleanVar(value=False)",
    "is_visible_var = tk.BooleanVar(value=True)"
)

# 2. Toggle state initialization
toggle_init = """        content_builder(content_frame)

        # Initial render based on is_visible_var
        if is_visible_var.get():
            btn_text_var.set(f"▼ {self._t(title_key)}")
            content_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
            content_frame.grid_columnconfigure(1, weight=1)
            content_frame.grid_columnconfigure(3, weight=1)

        # Store these for _update_setup_visibility to show/hide the entire group"""
content = content.replace(
    """        content_builder(content_frame)

        # Store these for _update_setup_visibility to show/hide the entire group""",
    toggle_init
)


# 3. Remove Configuration Mode Section
mode_section_regex = r"""        # Section 1: Configuration Mode.*?# Section 2: Global Hotkeys"""

content = re.sub(mode_section_regex, "        # Section 2: Global Hotkeys", content, flags=re.DOTALL)

# 4. Remove _on_setup_mode_changed
on_mode_change_regex = r"""    def _on_setup_mode_changed\(self\):.*?self\._update_setup_visibility\(\)"""
content = re.sub(on_mode_change_regex, "", content, flags=re.DOTALL)

# 5. Remove or simplify _update_setup_visibility
update_vis_regex = r"""    def _update_setup_visibility\(self\):.*?self\.window_group\.grid\(\)"""
content = re.sub(update_vis_regex, """    def _update_setup_visibility(self):
        # All groups are always visible now since we only have advanced mode.
        self.adv_group.grid()
        self.window_group.grid()""", content, flags=re.DOTALL)

with open("ui/tabs/setup_tab.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied to setup_tab.py")
