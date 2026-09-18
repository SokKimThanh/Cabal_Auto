import re

with open('ui/views/icon_manager_frame.py', 'r') as f:
    content = f.read()

search_code = """    def _on_name_changed(self, *args):
        if self._current_state == "ADD":
            name = self.var_name.get()
            if name:
                # slugify logic: lowercase, replace spaces and special chars with underscore
                import re
                slug = name.lower().strip()
                slug = re.sub(r'[^a-z0-9]+', '_', slug)
                slug = slug.strip('_')"""

replace_code = """    def _on_name_changed(self, *args):
        if self._current_state == "ADD":
            name = self.var_name.get()
            if name:
                slug = name.strip()
                slug = self.to_non_accent_vietnamese(slug)
                slug = re.sub(r'[^a-z0-9]+', '_', slug)
                slug = slug.strip('_')"""

content = content.replace(search_code, replace_code)

with open('ui/views/icon_manager_frame.py', 'w') as f:
    f.write(content)
