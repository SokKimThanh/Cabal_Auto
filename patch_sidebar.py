import re

with open("ui/components/sidebar_component.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add registration code in sidebar
registry_import = "from ui.utils.component_registry import get_component_registry\n"
if "from ui.utils.component_registry" not in content:
    content = re.sub(r"(from lib.ui_style_v2 import UIStyleV2 as UI)", r"\1\n" + registry_import, content)

logic_pattern = r"(key, view_target, font, _unused_target, icon = item)"
logic_replacement = r"\1\n\n            # Auto-register sidebar buttons to the Component Registry\n            if isinstance(icon, str):\n                # Create a human readable name from the view_target, e.g., 'class_manager' -> 'Class Manager'\n                human_name = ' '.join(word.capitalize() for word in view_target.split('_'))\n                get_component_registry().register_component(\n                    name=f\"Sidebar: {human_name}\",\n                    mod=\"ui\",\n                    comp=\"sidebar_button\",\n                    element_id=icon\n                )"

content = re.sub(logic_pattern, logic_replacement, content, count=1)

with open("ui/components/sidebar_component.py", "w", encoding="utf-8") as f:
    f.write(content)
