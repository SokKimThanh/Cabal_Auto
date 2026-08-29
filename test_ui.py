import tkinter as tk
from dialogs.monster_edit import MonsterEditDialog
import sys

root = tk.Tk()
try:
    dialog = MonsterEditDialog(root, monster={"id": "m123", "name": "Goblin", "hp": 500, "description": "A green monster"})
    print("UI setup successful:", dialog.name_entry.get())
    dialog.destroy()
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
