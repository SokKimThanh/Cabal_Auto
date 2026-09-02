import sys, unittest.mock
sys.modules['lib.system.window_manager'] = unittest.mock.MagicMock()

import tkinter as tk
from app_gui import App

def dump_tree(widget, indent=0):
    try:
        req_h = widget.winfo_reqheight()
        h = widget.winfo_height()
        name = widget.winfo_name()
        cname = widget.winfo_class()
        print("  " * indent + f"{name} ({cname}) req={req_h} act={h}")
        for child in widget.winfo_children():
            dump_tree(child, indent + 1)
    except tk.TclError as e:
        print(f"dump_tree: failed for {widget!r}: {e}", file=sys.stderr)

def main():
    root = None
    try:
        root = App()
        root.geometry('1366x768')
        root.update_idletasks()

        print("\n--- TREE DUMP ---")
        dump_tree(root.main_shell)
    finally:
        if root is not None:
            root.destroy()

if __name__ == '__main__':
    main()
