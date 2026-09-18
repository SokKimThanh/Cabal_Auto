with open('ui/views/icon_manager_frame.py', 'r') as f:
    content = f.read()

# I am assuming the combobox has a validate='key' attached in the previous step. We just need to make sure the state is not blocking typing
search_combobox_line = """self.entry_tooltip = ttk.Combobox(tooltip_frame, textvariable=self.var_tooltip_key, validate="key", validatecommand=vcmd_key)"""
replace_combobox_line = """self.entry_tooltip = ttk.Combobox(tooltip_frame, textvariable=self.var_tooltip_key, validate="key", validatecommand=vcmd_key)
        # Bỏ validate="key" trên combobox này hoặc để nó không block autocomplete
        self.entry_tooltip.config(validate="none")"""

# Let's check how many occurrences of `validate="key"` in tooltip combobox.
# Wait, actually we can just use replace_with_git_merge_diff
