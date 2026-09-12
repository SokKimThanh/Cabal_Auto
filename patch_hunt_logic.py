with open('ui/controllers/app_state_controller.py', 'r') as f:
    content = f.read()

# Replace self.ui_vars['...'] and self.ui_vars.get('...') with self.get_ui_var(...)
# And also remove _validate_hunt_prerequisites entirely (we will update callers later if needed, but it seems there's none directly or we can just remove it and use WindowSelectionService directly, but it's safe to just delegate it properly)
content = content.replace("self.ui_vars[\"target_policy\"].get()", "self.get_ui_var(\"target_policy\")")
content = content.replace("\"target_policy\" in self.ui_vars", "self.get_ui_var(\"target_policy\") is not None")

content = content.replace("self.ui_vars[\"setup_template\"].get()", "self.get_ui_var(\"setup_template\")")
content = content.replace("\"setup_template\" in self.ui_vars", "self.get_ui_var(\"setup_template\") is not None")

content = content.replace("self.ui_vars.get(attr_name.replace(\"_var\", \"\"))", "self.get_ui_var(attr_name.replace(\"_var\", \"\"))")
# For the var is None check
content = content.replace("if var is None:\n                cfg.setdefault(key, default)\n                continue\n            raw_value = var.get()", "if var is None:\n                cfg.setdefault(key, default)\n                continue\n            raw_value = var")


content = content.replace("bool(\n            self.ui_vars[\"bring_front\"].get() if \"bring_front\" in self.ui_vars and self.ui_vars[\"bring_front\"].get() else False\n        )", "bool(self.get_ui_var(\"bring_front\"))")


with open('ui/controllers/app_state_controller.py', 'w') as f:
    f.write(content)
