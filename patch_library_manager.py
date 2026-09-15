import re

with open("ui/windows/library_manager.py", "r") as f:
    content = f.read()

# Make sure UIHelper is imported
if "from ui.helpers import UIHelper" not in content:
    content = re.sub(
        r'(import tkinter as tk\n)',
        r'\1from ui.helpers import UIHelper\n',
        content
    )

content = content.replace('self._icon("search", "🔍")', 'UIHelper.icon("search", "🔍")')

with open("ui/windows/library_manager.py", "w") as f:
    f.write(content)
