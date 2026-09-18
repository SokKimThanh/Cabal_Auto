import re

with open("ui/components/icon_button.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add mappable_name and mappable_comp to the arguments
arg_pattern = r"(auto_hover_disabled:\s*bool\s*=\s*True,)"
arg_replacement = r"\1\n    mappable_name: Optional[str] = None,\n    mappable_comp: str = 'button',"
content = re.sub(arg_pattern, arg_replacement, content)

# Add logic inside the function to register
logic_pattern = r"(def create_icon_button[\s\S]*?\"\"\"[\s\S]*?\"\"\")"
logic_replacement = r"\1\n\n    if mappable_name:\n        try:\n            from ui.utils.component_registry import get_component_registry\n            get_component_registry().register_component(\n                name=mappable_name,\n                mod=\"ui\",\n                comp=mappable_comp,\n                element_id=icon_name\n            )\n        except Exception as e:\n            import logging\n            logging.getLogger(__name__).warning(f\"Failed to auto-register component {mappable_name}: {e}\")"

content = re.sub(logic_pattern, logic_replacement, content, count=1)

with open("ui/components/icon_button.py", "w", encoding="utf-8") as f:
    f.write(content)
