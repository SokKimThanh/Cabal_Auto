import sys

with open("ui/views/icon_manager_frame.py", "r") as f:
    content = f.read()

content = content.replace("from tkinter import ttk\n", "")
content = content.replace("class IconManagerFrame", "\nclass IconManagerFrame")
content = content.replace("    \n", "\n")
content = content.replace("        \n", "\n")
content = content.replace(" # For visualizing", "  # For visualizing")
content = content.replace(" # Left Sidebar (Master List)", "  # Left Sidebar (Master List)")

with open("ui/views/icon_manager_frame.py", "w") as f:
    f.write(content.strip() + "\n")
