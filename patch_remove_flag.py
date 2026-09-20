with open("ui/views/icon_manager_frame.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove init
old_init = """        self._is_refreshing_tree = False
        self._suppress_tree_events = False
        self._suppress_available_elements_event = False"""
new_init = """        self._is_refreshing_tree = False
        self._suppress_tree_events = False
        self._current_available_element_selection = None"""
content = content.replace(old_init, new_init)

# 2. Update on_select
old_select = """    def _on_available_element_select(self, event=None):
        if getattr(self, '_suppress_available_elements_event', False):
            return

        selection = self.available_elements_tree.selection()"""
new_select = """    def _on_available_element_select(self, event=None):
        selection = self.available_elements_tree.selection()
        # Prevent infinite loop by checking if selection actually changed
        if not selection:
            self._current_available_element_selection = None
            return

        if self._current_available_element_selection == selection[0]:
            return

        self._current_available_element_selection = selection[0]"""
content = content.replace(old_select, new_select)

# 3. Update sync
old_sync = """        self._suppress_available_elements_event = True
        try:
            if target_node:
                self.available_elements_tree.selection_set(target_node)
                self.available_elements_tree.see(target_node)
            else:
                # Clear selection if no mapped node found for this icon
                if self.available_elements_tree.selection():
                    self.available_elements_tree.selection_remove(*self.available_elements_tree.selection())
        finally:
            self._suppress_available_elements_event = False"""

new_sync = """        if target_node:
            self._current_available_element_selection = target_node
            self.available_elements_tree.selection_set(target_node)
            self.available_elements_tree.see(target_node)
        else:
            self._current_available_element_selection = None
            if self.available_elements_tree.selection():
                self.available_elements_tree.selection_remove(*self.available_elements_tree.selection())"""
content = content.replace(old_sync, new_sync)


# 4. Also fix tree clear in _on_refresh to clear tracking
old_refresh = """        if hasattr(self, 'available_elements_tree'):
            if self.available_elements_tree.selection():
                self.available_elements_tree.selection_remove(*self.available_elements_tree.selection())
            self.available_elements_tree.focus('')"""
new_refresh = """        if hasattr(self, 'available_elements_tree'):
            self._current_available_element_selection = None
            if self.available_elements_tree.selection():
                self.available_elements_tree.selection_remove(*self.available_elements_tree.selection())
            self.available_elements_tree.focus('')"""
content = content.replace(old_refresh, new_refresh)


with open("ui/views/icon_manager_frame.py", "w", encoding="utf-8") as f:
    f.write(content)
