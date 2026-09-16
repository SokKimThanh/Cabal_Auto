import tkinter as tk

root = tk.Tk()

btn1 = tk.Button(root, text="Button 1")
btn1.pack(pady=10)


def create_tooltip(widget, text):
    def on_enter(event):
        print(f"enter: {text}")

    def on_leave(event):
        print("leave")

    if hasattr(widget, "_tooltip_enter_id"):
        widget.unbind("<Enter>", widget._tooltip_enter_id)
    if hasattr(widget, "_tooltip_leave_id"):
        widget.unbind("<Leave>", widget._tooltip_leave_id)

    enter_id = widget.bind("<Enter>", on_enter, add="+")
    leave_id = widget.bind("<Leave>", on_leave, add="+")

    widget._tooltip_enter_id = enter_id
    widget._tooltip_leave_id = leave_id

create_tooltip(btn1, "text1")
create_tooltip(btn1, "text2")

print("Bindings for btn1 <Enter>:", btn1.bind("<Enter>"))

root.after(100, root.destroy)
root.mainloop()
