with open("ui/windows/timing_calc_dialog.py", "r") as f:
    text = f.read()

text = text.replace("\\n", "\n")

with open("ui/windows/timing_calc_dialog.py", "w") as f:
    f.write(text)
