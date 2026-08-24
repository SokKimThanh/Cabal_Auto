with open("ui/windows/hotkey_diag_dialog.py", "r") as f:
    text = f.read()

text = text.replace("    try:\n        import keyboard\n", "    try:\n        import keyboard  # noqa\n")

with open("ui/windows/hotkey_diag_dialog.py", "w") as f:
    f.write(text)

with open("ui/windows/monster_manager_win.py", "r") as f:
    text = f.read()

text = text.replace("class MonsterManagerWin:\n\n\n\n", "class MonsterManagerWin:\n")
text = text.replace("from tkinter import ttk, messagebox\n\n\nclass MonsterManagerWin:", "from tkinter import ttk, messagebox\n\nclass MonsterManagerWin:")

with open("ui/windows/monster_manager_win.py", "w") as f:
    f.write(text)
