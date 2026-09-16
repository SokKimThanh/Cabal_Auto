import tkinter as tk
from ui.helpers.ui_helper import UIHelper

root = tk.Tk()
btn1 = tk.Button(root, text="Test")
btn1.pack()

UIHelper.create_tooltip(btn1, "Tip 1")
UIHelper.create_tooltip(btn1, "Tip 2")
print("Bindings for btn1 <Enter>:", btn1.bind("<Enter>"))

UIHelper.destroy_widget_tooltip(btn1)
print("Bindings for btn1 <Enter> after destroy:", btn1.bind("<Enter>"))

root.destroy()
