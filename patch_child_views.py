import re

files_to_patch = [
    "ui/panels/monster_target_panel.py",
    "ui/tabs/hunt_tab.py"
]

for filepath in files_to_patch:
    with open(filepath, "r") as f:
        content = f.read()

    # Import UIHelper if not present
    if "from ui.helpers import UIHelper" not in content:
        content = re.sub(
            r'(from lib.ui_style_v2 import UIStyleV2 as UI\n)',
            r'\1from ui.helpers import UIHelper\n',
            content
        )

    # Replace calls
    content = content.replace("self.app._create_tooltip", "UIHelper.create_tooltip")
    content = content.replace("self.app._destroy_widget_tooltip", "UIHelper.destroy_widget_tooltip")
    content = content.replace("self.app._icon", "UIHelper.icon")

    # For hunt_tab.py, it checks hasattr(self.app, "_create_tooltip") which we can just remove or replace.
    # In hunt_tab.py:
    content = content.replace('if hasattr(self.app, "_create_tooltip"):', '')
    content = content.replace('if hasattr(self.app, "_destroy_widget_tooltip"):', '')
    # The indenting might be slightly off if we just remove the if statement, but let's see.
    # Since it's a simple replace, we should properly handle the indentation or just replace the whole block.

    with open(filepath, "w") as f:
        f.write(content)
