import re
with open("ui/components/compact_window_selector.py", "r") as f:
    content = f.read()

content = content.replace(
    "def __init__(\n        self,\n        parent: tk.Widget,\n        on_window_selected: Callable[[Dict[str, Any]], None],\n        window_controller: Any,  # AppWindowController instance\n        root: Any,\n    ):",
    "def __init__(\n        self,\n        parent: tk.Widget,\n        on_window_selected: Callable[[Dict[str, Any]], None],\n        window_controller: Any,  # AppWindowController instance\n        root: Any,\n    ):\n        self.state_controller = getattr(root, 'state_controller', root) # Fallback to support both App and App.root"
)
with open("ui/components/compact_window_selector.py", "w") as f:
    f.write(content)
