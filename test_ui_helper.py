import tkinter as tk
from ui.helpers.ui_helper import UIHelper

root = tk.Tk()

btn1 = tk.Button(root, text="Button 1")
btn1.pack(pady=10)

UIHelper.create_tooltip(btn1, "Tooltip 1")

bindings_enter1 = btn1.bind("<Enter>")
print(bindings_enter1)

UIHelper.create_tooltip(btn1, "Tooltip 2")

bindings_enter2 = btn1.bind("<Enter>")
print(bindings_enter2)

root.destroy()
